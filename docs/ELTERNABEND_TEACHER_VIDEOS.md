# Elternabend: one guided two-pass lesson

Source: reading_elternabend_seed_de, published German B2, 137 sentences. Guiding language: English. Exact canonical German text remains unchanged.

Use one paper split layout with a classroom illustration. Read the complete first pass at 0.88x regular speed, explaining selected new words, phrases or grammar briefly between relevant sentences. There are 26 stops covering 27 saved points. Simple sentences continue consecutively. The second pass reads all 137 sentences at regular speed with no explanations or questions. No separate language review or practice section.

Additional concise glosses cover Betreuung, einen Termin vereinbaren, Rückmeldung, Unterschrift, Mitteilung, rechtzeitig and Ausflüge. Every teaching stop speaks a native German word or phrase, gives its English meaning, then briefly connects it to the sentence or structure. The audio is self-contained for headphone listening. Grammar-only stops also define useful lexical anchors such as abholen, einhalten, Lernstand and erledigen. The sample preserves the same complete speech beats as the full lesson. The mature German reference was approved by the user in the sample. English teacher speech uses the previously approved local Qwen radio identity. Full audio is separately checked by transcript, waveform and speaker consistency checks.

The registered reading-coach template displays exact German source sentences, contextual editorial underlines, English sentence meaning and selected pedagogy, chapter visuals, pass labels and QR continuation. Underlines are teaching spans, without guessed word timing.

## Local regeneration

1. Author with python3 scripts/elternabend_teacher.py author and obtain an independent checksum-bound editorial audit.
2. Generate German with local_whisper/.venv-tts/bin/python scripts/elternabend_mature_narrator.py. Reuse the approved narrator-mature-qwen reference.
3. Generate teacher audio with the same TTS Python and scripts/elternabend_teacher.py audio.
4. Check with ASR Python local_whisper/.venv/bin/python: scripts/qa-elternabend-narrator.py, scripts/qa-elternabend-teacher.py, and scripts/audit-elternabend-qwen.py waveform.
5. Check speaker and narrator with scripts/audit-elternabend-qwen.py in TTS Python, and measured pacing-qa.json.
6. Compile with python3 scripts/elternabend_teacher.py compile. Render representative stills using tsx scripts/render-elternabend.mts stills 01-close-reading, inspect them, then render 01-close-reading.
7. Run scripts/verify-elternabend-delivery.py 01-close-reading in TTS Python and scripts/verify-elternabend-qr.swift on the encoded QR frame.
8. Export with scripts/gff_video_script.py, copy the localization bundle to renders/reading-teacher-elternabend/script and rebuild the gallery with scripts/prepare-elternabend-gallery.py.

video-script.json stores ordered scenes, German text, teacher speech beats, delivery, pauses, meanings and grammar notes, panel/UI text, highlights, visuals, language roles and QR data. Translate the guiding-language values, preserve German quotations and scene order, generate new teacher audio and measure its new timing. See the script README for the materialize command and locale-specific adapter limitation.

These are local renders. The QR uses https://getfluentfast.app/reading/reading_elternabend_seed_de/ and the app continuation uses getfluentfast://reading/reading_elternabend_seed_de. Public landing-page hosting remains pending.
