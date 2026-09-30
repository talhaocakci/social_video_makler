import type {CSSProperties} from "react";
import {z} from "zod/v3";

const hex=z.string().regex(/^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$/);
const element=z.object({
  x:z.number().min(0).max(100),y:z.number().min(0).max(100),
  w:z.number().positive().max(100),h:z.number().positive().max(100),
  fontSize:z.number().min(8).max(160).optional(),lineHeight:z.number().min(.8).max(2.5).optional(),
  padding:z.number().min(0).max(160).optional(),borderRadius:z.number().min(0).max(120).optional(),
  borderWidth:z.number().min(0).max(12).optional(),color:hex.optional(),
  background:hex.optional(),borderColor:hex.optional(),visible:z.boolean(),
  align:z.enum(["left","center","right"]).optional(),
});
export const videoLayoutSchema=z.object({
  version:z.literal(1),
  canvas:z.object({
    format:z.enum(["horizontal","vertical"]),width:z.number().int().positive(),height:z.number().int().positive(),
    background:hex,background2:hex,gradientAngle:z.number().min(0).max(360),
    fontFamily:z.enum(["Avenir Next","Inter","Georgia","Helvetica Neue","Arial"]),
  }),
  elements:z.object({
    logo:element,meta:element,media:element,content:element,teaching:element,
    qr:element,footer:element,endText:element,endQr:element,progress:element,
  }),
}).nullish();

export type VideoLayout=z.infer<typeof videoLayoutSchema>;

export const videoCanvasStyle=(layout:VideoLayout,fallback:CSSProperties):CSSProperties=>{
  if(!layout)return fallback;
  return {...fallback,backgroundColor:layout.canvas.background,
    backgroundImage:`linear-gradient(${layout.canvas.gradientAngle}deg,${layout.canvas.background},${layout.canvas.background2})`,
    fontFamily:`'${layout.canvas.fontFamily}',system-ui,sans-serif`};
};

export const videoLayerStyle=(layout:VideoLayout,name:keyof NonNullable<VideoLayout>["elements"],fallback:CSSProperties):CSSProperties=>{
  if(!layout)return fallback;
  const item=layout.elements[name];
  return {...fallback,position:"absolute",left:`${item.x}%`,top:`${item.y}%`,
    width:`${item.w}%`,height:`${item.h}%`,right:undefined,bottom:undefined,
    display:item.visible?(fallback.display??"block"):"none",boxSizing:"border-box",
    fontSize:item.fontSize??fallback.fontSize,lineHeight:item.lineHeight??fallback.lineHeight,
    padding:item.padding??fallback.padding,borderRadius:item.borderRadius??fallback.borderRadius,
    borderWidth:item.borderWidth??fallback.borderWidth,borderStyle:item.borderWidth?"solid":fallback.borderStyle,
    color:item.color??fallback.color,background:item.background??fallback.background,
    borderColor:item.borderColor??fallback.borderColor,textAlign:item.align??fallback.textAlign};
};
