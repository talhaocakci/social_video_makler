from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gff_media", ROOT / "scripts" / "gff_media.py")
assert SPEC and SPEC.loader
gff_media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gff_media)


class GffMediaCompilerTests(unittest.TestCase):
    def test_guided_communication_compiles_without_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            props_path = Path(directory) / "props.json"
            manifest_path = Path(directory) / "manifest.json"
            manifest = gff_media.compile_source(
                ROOT / "examples" / "guided-communication.de.json",
                ROOT / "brand" / "getfluentfast.theme.json",
                props_path,
                manifest_path,
                "vertical",
                "tr",
            )
            props = json.loads(props_path.read_text(encoding="utf-8"))
            messages = props["spec"]["overlays"][1]["props"]["messages"]
            source = json.loads(
                (ROOT / "examples" / "guided-communication.de.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                [message["text"] for message in messages],
                [turn["text"] for turn in source["dialogue_turns"]],
            )
            self.assertEqual(manifest["source"]["version"], "000001")
            self.assertEqual(manifest["source"]["guiding_language"], "tr")
            self.assertEqual(manifest["render"]["publishing"], "disabled")

    def test_non_guided_input_requires_an_adapter(self) -> None:
        with self.assertRaisesRegex(gff_media.CompileError, "guided_communication_adapter_required"):
            gff_media.build_dialogue_pop(
                {"asset_id": "scenario-only", "missions": []},
                {},
                "vertical",
                "tr",
            )

    def test_timestamped_audio_selects_spoken_dialogue(self) -> None:
        source = json.loads(
            (ROOT / "examples" / "guided-communication.de.json").read_text(encoding="utf-8")
        )
        source["audio"] = {
            "src": "generated/test.wav",
            "duration_ms": 9000,
            "segments": [
                {
                    "turn_id": turn["turn_id"],
                    "start_ms": 1000 + index * 1800,
                    "end_ms": 2200 + index * 1800,
                }
                for index, turn in enumerate(source["dialogue_turns"])
            ],
            "provenance": "test",
        }
        props, manifest = gff_media.build_spoken_dialogue(
            source,
            json.loads((ROOT / "brand" / "getfluentfast.theme.json").read_text()),
            "vertical",
            "tr",
        )
        self.assertEqual(props["spec"]["source"]["type"], "audio")
        self.assertEqual(manifest["render"]["family"], "spoken-dialogue")
        self.assertEqual(manifest["audio"]["sync"], "provided_segment_timestamps")
        self.assertEqual(manifest["render"]["publishing"], "disabled")


if __name__ == "__main__":
    unittest.main()
