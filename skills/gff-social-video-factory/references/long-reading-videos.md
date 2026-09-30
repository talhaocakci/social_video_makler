# Long reading videos: natural teaching and two listens

Use for `long video`, `uzun video`, a reading lesson with a natural teacher,
or a request for any/all of the three hotel-pilot formats. This is a long-video
mode within the social video factory, not a separate installed skill.

## Current default: understand the situation, then listen again

Unless the user selects another format, create one `paper` layout using the
registered `reading-coach` template, 1920x1080 at 30 FPS. Follow the fuller
Elternabend vocabulary variation as the current teaching direction:

- First listen: preserve every source sentence in order, about 10–15% slower
  than the natural target-language narration (.88x is the proven local example).
  Read one sentence or several connected sentences. After a sentence containing
  worthwhile new language, briefly explain it, then continue. Simple sentences
  need no interruption. No separate explanation workshop after the first listen.
- Second listen: the complete source again at natural regular speed, with no
  teacher explanations, questions or practice interruptions inside the reading.
  A short spoken transition and final app invitation may surround it.
- Choose useful words, verbs, separable verbs, everyday phrases and contextual
  senses, alongside selected grammar. Give enough vocabulary support to follow
  the real-life situation; do not restrict teaching to saved grammar notes or
  the original sparse selection. Explain important first uses, avoid repeating
  settled meanings, and leave easy runs of sentences uninterrupted. Density
  depends on the reading and learner needs; the example’s counts are not quotas.
- Every selected expression needs a spoken native target-language anchor and
  a short guiding-language meaning. Usually one or two compact sentences suffice
  for a lexical gloss. Add a brief contextual connection or useful grammar
  pattern when needed. For passive collection rules, explain both the verb’s
  meaning (abholen: pick up/collect) and the passive structure; naming passive
  alone leaves headphone listeners without the essential meaning.
- Audio must stand alone like an engaging radio lesson. No “the underlined
  word,” “look at the panel,” or other screen-dependent explanation. Do not
  substitute comprehension guessing games for clear teaching. Questions are
  optional when requested and useful, after explaining the meaning or pattern.
- Speak warmly to an adult about their real-life goal: “Let’s make the school’s
  plans and requests easier to follow,” rather than “A teacher explains school
  life.” Keep teacher delivery engaged and conversational, with light emphasis
  and natural pauses. Slowing target narration does not mean making the teacher
  sleepy, stretching syllables or mechanically slowing all English speech.
- Use local Qwen audio and reuse an approved mature adult reference for each
  language when available. Keep native quotations as separate language-role
  speech beats so English synthesis does not pronounce the German anchor.
  Audition the voice early; childish, sing-song or obviously synthetic delivery
  needs correction. Machine transcript checks alone do not establish naturalness.
- Keep a relevant illustration on the left, the source sentence on the right,
  and concise meanings/grammar in the teaching panel. Choose visuals for the
  actual situation: hotel reception for booking, parents and a teacher in a
  classroom for Elternabend. Default to no left three-step summary diagrams,
  no “sample/example” production labels, no visible level badge, chapter heading
  or first/second-pass marker. Preserve source CEFR and chapter/pass metadata
  internally. The renderer supports `presentation.showLevel`, `showChapter`,
  and `showPassLabel`; set all three false for this default.

Use persisted pedagogy as evidence, then add source-bound lexical glosses where
helpful. Keep source Reading content immutable. Bind each added gloss to its
sentence, literal source form and contextual meaning, marking its provenance
as added video teaching; never fabricate a persisted pedagogy ID. Independently
review both saved-point commentary and added vocabulary against the exact source.

## App promotion: phone panel and QR

Include this promotional treatment in future long reading lessons. Use the
registered video layout; the interaction below is a production requirement,
not a claim that the current renderer already implements the animation.

### Composition and motion

Animate the lesson area inward from its corners with a smooth uniform scale
and translation. Keep the lesson visible beside the promotion, preserving its
original aspect ratio without cropping, stretching or squeezing text. The right
teaching area visually transitions into a portrait phone demonstration as the
promotion grows on the right. The lesson occupies the remaining left region;
the promotion occupies a phone-width portrait column, with readable CTA and QR
space. Use fit/contain geometry and safe margins, not a phone-shaped distortion
of the entire landscape lesson. Reverse the transition cleanly after the slot.
During silent slots, the miniature lesson continues playing in sync.

Show a short, authentic app journey inside the phone:

1. Open the relevant Reading in the actual GetFluentFast interface.
2. Select a useful word or expression and show the real add-to-vocabulary action.
3. Transition to the actual practice/quiz screen and demonstrate practising it.

