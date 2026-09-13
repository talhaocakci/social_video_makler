# GFF Social Video Factory

Build preview-ready social videos from exact GetFluentFast content versions.
The MVP accepts Guided Communication JSON, compiles a deterministic video spec,
and renders a branded vertical MP4 with Remotion.

## Local sample

Requires Node 20.19+, pnpm, and Python 3.10+.

```bash
pnpm install
pnpm gff:sample
```

Create a local two-voice, timestamped audio demo and render the Simplified
Guided Communication one turn at a time:

```bash
pnpm gff:demo-audio
pnpm gff:sample-spoken
```

The demo audio uses macOS `say` and is marked as synthetic in the source and
render manifests. Production renders should use the canonical GFF audio file
and its supplied/forced-aligned segment timestamps.

Outputs:

- `renders/bakery-dialogue-preview.mp4`
- `work/bakery-dialogue.props.json`
- `work/bakery-dialogue.manifest.json`

Open the template gallery with `pnpm studio`.

## Feed ingestion and safety boundary

An explicit request can upload a QA-passed render to the private GetFluentFast
S3/DynamoDB feed with `npm run gff:feed-upload -- ...`. This is internal feed
ingestion, not social publishing. Instagram, YouTube, TikTok, and other public
destinations remain a separate approval-gated layer. See
`docs/PUBLISHING_LAYER.md`.

## Upstream motion engine

The renderer is based on OverlayMotion Core 0.8.0. Its license and notices are
preserved in this repository. GFF-specific compilation, brand settings, skill,
and content adapters live alongside the engine.
