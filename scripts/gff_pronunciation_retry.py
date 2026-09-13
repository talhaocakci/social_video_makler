#!/usr/bin/env python3
"""Regenerate selected Qwen pronunciation turns without changing speaker identity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


LOCAL_WHISPER = Path("/Users/talhaocakci/Projects/local_whisper")
sys.path.insert(0, str(LOCAL_WHISPER))

import gff_tts_pipeline as pipeline  # type: ignore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("generation_dir", type=Path)
    parser.add_argument("--turn-ids", required=True)
    parser.add_argument("--seed-rotation", type=int, required=True)
    parser.add_argument(
        "--terminal-period",
        action="store_true",
        help="Add non-spoken terminal punctuation to stabilize isolated-word synthesis.",
    )
    parser.add_argument(
        "--title-case",
        action="store_true",
        help="Title-case the isolated source token without adding spoken content.",
    )
    args = parser.parse_args()

    if args.seed_rotation < 1:
        raise ValueError("retry seed rotation must be at least one")
    source = json.loads(args.source.resolve().read_text(encoding="utf-8"))
    output_dir = args.generation_dir.resolve()
    manifest_path = output_dir / "manifest.json"
    plan = json.loads(manifest_path.read_text(encoding="utf-8"))
    if plan.get("source_sha256") != pipeline.sha256_bytes(
        json.dumps(source, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ):
        raise ValueError("generation manifest is not bound to the supplied source")
    requested = {value.strip() for value in args.turn_ids.split(",") if value.strip()}
    turns = {str(turn["turn_id"]): turn for turn in source.get("turns") or []}
    missing = requested - set(turns)
    if missing:
        raise ValueError(f"unknown turn ids: {sorted(missing)}")
    artifacts = {
        str(row.get("turn_id")): row
        for row in plan.get("artifacts") or []
        if row.get("kind") == "guided_communication_turn"
    }
    if requested - set(artifacts):
        raise ValueError("selected turn is absent from generation manifest")

    model = pipeline.load_model(str(pipeline.BASE_SNAPSHOT))
    for turn_id in sorted(requested):
        turn = turns[turn_id]
        side = str(turn["speaker_side"])
        assignment = plan["voice_assignments"][side]
        seed_material = (
            f"{assignment['voice_assignment_id']}|{turn['turn_id']}|{turn['text']}"
            f"|retry={args.seed_rotation}"
        )
        artifact_seed = pipeline.stable_index(seed_material, 2**31 - 1)
        pipeline.mx.random.seed(artifact_seed)
        pipeline.np.random.seed(artifact_seed)
        synthesis_text = turn["text"].strip()
        if args.title_case:
            synthesis_text = synthesis_text[:1].upper() + synthesis_text[1:]
        synthesis_text += "." if args.terminal_period else ""
        generated = pipeline.save_generation(
            model,
            output_dir / "work" / "turns" / f"{turn_id}.wav",
            text=synthesis_text,
            lang_code=plan["language"],
            ref_audio=assignment["reference_audio_path"],
            ref_text=assignment["profile"]["reference_text"],
            instruct=pipeline.delivery_instruction(
                pipeline.infer_delivery_hint(turn["text"], plan["language"]),
                asset_type="guided_communication",
            ),
            split_pattern="",
            temperature=0.8,
            top_k=50,
            top_p=0.95,
            repetition_penalty=1.5,
        )
        generated.update(
            {
                "kind": "guided_communication_turn",
                "turn_id": turn_id,
                "speaker_side": side,
                "speaker_label": turn["speaker_label"],
                "voice_assignment_id": assignment["voice_assignment_id"],
                "seed": artifact_seed,
                "content_seed_rotation": args.seed_rotation,
                "synthesis_text": synthesis_text,
                "delivery_hint": pipeline.infer_delivery_hint(turn["text"], plan["language"]),
                "text_sha256": pipeline.sha256_bytes(turn["text"].encode("utf-8")),
                "intended_for_upload": False,
            }
        )
        artifacts[turn_id].clear()
        artifacts[turn_id].update(generated)

    pipeline.render_dialogue_master(source, plan, output_dir)
    pipeline.audit_speaker_consistency(model, plan)
    pipeline.release_model(model)
    plan.setdefault("selective_retries", []).append(
        {"turn_ids": sorted(requested), "content_seed_rotation": args.seed_rotation}
    )
    manifest_path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
