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

For visual dialogue, also inspect inward gaze, transparent edges on the actual
background, stable cast across clips, both sides of speaker handoffs, the longest
sentence and the timing/evidence of topic cues. See [visual dialogue](visual-dialogue.md).

## Paired dialogue delivery

Check adjacent exchanges as a pair, including questions, acknowledgments and
longer replies. Require compatible engagement and emotional intensity across
both voices; reject an animated person paired with an unintentionally weary or
reluctant partner. Record the delivery profile and any replacement reason.
Adult vocal body and perceived age must remain stable in more expressive
phrases. Reject childlike drift even when the two speakers match in volume or
energy; do not claim maturity from a low pitch or an adult persona description.
Audio level, ASR and source synchronization checks remain separate from perceived
energy and naturalness. See [dialogue delivery](dialogue-delivery.md).