Use supplied or verified current app screenshots/screen recordings, matching
real typography, controls and navigation. Obtain missing captures from the app
or a suitable existing asset source before final production. Do not invent a
lookalike UI, a nonexistent button, or an unsupported direct transition from a
Reading to a quiz. Keep genuine UI labels in their captured language; surrounding
promotional copy and narration use the lesson’s guiding language. Capture the
real app with that same guiding language selected; do not relabel old screenshots
or mix Turkish quiz screens into an English-guided lesson. Show a clear
tap/selection animation and the real resulting state. Choose an expression from
this lesson when the actual app flow supports it.

### Timing and sound

- Anchor the spoken phone demonstration immediately after the teacher finishes
  explaining the exact word shown in the app. The sequence is source sentence,
  complete explanation, save/practise that same word, then the next source
  sentence in the same pass. Record the explanation scene key and source word;
  do not place this demonstration at an unrelated pass boundary. Give it its own
  measured scene using the approved guiding voice, without interrupting speech.
  Its closing narration must match continuing the current reading, not restarting it.
- The first ad follows the second explained word or an explanation at source
  sentence 3 or later; never advertise before sentence 3. Überblick, the first
  explained word in sentence 3, therefore qualifies. Finish its explanation first.
- Later ads start at the first completed word/phrase explanation at least 360
  seconds after the preceding ad start on the final timeline. Never snap backward
  to a nearby explanation or insert at a fixed clock tick. Include inserted spoken
  ad duration when calculating later times. Demonstrate the word just explained
  in that slot’s actual app captures, not an unrelated word reused from another ad.
  If there is no later explanation, omit the slot; keep the second listen free of
  new teaching interruptions. These later slots are silent while narration continues.
  Silent means no promotional voice, chime or music and no audio ducking. It
  does not mean muting the reading. The second listen remains uninterrupted in
  audio even when this visual promotion appears.
- Default to roughly 15 seconds for silent slots, including a stable QR hold of
  at least 10 seconds. Size the spoken slot from its actual generated audio,
  allowing the same scan time; do not force translated narration into a fixed
  duration. Treat these durations as adjustable defaults, not content quotas.
- Resolve schedules with `scripts/reading_ad_schedule.py` after narration
  durations are measured. If a slot overlaps the closing QR, suppress it and
  record why; never stack two promos. Skip a final partial slot
  that cannot provide the scan hold. Avoid opening with an extra promo at 00:00.

### Invitation and destination

Use warm, concrete copy, localized into the guiding language. English example:
“Want to keep practising? Scan the QR code to find this reading and many more
in GetFluentFast. Download the app, save useful words and phrases, and revisit
the vocabulary and grammar with practice and quizzes. Let’s carry on.”
Adapt feature wording to verified app capabilities; do not promise practice
modes that the shown flow does not support. A short silent headline can be
“Keep learning in GetFluentFast”, with “Save words · Practise · Try a quiz” and
“Scan to open this reading”. The spoken message should also make sense to
headphone listeners, e.g. mention the lesson link as an alternative to scanning.

Keep a high-contrast, stationary QR with quiet zone throughout the stable part
of each promotion. It must remain readable from a television; never hide it
inside tiny phone UI. Encode the canonical HTTPS page for the exact Reading,
with app-opening deep link and verified download/install fallback on the landing
page. Preserve the lesson-specific destination, rather than substituting a
generic homepage. Follow the QR continuation requirements below and distinguish
local scan success from deployed landing-page/app routing verification.

Record each promo in the ordered script: spoken/silent mode, scheduling rule,
resolved start and duration, collision decisions, localized CTA/speech, exact
screenshot/recording assets and their app-flow provenance, phone/lesson bounds,
transition timing, QR payload and stable hold. Recompute the schedule for every
guiding-language render. Inspect entry, stable and exit frames and verify actual
encoded QR scanning and audio continuity around silent slots. Retain accepted
videos when producing a promotional revision as a new variation.

## Ordered script and retained variations

Before synthesis, store the entire ordered video script: both reading passes,
source text, teacher speech beats with language roles/directions/pauses, glosses,
grammar notes, panel text, highlights, visuals, UI/display flags, transitions,
CTA, phone-promotion events and reading QR/deep link. Export structured JSON, a readable script, and a
guiding-language translation file. A translated version must retain target
text and order, localize all peripheral teaching/display strings, regenerate
speech, measure its duration, and rebuild timings. Never reuse another language’s
audio timestamps. Check translated panels for overflow.

For revisions requested as another variation, retain the accepted MP4 and its
script/receipts. Use a distinct variant ID and work directory, record the parent
checksum, and expose both in the preview. Reuse matching audio/assets rather
than changing an approved voice unnecessarily.

