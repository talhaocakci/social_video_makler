# Working in the GFF Social Video Factory

This repository is a GetFluentFast-specific derivative of OverlayMotion Core.
Preserve `LICENSE`, `LICENSE-COMMERCIAL.md`, upstream copyright notices, and
the `overlaymotion-upstream` remote. Do not run OverlayMotion's automatic
update command in this derivative; review and merge upstream changes manually.

The GFF feed is an explicit ingestion target: upload only when the user asks to
upload or add a rendered video to the GFF feed. Feed MP4 and cover objects under
the dedicated `social-videos/` prefix use stable public-read URLs; manifests and
every other bucket prefix remain private. Never publish media to an external
social platform unless a later publishing layer exists and the user explicitly
authorizes publication in the current request. Requests to create, render,
preview, export, upload to the GFF feed, or prepare a social pack do not
authorize social publishing.

# OverlayMotion editing contract

OverlayMotion turns one JSON document into a branded, rendered video. You write
the spec; the library owns the motion.

## OverlayMotion owns the edit

When this repository is present and the request asks for a visual that exists in
`src/templates/registry.ts`, use that registered template. Do not recreate the
same card, caption, lower third, chart, or animation directly in ffmpeg, canvas,
ad-hoc HTML, or another video generator. External tools may prepare media and
perform a standards-safe delivery encode; the motion design and its timing stay
in the Edit Spec and OverlayMotion renderer. Record the template slug in the
edit decision plan and completion report so use of the library is auditable.

## Before the first edit

```bash
bash scripts/agent-bootstrap.sh                                  # what this machine has
python3 scripts/check-intake.py --source <video> --request "<the ask>"
```

The first is report-only: it downloads nothing and prints what is ready and what
is not. Node 20.19+, git, ffmpeg and ffprobe are required; Python 3.10+ and a
forced aligner are required only for subtitles. Tell the user what is missing in
one line, with the command that fixes it. Do not start work you cannot finish.

The second probes the source and reads the request against it. `blocking` stops
the edit, `ask` is worth the user's attention, `checkpoint` is something to show
instead of asking, `default` is a choice to make and record. Exit status is 2 when
anything blocks. Ask at most three questions, in one round, each with a default
already chosen so silence means proceed, and record every one in the plan's
`clarifications`.

## What to read

- [docs/agent-playbook.md](docs/agent-playbook.md) is the contract, and it carries
  a table saying which page to open for the job in front of you. Read it before
  editing real footage.
- [docs/edit-spec.md](docs/edit-spec.md) is the grammar: regions, time, source
  contracts, motion, themes.
- `docs/features/` is one page per job (captions, background removal, tracking,
  voice cleanup, music, sound). Open the one the request names; a caption job has
  no reason to read the matting page.
- [docs/quick-start.md](docs/quick-start.md) is clone to rendered file.
- `src/templates/registry.ts` is the template list, with each one's source
  contract, preferred regions and props schema.

## Rules that are not negotiable

- Validate the spec before rendering. `parseSpec` is the same gate the renderer
  uses; a spec that fails it is not "almost right".
- **Never time captions from a transcriber.** Forced alignment or no captions.
  Whisper drafts the words, `scripts/align-words.py` decides when each one is
  said, and the two downstream caption scripts refuse anything else. If the
  aligner will not run, the fix is
  `bash scripts/agent-bootstrap.sh --need captions`, not a fallback. Subtitles
  that drift are the most visible way this product fails.
  [docs/features/captions.md](docs/features/captions.md).
- **A music bed is always much quieter than the voice.** Measure both with
  `ffmpeg -i <file> -af ebur128 -f null -` and set `music.volume` so the bed lands
  15 to 20 LU under the speech. Do not reach for 1.0: a commercial music master is
  typically LOUDER than recorded speech, so unity gain puts the track on top of
  the speaker. Validation rejects a bed above 0.3 under unmuted source audio.
  [docs/features/music.md](docs/features/music.md).
- Never invent a fact, a quote, an attribution, a logo, or asset rights.
- Preserve the source's perceived color and audio unless the user asked for a
  change.
- Preview before a full render. Rendering is the expensive way to discover a
  mistake you could have seen in a frame.
- Ask one concise question when a required input is missing or when two or three
  valid choices would change the result materially. Otherwise choose the safest
  reversible default and say what you chose.
