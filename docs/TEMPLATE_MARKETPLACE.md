# Template marketplace decisions

Reviewed on 2026-08-31. Re-check upstream terms before importing a new source.

## Selected foundation: OverlayMotion Core

- Source: https://github.com/ricardo/overlay-motion
- Version at project start: 0.8.0
- Templates relevant to GFF: `chat-bubbles`, `caption-classic`, `speaker-card`,
  `audiogram`, `prompt-box`, `countdown`, `numbered-steps`, and `hero-title`
- License: OverlayMotion Sustainable Use License in this repository's
  `LICENSE`; internal commercial use and rendered commercial outputs are
  allowed, while resale or redistribution as a template library is restricted.
- Decision: use as the checked-in motion engine and preserve all notices.

## Approved component source: RemotionUI

- Gallery: https://remotionui.com/docs/components/browse
- Source: https://github.com/riaz37/remotion-ui
- License: MIT
- Candidates: `speaker-label-captions`, `karaoke-captions`,
  `subtitle-translate`, `word-pop-captions`, `quiz-question`, `audio-pulse`, and
  `social-clip`
- Decision: add components selectively after visual review; do not bulk-import
  the catalog.

## Official reference: Remotion TikTok template

- Source: https://github.com/remotion-dev/template-tiktok
- Use: reference implementation for paged, word-highlighted captions
- Decision: do not adopt its Whisper transcription path for canonical GFF
  dialogue. GFF captions should use authored text plus forced alignment.

## Deferred paid catalogs

RenderComp and OverlayMotion Premium may be reconsidered after the first GFF
visual family is approved. Do not purchase or copy paid source without explicit
user approval and a recorded license.
