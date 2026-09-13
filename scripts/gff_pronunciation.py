#!/usr/bin/env python3
"""Build target-language-only pronunciation audio and OverlayMotion previews."""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THEME = PROJECT_ROOT / "brand" / "getfluentfast.theme.json"
FORMAT_DIMENSIONS = {
    "vertical": (1080, 1920),
    "square": (1080, 1080),
}
VOICE_BY_LOCALE = {
    "de-DE": "Anna",
    "en-US": "Samantha",
    "es-ES": "Mónica",
    "es-419": "Mónica",
}
SAMPLE_RATE = 24_000
SAMPLE_WIDTH = 2
CHANNELS = 1


class PronunciationError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PronunciationError(f"source_not_found:{path}") from exc
    except json.JSONDecodeError as exc:
        raise PronunciationError(f"invalid_json:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise PronunciationError("source_must_be_a_json_object")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_text(value: Any, field: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise PronunciationError(f"non_empty_{field}_required")
    return normalized


def validate_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    if source.get("schema_version") != 1:
        raise PronunciationError("schema_version_1_required")
    if source.get("asset_type") != "pronunciation_module":
        raise PronunciationError("asset_type_must_be_pronunciation_module")
    for field in ("asset_id", "version", "target_language", "locale", "variety", "cefr"):
        required_text(source.get(field), field)
    if source.get("guiding_language") is not None:
        raise PronunciationError("guiding_language_must_be_null")
    if source.get("repetitions_per_word") != 2:
        raise PronunciationError("repetitions_per_word_must_equal_2")
    locale = required_text(source.get("locale"), "locale")
    if locale not in VOICE_BY_LOCALE:
        raise PronunciationError(f"unsupported_preview_locale:{locale}")
    raw_cards = source.get("cards")
    if not isinstance(raw_cards, list) or not 1 <= len(raw_cards) <= 8:
        raise PronunciationError("cards_must_contain_1_to_8_items")
    cards: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for raw in raw_cards:
        if not isinstance(raw, dict):
            raise PronunciationError("card_must_be_an_object")
        card = dict(raw)
        for field in ("card_id", "pattern", "phonetic", "word", "word_phonetic", "focus"):
            card[field] = required_text(card.get(field), f"card_{field}")
        if card["card_id"] in seen_ids:
            raise PronunciationError(f"duplicate_card_id:{card['card_id']}")
        seen_ids.add(card["card_id"])
        if card["focus"].casefold() not in card["word"].casefold():
            raise PronunciationError(f"focus_not_found_in_word:{card['card_id']}")
        artwork = card.get("artwork")
        if artwork is not None:
            if not isinstance(artwork, dict):
                raise PronunciationError(f"artwork_must_be_object:{card['card_id']}")
            for field in ("src", "provenance", "sha256"):
                required_text(artwork.get(field), f"artwork_{field}")
            if artwork.get("provenance") not in {"generated", "licensed", "brand-library"}:
                raise PronunciationError(f"invalid_artwork_provenance:{card['card_id']}")
        cards.append(card)
    return cards


def wave_info(path: Path) -> dict[str, int]:
    with wave.open(str(path), "rb") as handle:
        info = {
            "channels": handle.getnchannels(),
            "sample_width": handle.getsampwidth(),
            "sample_rate": handle.getframerate(),
            "frames": handle.getnframes(),
        }
    if (
        info["channels"] != CHANNELS
        or info["sample_width"] != SAMPLE_WIDTH
        or info["sample_rate"] != SAMPLE_RATE
    ):
        raise PronunciationError(
            "wav_contract_mismatch:"
            f"{path}:{info['channels']}ch:{info['sample_width'] * 8}bit:{info['sample_rate']}hz"
        )
    return info


def silence_frames(duration_ms: int) -> bytes:
    frame_count = round(SAMPLE_RATE * duration_ms / 1000)
    return b"\x00" * frame_count * SAMPLE_WIDTH * CHANNELS


def read_wave_frames(path: Path) -> bytes:
    wave_info(path)
    with wave.open(str(path), "rb") as handle:
        return handle.readframes(handle.getnframes())


def trim_silence(
    frames: bytes,
    *,
    threshold_dbfs: float = -45.0,
    padding_ms: int = 70,
) -> tuple[bytes, dict[str, Any]]:
    samples = array("h")
    samples.frombytes(frames)
    if sys.byteorder != "little":
        samples.byteswap()
    threshold = round(32767 * (10 ** (threshold_dbfs / 20)))
    audible = [index for index, sample in enumerate(samples) if abs(sample) >= threshold]
    if not audible:
        raise PronunciationError("single_utterance_has_no_audible_signal")
    padding_frames = round(SAMPLE_RATE * padding_ms / 1000)
    start = max(0, audible[0] - padding_frames)
    end = min(len(samples), audible[-1] + padding_frames + 1)
    trimmed = array("h", samples[start:end])
    if sys.byteorder != "little":
        trimmed.byteswap()
    return trimmed.tobytes(), {
        "threshold_dbfs": threshold_dbfs,
        "padding_ms": padding_ms,
        "removed_leading_ms": round(start * 1000 / SAMPLE_RATE),
        "removed_trailing_ms": round((len(samples) - end) * 1000 / SAMPLE_RATE),
    }


def write_wave(path: Path, frames: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(CHANNELS)
        handle.setsampwidth(SAMPLE_WIDTH)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(frames)


def synthesize_word_with_say(word: str, locale: str, destination: Path, rate: int) -> dict[str, Any]:
    voice = VOICE_BY_LOCALE[locale]
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "/usr/bin/say",
        "-v",
        voice,
        "-r",
        str(rate),
        "--file-format=WAVE",
        f"--data-format=LEI16@{SAMPLE_RATE}",
        "-o",
        str(destination),
        word,
    ]
    subprocess.run(command, check=True)
    info = wave_info(destination)
    return {
        "engine": "macOS say",
        "voice": voice,
        "locale": locale,
        "rate_wpm": rate,
        "sample_rate_hz": SAMPLE_RATE,
        "channels": CHANNELS,
        "sample_width_bits": SAMPLE_WIDTH * 8,
        "duration_ms": round(info["frames"] * 1000 / SAMPLE_RATE),
        "checksum_sha256": sha256_file(destination),
    }


def resolve_input_clip(card_id: str, clips_dir: Path) -> Path:
    candidates = [
        clips_dir / f"{card_id}.wav",
        clips_dir / "work" / "turns" / f"{card_id}.wav",
        clips_dir / "audio" / "turns" / f"{card_id}.wav",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise PronunciationError(f"input_clip_not_found:{card_id}:{clips_dir}")


def generate_audio(
    source_path: Path,
    output_dir: Path,
    *,
    clips_dir: Path | None,
    rate: int,
) -> dict[str, Any]:
    source = read_json(source_path)
    cards = validate_source(source)
    output_dir.mkdir(parents=True, exist_ok=True)
    locale = str(source["locale"])
    master_parts: list[bytes] = []
    markers: list[dict[str, Any]] = []
    artifact_rows: list[dict[str, Any]] = []
    cursor_frames = 0

    for card in cards:
        card_id = str(card["card_id"])
        with tempfile.TemporaryDirectory(prefix="gff-pronunciation-") as directory:
            if clips_dir:
                single_path = resolve_input_clip(card_id, clips_dir)
                single_provenance = {
                    "engine": "pre-generated local clip",
                    "input_path": str(single_path.resolve()),
                    "checksum_sha256": sha256_file(single_path),
                }
            else:
                single_path = Path(directory) / f"{card_id}.wav"
                single_provenance = synthesize_word_with_say(
                    str(card["word"]), locale, single_path, rate
                )
            raw_single_frames = read_wave_frames(single_path)

        single_frames, trim = trim_silence(raw_single_frames)
        normalized_single_path = output_dir / "singles" / f"{card_id}.wav"
        write_wave(normalized_single_path, single_frames)

        repeated_frames = single_frames + silence_frames(650) + single_frames
        card_path = output_dir / "cards" / f"{card_id}.wav"
        write_wave(card_path, repeated_frames)
        repeated_info = wave_info(card_path)

        visual_start = cursor_frames
        leading_frames = silence_frames(320)
        master_parts.append(leading_frames)
        cursor_frames += len(leading_frames) // (SAMPLE_WIDTH * CHANNELS)
        first_start = cursor_frames
        master_parts.append(single_frames)
        cursor_frames += len(single_frames) // (SAMPLE_WIDTH * CHANNELS)
        first_end = cursor_frames
        repeat_pause = silence_frames(650)
        master_parts.append(repeat_pause)
        cursor_frames += len(repeat_pause) // (SAMPLE_WIDTH * CHANNELS)
        second_start = cursor_frames
        master_parts.append(single_frames)
        cursor_frames += len(single_frames) // (SAMPLE_WIDTH * CHANNELS)
        second_end = cursor_frames
        trailing_frames = silence_frames(460)
        master_parts.append(trailing_frames)
        cursor_frames += len(trailing_frames) // (SAMPLE_WIDTH * CHANNELS)

        to_ms = lambda frames: round(frames * 1000 / SAMPLE_RATE)
        markers.append(
            {
                "card_id": card_id,
                "word": card["word"],
                "visual_start_ms": to_ms(visual_start),
                "first_start_ms": to_ms(first_start),
                "first_end_ms": to_ms(first_end),
                "second_start_ms": to_ms(second_start),
                "second_end_ms": to_ms(second_end),
                "visual_end_ms": to_ms(cursor_frames),
            }
        )
        artifact_rows.append(
            {
                "card_id": card_id,
                "word": card["word"],
                "spoken_repetitions": 2,
                "path": str(card_path.resolve()),
                "duration_ms": round(repeated_info["frames"] * 1000 / SAMPLE_RATE),
                "checksum_sha256": sha256_file(card_path),
                "single_utterance": single_provenance,
                "normalized_single_utterance": {
                    "path": str(normalized_single_path.resolve()),
                    "checksum_sha256": sha256_file(normalized_single_path),
                    "duration_ms": round(len(single_frames) * 1000 / SAMPLE_RATE / SAMPLE_WIDTH),
                    "trim": trim,
                },
            }
        )

    master_path = output_dir / "master.wav"
    write_wave(master_path, b"".join(master_parts))
    master_info = wave_info(master_path)
    manifest = {
        "schema_version": 1,
        "asset_id": source["asset_id"],
        "version": source["version"],
        "target_language": source["target_language"],
        "locale": locale,
        "guiding_language": None,
        "source_sha256": canonical_hash(source),
        "contract": {
            "learner_audio_contains_target_language_only": True,
            "spoken_repetitions_per_word": 2,
            "repetition_method": "byte-identical single utterance repeated with 650ms silence",
        },
        "master": {
            "path": str(master_path.resolve()),
            "duration_ms": round(master_info["frames"] * 1000 / SAMPLE_RATE),
            "sample_rate_hz": SAMPLE_RATE,
            "channels": CHANNELS,
            "checksum_sha256": sha256_file(master_path),
        },
        "markers": markers,
        "artifacts": artifact_rows,
        "requires_human_native_audition": True,
        "machine_validation": "pending",
        "publishing": "disabled",
    }
    write_json(output_dir / "audio.manifest.json", manifest)
    return manifest


def build_qwen_source(source: dict[str, Any]) -> dict[str, Any]:
    cards = validate_source(source)
    language_names = {"de": "German", "en": "English", "es": "Spanish"}
    code = str(source["target_language"])
    if code not in language_names:
        raise PronunciationError(f"qwen_persona_not_configured_for:{code}")
    return {
        "asset_type": "guided_communication",
        "asset_id": source["asset_id"],
        "version": source["version"],
        "language": language_names[code],
        "turns": [
            {
                "turn_id": card["card_id"],
                "speaker_side": "narrator",
                "speaker_label": "narrator",
                "text": card["word"],
            }
            for card in cards
        ],
    }


def compile_preview(
    source_path: Path,
    audio_manifest_path: Path,
    theme_path: Path,
    props_path: Path,
    manifest_path: Path,
    format_name: str,
) -> dict[str, Any]:
    if format_name not in FORMAT_DIMENSIONS:
        raise PronunciationError(f"unsupported_format:{format_name}")
    source = read_json(source_path)
    cards = validate_source(source)
    audio = read_json(audio_manifest_path)
    theme = read_json(theme_path)
    if audio.get("source_sha256") != canonical_hash(source):
        raise PronunciationError("audio_source_checksum_mismatch")
    markers = audio.get("markers")
    if not isinstance(markers, list) or len(markers) != len(cards):
        raise PronunciationError("audio_marker_count_mismatch")
    markers_by_id = {row.get("card_id"): row for row in markers if isinstance(row, dict)}
    overlays: list[dict[str, Any]] = []
    for card in cards:
        marker = markers_by_id.get(card["card_id"])
        if not isinstance(marker, dict):
            raise PronunciationError(f"audio_marker_missing:{card['card_id']}")
        start = int(marker["visual_start_ms"]) / 1000
        end = int(marker["visual_end_ms"]) / 1000
        artwork = card.get("artwork") if isinstance(card.get("artwork"), dict) else None
        overlays.append(
            {
                "template": "pronunciation-card",
                "region": "fullscreen",
                "time": {
                    "start": f"{start:.3f}s",
                    "duration": f"{end - start:.3f}s",
                    "appear": "0.36s",
                },
                "enter": "spring",
                "exit": "blur-out",
                "motion": {"style": "float", "amount": 0.035, "frequency": 0.12},
                "props": {
                    "pattern": card["pattern"],
                    "phonetic": card["phonetic"],
                    "word": card["word"],
                    "wordPhonetic": card["word_phonetic"],
                    "focus": card["focus"],
                    "direction": "rtl" if source["target_language"] == "ar" else "ltr",
                    "language": source["locale"],
                    "repetitionCount": 2,
                    "secondStartFraction": round(
                        (int(marker["second_start_ms"]) - int(marker["visual_start_ms"]))
                        / max(1, int(marker["visual_end_ms"]) - int(marker["visual_start_ms"])),
                        6,
                    ),
                    **({"artwork": artwork["src"]} if artwork else {}),
                },
            }
        )
    # Give Remotion one frame of silent video headroom so the final overlay
    # never rounds past the composition boundary at 30 fps.
    duration_seconds = int(audio["master"]["duration_ms"]) / 1000 + 0.05
    master_path = Path(str(audio["master"]["path"])).resolve()
    try:
        public_relative = master_path.relative_to(PROJECT_ROOT / "public")
    except ValueError as exc:
        raise PronunciationError("master_audio_must_be_inside_project_public") from exc
    spec = {
        "version": 1,
        "format": format_name,
        "fps": 30,
        "durationSec": duration_seconds,
        "source": {"type": "audio", "src": f"/{public_relative.as_posix()}"},
        "sound": {"enabled": False, "volume": 0, "sounds": {}},
        "overlays": overlays,
    }
    props = {"spec": spec, "theme": theme}
    decision_plan = {
        "version": 1,
        "objective": "Teach one target-language spelling-sound contrast without guiding-language speech or copy.",
        "assumptions": [
            {
                "choice": "Use the exact approved target word twice from one lossless utterance.",
                "basis": "explicit-user",
                "confidence": "high",
                "reversible": True,
            },
            {
                "choice": "Show IPA as language-neutral pronunciation notation.",
                "basis": "editorial-default",
                "confidence": "high",
                "reversible": True,
            },
        ],
        "clarifications": [],
        "protectedSubjects": [],
        "decisions": [
            {
                "intent": "Make the grapheme, its sound, and the example word the complete lesson.",
                "evidence": ["explicit-user", "verified-source"],
                "template": "pronunciation-card",
                "placement": "fullscreen",
                "confidence": "high",
            }
        ],
        "captions": {"enabled": False, "timing": "none"},
        "assets": [
            {
                "role": f"artwork:{card['card_id']}",
                "src": card["artwork"]["src"],
                "provenance": card["artwork"]["provenance"],
            }
            for card in cards
            if isinstance(card.get("artwork"), dict)
        ],
        "qa": {
            "checkpoints": ["early-frame", "middle-frame", "late-frame"],
            "checks": [
                "target-language source fidelity",
                "exactly two repetitions per word",
                "no guiding-language learner-visible content",
                "phone-safe text and artwork",
                "audio stream present",
            ],
        },
    }
    manifest = {
        "schema_version": 1,
        "source": {
            "kind": "pronunciation_module",
            "asset_id": source["asset_id"],
            "version": source["version"],
            "target_language": source["target_language"],
            "locale": source["locale"],
            "variety": source["variety"],
            "cefr": source["cefr"],
            "guiding_language": None,
            "sha256": canonical_hash(source),
        },
        "audio": audio,
        "render": {
            "family": "pronunciation-shadowing",
            "format": format_name,
            "fps": 30,
            "duration_seconds": duration_seconds,
            "motion_templates": ["pronunciation-card"],
            "publishing": "disabled",
        },
        "decision_plan": decision_plan,
        "input_file": str(source_path.resolve()),
        "props_file": str(props_path.resolve()),
    }
    write_json(props_path, props)
    write_json(manifest_path, manifest)
    return manifest


def resolve_pnpm(explicit: str | None) -> str:
    if explicit:
        return explicit
    if configured := os.environ.get("PNPM_BIN"):
        return configured
    if discovered := shutil.which("pnpm"):
        return discovered
    bundled = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm"
    if bundled.is_file():
        return str(bundled)
    raise PronunciationError("pnpm_not_found")


def render(
    pnpm: str,
    props_path: Path,
    video_path: Path,
    thumbnail_path: Path,
    quality: str,
) -> None:
    video_path.parent.mkdir(parents=True, exist_ok=True)
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    bundled_node = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
    if bundled_node.is_dir():
        env["PATH"] = f"{bundled_node}:{env.get('PATH', '')}"
    subprocess.run(
        [
            pnpm,
            "exec",
            "remotion",
            "render",
            "remotion/index.ts",
            "custom",
            str(video_path),
            f"--props={props_path}",
            "--codec=h264",
            f"--crf={'28' if quality == 'preview' else '20'}",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )
    subprocess.run(
        [
            pnpm,
            "exec",
            "remotion",
            "still",
            "remotion/index.ts",
            "custom",
            str(thumbnail_path),
            f"--props={props_path}",
            "--frame=30",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
    )


def resolve_ffprobe() -> Path:
    if discovered := shutil.which("ffprobe"):
        return Path(discovered)
    candidates = sorted(
        PROJECT_ROOT.glob(
            "node_modules/.pnpm/@remotion+compositor-*/node_modules/@remotion/compositor-*/ffprobe"
        )
    )
    if candidates:
        return candidates[0]
    raise PronunciationError("ffprobe_not_found")


def verify_video(video_path: Path, format_name: str, expected_duration: float) -> dict[str, Any]:
    ffprobe = resolve_ffprobe()
    env = os.environ.copy()
    if sys.platform == "darwin" and "@remotion/compositor-" in str(ffprobe):
        env["DYLD_LIBRARY_PATH"] = str(ffprobe.parent)
    result = subprocess.run(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size",
            "-of",
            "json",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    probe = json.loads(result.stdout)
    streams = probe.get("streams") or []
    video = next((row for row in streams if row.get("codec_type") == "video"), None)
    audio = next((row for row in streams if row.get("codec_type") == "audio"), None)
    if not video or not audio:
        raise PronunciationError("render_requires_video_and_audio_streams")
    dimensions = (int(video.get("width") or 0), int(video.get("height") or 0))
    if dimensions != FORMAT_DIMENSIONS[format_name]:
        raise PronunciationError(f"unexpected_dimensions:{dimensions}")
    duration = float((probe.get("format") or {}).get("duration") or 0)
    if abs(duration - expected_duration) > 0.25:
        raise PronunciationError(f"unexpected_duration:{duration}:{expected_duration}")
    return {
        "status": "passed",
        "width": dimensions[0],
        "height": dimensions[1],
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name"),
        "duration_seconds": round(duration, 3),
        "size_bytes": int((probe.get("format") or {}).get("size") or 0),
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate")
    validate.add_argument("--source", type=Path, required=True)

    qwen = commands.add_parser("qwen-source")
    qwen.add_argument("--source", type=Path, required=True)
    qwen.add_argument("--output", type=Path, required=True)

    audio = commands.add_parser("audio")
    audio.add_argument("--source", type=Path, required=True)
    audio.add_argument("--output-dir", type=Path, required=True)
    audio.add_argument("--clips-dir", type=Path)
    audio.add_argument("--rate", type=int, default=145)

    for command_name in ("compile", "render"):
        command = commands.add_parser(command_name)
        command.add_argument("--source", type=Path, required=True)
        command.add_argument("--audio-manifest", type=Path, required=True)
        command.add_argument("--theme", type=Path, default=DEFAULT_THEME)
        command.add_argument("--props-out", type=Path, required=True)
        command.add_argument("--manifest-out", type=Path, required=True)
        command.add_argument("--format", choices=sorted(FORMAT_DIMENSIONS), default="vertical")
        if command_name == "render":
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--thumbnail", type=Path, required=True)
            command.add_argument("--quality", choices=("preview", "final"), default="preview")
            command.add_argument("--pnpm")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "validate":
            source = read_json(args.source)
            cards = validate_source(source)
            result: dict[str, Any] = {
                "status": "passed",
                "asset_id": source["asset_id"],
                "source_sha256": canonical_hash(source),
                "card_count": len(cards),
                "guiding_language": None,
                "repetitions_per_word": 2,
            }
        elif args.command == "qwen-source":
            result = build_qwen_source(read_json(args.source))
            write_json(args.output, result)
        elif args.command == "audio":
            result = generate_audio(
                args.source,
                args.output_dir,
                clips_dir=args.clips_dir,
                rate=args.rate,
            )
        else:
            result = compile_preview(
                args.source,
                args.audio_manifest,
                args.theme,
                args.props_out,
                args.manifest_out,
                args.format,
            )
            if args.command == "render":
                render(
                    resolve_pnpm(args.pnpm),
                    args.props_out,
                    args.output,
                    args.thumbnail,
                    args.quality,
                )
                result["render"]["output_file"] = str(args.output.resolve())
                result["render"]["thumbnail_file"] = str(args.thumbnail.resolve())
                result["render"]["qa"] = verify_video(
                    args.output, args.format, float(result["render"]["duration_seconds"])
                )
                write_json(args.manifest_out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (PronunciationError, subprocess.CalledProcessError) as exc:
        print(f"gff-pronunciation-error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
