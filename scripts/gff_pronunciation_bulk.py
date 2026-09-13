#!/usr/bin/env python3
"""Author and build the complete EN/ES/DE pronunciation preview catalog."""

from __future__ import annotations

import argparse
from array import array
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
import unicodedata
import wave

from pronunciation_catalog_v1 import LANGUAGES, MODULES
from gff_pronunciation import (
    PronunciationError,
    canonical_hash,
    compile_preview,
    generate_audio,
    read_json,
    resolve_pnpm,
    validate_source,
    verify_video,
    write_json,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "examples" / "pronunciation-bulk"
PUBLIC_ROOT = PROJECT_ROOT / "public" / "generated" / "pronunciation-bulk"
WORK_ROOT = PROJECT_ROOT / "work" / "pronunciation-bulk"
RENDER_ROOT = PROJECT_ROOT / "renders" / "pronunciation-bulk"
THEME_PATH = PROJECT_ROOT / "brand" / "getfluentfast.theme.json"


VOWELS = set("aeiouyæɑɒɔəɛɜɚɝɪʊʌøœɐɞɶɨʉɯɤɵɘɒ")


# Dictionary G2P is a draft, not an authority.  These corrections are frozen here
# where the local lexicon is known to use another variety or an unsuitable form.
IPA_OVERRIDES: dict[tuple[str, str], str] = {
    ("en", "three"): "θɹiː",
    ("en", "mother"): "ˈmʌðɚ",
    ("en", "one"): "wʌn",
    ("en", "two"): "tuː",
    ("en", "women"): "ˈwɪmɪn",
    ("en", "people"): "ˈpiːpəl",
    ("en", "could"): "kʊd",
    ("en", "new"): "nuː",
    ("es", "viaje"): "ˈbjaxe",
    ("es", "tierra"): "ˈtjera",
    ("es", "patio"): "ˈpatjo",
    ("es", "cuatro"): "ˈkwatɾo",
    ("es", "puerta"): "ˈpweɾta",
    ("es", "cuota"): "ˈkwota",
    ("es", "aire"): "ˈai̯ɾe",
    ("es", "hay"): "ai̯",
    ("es", "peine"): "ˈpei̯ne",
    ("es", "rey"): "rei̯",
    ("es", "boina"): "ˈboi̯na",
    ("es", "hoy"): "oi̯",
    ("es", "causa"): "ˈkau̯sa",
    ("es", "Europa"): "eu̯ˈɾopa",
    ("es", "país"): "paˈis",
    ("es", "raíz"): "raˈiθ",
    ("es", "río"): "ˈri.o",
    ("es", "día"): "ˈdi.a",
    ("es", "baúl"): "baˈul",
    ("es", "actúa"): "akˈtu.a",
    ("es", "termino"): "teɾˈmino",
    ("es", "terminó"): "teɾmiˈno",
    ("es", "llave"): "ˈʝabe",
    ("es", "pollo"): "ˈpoʝo",
    ("es", "México"): "ˈmexiko",
    ("es", "xilófono"): "siˈlofono",
    ("es", "alrededor"): "alreðeˈðoɾ",
    ("es", "uva"): "ˈuβa",
    ("es", "vivir"): "biˈβiɾ",
    ("es", "beber"): "beˈβeɾ",
    ("es", "dedo"): "ˈdeðo",
    ("es", "cada"): "ˈkaða",
    ("es", "nada"): "ˈnaða",
    ("es", "ciudad"): "θjuˈðað",
    ("es", "usted"): "usˈteð",
    ("es", "dos amigos"): "dos‿aˈmiɣos",
    ("es", "el amor"): "el‿aˈmoɾ",
    ("es", "vivo en Málaga"): "ˈbiβo‿en‿ˈmalaɣa",
    ("es", "la amiga"): "la‿aˈmiɣa",
    ("es", "mi hermano"): "mi‿eɾˈmano",
    ("es", "vivo en España"): "ˈbiβo‿en‿esˈpaɲa",
    ("de", "Biene"): "ˈbiːnə",
    ("de", "Liebe"): "ˈliːbə",
    ("de", "Ende"): "ˈʔɛndə",
    ("de", "Name"): "ˈnaːmə",
    ("de", "Bayern"): "ˈbaɪ̯ɐn",
    ("de", "Meyer"): "ˈmaɪ̯ɐ",
    ("de", "fertig"): "ˈfɛʁtɪç",
    ("de", "richtig"): "ˈʁɪçtɪç",
    ("de", "wichtig"): "ˈvɪçtɪç",
    ("de", "König"): "ˈkøːnɪç",
    ("de", "Verein"): "fɛɐ̯ˈʔaɪ̯n",
    ("de", "arbeiten"): "ˈʔaʁbaɪ̯tən",
    ("de", "erinnern"): "ʔɛɐ̯ˈʔɪnɐn",
    ("de", "beachten"): "bəˈʔaxtən",
    ("de", "bequem"): "bəˈkveːm",
    ("de", "Zeit"): "tsaɪ̯t",
    ("de", "Deutsch"): "dɔʏ̯tʃ",
    ("de", "Dschinn"): "dʒɪn",
    ("de", "Quelle"): "ˈkvɛlə",
    ("de", "Straße"): "ˈʃtʁaːsə",
    ("de", "neu"): "nɔʏ̯",
    ("de", "blau"): "blaʊ̯",
    ("de", "kaufen"): "ˈkaʊ̯fən",
    ("de", "Vase"): "ˈvaːzə",
    ("de", "Bäume"): "ˈbɔʏ̯mə",
    ("de", "Mai"): "maɪ̯",
    ("de", "Mann"): "man",
    ("de", "offen"): "ˈʔɔfən",
    ("de", "Taxi"): "ˈtaksi",
}


GERMAN_SECOND_STRESS = {"beachten", "bequem", "erinnern", "Verein"}


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    compact = re.sub(r"[^a-z0-9]+", "-", normalized.casefold()).strip("-")
    return compact or hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]


