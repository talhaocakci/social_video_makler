# Publishing boundary

The GetFluentFast feed and public social-platform publishing are separate
operations.

Uploading a rendered artifact to the configured GFF S3 bucket and registering
it in the GFF feed catalog is an internal ingestion action. It is allowed only
when the user explicitly asks to upload or add the video to the GFF feed. Use
`scripts/gff_feed.py upload`. The dedicated `social-videos/*/video.mp4` and
`social-videos/*/cover.png` objects are intentionally public-read so clients can
use stable unsigned URLs and cache ahead. Manifests and all unrelated prefixes
remain private. Never use public object ACLs or expand the public bucket-policy
scope beyond those feed asset patterns without a new explicit decision.

Anyone who obtains a feed asset URL can copy or redistribute that asset. The
public-read model prevents presigning load; it is not content-rights protection.

Publishing to Instagram, YouTube, TikTok, or another external social platform
is a separate second layer and is not implemented in this repository. Do not
work around its absence with browser automation, curl, a third-party scheduler,
or direct platform APIs.

When a publishing layer is later implemented, require all of the following in
the current request:

1. An explicit action: `publish`, `post`, `yayınla`, or `paylaş`.
2. Exact destination accounts or channels.
3. The exact approved artifact or social pack version.

Preview approval by itself is not publication approval. Stop after one failed
external publish attempt unless the failure is clearly retryable and the retry
cannot create a duplicate post.
