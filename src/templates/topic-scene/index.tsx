import { useMemo } from "react";
import { z } from "zod/v3";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { useBrand } from "../../theme/themes";
import type { TemplateDef } from "../types";

const schema = z.object({
  scene: z.enum(["transit", "clock", "coffee", "cooking", "night"]).default("transit"),
  action: z.enum(["notice", "change", "confirm", "walk", "hold"]).default("hold"),
  from: z.string().default(""),
  to: z.string().default(""),
  timeLabel: z.string().default(""),
});

/** Small semantic animation beside dialogue. Values come from the source, never a demo schedule. */
const TopicScene = (raw: Record<string, unknown>) => {
  const p = useMemo(() => schema.parse(raw), [raw]);
  const brand = useBrand();
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;
  const t = Math.max(0, Math.min(1, sec / 1.1));
  const ease = t * t * (3 - 2 * t);
  const color = brand.colors.primary;
  const muted = brand.colors.muted;
  const text = brand.colors.onSurface;
  const travel = p.action === "change" || p.action === "walk" ? ease : p.to ? 1 : 0;
  const tick = Math.min(1, sec / .65);
  const clock = (x: number, label: string) => {
    const value = label.match(/(\d{1,2}):(\d{2})/);
    const hour = value ? Number(value[1]) : 12;
    const minute = value ? Number(value[2]) : 0;
    return <g transform={`translate(${x}, 84)`}>
      <circle r="53" fill="rgba(255,255,255,.035)" stroke={muted} strokeWidth="2" opacity=".6" />
      {[0,1,2,3].map(i => <line key={i} x1="0" y1="-45" x2="0" y2="-40" stroke={muted}
        strokeWidth="2" transform={`rotate(${i * 90})`} />)}
      {value ? <>
        <line x1="0" y1="5" x2="0" y2="-26" stroke={text} strokeWidth="5" strokeLinecap="round"
          transform={`rotate(${hour * 30 + minute / 2})`} />
        <line x1="0" y1="6" x2="0" y2="-38" stroke={color} strokeWidth="3" strokeLinecap="round"
          transform={`rotate(${minute * 6})`} />
        <circle r="4" fill={color} />
      </> : <circle r="4" fill={muted} />}
      {label ? <text y="89" textAnchor="middle" fill={text} fontSize="27" fontWeight="650">{label}</text> : null}
    </g>;
  };
  return <svg viewBox="0 0 780 190" style={{ width: "100%", height: "100%", overflow: "visible",
    fontFamily: brand.fonts.body }} role="img" aria-label={`Source-bound ${p.scene} illustration`}>
    {p.scene === "transit" ? <>
      <path d="M 80 118 H 448" stroke={muted} strokeWidth="3" opacity=".3" strokeDasharray="7 10" />
      <path d="M 80 118 H 448" stroke={color} strokeWidth="4" pathLength="1"
        strokeDasharray="1" strokeDashoffset={1 - travel} opacity=".7" />
      <circle cx="80" cy="118" r="9" fill={color} opacity={p.to ? .4 : 1} />
      <circle cx="448" cy="118" r="9" fill={p.to ? color : muted} opacity={p.to ? 1 : .25} />
      {p.from ? <text x="80" y="170" textAnchor="middle" fill={muted} fontSize="34">{p.from}</text> : null}
      {p.to ? <text x="448" y="170" textAnchor="middle" fill={text} fontSize="34" fontWeight="700">{p.to}</text> : null}
      <g transform={`translate(${80 + travel * 368 - 39}, 31)`}>
        <rect width="78" height="62" rx="13" fill={color} />
        <rect x="9" y="9" width="60" height="27" rx="5" fill={brand.colors.background} />
        <line x1="39" y1="9" x2="39" y2="36" stroke={color} strokeWidth="3" />
        <circle cx="17" cy="49" r="4" fill={text} /><circle cx="61" cy="49" r="4" fill={text} />
        <rect x="11" y="58" width="10" height="12" rx="4" fill={muted} />
        <rect x="57" y="58" width="10" height="12" rx="4" fill={muted} />
      </g>
      {p.action === "notice" ? <g opacity={.5 + .5 * Math.sin(Math.min(sec, 1) * Math.PI)}>
        <path d="M 360 28 L 385 72 H 335 Z" fill={brand.colors.accent} /><text x="360" y="62" textAnchor="middle" fill="#17242b" fontSize="28">!</text>
      </g> : null}
      {p.action === "confirm" ? <path d="M 365 65 l 14 14 29 -32" fill="none" stroke={color}
        strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" pathLength="1"
        strokeDasharray="1" strokeDashoffset={1 - tick} /> : null}
      {clock(650, p.timeLabel)}
    </> : p.scene === "clock" ? <>
      {clock(390, p.timeLabel)}
      <circle cx="390" cy="84" r={60 + ease * 9} fill="none" stroke={color} strokeWidth="2" opacity={(1 - ease) * .6} />
    </> : p.scene === "coffee" ? <>
      <g transform="translate(285, 68)">
        <path d="M 0 8 H 108 V 52 Q 108 78 78 78 H 30 Q 0 78 0 52 Z" fill="rgba(255,255,255,.08)" stroke={muted} strokeWidth="3" />
        <path d="M 110 18 C 157 12 151 66 109 60" fill="none" stroke={muted} strokeWidth="6" />
        <ellipse cx="54" cy="9" rx="52" ry="9" fill={brand.colors.accent} opacity=".5" />
        <path d="M -12 87 H 131" stroke={muted} strokeWidth="3" strokeLinecap="round" />
        {[0,1,2].map(i => {
          const rise = (sec * .32 + i / 3) % 1;
          return <path key={i} d={`M ${22+i*29} -4 q -12 -13 0 -24 q 12 -11 0 -23`}
            transform={`translate(0,${-rise * 26})`} fill="none" stroke={text} strokeWidth="3"
            strokeLinecap="round" opacity={Math.sin(rise * Math.PI) * .55} />;
        })}
      </g>
      {p.timeLabel ? clock(570, p.timeLabel) : null}
    </> : p.scene === "cooking" ? <g transform="translate(295, 72)">
      <path d="M 0 35 Q 10 91 112 91 Q 176 91 190 35 Z" fill="rgba(255,255,255,.06)" stroke={muted} strokeWidth="3" />
      <path d="M 190 44 H 256" stroke={muted} strokeWidth="10" strokeLinecap="round" />
      <ellipse cx="95" cy="35" rx="94" ry="18" fill={color} opacity=".25" />
      <path d="M 50 20 Q 80 38 120 22 L 162 -47" fill="none" stroke={brand.colors.accent} strokeWidth="8" strokeLinecap="round"
        transform={`rotate(${Math.sin(sec * 1.7) * 6}, 95,35)`} />
      {[0,1,2].map(i => <path key={i} d={`M ${35+i*48} 0 q -10 -14 0 -30`}
        fill="none" stroke={text} strokeWidth="3" opacity={.2 + .2 * Math.sin(sec * 2 + i)}
        transform={`translate(0,${-4 - 5 * Math.sin(sec * 1.5+i)})`} />)}
    </g> : <>
      <path d="M 362 24 A 64 64 0 1 0 432 115 A 58 58 0 0 1 362 24" fill={brand.colors.accent} opacity=".85"
        transform={`translate(0,${Math.sin(sec * .8) * 3})`} />
      {p.timeLabel ? clock(570, p.timeLabel) : null}
    </>}
  </svg>;
};

export const topicSceneDef: TemplateDef = {
  slug: "topic-scene", title: "Dialogue Topic Scene", tier: "free", category: "Social",
  description: "Quiet source-bound transit, clock, coffee, cooking or evening motion beside a dialogue. Supply only values already revealed by its source sentence.",
  sourceContract: "overlay", regions: ["center", "lower-third"], schema,
  demoProps: { scene: "coffee" }, demoDurationSec: 5, component: TopicScene,
};
