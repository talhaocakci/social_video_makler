#!/usr/bin/env python3
"""Create a timestamped two-voice local demo track for the Simplified GC example."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "examples" / "guided-communication.simplified.de.json"
DEFAULT_OUTPUT_SOURCE = PROJECT_ROOT / "examples" / "guided-communication.simplified.de.audio.json"
DEFAULT_AUDIO = PROJECT_ROOT / "public" / "generated" / "simplified-restaurant-de.wav"
INTRO_MS = 1750
PAUSE_MS = 380
OUTRO_MS = 1450


def compositor_binary(name: str) -> Path:
    discovered = shutil.which(name)
    if discovered:
        return Path(discovered)
    candidates = sorted(
        PROJECT_ROOT.glob(
            f"node_modules/.pnpm/@remotion+compositor-*/node_modules/@remotion/compositor-*/{name}"
        )
    )
    if not candidates:
        raise RuntimeError(f"{name}_not_found")
    return candidates[0]


def compositor_env(binary: Path) -> dict[str, str]:
    environment = os.environ.copy()
    if sys.platform == "darwin" and "@remotion/compositor-" in str(binary):
        existing_paths = environment.get("DYLD_LIBRARY_PATH")
        environment["DYLD_LIBRARY_PATH"] = (
            f"{binary.parent}:{existing_paths}" if existing_paths else str(binary.parent)
        )
    return environment


def duration_ms(path: Path, ffprobe: Path) -> int:
    result = subprocess.run(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=compositor_env(ffprobe),
    )
    return round(float(result.stdout.strip()) * 1000)


def generate(source_path: Path, output_source: Path, audio_path: Path) -> dict[str, Any]:
    if sys.platform != "darwin" or not shutil.which("say"):
        raise RuntimeError("demo_tts_requires_macos_say")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    turns = source.get("dialogue_turns") or []
    if not turns:
        raise RuntimeError("dialogue_turns_required")

    ffmpeg = compositor_binary("ffmpeg")
    ffprobe = compositor_binary("ffprobe")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="gff-guided-audio-") as directory:
        temporary = Path(directory)
        rendered_turns: list[tuple[dict[str, Any], Path, int, str]] = []
        for index, turn in enumerate(turns):
            voice = "Anna" if turn.get("speaker_side") == "side_a" else "Eddy (German (Germany))"
            native_path = temporary / f"turn-{index + 1:03d}.aiff"
            turn_path = temporary / f"turn-{index + 1:03d}.wav"
            subprocess.run(
                ["say", "-v", voice, "-r", "178", "-o", str(native_path), str(turn["text"])],
                check=True,
            )
            subprocess.run(
                ["afconvert", "-f", "WAVE", "-d", "LEI16@44100", str(native_path), str(turn_path)],
                check=True,
            )
            rendered_turns.append((turn, turn_path, duration_ms(turn_path, ffprobe), voice))

        inputs = ["-f", "lavfi", "-t", f"{INTRO_MS / 1000:.3f}", "-i", "anullsrc=r=44100:cl=mono"]
        for _, turn_path, _, _ in rendered_turns:
            inputs.extend(["-i", str(turn_path)])
        inputs.extend(["-f", "lavfi", "-t", f"{OUTRO_MS / 1000:.3f}", "-i", "anullsrc=r=44100:cl=mono"])

        filter_parts = ["[0:a]aformat=sample_rates=44100:channel_layouts=mono[a0]"]
        for index, (_, _, turn_duration, _) in enumerate(rendered_turns, start=1):
            padded_seconds = (turn_duration + PAUSE_MS) / 1000
            filter_parts.append(
                f"[{index}:a]aresample=44100,aformat=channel_layouts=mono,"
                f"apad=pad_dur={PAUSE_MS / 1000:.3f},atrim=duration={padded_seconds:.3f}[a{index}]"
            )
        outro_index = len(rendered_turns) + 1
        filter_parts.append(
            f"[{outro_index}:a]aformat=sample_rates=44100:channel_layouts=mono[a{outro_index}]"
        )
        labels = "".join(f"[a{index}]" for index in range(outro_index + 1))
        filter_parts.append(f"{labels}concat=n={outro_index + 1}:v=0:a=1[out]")
        subprocess.run(
            [
                str(ffmpeg),
                "-y",
                *inputs,
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                "[out]",
                "-c:a",
                "pcm_s16le",
                str(audio_path),
            ],
            check=True,
            env=compositor_env(ffmpeg),
        )

    cursor_ms = INTRO_MS
    segments = []
    voices: dict[str, str] = {}
    for turn, _, turn_duration, voice in rendered_turns:
        segments.append(
            {
                "turn_id": turn["turn_id"],
                "start_ms": cursor_ms,
                "end_ms": cursor_ms + turn_duration,
            }
        )
        voices[str(turn.get("speaker_side"))] = voice
        cursor_ms += turn_duration + PAUSE_MS
    source["audio"] = {
        "src": str(audio_path.relative_to(PROJECT_ROOT / "public")),
        "duration_ms": duration_ms(audio_path, ffprobe),
        "segments": segments,
        "provenance": {
            "kind": "local_demo_tts",
            "engine": "macOS say",
            "voices": voices,
            "note": "Preview-only synthetic audio; replace with canonical GFF audio for production.",
        },
    }
    output_source.parent.mkdir(parents=True, exist_ok=True)
    output_source.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-source", type=Path, default=DEFAULT_OUTPUT_SOURCE)
    parser.add_argument("--audio", type=Path, default=DEFAULT_AUDIO)
    args = parser.parse_args()
    try:
        result = generate(args.source, args.output_source, args.audio)
        print(json.dumps(result["audio"], ensure_ascii=False, indent=2))
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"gff-demo-audio-error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
