---
name: gff-social-video-factory
description: Compile a GetFluentFast LearningChain, Guided Communication, Scenario, or vocabulary export into branded preview videos and optionally ingest explicitly selected artifacts into the GFF S3 feed. Use for a Reel, Short, Story, dialogue video, social pack, thumbnail, render preview, or internal feed upload. Social-platform publication remains a separate approval-gated action.
---

# GFF Social Video Factory

Turn exact, versioned GFF content into repeatable video artifacts. Keep authored
learning text faithful to the source and make the visual treatment engaging.

## Hard boundary

Rendering writes local MP4, PNG, JSON, and validation artifacts only. Never
infer an upload from `create`, `render`, `preview`, `export`, `hazırla`, or a
request for a social pack.

GFF feed ingestion is implemented and is distinct from social-platform
publication. Run `scripts/gff_feed.py upload` only when the current request
explicitly says to upload/add the selected artifact to the internal S3/feed.
The upload must reserve a short collision-protected ID, write MP4, cover, and
manifest beneath that ID, and mark the DynamoDB row `ready` only after all
objects succeed. MP4 and cover objects beneath the dedicated `social-videos/`
prefix intentionally use stable public-read URLs; manifests and every other
bucket prefix stay private. Do not add object ACLs or broaden the prefix policy.

The skill must not call Instagram, YouTube, TikTok, scheduling, or their upload
APIs unless a separate social publishing layer exists and the current request
meets the approval requirements below.

Even after a publishing layer is added, publish only when the current user
request explicitly uses an unambiguous action such as `publish`, `post`,
`yayınla`, or `paylaş` and identifies the destination. `Create`, `render`,
`preview`, `export`, `social pack oluştur`, `hazırla`, `S3'e yükle`, and
`feed'e ekle` never authorize social-platform publication.

## Project

Resolve the repository root as the directory three levels above this file. When
the installed personal-skill copy is active, use
`/Users/talhaocakci/Projects/gff-social-video-factory`. Use the checked-in
scripts and templates instead of rewriting render logic in the conversation.

Before editing or rendering:

1. Read `../../../AGENTS.md`.
2. Read [source resolution](references/source-resolution.md) when the input is a
   URL, chain, scenario, or a non-canonical export.
3. Read [template routing](references/template-routing.md) before choosing a
   visual format.
4. Read [quality contract](references/quality-contract.md) before delivering a
   render.

Read [publishing boundary](references/publishing-boundary.md) only when the user
mentions uploading, scheduling, or publishing.

## Workflow

1. Resolve an exact source asset and version. Prefer immutable exports. Never
   silently switch to a later version.
2. Save or identify a local source JSON. Do not modify the source content.
3. Compile it with `python3 scripts/gff_media.py compile --source <json>
   --props-out <props.json> --manifest-out <manifest.json>`.
4. Inspect the generated manifest and props. Record the selected GFF template
   family and underlying motion templates.
   A Guided Communication carrying `audio.src` plus ordered per-turn
   `audio.segments` automatically routes to `spoken-dialogue`; do not discard
   those timestamps or replace them with estimated pacing.
5. Render a preview with `python3 scripts/gff_media.py render --source <json>
   --output <video.mp4> --props-out <props.json> --manifest-out <manifest.json>`.
6. Verify the output using the quality contract. Show the resulting local MP4
   and thumbnail to the user when the interface supports it.
7. Stop locally unless internal feed ingestion was explicitly requested in the
   current request. For an authorized upload, run `python3 scripts/gff_feed.py
   upload --video <video.mp4> --thumbnail <cover.png> --manifest
   <manifest.json> --feed-rank <integer>`, then report the returned video ID and
   receipt. This does not authorize any social-platform post.

For the first render of a new source, default to one 1080x1920 vertical preview.
Generate a larger social pack only when requested or after the user approves the
visual direction.

## Content invariants

- Bind outputs to source asset ID, exact version, and content checksum.
- Preserve target-language dialogue and vocabulary verbatim unless the user
  explicitly asks to edit the learning content.
- Hooks, Turkish guidance, CTA copy, cropping, and animation may change without
  altering the authored learning text.
- Do not invent translations, speaker identity, proficiency level, missions,
  claims, or brand assets.
- Reuse already-generated audio and visual assets when their checksum matches.
- Captions with audio require word timing from forced alignment. Do not ship
  guessed word timings.
- Dialogue cards may use supplied per-turn segment timestamps. Label locally
  synthesized demo audio as synthetic and never present it as canonical GFF
  audio.

## Template sources

The renderer includes OverlayMotion Core under its checked-in license. The
project may adopt MIT-licensed RemotionUI components after recording their
source and license in `../../../docs/TEMPLATE_MARKETPLACE.md`. Do not copy a
marketplace component whose license is unclear.