def is_vowel_phone(phone: str) -> bool:
    return any(char in VOWELS for char in phone)


def move_stress_to_syllable_start(
    phones: list[str], nucleus_index: int, *, language: str = ""
) -> str:
    vowel_positions = [index for index, phone in enumerate(phones) if is_vowel_phone(phone)]
    if not vowel_positions:
        return "".join(phones)
    nucleus_index = max(0, min(nucleus_index, len(vowel_positions) - 1))
    vowel_position = vowel_positions[nucleus_index]
    previous_vowel = vowel_positions[nucleus_index - 1] if nucleus_index else -1
    onset = previous_vowel + 1
    if language == "es" and previous_vowel >= 0:
        between = [
            phone.replace("ˈ", "").replace("ˌ", "")
            for phone in phones[previous_vowel + 1 : vowel_position]
        ]
        valid_two_phone_onsets = {
            (first, second)
            for first in ("p", "b", "t", "d", "k", "g", "ɡ", "f")
            for second in ("ɾ", "l")
        }
        if len(between) >= 2 and tuple(between[-2:]) in valid_two_phone_onsets:
            onset = vowel_position - 2
        elif between:
            onset = vowel_position - 1
        else:
            onset = vowel_position
    cleaned = [phone.replace("ˈ", "").replace("ˌ", "") for phone in phones]
    cleaned[onset] = "ˈ" + cleaned[onset]
    return "".join(cleaned)


def existing_stress_nucleus(phones: list[str]) -> int | None:
    nucleus = -1
    for phone in phones:
        if is_vowel_phone(phone):
            nucleus += 1
        if "ˈ" in phone:
            return max(0, nucleus)
    return None


def spanish_nuclei(word: str) -> list[list[int]]:
    letters = word.casefold()
    vowels = "aeiouáéíóúü"
    weak = "iuü"
    nuclei: list[list[int]] = []
    index = 0
    while index < len(letters):
        if letters[index] not in vowels and not (letters[index] == "y" and index == len(letters) - 1):
            index += 1
            continue
        current = [index]
        cursor = index + 1
        while cursor < len(letters) and letters[cursor] in vowels:
            left = letters[current[-1]]
            right = letters[cursor]
            left_plain = unicodedata.normalize("NFD", left)[0]
            right_plain = unicodedata.normalize("NFD", right)[0]
            separated = left in "íú" or right in "íú" or (
                left_plain not in weak and right_plain not in weak
            )
            if separated:
                break
            current.append(cursor)
            cursor += 1
        nuclei.append(current)
        index = cursor
    return nuclei


