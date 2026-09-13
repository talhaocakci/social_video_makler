#!/usr/bin/env python3
"""Upload an explicitly selected GFF render to the private in-app video feed."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import secrets
import string
import sys
from typing import Any

import boto3
from botocore.exceptions import ClientError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "feed.prod.json"
DEFAULT_RECEIPTS = PROJECT_ROOT / "work" / "uploads"
ID_ALPHABET = string.ascii_letters + string.digits


class FeedUploadError(ValueError):
    pass


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FeedUploadError(f"file_not_found:{path}") from exc
    except json.JSONDecodeError as exc:
        raise FeedUploadError(f"invalid_json:{path}:{exc}") from exc
    if not isinstance(value, dict):
        raise FeedUploadError(f"json_object_required:{path}")
    return value


def text(value: Any) -> str:
    return str(value or "").strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aws_session(config: dict[str, Any]):
    region = text(config.get("region"))
    base = boto3.Session(region_name=region)
    role_arn = text(config.get("role_arn"))
    if not role_arn:
        return base
    response = base.client("sts").assume_role(
        RoleArn=role_arn,
        RoleSessionName="gff-social-video-feed-upload",
        DurationSeconds=3600,
    )
    credentials = response["Credentials"]
    return boto3.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region,
    )


def unique_id(length: int) -> str:
    if length < 8 or length > 22:
        raise FeedUploadError("id_length_must_be_between_8_and_22")
    return "".join(secrets.choice(ID_ALPHABET) for _ in range(length))


def nested(value: dict[str, Any], key: str) -> dict[str, Any]:
    result = value.get(key)
    return result if isinstance(result, dict) else {}


def build_item(
    manifest: dict[str, Any],
    video_id: str,
    prefix: str,
    feed_rank: int,
    video_hash: str,
    thumbnail_hash: str,
) -> dict[str, Any]:
    source = nested(manifest, "source")
    render = nested(manifest, "render")
    qa = nested(render, "qa")
    content = nested(manifest, "content")
    category = nested(manifest, "category")
    chain = nested(manifest, "learning_chain")
    if text(qa.get("status")) != "passed":
        raise FeedUploadError("manifest_render_qa_must_be_passed")
    required = {
        "title": content.get("title"),
        "target_language": source.get("target_language"),
        "cefr": source.get("cefr"),
        "category_id": category.get("id"),
        "category_title": category.get("title"),
    }
    missing = [key for key, value in required.items() if not text(value)]
    if missing:
        raise FeedUploadError(f"manifest_feed_metadata_missing:{','.join(missing)}")
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    duration_ms = round(float(qa.get("duration_seconds") or render.get("duration_seconds") or 0) * 1000)
    root = f"{prefix.strip('/')}/{video_id}"
    return {
        "video_id": video_id,
        "status": "uploading",
        "active": True,
        "feed_rank": feed_rank,
        "title": text(content.get("title")),
        "subtitle": text(content.get("subtitle")),
        "target_language": text(source.get("target_language")).lower(),
        "cefr": text(source.get("cefr")).upper(),
        "category_id": text(category.get("id")),
        "category_title": text(category.get("title")),
        "chain_asset_id": text(chain.get("asset_id")),
        "chain_version": text(chain.get("version")),
        "chain_title": text(chain.get("title")),
        "source_kind": text(source.get("kind")),
        "source_asset_id": text(source.get("asset_id")),
        "source_version": text(source.get("version")),
        "source_sha256": text(source.get("sha256")),
        "template_family": text(render.get("family")),
        "duration_ms": duration_ms,
        "width": int(qa.get("width") or 0),
        "height": int(qa.get("height") or 0),
        "fps": text(qa.get("fps") or render.get("fps")),
        "has_audio": bool(text(qa.get("audio_codec"))),
        "s3_video_key": f"{root}/video.mp4",
        "s3_thumbnail_key": f"{root}/cover.png",
        "s3_manifest_key": f"{root}/manifest.json",
        "video_sha256": video_hash,
        "thumbnail_sha256": thumbnail_hash,
        "created_at": now,
        "updated_at": now,
    }


def reserve(table, item: dict[str, Any], id_length: int, prefix: str, manifest: dict[str, Any], feed_rank: int, video_hash: str, thumbnail_hash: str) -> dict[str, Any]:
    candidate = item
    for _ in range(12):
        try:
            table.put_item(Item=candidate, ConditionExpression="attribute_not_exists(video_id)")
            return candidate
        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") != "ConditionalCheckFailedException":
                raise
            candidate = build_item(
                manifest,
                unique_id(id_length),
                prefix,
                feed_rank,
                video_hash,
                thumbnail_hash,
            )
    raise FeedUploadError("unable_to_reserve_unique_video_id")


def decimal_safe(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: decimal_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [decimal_safe(item) for item in value]
    return value


def upload(args: argparse.Namespace, *, session=None) -> dict[str, Any]:
    config = read_object(args.config)
    manifest = read_object(args.manifest)
    for path in (args.video, args.thumbnail):
        if not path.is_file() or path.stat().st_size <= 0:
            raise FeedUploadError(f"artifact_missing_or_empty:{path}")
    video_hash = sha256_file(args.video)
    thumbnail_hash = sha256_file(args.thumbnail)
    id_length = int(config.get("id_length") or 10)
    prefix = text(config.get("s3_prefix")) or "social-videos"
    item = build_item(
        manifest,
        unique_id(id_length),
        prefix,
        args.feed_rank,
        video_hash,
        thumbnail_hash,
    )
    if args.dry_run:
        return {"dry_run": True, "item": item}

    session = session or aws_session(config)
    table = session.resource("dynamodb").Table(text(config.get("table")))
    s3 = session.client("s3")
    bucket = text(config.get("bucket"))
    if not bucket or not text(config.get("table")):
        raise FeedUploadError("bucket_and_table_are_required")
    item = reserve(
        table,
        decimal_safe(item),
        id_length,
        prefix,
        manifest,
        args.feed_rank,
        video_hash,
        thumbnail_hash,
    )
    catalog_source = dict(nested(manifest, "source"))
    catalog_source.pop("guiding_language", None)
    catalog_manifest = {
        **manifest,
        "source": catalog_source,
        "catalog": {
            "video_id": item["video_id"],
            "bucket": bucket,
            "video_key": item["s3_video_key"],
            "thumbnail_key": item["s3_thumbnail_key"],
            "uploaded_at": item["created_at"],
        },
    }
    try:
        common = {"ServerSideEncryption": "AES256"}
        s3.upload_file(
            str(args.video), bucket, item["s3_video_key"],
            ExtraArgs={**common, "ContentType": "video/mp4", "CacheControl": "public,max-age=31536000,immutable"},
        )
        s3.upload_file(
            str(args.thumbnail), bucket, item["s3_thumbnail_key"],
            ExtraArgs={**common, "ContentType": "image/png", "CacheControl": "public,max-age=31536000,immutable"},
        )
        s3.put_object(
            Bucket=bucket,
            Key=item["s3_manifest_key"],
            Body=(json.dumps(catalog_manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )
        ready_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        table.update_item(
            Key={"video_id": item["video_id"]},
            UpdateExpression="SET #status = :ready, updated_at = :now",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":ready": "ready",
                ":now": ready_at,
                ":uploading": "uploading",
            },
            ConditionExpression="#status = :uploading",
        )
    except Exception:
        try:
            table.update_item(
                Key={"video_id": item["video_id"]},
                UpdateExpression="SET #status = :failed, updated_at = :now",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":failed": "failed",
                    ":now": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                },
            )
        except Exception:
            pass
        raise

    receipt = {
        "video_id": item["video_id"],
        "status": "ready",
        "bucket": bucket,
        "video_key": item["s3_video_key"],
        "thumbnail_key": item["s3_thumbnail_key"],
        "manifest_key": item["s3_manifest_key"],
        "table": text(config.get("table")),
        "metadata": {key: item[key] for key in (
            "title", "target_language", "cefr",
            "category_id", "chain_asset_id", "source_asset_id", "template_family",
        )},
    }
    receipt_path = args.receipts / f"{item['video_id']}.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**receipt, "receipt": str(receipt_path.resolve())}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    command = commands.add_parser("upload")
    command.add_argument("--video", type=Path, required=True)
    command.add_argument("--thumbnail", type=Path, required=True)
    command.add_argument("--manifest", type=Path, required=True)
    command.add_argument("--feed-rank", type=int, default=100)
    command.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    command.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPTS)
    command.add_argument("--dry-run", action="store_true")
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        result = upload(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (FeedUploadError, ClientError) as exc:
        print(f"gff-feed-error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
