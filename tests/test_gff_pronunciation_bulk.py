import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from pronunciation_catalog_v1 import MODULES  # noqa: E402
from gff_pronunciation import validate_source  # noqa: E402


class PronunciationBulkTests(unittest.TestCase):
    def test_catalog_has_exact_bounded_scope(self) -> None:
        self.assertEqual({key: len(value) for key, value in MODULES.items()}, {
            "en": 38,
            "es": 25,
            "de": 24,
        })

    def test_authored_sources_are_complete_and_unique(self) -> None:
        source_root = ROOT / "examples" / "pronunciation-bulk"
        asset_ids: set[str] = set()
        card_ids: set[str] = set()
        module_count = 0
        card_count = 0
        for language, expected_modules in (("en", 38), ("es", 25), ("de", 24)):
            paths = sorted((source_root / language).glob("*.json"))
            self.assertEqual(len(paths), expected_modules)
            for path in paths:
                source = json.loads(path.read_text(encoding="utf-8"))
                cards = validate_source(source)
                self.assertEqual(source["target_language"], language)
                self.assertIsNone(source["guiding_language"])
                self.assertEqual(source["repetitions_per_word"], 2)
                self.assertEqual(source["release_state"], "local_preview_only")
                self.assertNotIn(source["asset_id"], asset_ids)
                asset_ids.add(source["asset_id"])
                module_count += 1
                for card in cards:
                    self.assertNotIn(card["card_id"], card_ids)
                    card_ids.add(card["card_id"])
                    self.assertTrue(card["phonetic"].startswith("/"))
                    self.assertTrue(card["phonetic"].endswith("/"))
                    self.assertTrue(card["word_phonetic"].startswith("/"))
                    self.assertTrue(card["word_phonetic"].endswith("/"))
                    card_count += 1
        self.assertEqual(module_count, 87)
        self.assertEqual(card_count, 435)

    def test_qwen_batches_speak_only_source_examples(self) -> None:
        source_root = ROOT / "examples" / "pronunciation-bulk"
        qwen_root = ROOT / "work" / "pronunciation-bulk" / "qwen"
        for language in ("en", "es", "de"):
            expected = []
            for path in sorted((source_root / language).glob("*.json")):
                source = json.loads(path.read_text(encoding="utf-8"))
                expected.extend((card["card_id"], card["word"]) for card in source["cards"])
            batch = json.loads((qwen_root / f"{language}.source.json").read_text(encoding="utf-8"))
            actual = [(turn["turn_id"], turn["text"]) for turn in batch["turns"]]
            self.assertEqual(actual, expected)
            self.assertIsNone(batch["learner_audio_contract"]["guiding_language"])
            self.assertTrue(batch["learner_audio_contract"]["target_language_only"])


if __name__ == "__main__":
    unittest.main()