def spanish_stress_nucleus(word: str) -> int:
    nuclei = spanish_nuclei(word)
    for index, nucleus in enumerate(nuclei):
        if any(word[position].casefold() in "áéíóú" for position in nucleus):
            return index
    if len(nuclei) <= 1:
        return 0
    plain = re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", word)
    return len(nuclei) - 2 if plain.casefold().endswith(("a", "e", "i", "o", "u", "n", "s")) else len(nuclei) - 1


def phonemize_word(word: str, language: str) -> str:
    override = IPA_OVERRIDES.get((language, word))
    if override:
        if language == "es":
            override = override.replace("θ", "s")
        return f"/{override}/"
    try:
        from gruut import sentences
    except ImportError as exc:
        raise PronunciationError(
            "gruut_required_run_with_the_documented_local_g2p_environment"
        ) from exc
    gruut_language = {"en": "en-us", "es": "es-es", "de": "de-de"}[language]
    transcribed_words: list[str] = []
    for sentence in sentences(word, lang=gruut_language):
        for token in sentence:
            phones = list(token.phonemes or [])
            if not phones:
                continue
            if language == "en":
                phones = [
                    (
                        phone.replace("ˈɚ", "ˈɝ")
                        if "ˈɚ" in phone
                        else
                        phone.replace("i", "iː")
                        if "ˈ" in phone and phone.replace("ˈ", "").replace("ˌ", "") == "i"
                        else phone.replace("u", "uː")
                        if "ˈ" in phone and phone.replace("ˈ", "").replace("ˌ", "") == "u"
                        else phone
                    )
                    for phone in phones
                ]
                nucleus = existing_stress_nucleus(phones)
                rendered = (
                    move_stress_to_syllable_start(phones, nucleus)
                    if nucleus is not None and sum(is_vowel_phone(p) for p in phones) > 1
                    else "".join(p.replace("ˈ", "").replace("ˌ", "") for p in phones)
                )
            elif language == "es":
                rendered = move_stress_to_syllable_start(
                    phones, spanish_stress_nucleus(token.text), language="es"
                )
                rendered = rendered.replace("ʎ", "ʝ").replace("b", "b")
            else:
                default_nucleus = 1 if token.text in GERMAN_SECOND_STRESS else 0
                rendered = move_stress_to_syllable_start(phones, default_nucleus)
            rendered = (
                rendered.replace("t͡ʃ", "tʃ")
                .replace("d͡ʒ", "dʒ")
                .replace("p͡f", "pf")
                .replace("t͡s", "ts")
                .replace("g", "ɡ")
            )
            if language == "es":
                rendered = rendered.replace("θ", "s")
            transcribed_words.append(rendered)
    if not transcribed_words:
        raise PronunciationError(f"g2p_returned_no_phonemes:{language}:{word}")
    return "/" + " ".join(transcribed_words) + "/"


def asset_id(language: str, code: str, cefr: str) -> str:
    pilots = {
        ("en", "D02"): "pronunciation-en-a1-th",
        ("es", "C07"): "pronunciation-es-a1-g-gu-gue",
        ("de", "D01"): "pronunciation-de-a1-ei-ie",
    }
    return pilots.get(
        (language, code), f"pronunciation-{language}-{cefr.casefold()}-{code.casefold()}"
    )


