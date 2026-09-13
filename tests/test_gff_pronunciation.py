from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import wave


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "gff_pronunciation", ROOT / "scripts" / "gff_pronunciation.py"
)
assert SPEC and SPEC.loader
gff_pronunciation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gff_pronunciation)


def write_tone(path: Path, frames: int = 2400) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(24000)
        handle.writeframes(b"\xe8\x03" * frames)


class GffPronunciationTests(unittest.TestCase):
    def source(self) -> dict:
        return json.loads(
            (ROOT / "examples" / "pronunciation.de.ei-ie.json").read_text(encoding="utf-8")
        )

    def test_source_rejects_guiding_language_and_non_double_repeat(self) -> None:
        source = self.source()
        source["guiding_language"] = "tr"
        with self.assertRaisesRegex(gff_pronunciation.PronunciationError, "guiding_language"):
            gff_pronunciation.validate_source(source)
        source["guiding_language"] = None
        source["repetitions_per_word"] = 3
        with self.assertRaisesRegex(gff_pronunciation.PronunciationError, "must_equal_2"):
            gff_pronunciation.validate_source(source)

    def test_qwen_source_contains_only_single_target_words(self) -> None:
        source = self.source()
        qwen = gff_pronunciation.build_qwen_source(source)
        self.assertEqual(qwen["language"], "German")
        self.assertEqual(
            [turn["text"] for turn in qwen["turns"]],
            [card["word"] for card in source["cards"]],
        )
        self.assertEqual({turn["speaker_side"] for turn in qwen["turns"]}, {"narrator"})

    def test_audio_assembly_repeats_identical_frames_twice(self) -> None:
        source = self.source()
        source["cards"] = source["cards"][:1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_path = root / "source.json"
            source_path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
            clips = root / "clips"
            write_tone(clips / "ei-eis.wav")
            manifest = gff_pronunciation.generate_audio(
                source_path, root / "audio", clips_dir=clips, rate=145
            )
            artifact = manifest["artifacts"][0]
            with wave.open(artifact["path"], "rb") as handle:
                frames = handle.readframes(handle.getnframes())
            single_size = 2400 * 2
            pause_size = round(24000 * 0.65) * 2
            self.assertEqual(frames[:single_size], frames[single_size + pause_size :])
            self.assertEqual(artifact["spoken_repetitions"], 2)
            self.assertEqual(artifact["normalized_single_utterance"]["duration_ms"], 100)
            self.assertTrue(manifest["contract"]["learner_audio_contains_target_language_only"])

    def test_compiler_uses_only_pronunciation_cards_and_no_guiding_language(self) -> None:
        source = self.source()
        source["cards"] = source["cards"][:1]
        with tempfile.TemporaryDirectory(dir=ROOT / "public") as public_directory:
            public_root = Path(public_directory)
            source_path = public_root / "source.json"
            source_path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
            clips = public_root / "clips"
            write_tone(clips / "ei-eis.wav")
            audio = gff_pronunciation.generate_audio(
                source_path, public_root / "audio", clips_dir=clips, rate=145
            )
            props_path = public_root / "props.json"
            manifest_path = public_root / "manifest.json"
            manifest = gff_pronunciation.compile_preview(
                source_path,
                public_root / "audio" / "audio.manifest.json",
                ROOT / "brand" / "getfluentfast.theme.json",
                props_path,
                manifest_path,
                "vertical",
            )
            props = json.loads(props_path.read_text(encoding="utf-8"))
            self.assertEqual(props["spec"]["source"]["type"], "audio")
            self.assertEqual(
                {overlay["template"] for overlay in props["spec"]["overlays"]},
                {"pronunciation-card"},
            )
            self.assertIsNone(manifest["source"]["guiding_language"])
            self.assertEqual(manifest["render"]["publishing"], "disabled")


if __name__ == "__main__":
    unittest.main()
