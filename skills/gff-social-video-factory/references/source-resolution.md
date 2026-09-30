# Source resolution

## Accepted sources

- A Reading snapshot with matching existing narration, sentence/word alignment,
  and current sentence pedagogy; route to [long reading videos](long-reading-videos.md)
- Canonical Guided Communication JSON with `dialogue_turns`
- Canonical Scenario JSON with `missions`
- Vocabulary group JSON with `items`
- A resolved LearningChain bundle containing exact referenced assets
- An authenticated Content Studio URL that can be resolved without changing
  server state

## Exactness

Record `asset_id`, exact `version`, `target_language`, and a SHA-256 checksum of
the canonical source JSON. If a URL omits a version, resolve the current exact
version and disclose it before rendering. Never substitute a newer version
during the same job.

The `gff_media.py` compiler directly supports Guided Communication JSON. The
reading-teacher mode has its own storyboard/template route; do not pass a
Reading to the dialogue adapter. Scenario,
vocabulary, and chain inputs should be resolved to a local bundle before calling
the compiler; if that adapter is not yet present, report the missing adapter
instead of fabricating content.

Authenticated reads are allowed when the user supplied a Content Studio source.
Reads do not authorize edits, regeneration, publication, or platform uploads.