def author_sources(languages: list[str]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    card_total = 0
    for language in languages:
        language_info = LANGUAGES[language]
        destination = SOURCE_ROOT / language
        destination.mkdir(parents=True, exist_ok=True)
        for module in MODULES[language]:
            cards = []
            index = 0
            for pattern, pattern_ipa, examples in module["groups"]:
                for word, focus in examples:
                    index += 1
                    cards.append(
                        {
                            "card_id": f"{language}-{module['code'].casefold()}-{index:02d}-{slug(word)}",
                            "pattern": pattern,
                            "phonetic": pattern_ipa,
                            "word": word,
                            "word_phonetic": phonemize_word(word, language),
                            "focus": focus,
                        }
                    )
            source = {
                "schema_version": 1,
                "asset_type": "pronunciation_module",
                "asset_id": asset_id(language, module["code"], module["cefr"]),
                "module_code": f"{language.upper()}-{module['code']}",
                "version": "000001",
                "target_language": language,
                "locale": language_info["locale"],
                "variety": language_info["variety"],
                "cefr": module["cefr"],
                "guiding_language": None,
                "repetitions_per_word": 2,
                "cards": cards,
                "source_evidence": language_info["evidence"],
                "phonetic_provenance": {
                    "draft_engine": "gruut 2.4.0 local language dictionaries",
                    "editorial_overrides": "scripts/gff_pronunciation_bulk.py:IPA_OVERRIDES",
                    "human_native_review": "required",
                },
                "release_state": "local_preview_only",
            }
            validate_source(source)
            path = destination / f"{module['code'].casefold()}.json"
            write_json(path, source)
            rows.append(
                {
                    "module_code": source["module_code"],
                    "asset_id": source["asset_id"],
                    "cefr": source["cefr"],
                    "card_count": len(cards),
                    "source_path": str(path.resolve()),
                    "source_sha256": canonical_hash(source),
                }
            )
            card_total += len(cards)
    report = {
        "schema_version": 1,
        "status": "passed",
        "languages": languages,
        "module_count": len(rows),
        "card_count": card_total,
        "modules": rows,
        "human_native_audition": "required",
        "publishing": "disabled",
    }
    write_json(WORK_ROOT / "source-inventory.json", report)
    return report


def iter_sources(languages: list[str]) -> list[Path]:
    return [
        SOURCE_ROOT / language / f"{module['code'].casefold()}.json"
        for language in languages
        for module in MODULES[language]
    ]


def validate_inventory(languages: list[str]) -> dict[str, Any]:
    paths = iter_sources(languages)
    expected = sum(len(MODULES[language]) for language in languages)
    if len(paths) != expected:
        raise PronunciationError(f"source_count_mismatch:{len(paths)}:{expected}")
    rows = []
    ids: set[str] = set()
    card_ids: set[str] = set()
    for path in paths:
        source = read_json(path)
        cards = validate_source(source)
        if source["target_language"] not in languages:
            raise PronunciationError(f"unexpected_language:{path}")
        if source["asset_id"] in ids:
            raise PronunciationError(f"duplicate_asset_id:{source['asset_id']}")
        ids.add(source["asset_id"])
        for card in cards:
            if card["card_id"] in card_ids:
                raise PronunciationError(f"duplicate_global_card_id:{card['card_id']}")
            card_ids.add(card["card_id"])
        rows.append(
            {
                "module_code": source.get("module_code"),
                "asset_id": source["asset_id"],
                "card_count": len(cards),
                "source_sha256": canonical_hash(source),
            }
        )
    result = {
        "status": "passed",
        "languages": languages,
        "module_count": len(paths),
        "card_count": len(card_ids),
        "modules": rows,
        "guiding_language": None,
        "repetitions_per_word": 2,
        "publishing": "disabled",
    }
    write_json(WORK_ROOT / "source-validation.json", result)
    return result


def build_qwen_batches(languages: list[str]) -> dict[str, Any]:
    rows = []
    for language in languages:
        turns = []
        source_hashes = []
        # Synthesis order is lexical and checksum-stable; learner delivery order is
        # independently preserved by ``iter_sources`` from the authored curriculum.
        for path in sorted((SOURCE_ROOT / language).glob("*.json")):
            source = read_json(path)
            cards = validate_source(source)
            source_hashes.append(canonical_hash(source))
            turns.extend(
                {
                    "turn_id": card["card_id"],
                    "speaker_side": "narrator",
                    "speaker_label": "narrator",
                    "text": card["word"],
                }
                for card in cards
            )
        batch = {
            "asset_type": "guided_communication",
            "asset_id": f"pronunciation-bulk-{language}-v1",
            "version": "000001",
            "language": LANGUAGES[language]["language_name"],
            "turns": turns,
            "source_module_sha256s": source_hashes,
            "learner_audio_contract": {
                "target_language_only": True,
                "single_utterance_per_turn": True,
                "guiding_language": None,
            },
        }
        path = WORK_ROOT / "qwen" / f"{language}.source.json"
        write_json(path, batch)
        rows.append({"language": language, "turn_count": len(turns), "path": str(path)})
    result = {"status": "passed", "batches": rows, "publishing": "disabled"}
    write_json(WORK_ROOT / "qwen" / "batch-plan.json", result)
    return result


def assemble_audio(languages: list[str]) -> dict[str, Any]:
    rows = []
    for path in iter_sources(languages):
        source = read_json(path)
        output = PUBLIC_ROOT / source["asset_id"] / "audio"
        qwen_output = WORK_ROOT / "qwen" / source["target_language"]
        manifest = generate_audio(path, output, clips_dir=qwen_output, rate=145)
        rows.append(
            {
                "asset_id": source["asset_id"],
                "master": manifest["master"],
                "artifact_count": len(manifest["artifacts"]),
                "source_sha256": manifest["source_sha256"],
            }
        )
    result = {"status": "passed", "module_count": len(rows), "modules": rows}
    write_json(WORK_ROOT / "audio-assembly.json", result)
    return result


def compile_all(languages: list[str]) -> dict[str, Any]:
    rows = []
    for path in iter_sources(languages):
        source = read_json(path)
        build_dir = WORK_ROOT / "compiled" / source["asset_id"]
        manifest = compile_preview(
            path,
            PUBLIC_ROOT / source["asset_id"] / "audio" / "audio.manifest.json",
            THEME_PATH,
            build_dir / "props.json",
            build_dir / "manifest.json",
            "vertical",
        )
        rows.append(
            {
                "asset_id": source["asset_id"],
                "duration_seconds": manifest["render"]["duration_seconds"],
                "props": str((build_dir / "props.json").resolve()),
                "manifest": str((build_dir / "manifest.json").resolve()),
            }
        )
    result = {"status": "passed", "module_count": len(rows), "modules": rows}
    write_json(WORK_ROOT / "compile-report.json", result)
    return result


def render_all(languages: list[str], quality: str, workers: int) -> dict[str, Any]:
    pnpm = resolve_pnpm(None)
    paths = iter_sources(languages)

    def render_one(path: Path) -> dict[str, Any]:
        source = read_json(path)
        asset = source["asset_id"]
        build_dir = WORK_ROOT / "compiled" / asset
        output = RENDER_ROOT / source["target_language"] / f"{asset}-preview.mp4"
        thumbnail = RENDER_ROOT / source["target_language"] / f"{asset}-cover.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        compiled_manifest = read_json(build_dir / "manifest.json")
        if output.is_file() and thumbnail.is_file():
            try:
                video_qa = verify_video(
                    output, "vertical", compiled_manifest["render"]["duration_seconds"]
                )
                return {
                    "asset_id": asset,
                    "video": str(output.resolve()),
                    "thumbnail": str(thumbnail.resolve()),
                    "video_qa": video_qa,
                    "reused_existing_render": True,
                }
            except (PronunciationError, subprocess.CalledProcessError):
                pass
        command = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "gff_pronunciation.py"),
            "render",
            "--source",
            str(path),
            "--audio-manifest",
            str(PUBLIC_ROOT / asset / "audio" / "audio.manifest.json"),
            "--props-out",
            str(build_dir / "props.json"),
            "--manifest-out",
            str(build_dir / "manifest.json"),
            "--output",
            str(output),
            "--thumbnail",
            str(thumbnail),
            "--quality",
            quality,
            "--pnpm",
            pnpm,
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode:
            raise PronunciationError(
                f"render_failed:{asset}:\n{completed.stdout[-2000:]}\n{completed.stderr[-2000:]}"
            )
        manifest = read_json(build_dir / "manifest.json")
        video_qa = verify_video(output, "vertical", manifest["render"]["duration_seconds"])
        return {
            "asset_id": asset,
            "video": str(output.resolve()),
            "thumbnail": str(thumbnail.resolve()),
            "video_qa": video_qa,
        }

    if workers < 1:
        raise PronunciationError("workers_must_be_positive")
    if workers == 1:
        rows = [render_one(path) for path in paths]
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(render_one, paths))
    result = {"status": "passed", "module_count": len(rows), "modules": rows}
    write_json(WORK_ROOT / "render-report.json", result)
    return result


