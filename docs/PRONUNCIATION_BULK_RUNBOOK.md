# Pronunciation bulk preview runbook

This workflow builds the bounded v1 pronunciation catalog for English (`en-US`),
Spanish (`es-419`, international seseo and yeísmo), and German (`de-DE`). It creates local previews only.

## Fixed contract

- 87 modules: 38 English, 25 Spanish, 24 German.
- 435 learner examples: 203 English, 123 Spanish, 109 German.
- Learner-visible content contains only the target language plus IPA.
- Spoken input is only the example word or connected-speech example.
- Each single 24 kHz mono WAV is silence-trimmed and byte-copied exactly twice
  with 650 ms of silence between copies.
- Upload, ingestion, release, and social publication are disabled.
- Native-speaker audition of every example remains mandatory after machine QA.

## Reproducible local sequence

Authoring uses `gruut==2.4.0` and its pinned `2.0.1` language dictionaries in a
temporary local virtual environment. Editorial corrections live in
`scripts/gff_pronunciation_bulk.py:IPA_OVERRIDES`; generated IPA is never treated
as independently approved.

```sh
/tmp/gff-pronunciation-gruut-venv/bin/python scripts/gff_pronunciation_bulk.py author
python3 scripts/gff_pronunciation_bulk.py validate
python3 scripts/gff_pronunciation_bulk.py qwen-batches
```

For each of `en`, `es`, and `de`, plan and generate the local Qwen batch with:

```sh
/Users/talhaocakci/Projects/local_whisper/.venv-tts/bin/python \
  /Users/talhaocakci/Projects/local_whisper/gff_tts_pipeline.py \
  work/pronunciation-bulk/qwen/en.source.json \
  work/pronunciation-bulk/qwen/en --plan-only

/Users/talhaocakci/Projects/local_whisper/.venv-tts/bin/python \
  /Users/talhaocakci/Projects/local_whisper/gff_tts_pipeline.py \
  work/pronunciation-bulk/qwen/en.source.json \
  work/pronunciation-bulk/qwen/en
```

Then assemble, compile, render, and audit:

```sh
python3 scripts/gff_pronunciation_bulk.py audio
python3 scripts/gff_pronunciation_bulk.py compile
python3 scripts/gff_pronunciation_bulk.py render --quality preview --workers 2

/Users/talhaocakci/Projects/local_whisper/.venv/bin/python \
  scripts/gff_pronunciation_asr.py \
  work/pronunciation-bulk/qwen/en.source.json \
  work/pronunciation-bulk/qwen/en/manifest.json \
  work/pronunciation-bulk/qwen/en/strict-validation.json --language en

python3 scripts/gff_pronunciation_bulk.py qa
python3 scripts/gff_pronunciation_bulk.py package
```

The strict ASR screen runs local `large-v3-turbo` on every single utterance and
local `large-v3` on every disagreement. An exact accent-folded, normalized-number,
or declared homophone match is required. This screen is diagnostic and does not
replace native audition.

## Outputs

- Sources: `examples/pronunciation-bulk/{language}/*.json`
- Single, repeated, and master WAVs:
  `public/generated/pronunciation-bulk/{asset_id}/audio/`
- Compiled props/manifests: `work/pronunciation-bulk/compiled/{asset_id}/`
- MP4 and cover PNG previews: `renders/pronunciation-bulk/{language}/`
- Machine QA: `work/pronunciation-bulk/machine-qa.json`
- Delivery index, playlists, and audition queue:
  `renders/pronunciation-bulk/delivery/`
