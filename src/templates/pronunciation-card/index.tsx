import { useMemo } from "react";
import { z } from "zod/v3";
import { Img, interpolate, staticFile, useCurrentFrame } from "remotion";
import { surfaceStyle, useBrand, withAlpha } from "../../theme/themes";
import { useInOut } from "../../player/motion";
import { useRem } from "../../player/scale";
import type { TemplateDef } from "../types";

const resolveAsset = (src: string) =>
  /^(https?:|data:|blob:)/.test(src) ? src : staticFile(src.replace(/^\//, ""));

const schema = z.object({
  pattern: z.string().min(1),
  phonetic: z.string().min(1),
  word: z.string().min(1),
  wordPhonetic: z.string().min(1),
  focus: z.string().min(1),
  artwork: z.string().optional(),
  direction: z.enum(["ltr", "rtl"]).default("ltr"),
  language: z.string().min(2).max(16).default("und"),
  repetitionCount: z.literal(2).default(2),
  secondStartFraction: z.number().min(0.25).max(0.9).default(0.55),
});

const highlightedWord = (
  word: string,
  focus: string,
  locale: string,
  accent: string,
) => {
  const direct = word.indexOf(focus);
  const index =
    direct >= 0
      ? direct
      : word.toLocaleLowerCase(locale).indexOf(focus.toLocaleLowerCase(locale));
  if (index < 0) return word;
  return (
    <>
      {word.slice(0, index)}
      <span
        style={{
          color: accent,
          textDecoration: "underline",
          textDecorationThickness: "0.11em",
          textUnderlineOffset: "0.12em",
        }}
      >
        {word.slice(index, index + focus.length)}
      </span>
      {word.slice(index + focus.length)}
    </>
  );
};

const PronunciationCard = (raw: Record<string, unknown>) => {
  const p = useMemo(() => schema.parse(raw), [raw]);
  const brand = useBrand();
  const accent = brand.colors.accent ?? brand.colors.secondary ?? brand.colors.primary;
  const rem = useRem();
  const frame = useCurrentFrame();
  const { enter, exit, durationInFrames } = useInOut();
  const secondStartFrame = Math.round(durationInFrames * p.secondStartFraction);
  const activeRepeat = frame < secondStartFrame ? 0 : 1;
  const repeatWindow = activeRepeat === 0 ? secondStartFrame : durationInFrames - secondStartFrame;
  const repeatFrame = activeRepeat === 0 ? frame : frame - secondStartFrame;
  const patternSize = p.pattern.length > 14 ? 78 : p.pattern.length > 10 ? 104 : p.pattern.length > 6 ? 142 : 190;
  const wordSize = p.word.length > 12 ? 76 : p.word.length > 9 ? 92 : p.direction === "rtl" ? 112 : 126;
  const wordPhoneticSize = p.wordPhonetic.length > 16 ? 32 : p.wordPhonetic.length > 12 ? 36 : 42;
  const pulse = interpolate(
    repeatFrame,
    [0, Math.max(1, repeatWindow * 0.08), Math.max(2, repeatWindow * 0.22)],
    [0.72, 1.08, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <div
      dir={p.direction}
      style={{
        width: "92%",
        minHeight: rem(1160),
        padding: rem(58),
        borderRadius: rem(52),
        ...surfaceStyle(brand, rem),
        color: brand.colors.onSurface,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "space-between",
        gap: rem(34),
        opacity: enter * exit,
        transform: `translateY(${(1 - enter) * rem(48)}px) scale(${0.96 + enter * 0.04})`,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          fontFamily: brand.fonts.heading,
          fontSize: rem(patternSize),
          fontWeight: 800,
          lineHeight: 0.92,
          letterSpacing: "-0.045em",
          color: brand.colors.primary,
          textAlign: "center",
        }}
      >
        {p.pattern}
      </div>
      <div
        style={{
          fontFamily: brand.fonts.body,
          fontSize: rem(p.phonetic.length > 18 ? 34 : p.phonetic.length > 12 ? 40 : 48),
          color: brand.colors.muted,
          direction: "ltr",
          textAlign: "center",
        }}
      >
        {p.phonetic}
      </div>

      {p.artwork ? (
        <div
          style={{
            width: rem(510),
            height: rem(510),
            borderRadius: "50%",
            display: "grid",
            placeItems: "center",
            background: `radial-gradient(circle, ${withAlpha(brand.colors.primary, 0.2)} 0%, transparent 70%)`,
          }}
        >
          <Img
            src={resolveAsset(p.artwork)}
            style={{ width: "92%", height: "92%", objectFit: "contain" }}
          />
        </div>
      ) : (
        <div
          style={{
            width: rem(390),
            height: rem(390),
            borderRadius: "50%",
            border: `${rem(18)}px solid ${withAlpha(brand.colors.primary, 0.22)}`,
            boxShadow: `inset 0 0 0 ${rem(42)}px ${withAlpha(accent, 0.08)}`,
            display: "grid",
            placeItems: "center",
          }}
        >
          <div
            style={{
              width: rem(128),
              height: rem(128),
              borderRadius: "50%",
              background: accent,
              boxShadow: `0 0 ${rem(90)}px ${withAlpha(accent, 0.55)}`,
            }}
          />
        </div>
      )}

      <div style={{ textAlign: "center", maxWidth: "100%" }}>
        <div
          style={{
            fontFamily: brand.fonts.heading,
            fontSize: rem(wordSize),
            fontWeight: 720,
            lineHeight: 1.05,
            overflowWrap: "anywhere",
          }}
        >
          {highlightedWord(p.word, p.focus, p.language, accent)}
        </div>
        <div
          style={{
            marginTop: rem(18),
            fontFamily: brand.fonts.body,
            fontSize: rem(wordPhoneticSize),
            color: brand.colors.muted,
            direction: "ltr",
          }}
        >
          {p.wordPhonetic}
        </div>
      </div>

      <div style={{ display: "flex", gap: rem(22), direction: "ltr" }}>
        {[0, 1].map((index) => (
          <div
            key={index}
            style={{
              width: rem(92),
              height: rem(22),
              borderRadius: rem(99),
              background:
                index <= activeRepeat ? brand.colors.primary : withAlpha(brand.colors.muted, 0.22),
              transform: index === activeRepeat ? `scale(${pulse})` : undefined,
              boxShadow:
                index === activeRepeat
                  ? `0 0 ${rem(34)}px ${withAlpha(brand.colors.primary, 0.5)}`
                  : undefined,
            }}
          />
        ))}
      </div>
    </div>
  );
};

export const pronunciationCardDef: TemplateDef = {
  slug: "pronunciation-card",
  title: "Pronunciation Card",
  tier: "free",
  category: "Audio",
  description:
    "Target-language-only grapheme and word card with IPA, optional original artwork, and a two-repeat progress cue.",
  sourceContract: "overlay",
  regions: ["fullscreen", "center"],
  schema,
  demoProps: {
    pattern: "ie",
    phonetic: "/iː/",
    word: "Biene",
    wordPhonetic: "/ˈbiːnə/",
    focus: "ie",
    language: "de-DE",
    repetitionCount: 2,
    secondStartFraction: 0.56,
  },
  demoDurationSec: 5,
  demoTime: { appear: 0.55, hold: 4.45 },
  defaultMotion: { style: "float", amount: 0.05, frequency: 0.14 },
  component: PronunciationCard,
};
