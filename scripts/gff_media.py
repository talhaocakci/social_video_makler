#!/usr/bin/env python3
"""Compile canonical GFF content into an OverlayMotion preview and render it."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_THEME = PROJECT_ROOT / "brand" / "getfluentfast.theme.json"
DEFAULT_PROPS = PROJECT_ROOT / "work" / "preview.props.json"
DEFAULT_MANIFEST = PROJECT_ROOT / "work" / "preview.manifest.json"
SUPPORTED_FORMATS = {"vertical", "horizontal", "landscape", "square"}
FORMAT_DIMENSIONS = {
    "vertical": (1080, 1920),
    "horizontal": (1920, 1080),
    "landscape": (1620, 1080),
    "square": (1080, 1080),
}


class CompileError(ValueError):
    pass


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CompileError(f"source_not_found:{path}") from exc
    except json.JSONDecodeError as exc:
        raise CompileError(f"invalid_json:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise CompileError("source_must_be_a_json_object")
    return value


def canonical_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def unwrap_guided(source: dict[str, Any]) -> dict[str, Any]:
    for key in ("guided_communication", "asset"):
        candidate = source.get(key)
        if isinstance(candidate, dict) and isinstance(candidate.get("dialogue_turns"), list):
            return candidate

    resolved = source.get("resolved_assets")
    if isinstance(resolved, dict):
        candidate = resolved.get("guided_communication")
        if isinstance(candidate, dict) and isinstance(candidate.get("dialogue_turns"), list):
            return candidate

    if isinstance(source.get("dialogue_turns"), list):
        return source
    raise CompileError("guided_communication_adapter_required")


def text(value: Any) -> str:
    return str(value or "").strip()


def dialogue_messages(guided: dict[str, Any]) -> list[dict[str, Any]]:
    turns = guided.get("dialogue_turns")
    if not isinstance(turns, list):
        raise CompileError("dialogue_turns_required")

    messages: list[dict[str, Any]] = []
    for index, raw in enumerate(turns[:8]):
        if not isinstance(raw, dict):
            continue
        value = text(raw.get("text"))
        if not value:
            continue
        side = text(raw.get("speaker_side"))
        messages.append(
            {
                "text": value,
                "side": "right" if side == "side_b" or (not side and index % 2 == 1) else "left",
                "delaySec": 0.35 if index else 0,
            }
        )
    if not messages:
        raise CompileError("non_empty_dialogue_turns_required")
    return messages


def dialogue_turns(guided: dict[str, Any]) -> list[dict[str, str]]:
    raw_turns = guided.get("dialogue_turns")
    if not isinstance(raw_turns, list):
        raise CompileError("dialogue_turns_required")
    turns: list[dict[str, str]] = []
    for index, raw in enumerate(raw_turns[:8]):
        if not isinstance(raw, dict) or not text(raw.get("text")):
            continue
        turns.append(
            {
                "turn_id": text(raw.get("turn_id")) or f"turn_{index + 1:03d}",
                "speaker_side": text(raw.get("speaker_side")) or (
                    "side_a" if index % 2 == 0 else "side_b"
                ),
                "text": text(raw.get("text")),
            }
        )
    if not turns:
        raise CompileError("non_empty_dialogue_turns_required")
    return turns


def audio_track(guided: dict[str, Any]) -> tuple[str, list[dict[str, Any]], float] | None:
    raw_audio = guided.get("audio")
    if not isinstance(raw_audio, dict) or not text(raw_audio.get("src")):
        return None
    raw_segments = raw_audio.get("segments")
    if not isinstance(raw_segments, list):
        raise CompileError("audio_segments_required")
    segments: list[dict[str, Any]] = []
    previous_end = 0
    for raw in raw_segments:
        if not isinstance(raw, dict):
            continue
        start_ms = int(raw.get("start_ms") or 0)
        end_ms = int(raw.get("end_ms") or 0)
        if start_ms < previous_end or end_ms <= start_ms:
            raise CompileError("audio_segments_must_be_ordered_and_positive")
        segments.append(
            {
                "turn_id": text(raw.get("turn_id")),
                "start_ms": start_ms,
                "end_ms": end_ms,
            }
        )
        previous_end = end_ms
    if not segments:
        raise CompileError("non_empty_audio_segments_required")
    duration_ms = int(raw_audio.get("duration_ms") or segments[-1]["end_ms"])
    if duration_ms < segments[-1]["end_ms"]:
        raise CompileError("audio_duration_shorter_than_segments")
    return text(raw_audio.get("src")), segments, duration_ms / 1000


def guidance_copy(guided: dict[str, Any], guiding_language: str) -> tuple[str, str, str, str]:
    subtitle = ""
    localizations = guided.get("localizations")
    if isinstance(localizations, list):
        for row in localizations:
            if not isinstance(row, dict):
                continue
            if text(row.get("guiding_language")).lower() != guiding_language:
                continue
            if text(row.get("component_ref") or "ROOT").upper() != "ROOT":
                continue
            subtitle = text(row.get("instruction")) or text(row.get("explanation"))
            if subtitle:
                break

    if guiding_language == "tr":
        return (
            subtitle or "Gerçek hayatta kullanacağın kısa bir diyalog.",
            "SIRA SENDE",
            "Cevabı sesli söyle",
            "Dinle · Tekrarla · Konuş",
        )
    if guiding_language == "en":
        return (
            subtitle or text(guided.get("summary")) or "A short dialogue you can use in real life.",
            "YOUR TURN",
            "Say the answer aloud",
            "Listen · Repeat · Speak",
        )
    return (
        subtitle or text(guided.get("summary")) or "Listen, repeat, and speak.",
        "YOUR TURN",
        "Say the answer aloud",
        "Listen · Repeat · Speak",
    )


def catalog_metadata(source: dict[str, Any], guided: dict[str, Any]) -> dict[str, Any]:
    """Keep feed-facing lineage beside the immutable render checksum."""
    category = source.get("category") if isinstance(source.get("category"), dict) else {}
    chain = source.get("learning_chain") if isinstance(source.get("learning_chain"), dict) else {}
    return {
        "content": {
            "title": text(guided.get("title")) or "Real-life dialogue",
            "subtitle": text(guided.get("summary")),
        },
        "category": {
            "id": text(category.get("id")),
            "title": text(category.get("title")),
        },
        "learning_chain": {
            "asset_id": text(chain.get("asset_id")),
            "version": text(chain.get("version")),
            "title": text(chain.get("title")),
        },
    }


def build_dialogue_pop(
    source: dict[str, Any],
    theme: dict[str, Any],
    format_name: str,
    guiding_language: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    guided = unwrap_guided(source)
    messages = dialogue_messages(guided)
    language = text(guided.get("target_language")).lower() or "und"
    cefr = text(guided.get("cefr")).upper() or "ANY"
    title = text(guided.get("title")) or "Real-life dialogue"
    subtitle, cta_kicker, cta_title, cta_subtitle = guidance_copy(guided, guiding_language)

    intro_sec = 2.8
    seconds_per_message = 1.55
    dialogue_sec = max(5.0, len(messages) * seconds_per_message + 1.4)
    outro_sec = 2.8
    outro_start_sec = round(intro_sec + dialogue_sec, 2)
    total_sec = round(outro_start_sec + outro_sec, 2)

    spec = {
        "version": 1,
        "format": format_name,
        "fps": 30,
        "durationSec": total_sec,
        "source": {"type": "none"},
        "sound": {"enabled": True, "volume": 0.38, "sounds": {}},
        "overlays": [
            {
                "template": "hero-title",
                "region": "fullscreen",
                "time": {"start": "0s", "duration": f"{intro_sec}s"},
                "enter": "spring",
                "exit": "blur-out",
                "props": {
                    "kicker": f"{language.upper()} · {cefr}",
                    "title": title,
                    "subtitle": subtitle,
                },
            },
            {
                "template": "chat-bubbles",
                "region": "center",
                "time": {"start": f"{intro_sec}s", "duration": f"{dialogue_sec}s"},
                "enter": "spring",
                "exit": "blur-out",
                "camera": {"preset": "push-in", "amount": 0.08},
                "props": {
                    "messages": messages,
                    "secondsPerMessage": seconds_per_message,
                },
            },
            {
                "template": "hero-title",
                "region": "fullscreen",
                "time": {"start": f"{outro_start_sec}s", "duration": f"{outro_sec}s"},
                "enter": "mask",
                "props": {
                    "kicker": cta_kicker,
                    "title": cta_title,
                    "subtitle": cta_subtitle,
                },
            },
        ],
    }
    digest = canonical_hash(guided)
    manifest = {
        "schema_version": 1,
        **catalog_metadata(source, guided),
        "source": {
            "kind": "guided_communication",
            "asset_id": text(guided.get("asset_id")) or "unidentified-guided-communication",
            "version": text(guided.get("version")) or "unversioned",
            "target_language": language,
            "cefr": cefr,
            "guiding_language": guiding_language,
            "sha256": digest,
        },
        "render": {
            "family": "dialogue-pop",
            "format": format_name,
            "fps": 30,
            "duration_seconds": total_sec,
            "motion_templates": ["hero-title", "chat-bubbles", "hero-title"],
            "publishing": "disabled",
        },
    }
    return {"spec": spec, "theme": theme}, manifest


def build_spoken_dialogue(
    source: dict[str, Any],
    theme: dict[str, Any],
    format_name: str,
    guiding_language: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    guided = unwrap_guided(source)
    turns = dialogue_turns(guided)
    track = audio_track(guided)
    if track is None:
        raise CompileError("spoken_dialogue_requires_audio")
    audio_src, segments, audio_duration = track
    segment_by_turn = {segment["turn_id"]: segment for segment in segments}
    if any(turn["turn_id"] not in segment_by_turn for turn in turns):
        raise CompileError("audio_segment_missing_for_dialogue_turn")

    language = text(guided.get("target_language")).lower() or "und"
    cefr = text(guided.get("cefr")).upper() or "ANY"
    title = text(guided.get("title")) or "Real-life dialogue"
    labels = guided.get("speaker_labels") if isinstance(guided.get("speaker_labels"), dict) else {}
    subtitle, _, cta_title, cta_subtitle = guidance_copy(guided, guiding_language)
    overlays: list[dict[str, Any]] = [
        {
            "template": "hero-title",
            "region": "fullscreen",
            "time": {"start": "0s", "duration": f"{max(1.2, segments[0]['start_ms'] / 1000 - 0.08):.3f}s"},
            "enter": "spring",
            "exit": "blur-out",
            "props": {
                "kicker": f"{language.upper()} · {cefr} · SIMPLIFIED",
                "title": title,
                "subtitle": subtitle,
                "sfx": False,
            },
        }
    ]
    for index, turn in enumerate(turns):
        segment = segment_by_turn[turn["turn_id"]]
        start_sec = max(0, segment["start_ms"] / 1000 - 0.18)
        if index + 1 < len(turns):
            next_segment = segment_by_turn[turns[index + 1]["turn_id"]]
            end_sec = max(segment["end_ms"] / 1000 + 0.08, next_segment["start_ms"] / 1000 - 0.08)
        else:
            end_sec = segment["end_ms"] / 1000 + 0.35
        speaker = text(labels.get(turn["speaker_side"])) or (
            "Konuşmacı A" if turn["speaker_side"] == "side_a" else "Konuşmacı B"
        )
        overlays.append(
            {
                "template": "quote-card",
                "region": "center",
                "time": {"start": f"{start_sec:.3f}s", "duration": f"{end_sec - start_sec:.3f}s", "appear": "0.45s"},
                "enter": "spring",
                "exit": "blur-out",
                "camera": {"preset": "push-in", "amount": 0.035},
                "props": {
                    "quote": turn["text"],
                    "author": speaker,
                    "role": f"{index + 1} / {len(turns)} · Dinle ve takip et",
                    "animateIn": "words",
                    "revealDurationSec": min(1.0, max(0.45, (segment["end_ms"] - segment["start_ms"]) / 2500)),
                    "wordSfx": False,
                },
            }
        )
    outro_start = max(audio_duration - 1.45, segments[-1]["end_ms"] / 1000 + 0.35)
    # Leave one frame of rounding headroom: Remotion resolves each overlay
    # window independently, so two rounded frame counts can otherwise exceed
    # a separately rounded composition by one frame.
    total_sec = round(max(audio_duration, outro_start + 1.4) + 0.05, 3)
    overlays.append(
        {
            "template": "hero-title",
            "region": "fullscreen",
            "time": {"start": f"{outro_start:.3f}s", "duration": f"{total_sec - outro_start:.3f}s"},
            "enter": "mask",
            "props": {
                "kicker": "SIRA SENDE" if guiding_language == "tr" else "YOUR TURN",
                "title": cta_title,
                "subtitle": cta_subtitle,
                "sfx": False,
            },
        }
    )
    spec = {
        "version": 1,
        "format": format_name,
        "fps": 30,
        "durationSec": total_sec,
        "source": {"type": "audio", "src": audio_src},
        "sound": {"enabled": True, "volume": 0.38, "sounds": {}},
        "overlays": overlays,
    }
    digest = canonical_hash(guided)
    manifest = {
        "schema_version": 1,
        **catalog_metadata(source, guided),
        "source": {
            "kind": "guided_communication",
            "asset_id": text(guided.get("asset_id")) or "unidentified-guided-communication",
            "version": text(guided.get("version")) or "unversioned",
            "target_language": language,
            "cefr": cefr,
            "guiding_language": guiding_language,
            "sha256": digest,
        },
        "audio": {
            "src": audio_src,
            "segment_count": len(segments),
            "sync": "provided_segment_timestamps",
            "provenance": guided.get("audio", {}).get("provenance", "provided"),
        },
        "render": {
            "family": "spoken-dialogue",
            "format": format_name,
            "fps": 30,
            "duration_seconds": total_sec,
            "motion_templates": ["hero-title", "quote-card", "hero-title"],
            "publishing": "disabled",
        },
    }
    return {"spec": spec, "theme": theme}, manifest


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compile_source(
    source_path: Path,
    theme_path: Path,
    props_path: Path,
    manifest_path: Path,
    format_name: str,
    guiding_language: str = "tr",
) -> dict[str, Any]:
    if format_name not in SUPPORTED_FORMATS:
        raise CompileError(f"unsupported_format:{format_name}")
    source = read_json(source_path)
    theme = read_json(theme_path)
    guided = unwrap_guided(source)
    if audio_track(guided) is not None:
        props, manifest = build_spoken_dialogue(source, theme, format_name, guiding_language.lower())
    else:
        props, manifest = build_dialogue_pop(source, theme, format_name, guiding_language.lower())
    manifest["input_file"] = str(source_path.resolve())
    manifest["props_file"] = str(props_path.resolve())
    write_json(props_path, props)
    write_json(manifest_path, manifest)
    return manifest


def resolve_pnpm(explicit: str | None) -> str:
    if explicit:
        return explicit
    configured = os.environ.get("PNPM_BIN")
    if configured:
        return configured
    discovered = shutil.which("pnpm")
    if discovered:
        return discovered
    raise CompileError("pnpm_not_found:set_PNPM_BIN_or_add_pnpm_to_PATH")


def render_video(pnpm: str, props_path: Path, output_path: Path, quality: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    crf = "28" if quality == "preview" else "20"
    command = [
        pnpm,
        "exec",
        "remotion",
        "render",
        "remotion/index.ts",
        "custom",
        str(output_path),
        f"--props={props_path}",
        "--codec=h264",
        f"--crf={crf}",
    ]
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def render_thumbnail(pnpm: str, props_path: Path, thumbnail_path: Path, frame: int = 45) -> None:
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        pnpm,
        "exec",
        "remotion",
        "still",
        "remotion/index.ts",
        "custom",
        str(thumbnail_path),
        f"--props={props_path}",
        f"--frame={frame}",
    ]
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def resolve_ffprobe() -> Path:
    discovered = shutil.which("ffprobe")
    if discovered:
        return Path(discovered)
    candidates = sorted(
        PROJECT_ROOT.glob(
            "node_modules/.pnpm/@remotion+compositor-*/node_modules/@remotion/compositor-*/ffprobe"
        )
    )
    if candidates:
        return candidates[0]
    raise CompileError("ffprobe_not_found")


def verify_video(
    output_path: Path,
    format_name: str,
    expected_duration: float,
    require_audio: bool = False,
) -> dict[str, Any]:
    ffprobe = resolve_ffprobe()
    command = [
        str(ffprobe),
        "-v",
        "error",
        "-show_entries",
        "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration,size",
        "-of",
        "json",
        str(output_path),
    ]
    probe_env = os.environ.copy()
    # Remotion's self-contained macOS ffprobe ships its dylibs beside the
    # executable instead of installing them globally.
    if sys.platform == "darwin" and "@remotion/compositor-" in str(ffprobe):
        existing_paths = probe_env.get("DYLD_LIBRARY_PATH")
        probe_env["DYLD_LIBRARY_PATH"] = (
            f"{ffprobe.parent}:{existing_paths}" if existing_paths else str(ffprobe.parent)
        )
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env=probe_env,
    )
    probe = json.loads(result.stdout)
    streams = probe.get("streams") if isinstance(probe, dict) else None
    video_stream = next(
        (row for row in streams or [] if isinstance(row, dict) and row.get("codec_type") == "video"),
        None,
    )
    if not isinstance(video_stream, dict):
        raise CompileError("render_has_no_video_stream")
    audio_stream = next(
        (row for row in streams or [] if isinstance(row, dict) and row.get("codec_type") == "audio"),
        None,
    )
    if require_audio and not isinstance(audio_stream, dict):
        raise CompileError("render_has_no_audio_stream")
    expected_width, expected_height = FORMAT_DIMENSIONS[format_name]
    width = int(video_stream.get("width") or 0)
    height = int(video_stream.get("height") or 0)
    duration = float((probe.get("format") or {}).get("duration") or 0)
    size = int((probe.get("format") or {}).get("size") or 0)
    if (width, height) != (expected_width, expected_height):
        raise CompileError(f"unexpected_dimensions:{width}x{height}")
    if abs(duration - expected_duration) > 0.25:
        raise CompileError(f"unexpected_duration:{duration}")
    if size <= 0:
        raise CompileError("empty_render")
    return {
        "status": "passed",
        "codec": text(video_stream.get("codec_name")),
        "width": width,
        "height": height,
        "fps": text(video_stream.get("r_frame_rate")),
        "audio_codec": text(audio_stream.get("codec_name")) if isinstance(audio_stream, dict) else None,
        "duration_seconds": round(duration, 3),
        "size_bytes": size,
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("compile", "render"):
        command = commands.add_parser(name)
        command.add_argument("--source", type=Path, required=True)
        command.add_argument("--theme", type=Path, default=DEFAULT_THEME)
        command.add_argument("--props-out", type=Path, default=DEFAULT_PROPS)
        command.add_argument("--manifest-out", type=Path, default=DEFAULT_MANIFEST)
        command.add_argument("--format", choices=sorted(SUPPORTED_FORMATS), default="vertical")
        command.add_argument("--guiding-language", default="tr")
        if name == "render":
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--thumbnail", type=Path)
            command.add_argument("--quality", choices=("preview", "final"), default="preview")
            command.add_argument("--pnpm")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        manifest = compile_source(
            args.source,
            args.theme,
            args.props_out,
            args.manifest_out,
            args.format,
            args.guiding_language,
        )
        if args.command == "render":
            pnpm = resolve_pnpm(args.pnpm)
            render_video(pnpm, args.props_out, args.output, args.quality)
            thumbnail = args.thumbnail or args.output.with_name(f"{args.output.stem}-cover.png")
            render_thumbnail(
                pnpm,
                args.props_out,
                thumbnail,
                frame=30 if manifest["render"]["family"] == "spoken-dialogue" else 45,
            )
            manifest["render"]["output_file"] = str(args.output.resolve())
            manifest["render"]["thumbnail_file"] = str(thumbnail.resolve())
            manifest["render"]["qa"] = verify_video(
                args.output,
                args.format,
                float(manifest["render"]["duration_seconds"]),
                require_audio=manifest["render"]["family"] == "spoken-dialogue",
            )
            write_json(args.manifest_out, manifest)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except (CompileError, subprocess.CalledProcessError) as exc:
        print(f"gff-media-error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
