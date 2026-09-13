#!/usr/bin/env python3
"""Publish the checksum-bound pronunciation bundle to the internal GFF feed."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import gff_feed
from gff_pronunciation import canonical_hash, read_json, write_json


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DELIVERY_INDEX = PROJECT_ROOT / "renders" / "pronunciation-bulk" / "delivery" / "delivery-index.json"
MACHINE_QA = PROJECT_ROOT / "work" / "pronunciation-bulk" / "machine-qa.json"
RENDER_REPORT = PROJECT_ROOT / "work" / "pronunciation-bulk" / "render-report.json"
WORK_ROOT = PROJECT_ROOT / "work" / "pronunciation-bulk" / "publishing"
MANIFEST_ROOT = WORK_ROOT / "manifests"
PLAN_PATH = WORK_ROOT / "dry-run.json"
BATCH_RECEIPT_PATH = WORK_ROOT / "publish-receipt.json"
VERIFY_PATH = WORK_ROOT / "verification.json"
RECEIPT_ROOT = PROJECT_ROOT / "work" / "uploads" / "pronunciation-bulk-v1"
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "feed.prod.json"
FEED_API = "https://api.getfluentfast.app/social-videos/feed"

CATEGORY_ID = "pronunciation"
CATEGORY_TITLES = {
    "en": "Pronunciation",
    "es": "Pronunciación",
    "de": "Aussprache",
}
EXPECTED_MODULES = 87
EXPECTED_CARDS = 435
BASE_FEED_RANK = 1000


class BulkPublishError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def json_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def decimal_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: decimal_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decimal_json(item) for item in value]
    if hasattr(value, "as_integer_ratio") and value.__class__.__name__ == "Decimal":
        integer = int(value)
        return integer if value == integer else str(value)
    return value


def module_title(source: dict[str, Any]) -> str:
    patterns: list[str] = []
    for card in source.get("cards") or []:
        pattern = str(card.get("pattern") or "").strip()
        if pattern and pattern not in patterns:
            patterns.append(pattern)
    title = " · ".join(patterns)
    if not title:
        raise BulkPublishError(f"module_title_missing:{source.get('asset_id')}")
    return title


def load_bundle() -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    delivery = read_json(DELIVERY_INDEX)
    machine_qa = read_json(MACHINE_QA)
    render_report = read_json(RENDER_REPORT)
    modules = delivery.get("modules") or []
    if delivery.get("module_count") != EXPECTED_MODULES or len(modules) != EXPECTED_MODULES:
        raise BulkPublishError("delivery_must_contain_exactly_87_modules")
    if delivery.get("card_count") != EXPECTED_CARDS:
        raise BulkPublishError("delivery_must_contain_exactly_435_cards")
    if machine_qa.get("machine_gate") != "passed":
        raise BulkPublishError("machine_qa_must_pass_before_publish")
    if machine_qa.get("module_count") != EXPECTED_MODULES or machine_qa.get("card_count") != EXPECTED_CARDS:
        raise BulkPublishError("machine_qa_scope_mismatch")
    if len(render_report.get("modules") or []) != EXPECTED_MODULES:
        raise BulkPublishError("render_report_scope_mismatch")
    return modules, machine_qa, render_report


def require_pending_audition_ack(args: argparse.Namespace, machine_qa: dict[str, Any]) -> None:
    if machine_qa.get("human_native_audition") == "pending" and not args.ack_human_audition_pending:
        raise BulkPublishError("human_native_audition_pending_ack_required")


def prepare_manifests(args: argparse.Namespace) -> list[dict[str, Any]]:
    modules, machine_qa, render_report = load_bundle()
    require_pending_audition_ack(args, machine_qa)
    render_by_asset = {row["asset_id"]: row for row in render_report["modules"]}
    MANIFEST_ROOT.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for offset, module in enumerate(modules):
        source_path = Path(module["source"])
        source = read_json(source_path)
        asset_id = str(source.get("asset_id") or "")
        if asset_id != module.get("asset_id"):
            raise BulkPublishError(f"delivery_source_asset_mismatch:{asset_id}")
        source_sha256 = canonical_hash(source)
        audio_manifest = read_json(Path(module["audio_manifest"]))
        if audio_manifest.get("source_sha256") != source_sha256:
            raise BulkPublishError(f"audio_source_checksum_mismatch:{asset_id}")
        render = render_by_asset.get(asset_id)
        if not render or (render.get("video_qa") or {}).get("status") != "passed":
            raise BulkPublishError(f"render_qa_not_passed:{asset_id}")
        video = Path(module["video"])
        cover = Path(module["cover"])
        if not video.is_file() or not cover.is_file():
            raise BulkPublishError(f"publish_artifact_missing:{asset_id}")
        language = str(source.get("target_language") or "")
        if language not in CATEGORY_TITLES:
            raise BulkPublishError(f"unsupported_target_language:{asset_id}:{language}")
        qa = dict(render["video_qa"])
        manifest = {
            "schema_version": 1,
            "source": {
                "kind": source["asset_type"],
                "asset_id": asset_id,
                "version": source["version"],
                "target_language": language,
                "locale": source["locale"],
                "variety": source["variety"],
                "cefr": source["cefr"],
                "guiding_language": None,
                "sha256": source_sha256,
            },
            "content": {
                "title": module_title(source),
                "subtitle": "",
                "module_code": source["module_code"],
                "card_count": len(source["cards"]),
                "repetitions_per_word": source["repetitions_per_word"],
            },
            "category": {
                "id": CATEGORY_ID,
                "title": CATEGORY_TITLES[language],
            },
            "learning_chain": {},
            "render": {
                "family": "pronunciation-shadowing",
                "format": "vertical",
                "fps": 30,
                "motion_templates": ["pronunciation-card"],
                "output_file": str(video.resolve()),
                "thumbnail_file": str(cover.resolve()),
                "qa": qa,
                "publishing": "authorized_internal_gff_feed",
            },
            "pronunciation": {
                "locale": source["locale"],
                "variety": source["variety"],
                "cards": source["cards"],
                "source_evidence": source["source_evidence"],
                "phonetic_provenance": source["phonetic_provenance"],
            },
            "release": {
                "destination": "internal_gff_feed",
                "authorization": args.authorization,
                "human_native_audition": machine_qa["human_native_audition"],
                "human_audition_pending_acknowledged": bool(args.ack_human_audition_pending),
            },
        }
        manifest_path = MANIFEST_ROOT / f"{asset_id}.json"
        write_json(manifest_path, manifest)
        rows.append(
            {
                "index": offset,
                "asset_id": asset_id,
                "target_language": language,
                "source_version": source["version"],
                "source_sha256": source_sha256,
                "video": str(video.resolve()),
                "video_sha256": gff_feed.sha256_file(video),
                "video_size_bytes": video.stat().st_size,
                "cover": str(cover.resolve()),
                "thumbnail_sha256": gff_feed.sha256_file(cover),
                "cover_size_bytes": cover.stat().st_size,
                "manifest": str(manifest_path.resolve()),
                "manifest_sha256": gff_feed.sha256_file(manifest_path),
                "feed_rank": BASE_FEED_RANK + offset,
            }
        )
    if len({row["asset_id"] for row in rows}) != EXPECTED_MODULES:
        raise BulkPublishError("duplicate_asset_id_in_publish_bundle")
    return rows


def scan_catalog(table) -> list[dict[str, Any]]:
    projection = (
        "video_id, #st, active, feed_rank, source_asset_id, source_version, "
        "source_sha256, video_sha256, thumbnail_sha256, s3_video_key, "
        "s3_thumbnail_key, s3_manifest_key"
    )
    names = {"#st": "status"}
    response = table.scan(ProjectionExpression=projection, ExpressionAttributeNames=names)
    items = list(response.get("Items") or [])
    while response.get("LastEvaluatedKey"):
        response = table.scan(
            ProjectionExpression=projection,
            ExpressionAttributeNames=names,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items") or [])
    return items


def classify_existing(rows: list[dict[str, Any]], catalog: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_asset: dict[str, list[dict[str, Any]]] = {}
    for item in catalog:
        by_asset.setdefault(str(item.get("source_asset_id") or ""), []).append(item)
    blocked: list[dict[str, Any]] = []
    for row in rows:
        matches = by_asset.get(row["asset_id"], [])
        exact = [
            item for item in matches
            if str(item.get("status")) == "ready"
            and str(item.get("source_version") or "") == row["source_version"]
            and str(item.get("source_sha256") or "") == row["source_sha256"]
            and str(item.get("video_sha256") or "") == row["video_sha256"]
            and str(item.get("thumbnail_sha256") or "") == row["thumbnail_sha256"]
        ]
        if len(exact) == 1 and len(matches) == 1:
            row["action"] = "already_ready"
            row["existing_video_id"] = str(exact[0]["video_id"])
        elif not matches:
            row["action"] = "upload"
        else:
            row["action"] = "blocked_existing_conflict"
            blocked.append(
                {
                    "asset_id": row["asset_id"],
                    "existing": decimal_json(matches),
                }
            )
    return rows, blocked


def dry_run(args: argparse.Namespace) -> dict[str, Any]:
    rows = prepare_manifests(args)
    config = read_json(args.config)
    session = gff_feed.aws_session(config)
    table = session.resource("dynamodb").Table(str(config["table"]))
    catalog = scan_catalog(table)
    rows, blocked = classify_existing(rows, catalog)
    for index, row in enumerate(rows, start=1):
        manifest = read_json(Path(row["manifest"]))
        item = gff_feed.build_item(
            manifest,
            f"DRY{index:07d}",
            str(config.get("s3_prefix") or "social-videos"),
            row["feed_rank"],
            row["video_sha256"],
            row["thumbnail_sha256"],
        )
        if item["target_language"] != row["target_language"] or item["source_asset_id"] != row["asset_id"]:
            raise BulkPublishError(f"dry_run_projection_mismatch:{row['asset_id']}")
    plan_core = {
        "destination": {
            "region": config["region"],
            "bucket": config["bucket"],
            "table": config["table"],
            "prefix": config.get("s3_prefix") or "social-videos",
        },
        "authorization": args.authorization,
        "human_native_audition": "pending",
        "human_audition_pending_acknowledged": bool(args.ack_human_audition_pending),
        "rows": rows,
    }
    report = {
        "schema_version": 1,
        "status": "passed" if not blocked else "blocked",
        "generated_at": utc_now(),
        "plan_sha256": json_hash(plan_core),
        **plan_core,
        "impact": {
            "catalog_items_before": len(catalog),
            "add": sum(row["action"] == "upload" for row in rows),
            "reuse": sum(row["action"] == "already_ready" for row in rows),
            "change": 0,
            "destroy": 0,
            "s3_objects_to_add": 3 * sum(row["action"] == "upload" for row in rows),
        },
        "blocked": blocked,
    }
    write_json(PLAN_PATH, report)
    if blocked:
        raise BulkPublishError("publish_dry_run_has_existing_conflicts")
    return report


def upload_args(args: argparse.Namespace, row: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        video=Path(row["video"]),
        thumbnail=Path(row["cover"]),
        manifest=Path(row["manifest"]),
        feed_rank=int(row["feed_rank"]),
        config=args.config,
        receipts=RECEIPT_ROOT,
        dry_run=False,
    )


def publish(args: argparse.Namespace) -> dict[str, Any]:
    fresh = dry_run(args)
    stored = read_json(PLAN_PATH)
    if stored.get("status") != "passed" or stored.get("plan_sha256") != fresh.get("plan_sha256"):
        raise BulkPublishError("checksum_bound_dry_run_required")
    config = read_json(args.config)
    session = gff_feed.aws_session(config)
    results: list[dict[str, Any]] = []
    running = {
        "schema_version": 1,
        "status": "running",
        "started_at": utc_now(),
        "plan_sha256": fresh["plan_sha256"],
        "authorization": args.authorization,
        "results": results,
    }
    write_json(BATCH_RECEIPT_PATH, running)
    try:
        for row in fresh["rows"]:
            if row["action"] == "already_ready":
                result = {
                    "asset_id": row["asset_id"],
                    "video_id": row["existing_video_id"],
                    "status": "already_ready",
                    "feed_rank": row["feed_rank"],
                }
            else:
                receipt = gff_feed.upload(upload_args(args, row), session=session)
                result = {
                    "asset_id": row["asset_id"],
                    "video_id": receipt["video_id"],
                    "status": receipt["status"],
                    "feed_rank": row["feed_rank"],
                    "receipt": receipt["receipt"],
                    "video_key": receipt["video_key"],
                    "thumbnail_key": receipt["thumbnail_key"],
                    "manifest_key": receipt["manifest_key"],
                }
            results.append(result)
            write_json(BATCH_RECEIPT_PATH, running)
    except Exception as exc:
        running["status"] = "failed"
        running["failed_at"] = utc_now()
        running["error"] = f"{type(exc).__name__}:{exc}"
        write_json(BATCH_RECEIPT_PATH, running)
        raise
    running["status"] = "uploaded"
    running["completed_at"] = utc_now()
    running["uploaded_count"] = sum(row["status"] == "ready" for row in results)
    running["already_ready_count"] = sum(row["status"] == "already_ready" for row in results)
    write_json(BATCH_RECEIPT_PATH, running)
    return running


def public_probe(url: str, *, expect_private: bool = False) -> dict[str, Any]:
    request = Request(url, headers={"Range": "bytes=0-31", "User-Agent": "gff-pronunciation-publish-verify/1"})
    try:
        with urlopen(request, timeout=20) as response:
            status = int(response.status)
            body = response.read()
        if expect_private:
            return {"passed": False, "status": status, "reason": "private_object_was_public"}
        return {"passed": status == 206 and len(body) == 32, "status": status, "bytes": len(body)}
    except HTTPError as exc:
        if expect_private and exc.code in (403, 404):
            return {"passed": True, "status": exc.code}
        return {"passed": False, "status": exc.code}
    except Exception as exc:
        return {"passed": False, "error": f"{type(exc).__name__}:{exc}"}


def verify_feed_api(plan_rows: list[dict[str, Any]]) -> dict[str, Any]:
    languages: list[dict[str, Any]] = []
    for language in CATEGORY_TITLES:
        expected = {row["asset_id"] for row in plan_rows if row["target_language"] == language}
        url = FEED_API + "?" + urlencode(
            {"target_language": language, "category": CATEGORY_ID, "limit": 100}
        )
        request = Request(url, headers={"User-Agent": "gff-pronunciation-publish-verify/1"})
        try:
            with urlopen(request, timeout=30) as response:
                status = int(response.status)
                payload = json.loads(response.read().decode("utf-8"))
            items = payload.get("items") or []
            actual = {
                str((item.get("source") or {}).get("asset_id") or "")
                for item in items
            }
            passed = (
                status == 200
                and payload.get("count") == len(expected)
                and len(items) == len(expected)
                and actual == expected
                and all((item.get("category") or {}).get("id") == CATEGORY_ID for item in items)
                and all(str(item.get("target_language") or "") == language for item in items)
            )
            languages.append(
                {
                    "language": language,
                    "url": url,
                    "http_status": status,
                    "expected_count": len(expected),
                    "actual_count": len(items),
                    "unique_source_asset_count": len(actual),
                    "passed": passed,
                }
            )
        except Exception as exc:
            languages.append(
                {
                    "language": language,
                    "url": url,
                    "expected_count": len(expected),
                    "passed": False,
                    "error": f"{type(exc).__name__}:{exc}",
                }
            )
    return {"passed": all(row["passed"] for row in languages), "languages": languages}


def verify(args: argparse.Namespace) -> dict[str, Any]:
    batch = read_json(BATCH_RECEIPT_PATH)
    plan = read_json(PLAN_PATH)
    if batch.get("status") not in ("uploaded", "verified") or len(batch.get("results") or []) != EXPECTED_MODULES:
        raise BulkPublishError("complete_publish_receipt_required")
    if batch.get("plan_sha256") != plan.get("plan_sha256"):
        raise BulkPublishError("publish_receipt_plan_checksum_mismatch")
    config = read_json(args.config)
    session = gff_feed.aws_session(config)
    table = session.resource("dynamodb").Table(str(config["table"]))
    s3 = session.client("s3")
    bucket = str(config["bucket"])
    region = str(config["region"])
    row_by_asset = {row["asset_id"]: row for row in plan["rows"]}
    results: list[dict[str, Any]] = []
    probe_jobs: list[tuple[str, str, bool]] = []
    for published in batch["results"]:
        asset_id = published["asset_id"]
        row = row_by_asset[asset_id]
        item = table.get_item(Key={"video_id": published["video_id"]}, ConsistentRead=True).get("Item") or {}
        keys = {
            "video": str(item.get("s3_video_key") or published.get("video_key") or ""),
            "cover": str(item.get("s3_thumbnail_key") or published.get("thumbnail_key") or ""),
            "manifest": str(item.get("s3_manifest_key") or published.get("manifest_key") or ""),
        }
        table_passed = (
            str(item.get("status")) == "ready"
            and bool(item.get("active"))
            and str(item.get("source_asset_id")) == asset_id
            and str(item.get("source_version")) == row["source_version"]
            and str(item.get("source_sha256")) == row["source_sha256"]
            and str(item.get("video_sha256")) == row["video_sha256"]
            and str(item.get("thumbnail_sha256")) == row["thumbnail_sha256"]
        )
        video_head = s3.head_object(Bucket=bucket, Key=keys["video"])
        cover_head = s3.head_object(Bucket=bucket, Key=keys["cover"])
        manifest_head = s3.head_object(Bucket=bucket, Key=keys["manifest"])
        objects_passed = (
            int(video_head["ContentLength"]) == row["video_size_bytes"]
            and str(video_head.get("ContentType")) == "video/mp4"
            and int(cover_head["ContentLength"]) == row["cover_size_bytes"]
            and str(cover_head.get("ContentType")) == "image/png"
            and int(manifest_head["ContentLength"]) > 0
            and str(manifest_head.get("ContentType")) == "application/json"
        )
        base = f"https://{bucket}.s3.{region}.amazonaws.com/"
        video_url = base + quote(keys["video"], safe="/")
        cover_url = base + quote(keys["cover"], safe="/")
        manifest_url = base + quote(keys["manifest"], safe="/")
        probe_jobs.extend(
            [
                (asset_id + ":video", video_url, False),
                (asset_id + ":cover", cover_url, False),
                (asset_id + ":manifest", manifest_url, True),
            ]
        )
        results.append(
            {
                "asset_id": asset_id,
                "video_id": published["video_id"],
                "table_passed": table_passed,
                "objects_passed": objects_passed,
                "keys": keys,
                "video_url": video_url,
                "cover_url": cover_url,
            }
        )
    with ThreadPoolExecutor(max_workers=12) as pool:
        probes = list(pool.map(lambda job: (job[0], public_probe(job[1], expect_private=job[2])), probe_jobs))
    probe_by_name = dict(probes)
    for row in results:
        asset_id = row["asset_id"]
        row["public_video"] = probe_by_name[asset_id + ":video"]
        row["public_cover"] = probe_by_name[asset_id + ":cover"]
        row["private_manifest"] = probe_by_name[asset_id + ":manifest"]
        row["passed"] = (
            row["table_passed"]
            and row["objects_passed"]
            and row["public_video"]["passed"]
            and row["public_cover"]["passed"]
            and row["private_manifest"]["passed"]
        )
    api_visibility = verify_feed_api(plan["rows"])
    report = {
        "schema_version": 1,
        "status": "passed"
        if len(results) == EXPECTED_MODULES
        and all(row["passed"] for row in results)
        and api_visibility["passed"]
        else "failed",
        "verified_at": utc_now(),
        "plan_sha256": plan["plan_sha256"],
        "item_count": len(results),
        "checks": {
            "dynamodb_ready_and_checksum_bound": all(row["table_passed"] for row in results),
            "s3_objects_present_with_expected_sizes": all(row["objects_passed"] for row in results),
            "public_video_http_206": all(row["public_video"]["passed"] for row in results),
            "public_cover_http_206": all(row["public_cover"]["passed"] for row in results),
            "manifest_not_public": all(row["private_manifest"]["passed"] for row in results),
            "feed_api_visibility": api_visibility["passed"],
        },
        "feed_api_visibility": api_visibility,
        "results": results,
    }
    write_json(VERIFY_PATH, report)
    if report["status"] != "passed":
        raise BulkPublishError("post_publish_verification_failed")
    batch["status"] = "verified"
    batch["verified_at"] = report["verified_at"]
    batch["verification"] = str(VERIFY_PATH.resolve())
    write_json(BATCH_RECEIPT_PATH, batch)
    return report


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("command", choices=("prepare", "dry-run", "publish", "verify"))
    root.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    root.add_argument("--authorization", default="Current user request: yayinla hepsini")
    root.add_argument("--ack-human-audition-pending", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            rows = prepare_manifests(args)
            result: dict[str, Any] = {"status": "passed", "module_count": len(rows), "rows": rows}
        elif args.command == "dry-run":
            result = dry_run(args)
        elif args.command == "publish":
            result = publish(args)
        else:
            result = verify(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (BulkPublishError, gff_feed.FeedUploadError) as exc:
        print(f"gff-pronunciation-publish-error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
