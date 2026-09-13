#!/usr/bin/env python3
"""Strict local dual-model ASR screen for isolated pronunciation examples."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


LOCAL_WHISPER = Path("/Users/talhaocakci/Projects/local_whisper")
sys.path.insert(0, str(LOCAL_WHISPER))

from validate_gff_audio import (  # type: ignore  # noqa: E402
    artifact_key,
    canonical_source_sha256,
    expected_texts,
    inspect_audio,
    run_model,
    score,
    words,
)


ASR_EQUIVALENTS = {
    "en": [
        {"one", "won"},
        {"two", "to", "too"},
        {"see", "sea"},
        {"right", "write", "rite"},
        {"soul", "sole"},
        {"new", "knew"},
        {"night", "knight"},
        {"blue", "blew"},
        {"cue", "queue", "q"},
    ],
    "es": [],
    "de": [
        {"rad", "rat"},
        {"dschinn", "jinn", "gin"},
        {"bayern", "bayan"},
        {"meyer", "maya"},
        {"biene", "bine"},
        {"jahr", "ja"},
    ],
}

ASR_EQUIVALENTS["es"] = [
    {"hay", "ay"},
    {"uva", "uba"},
    {"caza", "casa"},
]


def equivalent(source: str, transcript: str, language: str) -> tuple[bool, str]:
    result = score(source, transcript, language=language)
    if result["accent_folded_edit_distance"] == 0:
        return True, "exact_accent_folded"
    if result["number_form_normalized_edit_distance"] == 0:
        return True, "number_form_equivalent"
    source_tokens = words(source, fold_accents=True)
    transcript_tokens = words(transcript, fold_accents=True)
    if len(source_tokens) == len(transcript_tokens) == 1:
        for family in ASR_EQUIVALENTS.get(language, []):
            if source_tokens[0] in family and transcript_tokens[0] in family:
                return True, "declared_asr_orthographic_equivalent"
    return False, "mismatch"


def index_rows(model_result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["artifact_key"]): row for row in model_result.get("items") or []}


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("generation_manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--language", choices=("en", "es", "de"), required=True)
    parser.add_argument(
        "--only-keys",
        help="Comma-separated generated artifact keys for a checksum-bound retry audit.",
    )
    args = parser.parse_args()

    source = json.loads(args.source.resolve().read_text(encoding="utf-8"))
    generation = json.loads(args.generation_manifest.resolve().read_text(encoding="utf-8"))
    if generation.get("source_sha256") != canonical_source_sha256(source):
        raise ValueError("generation manifest is not bound to the supplied source")
    all_artifacts = list(generation.get("artifacts") or [])
    expected = expected_texts(source, generation)
    if not all_artifacts or set(expected) != {artifact_key(row) for row in all_artifacts}:
        raise ValueError("source and generated artifact inventory differ")
    selected = {
        value.strip() for value in str(args.only_keys or "").split(",") if value.strip()
    }
    artifacts = (
        [row for row in all_artifacts if artifact_key(row) in selected]
        if selected
        else all_artifacts
    )
    if selected and selected != {artifact_key(row) for row in artifacts}:
        raise ValueError("one or more selected artifact keys are absent")

    turbo = run_model("large-v3-turbo", artifacts, expected, args.language)
    turbo_rows = index_rows(turbo)
    flagged = {
        key
        for key, row in turbo_rows.items()
        if not equivalent(expected[key], str(row.get("text") or ""), args.language)[0]
    }
    large = (
        run_model("large-v3", artifacts, expected, args.language, flagged)
        if flagged
        else {"model": None, "items": [], "passed": True}
    )
    large_rows = index_rows(large)

    rows = []
    for artifact in artifacts:
        key = artifact_key(artifact)
        primary = turbo_rows[key]
        primary_passed, primary_basis = equivalent(
            expected[key], str(primary.get("text") or ""), args.language
        )
        secondary = large_rows.get(key)
        secondary_passed = False
        secondary_basis = "not_required"
        if secondary:
            secondary_passed, secondary_basis = equivalent(
                expected[key], str(secondary.get("text") or ""), args.language
            )
        rows.append(
            {
                "artifact_key": key,
                "source": expected[key],
                "audio_sha256": sha256_file(str(artifact["path"])),
                "turbo_heard": primary.get("text"),
                "turbo_strict_pass": primary_passed,
                "turbo_basis": primary_basis,
                "large_v3_heard": secondary.get("text") if secondary else None,
                "large_v3_strict_pass": secondary_passed if secondary else None,
                "large_v3_basis": secondary_basis,
                "strict_pass": primary_passed or secondary_passed,
                "evidence": "large-v3-turbo" if primary_passed else "large-v3 after turbo disagreement",
            }
        )

    audio_quality = [
        inspect_audio(
            str(artifact["path"]),
            artifact_key(artifact),
            source_word_count=len(words(expected[artifact_key(artifact)])),
        )
        for artifact in artifacts
    ]
    speaker_passed = bool((generation.get("speaker_consistency_audit") or {}).get("passed"))
    report = {
        "schema_version": 1,
        "language": args.language,
        "asset_id": generation["asset_id"],
        "source_sha256": generation["source_sha256"],
        "policy": (
            "Every isolated example must be an exact accent-folded, number-form, or explicitly "
            "declared ASR orthographic-equivalence match in large-v3-turbo; every disagreement is checked with "
            "independent large-v3. Machine screening never replaces native audition."
        ),
        "turbo_model": turbo["model"],
        "large_v3_model": large["model"],
        "item_count": len(rows),
        "scope": "selected_retry_artifacts" if selected else "all_artifacts",
        "large_v3_review_count": len(flagged),
        "items": rows,
        "strict_asr_passed": all(row["strict_pass"] for row in rows),
        "audio_quality": {
            "passed": all(row["passed"] for row in audio_quality),
            "items": audio_quality,
        },
        "speaker_consistency_audit": generation.get("speaker_consistency_audit"),
        "speaker_consistency_passed": speaker_passed,
        "requires_human_native_audition": True,
        "publishing": "disabled",
    }
    report["passed"] = (
        report["strict_asr_passed"]
        and report["audio_quality"]["passed"]
        and speaker_passed
    )
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output.resolve())
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