def render_covers(languages: list[str], workers: int) -> dict[str, Any]:
    pnpm = resolve_pnpm(None)
    paths = iter_sources(languages)

    def render_one(path: Path) -> dict[str, Any]:
        source = read_json(path)
        asset = source["asset_id"]
        props = WORK_ROOT / "compiled" / asset / "props.json"
        output = RENDER_ROOT / source["target_language"] / f"{asset}-cover.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        bundled_node = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
        env["PATH"] = f"{bundled_node}:{env.get('PATH', '')}"
        completed = subprocess.run(
            [
                pnpm,
                "exec",
                "remotion",
                "still",
                "remotion/index.ts",
                "custom",
                str(output),
                f"--props={props}",
                "--frame=30",
            ],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        if completed.returncode:
            raise PronunciationError(f"cover_render_failed:{asset}:{completed.stderr[-2000:]}")
        return {"asset_id": asset, "cover": str(output.resolve()), "frame": 30}

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        rows = list(executor.map(render_one, paths))
    result = {"status": "passed", "module_count": len(rows), "covers": rows}
    write_json(WORK_ROOT / "cover-report.json", result)
    return result


def read_wave_bytes(path: Path) -> tuple[bytes, int]:
    with wave.open(str(path), "rb") as handle:
        if (
            handle.getnchannels() != 1
            or handle.getsampwidth() != 2
            or handle.getframerate() != 24_000
        ):
            raise PronunciationError(f"unexpected_wave_contract:{path}")
        return handle.readframes(handle.getnframes()), handle.getnframes()


def inspect_final_single(frames: bytes, card_id: str) -> dict[str, Any]:
    samples = array("h")
    samples.frombytes(frames)
    if sys.byteorder != "little":
        samples.byteswap()
    duration_ms = round(len(samples) * 1000 / 24_000)
    threshold = round(32767 * (10 ** (-45 / 20)))
    audible = [index for index, sample in enumerate(samples) if abs(sample) >= threshold]
    if not audible:
        return {"card_id": card_id, "passed": False, "failure": "no_audible_signal"}
    silence_fraction = 1 - len(audible) / max(1, len(samples))
    leading_ms = round(audible[0] * 1000 / 24_000)
    trailing_ms = round((len(samples) - audible[-1] - 1) * 1000 / 24_000)
    clipping_fraction = sum(abs(sample) >= 32760 for sample in samples) / max(1, len(samples))
    peak = max(abs(sample) for sample in samples) / 32768
    gates = {
        "duration": 200 <= duration_ms <= 5000,
        "signal": peak >= 0.01,
        "silence_fraction": silence_fraction <= 0.75,
        "leading_silence": leading_ms <= 180,
        "trailing_silence": trailing_ms <= 180,
        "clipping": clipping_fraction <= 0.001,
    }
    return {
        "card_id": card_id,
        "duration_ms": duration_ms,
        "peak_absolute": round(peak, 6),
        "silence_fraction": round(silence_fraction, 6),
        "leading_silence_ms": leading_ms,
        "trailing_silence_ms": trailing_ms,
        "clipping_fraction": round(clipping_fraction, 8),
        "gates": gates,
        "passed": all(gates.values()),
    }


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        raise PronunciationError(f"invalid_png:{path}")
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def qa_all(languages: list[str]) -> dict[str, Any]:
    source_paths = iter_sources(languages)
    rows = []
    card_total = 0
    final_audio_quality: list[dict[str, Any]] = []
    silence = b"\x00" * round(24_000 * 0.650) * 2
    for path in source_paths:
        source = read_json(path)
        cards = validate_source(source)
        asset = source["asset_id"]
        manifest_path = PUBLIC_ROOT / asset / "audio" / "audio.manifest.json"
        manifest = read_json(manifest_path)
        if manifest.get("source_sha256") != canonical_hash(source):
            raise PronunciationError(f"audio_source_checksum_mismatch:{asset}")
        artifacts = {row["card_id"]: row for row in manifest.get("artifacts") or []}
        if set(artifacts) != {card["card_id"] for card in cards}:
            raise PronunciationError(f"audio_card_inventory_mismatch:{asset}")
        for card in cards:
            card_id = card["card_id"]
            single_path = PUBLIC_ROOT / asset / "audio" / "singles" / f"{card_id}.wav"
            repeated_path = PUBLIC_ROOT / asset / "audio" / "cards" / f"{card_id}.wav"
            single_frames, _ = read_wave_bytes(single_path)
            repeated_frames, _ = read_wave_bytes(repeated_path)
            final_audio_quality.append(inspect_final_single(single_frames, card_id))
            if repeated_frames != single_frames + silence + single_frames:
                raise PronunciationError(f"non_identical_repetition:{asset}:{card_id}")
            if artifacts[card_id].get("spoken_repetitions") != 2:
                raise PronunciationError(f"repetition_manifest_mismatch:{asset}:{card_id}")
            card_total += 1
        rows.append(
            {
                "module_code": source["module_code"],
                "asset_id": asset,
                "card_count": len(cards),
                "source_sha256": manifest["source_sha256"],
                "exact_repetition_gate": "passed",
                "human_native_audition": "pending",
            }
        )
    asr_rows = []
    for language in languages:
        validation_path = WORK_ROOT / "qwen" / language / "strict-validation.json"
        validation = read_json(validation_path)
        asr_rows.append(
            {
                "language": language,
                "path": str(validation_path.resolve()),
                "passed": validation.get("strict_asr_passed") is True
                and validation.get("speaker_consistency_passed") is True,
                "primary_model": validation.get("turbo_model"),
                "primary_item_count": validation.get("item_count"),
                "large_v3_review_count": validation.get("large_v3_review_count"),
                "raw_pretrim_audio_quality_passed": (validation.get("audio_quality") or {}).get("passed") is True,
                "delivery_audio_quality_evaluated_separately": True,
                "speaker_consistency_passed": validation.get("speaker_consistency_passed") is True,
            }
        )
    render_report = read_json(WORK_ROOT / "render-report.json")
    expected_render_count = len(source_paths)
    render_rows = render_report.get("modules") or []
    cover_checks = [
        {
            "asset_id": row.get("asset_id"),
            "path": row.get("thumbnail"),
            "dimensions": list(png_dimensions(Path(str(row.get("thumbnail"))))),
        }
        for row in render_rows
    ]
    render_passed = (
        len(render_rows) == expected_render_count
        and all((row.get("video_qa") or {}).get("status") == "passed" for row in render_rows)
        and all(row["dimensions"] == [1080, 1920] for row in cover_checks)
    )
    visual_report_path = WORK_ROOT / "visual-qa" / "report.json"
    visual_report = read_json(visual_report_path)
    visual_checks = visual_report.get("checks") or {}
    visual_passed = (
        visual_report.get("status") == "passed"
        and visual_checks.get("guiding_language_visible") is False
        and visual_checks.get("call_to_action_visible") is False
        and all(
            visual_checks.get(name) is True
            for name in (
                "phone_safe_margins",
                "pattern_legibility",
                "ipa_legibility",
                "word_legibility",
                "focus_highlight_visible",
                "long_copy_fits",
                "early_middle_late_states_visible",
            )
        )
    )
    report = {
        "schema_version": 1,
        "machine_gate": "passed"
        if len(rows) == len(source_paths)
        and all(row["passed"] for row in asr_rows)
        and all(row["passed"] for row in final_audio_quality)
        and render_passed
        and visual_passed
        else "failed",
        "languages": languages,
        "module_count": len(rows),
        "card_count": card_total,
        "source_and_exact_repetition": {"passed": True, "modules": rows},
        "final_audio_quality": {
            "passed": all(row["passed"] for row in final_audio_quality),
            "item_count": len(final_audio_quality),
            "items": final_audio_quality,
        },
        "asr_and_audio": {"passed": all(row["passed"] for row in asr_rows), "languages": asr_rows},
        "render": {
            "passed": render_passed,
            "module_count": len(render_rows),
            "cover_checks": cover_checks,
        },
        "representative_visual_inspection": {
            "passed": visual_passed,
            "path": str(visual_report_path.resolve()),
            "report": visual_report,
        },
        "human_native_audition": "pending",
        "release_ready": False,
        "publishing": "disabled",
    }
    write_json(WORK_ROOT / "machine-qa.json", report)
    if report["machine_gate"] != "passed":
        raise PronunciationError("bulk_machine_qa_failed")
    return report


def package_delivery(languages: list[str]) -> dict[str, Any]:
    delivery_root = RENDER_ROOT / "delivery"
    delivery_root.mkdir(parents=True, exist_ok=True)
    render_report = read_json(WORK_ROOT / "render-report.json")
    render_by_asset = {row["asset_id"]: row for row in render_report.get("modules") or []}
    modules = []
    audition_rows = []
    playlists: dict[str, list[str]] = {language: [] for language in languages}
    for path in iter_sources(languages):
        source = read_json(path)
        asset = source["asset_id"]
        render_row = render_by_asset.get(asset)
        if not render_row:
            raise PronunciationError(f"render_missing_from_delivery:{asset}")
        audio_manifest_path = PUBLIC_ROOT / asset / "audio" / "audio.manifest.json"
        audio_manifest = read_json(audio_manifest_path)
        module_row = {
            "module_code": source["module_code"],
            "asset_id": asset,
            "target_language": source["target_language"],
            "locale": source["locale"],
            "variety": source["variety"],
            "cefr": source["cefr"],
            "card_count": len(source["cards"]),
            "source": str(path.resolve()),
            "audio_manifest": str(audio_manifest_path.resolve()),
            "master_audio": audio_manifest["master"]["path"],
            "video": render_row["video"],
            "cover": render_row["thumbnail"],
            "native_audition": "pending",
            "release_state": "local_preview_only",
        }
        modules.append(module_row)
        playlists[source["target_language"]].append(render_row["video"])
        artifacts = {row["card_id"]: row for row in audio_manifest["artifacts"]}
        for card in source["cards"]:
            audition_rows.append(
                {
                    "language": source["target_language"],
                    "locale": source["locale"],
                    "variety": source["variety"],
                    "module_code": source["module_code"],
                    "asset_id": asset,
                    "card_id": card["card_id"],
                    "pattern": card["pattern"],
                    "pattern_ipa": card["phonetic"],
                    "word": card["word"],
                    "word_ipa": card["word_phonetic"],
                    "single_audio": artifacts[card["card_id"]]["normalized_single_utterance"]["path"],
                    "repeated_audio": artifacts[card["card_id"]]["path"],
                    "audition_status": "pending",
                    "reviewer": "",
                    "notes": "",
                }
            )
    queue_path = delivery_root / "native-audition-queue.csv"
    with queue_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audition_rows[0]))
        writer.writeheader()
        writer.writerows(audition_rows)
    for language, videos in playlists.items():
        (delivery_root / f"{language}-previews.m3u8").write_text(
            "#EXTM3U\n" + "\n".join(videos) + "\n", encoding="utf-8"
        )
    result = {
        "schema_version": 1,
        "status": "machine_qa_passed_human_audition_pending",
        "languages": languages,
        "module_count": len(modules),
        "card_count": len(audition_rows),
        "modules": modules,
        "native_audition_queue": str(queue_path.resolve()),
        "playlist_paths": {
            language: str((delivery_root / f"{language}-previews.m3u8").resolve())
            for language in languages
        },
        "release_ready": False,
        "publishing": "disabled",
    }
    write_json(delivery_root / "delivery-index.json", result)
    return result


def parse_languages(raw: str) -> list[str]:
    values = [part.strip().casefold() for part in raw.split(",") if part.strip()]
    invalid = sorted(set(values) - set(MODULES))
    if invalid:
        raise PronunciationError(f"unsupported_languages:{','.join(invalid)}")
    return values


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument(
        "command",
        choices=("author", "validate", "qwen-batches", "audio", "compile", "render", "covers", "qa", "package"),
    )
    root.add_argument("--languages", default="en,es,de")
    root.add_argument("--quality", choices=("preview", "final"), default="preview")
    root.add_argument("--workers", type=int, default=2)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        languages = parse_languages(args.languages)
        if args.command == "author":
            result = author_sources(languages)
        elif args.command == "validate":
            result = validate_inventory(languages)
        elif args.command == "qwen-batches":
            result = build_qwen_batches(languages)
        elif args.command == "audio":
            result = assemble_audio(languages)
        elif args.command == "compile":
            result = compile_all(languages)
        elif args.command == "render":
            result = render_all(languages, args.quality, args.workers)
        elif args.command == "covers":
            result = render_covers(languages, args.workers)
        elif args.command == "qa":
            result = qa_all(languages)
        else:
            result = package_delivery(languages)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (PronunciationError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
