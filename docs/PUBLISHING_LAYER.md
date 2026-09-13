# Publishing layer (phase 2)

The current repository can render preview artifacts and explicitly ingest an
approved render into the private GetFluentFast S3/DynamoDB feed. Feed ingestion
uses `scripts/gff_feed.py upload`, keeps objects private, and is not a public
post.

The repository contains no social-platform credentials, OAuth clients, browser
macros, or scheduler integrations.

When phase 2 begins, publishing will remain separate from compilation and
rendering. A publish request must name an already-rendered artifact, its source
checksum, its destination, and an explicit user authorization from the current
request. Idempotency keys and remote post IDs must prevent duplicate posts.
