# Render quality contract

Before delivery, verify:

- The generated manifest names source asset ID, exact version, checksum, GFF
  template family, and underlying motion templates.
- The render exists, is non-empty, and uses the requested aspect ratio.
- Target-language text matches the source export.
- Text remains inside platform-safe zones and is readable on a phone-sized
  preview.
- No two full-screen overlays unintentionally overlap.
- Audio, when present, is intelligible. Word-level captions are forced-aligned;
  turn-level dialogue cards use supplied segment timestamps.
- A spoken-dialogue render contains an audio stream and its manifest records
  audio provenance, segment count, and synchronization method.
- Music, when present, sits 15-20 LU below speech.
- The preview contains no publishing side effects, platform tokens, secrets, or
  private source URLs.

For a new visual family, inspect at least an early, middle, and late frame before
accepting the full render.
