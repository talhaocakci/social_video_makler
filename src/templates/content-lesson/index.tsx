import {useMemo} from "react";
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {z} from "zod/v3";
import type {TemplateDef} from "../types";
import {videoCanvasStyle,videoLayerStyle,videoLayoutSchema} from "../video-layout";

const segmentSchema=z.object({
  start:z.number().nonnegative(),duration:z.number().positive(),text:z.string().min(1),
  speaker:z.string().default(""),index:z.number().int().positive(),total:z.number().int().positive(),
});

export const contentLessonSchema=z.object({
  title:z.string().min(1),kind:z.enum(["reading","guided_communication"]),
  targetLabel:z.string().min(1),guidingLabel:z.string().min(1),
  introLabel:z.string().min(1),listenLabel:z.string().min(1),
  continueLabel:z.string().min(1),qrInstruction:z.string().min(1),
  qrDomain:z.string().min(1),qrImage:z.string().min(1),qrScope:z.enum(["content","app_home"]),
  endCardStart:z.number().nonnegative(),segments:z.array(segmentSchema).min(1),layout:videoLayoutSchema,
});

const ContentLesson=(raw:Record<string,unknown>)=>{
  const p=useMemo(()=>contentLessonSchema.parse(raw),[raw]);
  const frame=useCurrentFrame();const {fps,width,height,durationInFrames}=useVideoConfig();
  const time=frame/fps;const horizontal=width/height>1.3;
  const end=time>=p.endCardStart;
  const segment=p.segments.find(row=>time>=row.start&&time<row.start+row.duration)??(time<p.segments[0].start?p.segments[0]:p.segments[p.segments.length-1]);
  const local=Math.max(0,time-segment.start);
  const appear=interpolate(local,[0,.42],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});
  const accent="#167C58",ink="#163D33",muted="#61766D",paper="#F7F3EA";
  const scale=horizontal?width/1920:width/1080;
  const baseW=horizontal?1920:1080,baseH=horizontal?1080:1920;
  const textSize=Math.max(horizontal?38:44,Math.min(horizontal?64:62,(horizontal?2200:1200)/Math.sqrt(segment.text.length+20)));
  const L=(name:any,fallback:any)=>videoLayerStyle(p.layout,name,fallback);
  return <AbsoluteFill style={videoCanvasStyle(p.layout,{background:paper,color:ink,fontFamily:"'Avenir Next',system-ui,sans-serif",overflow:"hidden"})}>
    <div style={{position:"absolute",width:baseW,height:baseH,transform:`scale(${scale})`,transformOrigin:"top left"}}>
      <div style={L("logo",{position:"absolute",left:horizontal?72:58,top:horizontal?45:58,fontWeight:800,fontSize:horizontal?30:34})}>GetFluentFast<span style={{color:accent}}>●</span></div>
      {!end&&<Img src={staticFile(p.qrImage)} style={L("qr",{position:"absolute",right:horizontal?72:58,top:horizontal?45:58,width:horizontal?142:156,height:horizontal?142:156,background:"white",objectFit:"contain"})}/>}
      {!end&&<div style={L("meta",{position:"absolute",left:horizontal?80:62,top:horizontal?150:225,right:horizontal?80:62})}>
        <div style={{display:"flex",gap:15,alignItems:"center",color:muted,fontSize:horizontal?21:24,textTransform:"uppercase",letterSpacing:2}}>
          <span style={{background:"#E0EBDC",border:"1px solid #BDD2BF",padding:"8px 16px",borderRadius:999,color:ink,fontWeight:700}}>{p.targetLabel}</span>
          <span>{p.kind==="reading"?p.introLabel:p.listenLabel}</span>
        </div>
        <div style={{fontSize:horizontal?30:35,color:muted,marginTop:22}}>{p.title}</div>
      </div>}
      {!end&&<div style={L("content",{position:"absolute",left:horizontal?150:70,right:horizontal?150:70,top:horizontal?300:430,bottom:horizontal?190:330,padding:horizontal?"55px 70px":"64px 54px",background:"#FFFFFFDB",border:"1px solid #CAD7C4",borderRadius:28,boxShadow:"0 24px 60px #10292016",opacity:appear,transform:`translateY(${(1-appear)*25}px)`,display:"flex",flexDirection:"column",justifyContent:"center"})}>
        {segment.speaker&&<div style={{alignSelf:"flex-start",padding:"9px 18px",borderRadius:999,background:accent,color:"white",fontWeight:750,fontSize:horizontal?22:26,marginBottom:26}}>{segment.speaker}</div>}
        <div style={{fontSize:p.layout?.elements.content.fontSize??textSize,lineHeight:p.layout?.elements.content.lineHeight??1.4,fontWeight:520,letterSpacing:-.6}}>{segment.text}</div>
      </div>}
      {!end&&<div style={L("footer",{position:"absolute",left:horizontal?80:62,right:horizontal?80:62,bottom:horizontal?55:95,display:"flex",justifyContent:"space-between",alignItems:"center",fontSize:horizontal?20:24,color:muted})}>
        <span>{p.listenLabel} · {p.guidingLabel}</span><span>{String(segment.index).padStart(2,"0")} / {String(segment.total).padStart(2,"0")}</span>
      </div>}
      {end&&<>
        <div style={L("endText",{position:"absolute",left:horizontal?130:90,top:horizontal?230:180,width:horizontal?930:900,height:horizontal?600:650,display:"flex",flexDirection:"column",justifyContent:"center"})}>
          <div style={{fontSize:horizontal?64:68,fontWeight:780,lineHeight:1.15}}>{p.continueLabel}</div>
          <div style={{fontSize:horizontal?34:38,color:muted,marginTop:28}}>{p.title}</div>
          <div style={{fontSize:horizontal?28:32,marginTop:42}}>{p.qrInstruction}</div>
          <div style={{fontSize:horizontal?23:27,color:muted,marginTop:18}}>{p.qrDomain}</div>
        </div>
        <Img src={staticFile(p.qrImage)} style={L("endQr",{position:"absolute",left:1210,top:240,width:590,height:590,background:"white",objectFit:"contain"})}/>
      </>}
      <div style={L("progress",{position:"absolute",left:0,bottom:0,height:7,width:"100%",background:"#D8E2D9",overflow:"hidden"})}><div style={{width:`${100*frame/durationInFrames}%`,height:"100%",background:accent}}/></div>
    </div>
  </AbsoluteFill>;
};

export const contentLessonDef:TemplateDef={
  slug:"content-lesson",title:"Content Lesson",tier:"free",category:"Text",sourceContract:"overlay",
  description:"Complete Reading or Guided Communication with source-bound synthetic narration and a QR continuation card.",
  regions:["fullscreen"],schema:contentLessonSchema,demoDurationSec:8,
  demoProps:{title:"Everyday language",kind:"reading",targetLabel:"English",guidingLabel:"English",introLabel:"Full reading",listenLabel:"Listen",continueLabel:"Continue in the app",qrInstruction:"Scan with your phone camera",qrDomain:"getfluentfast.app",qrImage:"reading-teacher-hotel/reading-qr.png",qrScope:"content",endCardStart:6,segments:[{start:0,duration:6,text:"A complete source-bound lesson.",speaker:"",index:1,total:1}]},
  component:ContentLesson,
};
