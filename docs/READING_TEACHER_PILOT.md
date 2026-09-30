# Reading teacher pilot

The local pilot turns the English B1 reading **Booking a hotel room** into
three complete lessons with Turkish teacher narration: close reading,
story-first review, and question-led recall. Each includes all five original
sentences. The story-first version additionally replays selected sentences.

`reading-coach` is registered in the existing OverlayMotion/Remotion engine.
It adds a source-aligned reading surface with editorial underlines, an opening
teaching panel, contextual illustrations, grammar diagrams, and an audio-level
indicator. All animation remains in the registered motion template. The
teacher panel contains teaching notes, not word-timed Turkish subtitles.

## Reproduce the local pilot

Use the installed Node runtime on PATH, the existing node_modules, Python 3,
and the installed macOS Yelda voice. No generation API is used. The original
reading snapshot, pedagogy snapshot and existing aligned Qwen audio live in
`work/reading-teacher-hotel/source` (local artifacts, not a production fetch).

```sh
python3 scripts/hotel_teacher_pilot.py
python3 scripts/gff_reading_teacher.py validate
python3 scripts/gff_reading_teacher.py audio
python3 scripts/gff_reading_teacher.py compile
node_modules/.bin/tsx scripts/render-reading-pilot.mts stills
node_modules/.bin/tsx scripts/render-reading-pilot.mts render
```

The teacher source is hand-authored and independently reviewed in this task;
`hotel_teacher_pilot.py` is an example storyboard, not a general automatic
pedagogy-to-speech author. A different reading requires an exact source bundle,
a new authored/reviewed storyboard, and verified matching audio. Production
reading, pedagogy, and audio records are never changed by these commands.

The original master is sliced at its existing contiguous sentence boundaries.
Word positions use the original Qwen forced-alignment evidence, including
zero-width native timestamps. Hyphenated display words remain unchanged when
the aligner tokenizes them without hyphens. Missing or incomplete alignment
fails compilation. A constant gain normalizes each voice clip; there is no
music bed. Teacher pace differs across scripts, but the teacher voice identity
is the same Yelda voice in all three. A recorded pronunciation mapping spells
Sarah as Sara only for Turkish synthesis; source text remains unchanged.

## Output and validation

Local outputs are in `renders/reading-teacher-hotel`, including a portable
comparison page, MP4s, covers and teacher scripts. Exact source identity,
revision, source text checksum, pedagogy bundle checksum, teacher text and audio
checksums, original voice provenance, and timeline are recorded in the work
manifests. The original scene artwork is generated with the built-in image
tool; the confirmation and calendar graphics are illustrative teaching diagrams,
not an actual hotel document or a claim about an external hotel's policy.

Verification includes an independent checksum-bound editorial audit, focused
alignment/fragment/template tests, TypeScript checking, full local large-v3
transcription of the teacher clips, selected second-model transcription,
rendered frame inspection, browser playback, and full video/audio decoding.

Remotion's first export introduced a measured 42.67 ms audio delay. Delivery
was corrected by copying the video stream and encoding AAC once from the exact
assembled WAV. `audio-remux-receipt.json` records the before/after hashes and
`delivery-qa.json` measures decoded-audio offsets at beginning, middle, and end.
Do not treat renderer success as the delivery sync check. Repeat that check
after any later mux or encoding step. Original exports are retained under
`work/reading-teacher-hotel/encoded-before-audio-fix`.

Human audio audition is not claimed. Passing transcription and waveform checks
does not establish that the teacher voice sounds natural to the user. Nothing
in this pilot is uploaded to the feed or published externally.
