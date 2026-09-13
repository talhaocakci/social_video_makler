#!/usr/bin/env python3
"""Merge checksum-bound selective pronunciation ASR retries into a full report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path)
    parser.add_argument("retry", type=Path)
    parser.add_argument("generation_manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    base = json.loads(args.base.resolve().read_text(encoding="utf-8"))
    retry = json.loads(args.retry.resolve().read_text(encoding="utf-8"))
    generation = json.loads(args.generation_manifest.resolve().read_text(encoding="utf-8"))
    if base.get("scope", "all_artifacts") != "all_artifacts":
        raise ValueError("base report must cover all artifacts")
    if retry.get("scope") != "selected_retry_artifacts":
        raise ValueError("retry report must cover selected artifacts")
    if not (
        base.get("source_sha256")
        == retry.get("source_sha256")
        == generation.get("source_sha256")
    ):
        raise ValueError("ASR reports and generation manifest are not source-bound")

    retry_items = {row["artifact_key"]: row for row in retry["items"]}
    merged_items = [retry_items.get(row["artifact_key"], row) for row in base["items"]]
    artifact_paths = {
        str(row["turn_id"]): str(row["path"])
        for row in generation.get("artifacts") or []
        if row.get("turn_id")
    }
    for row in merged_items:
        row["audio_sha256"] = sha256_file(artifact_paths[row["artifact_key"]])

    retry_quality = {
        row["artifact_key"]: row for row in retry["audio_quality"]["items"]
    }
    quality_items = [
        retry_quality.get(row["artifact_key"], row)
        for row in base["audio_quality"]["items"]
    ]
    base["items"] = merged_items
    base["large_v3_review_count"] = sum(
        not row["turbo_strict_pass"] for row in merged_items
    )
    base["audio_quality"] = {
        "passed": all(row["passed"] for row in quality_items),
        "items": quality_items,
    }
    base["speaker_consistency_audit"] = generation.get("speaker_consistency_audit")
    base["speaker_consistency_passed"] = bool(
        (generation.get("speaker_consistency_audit") or {}).get("passed")
    )
    base["strict_asr_passed"] = all(row["strict_pass"] for row in merged_items)
    base["passed"] = (
        base["strict_asr_passed"]
        and base["audio_quality"]["passed"]
        and base["speaker_consistency_passed"]
    )
    base.setdefault("selective_retry_reports", []).append(str(args.retry.resolve()))
    args.output.resolve().write_text(
        json.dumps(base, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(args.output.resolve())
    return 0 if base["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
