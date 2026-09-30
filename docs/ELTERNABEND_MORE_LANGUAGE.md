# Elternabend: more words and phrases

A separate local variation, `04-more-language.mp4`, preserves the accepted `01-close-reading.mp4` and its script/QA. It uses the registered `reading-coach` template, paper treatment, same approved German and English Qwen references, and exact same 137 source sentences.

Adds 31 short source-bound vocabulary stops containing 44 lexical pairs, alongside the earlier 26 stops. German anchor → spoken English contextual meaning. No speculative questions. First complete reading at .88x, followed by the complete normal-speed reading without teaching interruptions.

Presentation flags hide level, chapter and pass markers. Source CEFR remains in internal provenance. Classroom illustration, teaching panels and source-bound editorial underlines remain. No guessed word timestamps.

## Reproduction

```sh
python3 scripts/elternabend_more_language.py author
/Users/talhaocakci/Projects/local_whisper/.venv-tts/bin/python scripts/elternabend_more_language.py audio
GFF_READING_WORK="$PWD/work/reading-teacher-elternabend-more-language" /Users/talhaocakci/Projects/local_whisper/.venv/bin/python scripts/qa-elternabend-teacher.py
```

Independent editorial audit must bind the exact new lesson checksum. Run waveform and speaker audits with the same GFF_READING_WORK, compile using the new adapter, then render with GFF_READING_WORK and explicit ID 04-more-language. Delivery verification uses GFF_DELIVERY_RECEIPT=more-language-delivery-qa.json so the original receipt is preserved.

Export and materialize the complete new ordered script using gff_video_script.py and this variation’s work/script directory. German text/order, lexical pairs, all teacher speech, display flags, pauses, panel copy, highlighting, visuals and QR are retained. Translate guiding strings, select a guiding-language voice, regenerate speech, measure timings and inspect layout before rendering another language.

Outputs are local. QR destination publication/hosting remains separately pending.
