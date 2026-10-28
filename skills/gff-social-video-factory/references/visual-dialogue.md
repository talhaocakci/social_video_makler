# People and motion in dialogue videos

Use this treatment for conversational Stories and dialogue videos. It does not
replace the separate reading-teacher layout or authorize new voice generation.

## Cast and gaze

- Use original fictional adult portraits, retaining the source speaker labels.
  Visual casting adds no biography, ethnicity claim, quote or real-person identity.
- Favor candid photographic warmth: soft window side light, relaxed attentive
  expressions, slight facial asymmetry and understated natural skin variation.
  A useful style prompt is Fujifilm X-T5, 50mm f/1.4, Portra 400 color and fine
  grain. These are aesthetic directions, not claims about an actual camera shoot.
  Avoid glossy stock portraits, waxy skin, airbrushing, exaggerated freckles,
  gritty pore sharpening and painted skin texture. More texture is not more real.
- Ask imagegen for **genuine transparent alpha**, a complete head and shoulders,
  and clean hair edges. Do not bake in a room, circle, rectangle, shadow or halo.
  Inspect the alpha and the cutout on the actual video background.
- Generate both directions, retaining the same identity, hair and clothes:
  head and eyes turned roughly 40–55 degrees to image right, and to image left.
  Neither gaze should meet the camera. Put the right-looking person on the
  left and the left-looking person on the right, at similar eye height and scale.
- A transparent two-cell atlas is supported by `speaker-card`: the left half
  looks right; the right half looks left. Keep each silhouette within its half.
  Use `portraitCell: left` or `right`; do not accidentally show both atlas cells
  in one portrait. Separate image files use `portraitCell: full`.
- Save selected PNGs in the job's public assets and record prompts, generator,
  source references, checksums, alpha checks and directions in the asset receipt.
  Reuse a matching asset instead of generating a new face for each clip.

## Motion and layout

Use the registered `speaker-card` with `variant: cutout`, `photo`, `name`,
`portraitCell`, `active` and `fadeSec` (default 0.24). Set overlay motion to
`{style: none}` for this variant; a cutout should not inherit the intro card's
3D sway. Create one window per source turn for each fixed portrait position.
The active speaker is clear; the listener is quieter. Both soften out and back
in over the handoff. Multiple sentences by the same person do not trigger a
fresh portrait entrance. Keep source audio and sentence times unchanged.

Use registered `quote-card`, `variant: dialogue`, for the sentence and guiding
note; its compact surface omits the testimonial quote mark while keeping readable
type. Portraits, names, captions and guiding notes must not overlap. Check a
phone-sized preview and the longest sentence, not only the shortest title card.
Keep critical text clear of the intended platform's interface; record the
assumed margins without claiming universal platform safety.

Add quiet topic movement with the registered `topic-scene`:

| Source meaning | Scene / action | Motion |
| --- | --- | --- |
| Transport notice | `transit` / `notice` | Notice draws attention once |
| Platform changes | `transit` / `change` | Route marker moves from old to new stop |
| Confirming time or destination | `transit` / `confirm` | Small confirmation stroke; time stays correct |
| Walking to the stop | `transit` / `walk` | Route movement toward the stated stop |
| Daily schedule | `clock` | Gentle clock emphasis at the source time |
| Coffee / cooking / bedtime | `coffee`, `cooking`, `night` | Steam, slight stirring, or quiet evening motion |

Pass `from`, `to`, `timeLabel` only when the source has revealed their values.
Do not show a future platform number before its first mention, animate an
unchanged departure time as a changed one, or imply an unsupported event.
Bind each cue to source sentence/turn IDs, evidence text and local start/end
times. Carry already-revealed state correctly into a clipped Story.
If no existing scene matches, add an appropriate registered template instead
of looping unrelated decoration. Keep motion subordinate to speech and reading;
do not pulse, bounce or add sound effects on every word.

## Acceptance

Validate the Edit Spec, then inspect early/middle/late, the longest card,
both sides of speaker handoffs, and meaningful topic transitions. Check that
faces look inward and stay recognizable, silhouettes have no residual rectangle
or halo, the active name matches the heard speaker, and listener dimming remains
gentle. Verify the encoded file and source audio synchronization after rendering.
Record separate automatic checks and sampled visual review; do not upgrade either
to full human audition. Keep rendering local unless separately authorized to publish.