Current source-specific examples (paths relative to factory root):

- Accepted lesson: `work/reading-teacher-elternabend/lesson.json`,
  `scripts/elternabend_two_pass.py`, `scripts/elternabend_audio_first.py`.
- Fuller vocabulary variation: `scripts/elternabend_more_language.py`,
  `work/reading-teacher-elternabend-more-language/lesson.json` and `script/`.
  It retains the earlier 26 stops and adds 31 compact stops with 44 lexical pairs.
  These are example density choices for the 137-sentence source.
- Reproduction and limits: `docs/ELTERNABEND_MORE_LANGUAGE.md`.
- Script localization: `scripts/gff_video_script.py export` / `materialize`.
- Renderer: `scripts/render-elternabend.mts`, explicit variant ID and optional
  `GFF_READING_WORK`. Delivery verification supports `GFF_DELIVERY_RECEIPT` to
  preserve the accepted version’s receipt. Run the actual source-bound editorial,
  transcript, waveform, voice-consistency, visual, decoded-sync and encoded-QR
  checks. Public QR hosting/deep-link behavior is separate from local scanning.

These adapters remain Elternabend-specific, not an arbitrary-Reading or
arbitrary-language synthesis CLI. For another Reading, create a source-specific
adapter/work directory while reusing this sequence, script contract and renderer.
Do not reuse this reading’s teaching text, fixed source paths or classroom image
for an unrelated situation.

## Preserved experimental alternatives (explicit selection)

| Stable variant ID | User-facing name | Teaching sequence | Visual treatment |
| --- | --- | --- | --- |
| `pause-and-notice` | Pause & notice | Read a sentence or short connected group, pause on a useful word or structure, explain, then continue. | `paper`: warm illustrated split layout, source text, contextual underline and teaching panel. |
| `story-first` | Story first | Set a listening goal, play the complete reading without teacher interruptions, revisit selected sentences with explanations/examples, then recap. | `cinema`: darker scene backdrop, large readable source text and side panel. |
| `think-and-answer` | Think & answer | Read, ask a meaning or inference question, leave thinking time, explain the answer neutrally, continue, then recall. | `workshop`: large text, question/explanation panel, context thumbnail and thinking progress. |

Family: `reading-teacher`. Registered motion template: `reading-coach`.
Render an explicitly selected variant alone, or all three when requested.
Preserve differences in teaching order and spoken script, not just colors.
Use the same source for a comparison unless the user requests otherwise.

## Source and teaching script

Resolve a Reading with existing audio and useful sentence pedagogy. Snapshot
the exact source/revision and bind the text, pedagogy bundle and audio hashes.
Reuse matching narration and alignment. The hotel example is English B1 with
Turkish guidance; these languages, level, topic and five-sentence length are
example choices, not defaults for every future reading.

Choose target and guiding languages from the source and current request.
The language used to reply to the user does not determine the teacher language.
For new teaching narration, use the available `gff-content-skill` local-audio
workflow and its checks; do not silently substitute a different language or
voice engine.

Author a video-specific teaching layer from the pedagogy:

- Preserve source sentences and their contextual meanings. Select worthwhile
  teaching points rather than reading every annotation aloud.
- After narration, naturally connect the sentence to the highlighted word,
  phrase, or structure. Add short transitions and useful contextual examples.
  Store these as video commentary, not edits to the canonical Reading.
- Explain the meaning in this context first. Add another sense only if it
  clarifies a real contrast; do not enumerate unrelated dictionary senses.
- Bind each teaching point to its sentence index, exact highlighted substring,
  and supporting pedagogy point ID when one exists. Distinguish invented
  practice examples from source facts in speech and provenance, without adding
  a cold production label to the video.
- Keep a question distinct from confirmed information and an asked-about action
  distinct from a completed action. In recall videos, reveal the answer without
  pretending to have heard or scored the viewer's response.
- Independently review new teaching text against source and pedagogy before
  final delivery; bind the review to the actual script checksum.

Default to the complete reading for a long lesson. If sampling an excerpt,
state that scope. A long reading may need chapters or short connected groups;
do not truncate it to the pilot's five sentences. Let the content determine
duration; the pilot's roughly 100–115 seconds are not a duration requirement.

## Visual and audio behavior

Use relevant scenes that explain the actual events. A phone reservation can
show the traveler calling and the receptionist checking information; do not
turn it into an in-person check-in. Use original or rights-cleared visuals.
Teaching diagrams can show booking details or a deadline without inventing
actual dates, prices or hotel policies. Keep diagrams legible, rather than
placing large duplicate diagram text behind the reading.

