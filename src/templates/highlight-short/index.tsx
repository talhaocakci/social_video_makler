import {useMemo} from "react";
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {z} from "zod/v3";
import type {TemplateDef} from "../types";
import {videoCanvasStyle,videoLayerStyle,videoLayoutSchema} from "../video-layout";

export const highlightShortSchema=z.object({
  excerpt:z.string().min(1),sourceLabel:z.string().min(1),targetLabel:z.string().min(1),guidingLabel:z.string().min(1),
  introLabel:z.string().min(1),listenLabel:z.string().min(1),repeatLabel:z.string().min(1),turnLabel:z.string().min(1),
  continueLabel:z.string().min(1),qrInstruction:z.string().min(1),reason:z.string().default(""),
  tags:z.array(z.string()).max(3).default([]),qrDomain:z.string().min(1),qrImage:z.string().min(1),
  excerptStart:z.number().nonnegative(),repeatStart:z.number().nonnegative(),endCardStart:z.number().nonnegative(),
  layout:videoLayoutSchema,
}).superRefine((value,ctx)=>{
  if(!(value.excerptStart<value.repeatStart&&value.repeatStart<value.endCardStart)){
    ctx.addIssue({code:z.ZodIssueCode.custom,path:["repeatStart"],message:"Highlight phases must be ordered: listen, repeat, QR."});
  }
});

const HighlightShort=(raw:Record<string,unknown>)=>{
  const p=useMemo(()=>highlightShortSchema.parse(raw),[raw]);
  const frame=useCurrentFrame();const {fps,durationInFrames}=useVideoConfig();const time=frame/fps;
  const end=time>=p.endCardStart;const intro=time<p.excerptStart;const repeat=time>=p.repeatStart&&!end;
  const phaseStart=intro?0:repeat?p.repeatStart:p.excerptStart;
  const appear=interpolate(time-phaseStart,[0,.38],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});
  const accent="#167C58",ink="#163D33",muted="#61766D",paper="#F7F3EA";
  const textSize=Math.max(43,Math.min(74,1800/Math.sqrt(p.excerpt.length+18)));
  const L=(name:any,fallback:any)=>videoLayerStyle(p.layout,name,fallback);
  return <AbsoluteFill style={videoCanvasStyle(p.layout,{background:paper,color:ink,fontFamily:"'Avenir Next',system-ui,sans-serif",overflow:"hidden"})}>
    <div style={{position:"absolute",inset:0}}>
      <div style={L("logo",{position:"absolute",left:58,top:64,width:600,height:70,fontWeight:820,fontSize:34})}>GetFluentFast<span style={{color:accent}}>●</span></div>
      {!end&&<Img src={staticFile(p.qrImage)} style={L("qr",{position:"absolute",right:58,top:58,width:126,height:126,background:"white",objectFit:"contain"})}/>}
      {!end&&<div style={L("meta",{position:"absolute",left:58,top:185,width:800,height:125,display:"flex",gap:13,alignItems:"center",color:muted,fontSize:22,textTransform:"uppercase",letterSpacing:2})}>
        <span style={{background:"#E0EBDC",border:"1px solid #BDD2BF",padding:"9px 16px",borderRadius:999,color:ink,fontWeight:750}}>{p.targetLabel}</span><span>{p.sourceLabel}</span>
      </div>}
      {!end&&intro&&<div style={L("content",{position:"absolute",left:80,top:390,width:920,height:880,display:"flex",alignItems:"center",justifyContent:"center",textAlign:"center",opacity:appear,transform:`translateY(${(1-appear)*26}px)`})}>
        <div><div style={{fontSize:p.layout?.elements.content.fontSize??70,fontWeight:780,lineHeight:p.layout?.elements.content.lineHeight??1.2}}>{p.introLabel}</div><div style={{fontSize:30,color:muted,marginTop:38}}>{p.guidingLabel}</div></div>
      </div>}
      {!end&&!intro&&<div style={L("content",{position:"absolute",left:60,top:330,width:960,height:1320,padding:"66px 55px",background:"#FFFFFFE0",border:"1px solid #CAD7C4",borderRadius:34,boxShadow:"0 28px 70px #10292018",opacity:appear,transform:`translateY(${(1-appear)*28}px)`,display:"flex",flexDirection:"column",justifyContent:"center"})}>
        <div style={{alignSelf:"flex-start",padding:"10px 20px",borderRadius:999,background:repeat?"#E7A84B":accent,color:repeat?ink:"white",fontWeight:800,fontSize:25,marginBottom:34}}>{repeat?p.turnLabel:p.listenLabel}</div>
        <div style={{fontSize:p.layout?.elements.content.fontSize??textSize,lineHeight:p.layout?.elements.content.lineHeight??1.38,fontWeight:610,letterSpacing:-.7}}>{p.excerpt}</div>
        {p.reason&&<div style={{fontSize:26,lineHeight:1.42,color:muted,marginTop:38,paddingTop:30,borderTop:"1px solid #DCE5D8"}}>{p.reason}</div>}
        {p.tags.length>0&&<div style={{display:"flex",gap:10,flexWrap:"wrap",marginTop:34}}>{p.tags.map(tag=><span key={tag} style={{padding:"8px 13px",borderRadius:999,background:"#EAF0E5",fontSize:20,color:muted}}>#{tag}</span>)}</div>}
      </div>}
      {!end&&<div style={L("footer",{position:"absolute",left:62,top:1740,width:956,height:80,display:"flex",justifyContent:"space-between",fontSize:22,color:muted})}><span>{repeat?p.repeatLabel:p.listenLabel}</span><span>{p.guidingLabel}</span></div>}
      {end&&<>
        <div style={L("endText",{position:"absolute",left:72,top:220,width:936,height:620,display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",textAlign:"center"})}>
          <div style={{fontSize:66,fontWeight:800,lineHeight:1.15}}>{p.continueLabel}</div><div style={{fontSize:29,color:muted,marginTop:28}}>{p.qrInstruction}</div><div style={{fontSize:26,color:muted,marginTop:30}}>{p.qrDomain}</div>
        </div>
        <Img src={staticFile(p.qrImage)} style={L("endQr",{position:"absolute",left:195,top:930,width:690,height:690,background:"white",objectFit:"contain"})}/>
      </>}
      <div style={L("progress",{position:"absolute",left:0,bottom:0,height:9,width:"100%",background:"#D8E2D9",overflow:"hidden"})}><div style={{width:`${100*frame/durationInFrames}%`,height:"100%",background:accent}}/></div>
    </div>
  </AbsoluteFill>;
};

export const highlightShortDef:TemplateDef={
  slug:"highlight-short",title:"Highlight Short",tier:"free",category:"Text",sourceContract:"overlay",
  description:"Vertical listen-and-repeat clip generated from one exact saved GetFluentFast Highlight.",
  regions:["fullscreen"],schema:highlightShortSchema,demoDurationSec:12,
  demoProps:{excerpt:"I need a little more time to think about it.",sourceLabel:"Reading",targetLabel:"English",guidingLabel:"English",introLabel:"Listen to this useful line.",listenLabel:"Listen",repeatLabel:"Now say it again.",turnLabel:"Your turn",continueLabel:"Continue in Get Fluent Fast",qrInstruction:"Scan with your phone camera",reason:"A useful way to ask for thinking time.",tags:["daily-life"],qrDomain:"getfluentfast.app",qrImage:"reading-teacher-hotel/reading-qr.png",excerptStart:2.2,repeatStart:6,endCardStart:9},
  component:HighlightShort,
};
