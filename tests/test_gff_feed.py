from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gff_feed", ROOT / "scripts" / "gff_feed.py")
assert SPEC and SPEC.loader
gff_feed = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gff_feed)


class GffFeedTests(unittest.TestCase):
    def test_short_id_uses_url_safe_alphabet(self) -> None:
        value = gff_feed.unique_id(10)
        self.assertEqual(len(value), 10)
        self.assertTrue(value.isalnum())

    def test_build_item_projects_feed_metadata(self) -> None:
        manifest = {
            "content": {"title": "Im Restaurant", "subtitle": "Choose a dish."},
            "category": {"id": "food-and-drinks", "title": "Food & Drinks"},
            "learning_chain": {"asset_id": "chain-1", "version": "000001", "title": "Order food"},
            "source": {
                "kind": "guided_communication",
                "asset_id": "guided-1",
                "version": "000003",
                "guiding_language": "tr",
                "target_language": "de",
                "cefr": "A2",
                "sha256": "abc",
            },
            "render": {
                "family": "spoken-dialogue",
                "fps": 30,
                "qa": {
                    "status": "passed",
                    "width": 1080,
                    "height": 1920,
                    "fps": "30/1",
                    "duration_seconds": 34.2,
                    "audio_codec": "aac",
                },
            },
        }
        item = gff_feed.build_item(manifest, "Ab3dE7kPq9", "social-videos", 20, "video", "cover")
        self.assertEqual(item["video_id"], "Ab3dE7kPq9")
        self.assertEqual(item["duration_ms"], 34200)
        self.assertEqual(item["category_id"], "food-and-drinks")
        self.assertNotIn("guiding_language", item)
        self.assertTrue(item["has_audio"])
        self.assertEqual(item["s3_video_key"], "social-videos/Ab3dE7kPq9/video.mp4")

    def test_feed_metadata_is_required(self) -> None:
        with self.assertRaisesRegex(gff_feed.FeedUploadError, "manifest_feed_metadata_missing"):
            gff_feed.build_item(
                {"render": {"qa": {"status": "passed"}}},
                "Ab3dE7kPq9",
                "social-videos",
                20,
                "video",
                "cover",
            )


if __name__ == "__main__":
    unittest.main()