Highlight spoken words only from forced-alignment evidence for the exact audio.
An editorial underline identifies the teacher's selected source span; it is
not a guessed word timestamp. Keep the sentence visible while its explanation
panel opens. Panels contain concise teaching notes, not an entire transcript.
If teacher subtitles are added, obtain valid timing for that teacher audio.

Use measured clip durations to sequence narration, teacher speech and thinking
pauses. Preserve a consistent teacher identity within a variant. Variations in
pace do not constitute different voice identities. A local prototype voice
must be described as such; machine transcription is not proof of naturalness.

## Implementation and reusable baseline

All project paths below are relative to the resolved factory root from
`SKILL.md` (`/Users/talhaocakci/Projects/gff-social-video-factory` for the
installed personal copy).

- `src/templates/reading-coach/index.tsx`: registered renderer and Zod schema.
  Select `treatment` = `paper`, `cinema`, or `workshop`.
- `scripts/hotel_teacher_pilot.py`: three authored baseline storyboards.
- `scripts/gff_reading_teacher.py`: source checks, local teacher synthesis,
  audio assembly, exact-text word-span mapping and spec compilation.
- `scripts/render-reading-pilot.mts`: still and full-video rendering examples
  through the existing Remotion `custom` composition.
- `docs/READING_TEACHER_PILOT.md`: reproduction steps, provenance and QA details.
- `work/reading-teacher-hotel/lesson.json`, `source/`, per-variant manifests and
  audit reports: original local source-bound artifacts, when still present.
- `renders/reading-teacher-hotel/index.html`: completed comparison baseline.
  Pilot file stems map respectively to `01-close-reading`, `02-story-first`,
  and `03-predict-recall`.

The hotel scripts are hotel-specific; the newer Elternabend adapters above
are also source-specific. Neither is a general arbitrary-Reading CLI.
For that exact pilot, use the reproduction commands in the project document.
For a new reading, preserve the baseline and create a separate work/output
directory and source-specific adapter, reusing the renderer and assembly
logic. Do not run `hotel_teacher_pilot.py` expecting it to author another
source, overwrite the baseline, or silently reuse its teaching copy/artwork.

The renderer accepts `title`, `variantTitle`, `treatment`, `scenes`, and optional
measured audio `levels`. Each scene carries `kind` (`reading`, `teacher`,
`pause`), `sentence`, `start`, `duration`, exact source `text`, local `image`,
and optional `focus`, `title`, `body`, `note`, `diagram`, and aligned `words`.
Word entries use original character positions `start`/`end` and scene-relative
seconds `t0`/`t1`. Use the actual Zod schema as the contract. The composition's
base source is the assembled audio; render via `reading-coach` in `fullscreen`.

The hotel fallback renderer retains pilot-specific EN/TR labels, five-step labels,
diagram text and artwork fallback paths. Adapt those deliberately for another
source/language/length before rendering. Do not claim arbitrary-language or
arbitrary-length support is already parameterized. Never bypass validation by
making unrelated content pretend to be the hotel reading.

## Delivery and continuation

Default to 1920x1080, 30 FPS. Validate the spec, inspect early/middle/late frames
and panel transitions, then render each requested variant. Verify source
coverage, highlights, text bounds, audio intelligibility and final decoded
audio synchronization. Show playable MP4s and covers; a local comparison page
with chapter jumps is useful for multiple variants. The existing
`scripts/serve-reading-previews.py` supports byte ranges for the hotel gallery;
keep that behavior when adapting a gallery server so chapter seeking works.

The pilot exposed a 42.67 ms encoding delay. Do not apply that number blindly
to future exports. Measure the decoded output against the assembled WAV at
early, middle and late anchors. If needed, copy the video stream and encode
audio once from the exact WAV, then measure again. Keep the correction receipt.

Preserve these three variants as **experimental baselines with known gaps**.
The user intends to refine them later. Current gaps include prototype teacher
voice naturalness, limited scene motion, basic panel/underline transitions,
and hotel-specific labels/adapter assumptions. Improve the requested area in a
new iteration; do not present this baseline as a finished long-video product.
No new render, upload, publication, or canonical-content mutation follows
merely from saving or documenting the formats in the skill.

## QR continuation to the original reading

For a QR code or app continuation, follow `docs/READING_QR_FLOW.md` in the
factory repository. All three variants support the optional `readingLink`
props. Encode the canonical HTTPS content page, then link explicitly to the
exact reading in the app. Use a stationary large closing QR and preserve its
quiet zone. Verify the decoded final-frame payload and the deployed destination
before publication; a local QR image does not establish a working public flow.
