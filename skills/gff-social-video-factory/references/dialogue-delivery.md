# Dialogue delivery and matching energy

Treat the two voices as one conversation. Select a shared performance direction
before casting: an attentive, naturally lively adult conversation, light warmth,
responsive replies, clear forward movement and meaningful word stress. Keep
energy appropriate to the actual situation. Transportation clarification or
planning a meal does not require celebration, panic or theatrical acting.

Both people should sound equally present and willing to engage. Match perceived
engagement, pace, response rhythm, emphatic range and emotional intensity while
retaining distinct timbres. Never routinely cast one partner as exuberant and
the other as sleepy, weary, indifferent, resigned or forced to speak. A character
may be calmer only when the source or user explicitly calls for that difference.
Do not equate a lower voice register with lower energy.

## Adult timbre stays adult

Keep perceived vocal age separate from engagement. Expressiveness must preserve
the adult voice's body, vowel resonance, articulation and comfortable register.
Use rhythmic emphasis, responsive timing and conversational stress for energy;
do not automatically raise the whole pitch, brighten the formants or add a tiny,
chirpy, childlike delivery. This applies to every speaker. An adult voice can
naturally be bright or light; a low pitch or a husky prompt alone is not proof
of maturity, and every woman need not sound unusually deep or artificially aged.

When the user hears a childlike voice, repair the affected reference and its
performance. Do not try to solve perceived age by only lowering the waveform's
pitch or slowing it down. Keep unaffected partners' voices stable when possible.
Provide a short same-text comparison and adjacent replies, including the most
expressive phrase, and label new candidates truthfully until perceptual feedback
exists. Machine source, pitch or embedding checks must never turn rejected
childlike voices into an accepted adult casting.

## Generation and reuse

- Reuse existing audio only if the pair's performance meets this direction.
  A correct transcript and good pronunciation alone do not establish it.
- Keep one stable voice reference per side across all turns, related Stories,
  guiding-language variants and the long compilation.
- Inspect whether the chosen engine actually supports a delivery instruction.
  The installed Qwen3-TTS Base ICL path ignores `instruct`; saving a profile name
  or passing the same instruction to both voices does not prove a style change.
- For local Qwen Base cloning, carry the shared performance through compatible,
  checksum-locked references. If new references are needed, create one original
  synthetic reference per side with the same conversational direction and
  ordinary reference text, then reuse each reference for every assigned turn.
  Record new voice IDs when identities change. Do not relabel a redesigned
  voice as the previously approved voice. Alternatively use a supported stable
  CustomVoice model when already available and appropriate.
- Do not mix a Happy or highly energetic preset with a Calm/flat preset merely
  because they are the default male and female choices. Evaluate the pair.
- Preserve authored dialogue verbatim. Recompute alignment and every dependent
  visual/source timestamp when new audio changes duration; do not stretch speech
  into old timing or attach new audio to stale sentence boundaries.

## Pair checks and repair

Review at least three adjacent exchanges per pair: opening, middle and ending,
including a short response and a longer reply. Compare the two voices at the
same playback level. Both should respond naturally and carry the conversation
without one sounding forced or emotionally absent. Check sentence endings as
well as beginnings. If the pair fails, regenerate the affected delivery or
choose a compatible reference pair, then check the exchanges again before bulk
rendering.

Match comfortable listening levels separately. Measure clipping, silence,
source coverage, language, speaker consistency and encoded synchronization.
Loudness, pitch range, speech rate and ASR are diagnostic evidence, not proof of
perceived enthusiasm, naturalness or an energy match. Record human audition only
when it happened; otherwise provide a playable local comparison and state the
review boundary accurately. Never mark a user's rejected pair as accepted on
machine metrics alone. Keep rejected takes for traceable comparison.

Keep all work local unless publication is separately authorized.
