import {LongReadingLesson} from "./LongReadingLesson";
import { useMemo } from "react";
import { z } from "zod/v3";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { TemplateDef } from "../types";
import {videoLayoutSchema} from "../video-layout";

const wordSchema=z.object({start:z.number().int().nonnegative(),end:z.number().int().positive(),t0:z.number().nonnegative(),t1:z.number().nonnegative()});
const sceneSchema=z.object({
  pass_label:z.string().default(""),pace:z.string().default(""),
  kind:z.enum(["reading","teacher","pause"]), sentence:z.number().int().nonnegative(),
  start:z.number().nonnegative(), duration:z.number().positive(), text:z.string(),
  words:z.array(wordSchema).default([]), image:z.string(), focus:z.string().default(""),
  title:z.string().default(""),body:z.string().default(""),note:z.string().default(""),
  teaching_notes:z.array(z.object({kind:z.string(),term:z.string(),meaning:z.string(),explanation:z.string(),point_id:z.string(),form:z.string()})).default([]),
  diagram:z.string().default(""), chapter:z.string().default(""),
  lexical_pairs:z.array(z.object({term:z.string(),meaning:z.string(),source_sentence:z.string()})).optional(),
});
export const readingCoachSchema=z.object({title:z.string(),variantTitle:z.string(),layout:videoLayoutSchema,
  presentation:z.object({showLevel:z.boolean().default(true),showChapter:z.boolean().default(true),showPassLabel:z.boolean().default(true)}).default({}),
  promotions:z.array(z.object({start:z.number().nonnegative(),duration:z.number().positive(),mode:z.enum(["spoken","silent"]),headline:z.string(),instruction:z.string(),qrImage:z.string(),screens:z.array(z.object({src:z.string(),caption:z.string(),tap:z.object({x:z.number().min(0).max(1),y:z.number().min(0).max(1)}).optional()})).min(1)})).default([]),
  ui:z.record(z.string()).default({}),
  treatment:z.enum(["paper","cinema","workshop"]),scenes:z.array(sceneSchema).min(1),
  readingLink:z.object({
    url:z.string().regex(/^https:\/\/getfluentfast\.app\/reading\/[A-Za-z0-9][A-Za-z0-9_-]{0,159}\/$/),
    qrImage:z.string().min(1), endCardStart:z.number().nonnegative(),
    label:z.string().min(1), instruction:z.string().min(1),
  }).optional(),
  lessonUI:z.object({targetLabel:z.string(),guidingLabel:z.string(),cefr:z.string(),sentenceCount:z.number().int().positive()}).optional(),
  levels:z.array(z.number().min(0).max(1)).default([]),
});
type Scene=z.infer<typeof sceneSchema>;
const ease=(x:number)=>interpolate(x,[0,.32],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});

/** Sentence text is preserved byte-for-byte. Spoken word emphasis is driven
 * exclusively by source-bound forced alignment; teaching underlines are
 * editorial annotations on the selected exact source span, not fake captions. */
export function sentenceFragments(scene:Scene,time:number) {
  const focusAt=scene.focus?scene.text.indexOf(scene.focus):-1;
  const boundaries=new Set([0,scene.text.length]);
  for(const w of scene.words){boundaries.add(w.start);boundaries.add(w.end);}
  if(focusAt>=0){boundaries.add(focusAt);boundaries.add(focusAt+scene.focus.length);}
  const points=[...boundaries].sort((a,b)=>a-b);
  return points.slice(0,-1).map((start,i)=>{
    const end=points[i+1];const word=scene.words.find(w=>w.start<=start&&w.end>=end);
    return {text:scene.text.slice(start,end),start,
      current:!!word&&time>=word.t0&&time<word.t1,
      focus:focusAt>=0&&start>=focusAt&&end<=focusAt+scene.focus.length};
  });
}

const TeachingDiagram=({type,dark}:{type:string;dark:boolean})=>{
  const muted=dark?'#AFC8CB':'#54746A';
  const base={padding:'14px 18px',borderRadius:14,background:dark?'#213E40':'#E7EFE6',fontSize:26,lineHeight:1.4};
  if(type==='question')return <div style={{display:'grid',gap:10,marginTop:20}}>
    <div style={{fontSize:20,color:muted,letterSpacing:2}}>DOĞRUDAN SORU</div>
    <div style={base}><strong>Is</strong> a room available?</div>
    <div style={{fontSize:20,color:muted,letterSpacing:2,marginTop:4}}>CÜMLE İÇİNDE</div>
    <div style={base}>whether <strong>a room is</strong> available</div>
  </div>;
  if(type==='embedded')return <div style={{display:'flex',gap:10,flexWrap:'wrap',marginTop:25}}>
    {['if','she','can','cancel'].map((s,i)=><div key={s} style={{...base,background:i===1?'#CDEED8':i===2?'#F7DDA8':base.background,color:i===1||i===2?'#173D31':undefined,fontSize:29}}>{s}</div>)}
  </div>;
  if(type==='confirmation')return <div style={{display:'flex',gap:12,marginTop:25}}>
    {['Tarihler','Oda türü','Toplam fiyat'].map(s=><div key={s} style={{...base,fontSize:22,flex:1,padding:'15px 12px',textAlign:'center'}}><div style={{color:muted,marginBottom:8}}>✓</div>{s}</div>)}
  </div>;
  return null;
};

const ReadingCoach=(raw:Record<string,unknown>)=>{
  const p=useMemo(()=>readingCoachSchema.parse(raw),[raw]);
  const frame=useCurrentFrame();const {fps,width,height,durationInFrames}=useVideoConfig();
  const time=frame/fps;
  if(p.lessonUI)return <LongReadingLesson p={p} time={time} width={width} height={height}/>;
  const endCard=!!p.readingLink&&time>=p.readingLink.endCardStart;
  const scene=p.scenes.find(s=>time>=s.start&&time<s.start+s.duration)??p.scenes[p.scenes.length-1];
  const local=time-scene.start;const entry=ease(local);
  const dark=p.treatment==='cinema',workshop=p.treatment==='workshop';
  const ink=dark?'#F4F1E8':'#163D33';const muted=dark?'#B7C8C7':'#63776E';
  const accent=dark?'#F7CC85':'#167C58';const bg=workshop?'#EEF3E9':'#F7F3EA';
  const teaching=scene.kind!=='reading';
  const sentenceNumber=String(scene.sentence+1).padStart(2,'0');
  const pieces=sentenceFragments(scene,local);
  const imageSrc=staticFile(scene.image);
  const backgroundSrc=scene.sentence>=3?staticFile('reading-teacher-hotel/sarah.png'):imageSrc;
  const panelX=dark?1130:workshop?1175:860;
  const panelY=dark?235:workshop?225:550;
  const panelW=dark?710:workshop?665:980;
  const pictureX=workshop?1200:70;const pictureY=workshop?215:190;
  const pictureW=workshop?620:740;const pictureH=workshop?360:475;
  const sentenceX=dark?80:workshop?80:860;
  const sentenceY=dark?teaching?270:300:workshop?250:240;
  const sentenceW=dark?970:workshop?1000:975;
  const sceneLabels=['Bir iş seyahati','Müsaitliği sor','Bilgileri kontrol et','İptal koşulunu öğren','Onayı sakla'];
  const label=scene.kind==='reading'?'DİNLE · EN':scene.kind==='pause'?'SIRA SENDE':'BİRLİKTE BAKALIM · TR';
  const size=dark?60:workshop?62:51;
  return <AbsoluteFill style={{background:dark?'#112B2C':bg,color:ink,fontFamily:"'Avenir Next', system-ui, sans-serif",overflow:'hidden'}}>
    <div style={{width:1920,height:1080,position:'absolute',transform:`scale(${width/1920},${height/1080})`,transformOrigin:'top left'}}>
      {dark&&<><Img src={backgroundSrc} style={{position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover',opacity:.45}}/><div style={{position:'absolute',inset:0,background:'linear-gradient(90deg,rgba(8,30,31,.97) 0%,rgba(8,30,31,.86) 49%,rgba(8,30,31,.28) 100%)'}}/></>}
      {dark&&!teaching&&scene.sentence>=3&&<Img src={imageSrc} style={{position:'absolute',left:1130,top:265,width:710,height:456,borderRadius:24}}/>}
      {workshop&&teaching&&<Img src={imageSrc} style={{position:'absolute',left:1190,top:734,width:330,height:210,objectFit:'cover',borderRadius:16}}/>}
      <div style={{position:'absolute',left:70,top:49,right:75,display:'flex',alignItems:'center',justifyContent:'space-between'}}>
        <div style={{fontWeight:800,fontSize:29,letterSpacing:-1}}>GetFluentFast<span style={{color:accent}}>●</span></div>
        <div style={{display:p.readingLink?'none':'flex',alignItems:'center',gap:23,fontSize:22}}><span style={{color:muted}}>ENGLISH READING</span><span style={{background:dark?'#365346':'#E0EBDC',border:`1px solid ${dark?'#62856C':'#BDD2BF'}`,padding:'8px 17px',borderRadius:12,fontWeight:700}}>B1</span></div>
      </div>
      <div style={{position:'absolute',left:70,right:75,top:116,height:1,background:dark?'#FFFFFF25':'#173D3320'}}/>
      <div style={{position:'absolute',left:72,top:141,fontSize:22,color:muted,letterSpacing:1.5}}>{p.title.toUpperCase()}</div>
      {!dark&&!(workshop&&teaching)&&<div style={{position:'absolute',left:pictureX,top:pictureY,width:pictureW,height:pictureH,borderRadius:24,overflow:'hidden',boxShadow:'0 20px 45px #10292016'}}>
        <Img src={imageSrc} style={{width:'100%',height:'100%',objectFit:'cover'}}/>
        {scene.sentence<3&&<div style={{position:'absolute',bottom:0,left:0,right:0,padding:'36px 25px 21px',background:'linear-gradient(transparent,#122D2DCF)',color:'#FFF6E7',fontSize:21}}>{scene.sentence===2?'Otel resepsiyonu · Telefonla rezervasyon':'Sarah · Telefonla rezervasyon'}</div>}
      </div>}
      {!dark&&!workshop&&<div style={{position:'absolute',left:76,top:716,width:720}}>
        <div style={{fontSize:21,letterSpacing:3,color:muted,marginBottom:20}}>HİKÂYEDEKİ ADIM</div>
        <div style={{fontSize:40,fontWeight:600,lineHeight:1.25}}>{sceneLabels[scene.sentence]}</div>
        <div style={{display:'flex',gap:12,marginTop:32}}>{sceneLabels.map((_,i)=><div key={i} style={{height:5,width:110,borderRadius:5,background:i<=scene.sentence?accent:'#CFD8CC'}}/>)}</div>
      </div>}
      <div style={{position:'absolute',left:sentenceX,top:sentenceY,width:sentenceW}}>
        <div style={{display:'flex',alignItems:'center',gap:14,marginBottom:28,fontSize:20,fontWeight:650,letterSpacing:2.5,color:accent}}>
          <span style={{width:9,height:9,background:accent,borderRadius:'50%'}}/>{label}<span style={{color:muted,marginLeft:10}}> {sentenceNumber} / 05</span>
        </div>
        <div data-reading-sentence style={{fontSize:size,fontWeight:500,lineHeight:1.42,letterSpacing:-1.4}}>
          {pieces.map(part=><span key={part.start} style={{background:part.current?(dark?'#38574B':'#D7EAD8'):undefined,color:part.focus?accent:undefined,textDecoration:part.focus?'underline':undefined,textDecorationColor:dark?'#F7CC85':'#D98547',textDecorationThickness:5,textUnderlineOffset:10}}>{part.text}</span>)}
        </div>
        {!teaching&&<div style={{marginTop:32,fontSize:22,color:muted}}>{p.treatment==='cinema'?'Önce anlamı takip et. Ayrıntılara birazdan döneceğiz.':'Cümleyi dinle ve takip et.'}</div>}
      </div>
      {teaching&&<div data-teacher-panel style={{position:'absolute',left:panelX,top:panelY,width:panelW,boxSizing:'border-box',padding:dark||workshop?'33px 35px':'26px 30px',borderRadius:23,background:dark?'#132F30F0':workshop?'#FFFFFF':'#FFFFFFBF',border:`1px solid ${dark?'#638F7755':'#CAD7C4'}`,boxShadow:'0 18px 45px #09271E10',opacity:entry,transform:`translateX(${(1-entry)*28}px)`}}>
        <div style={{fontSize:18,letterSpacing:2.8,color:muted,marginBottom:14}}>{scene.kind==='pause'?'DÜŞÜNME ZAMANI':'ÖĞRETMEN NOTU'}</div>
        <div style={{fontSize:scene.title.length>38?34:40,fontWeight:750,letterSpacing:-.8,lineHeight:1.2,color:accent}}>{scene.title}</div>
        <div style={{fontSize:dark||workshop?30:29,lineHeight:1.43,marginTop:17,whiteSpace:'pre-line'}}>{scene.body}</div>
        <TeachingDiagram type={scene.diagram} dark={dark}/>
        {scene.note&&<div style={{fontSize:22,lineHeight:1.4,color:muted,marginTop:20,borderTop:`1px solid ${dark?'#66877955':'#DCE5D8'}`,paddingTop:15}}>{scene.note}</div>}
        {scene.kind==='pause'&&<div style={{marginTop:25,height:7,borderRadius:9,background:dark?'#35544D':'#E0EADD',overflow:'hidden'}}><div style={{height:'100%',width:`${100*Math.max(0,1-local/scene.duration)}%`,background:accent}}/></div>}
      </div>}
      {workshop&&teaching&&<div style={{position:'absolute',left:85,top:725,width:990,display:'flex',gap:15}}>{['01 · DİNLE','02 · ANLAMI BUL','03 · HATIRLA'].map((x,i)=><div key={x} style={{padding:'19px 23px',borderRadius:14,border:'1px solid #C9D8C7',background:i===(scene.kind==='pause'?2:1)?'#D5E8D4':'#F8FAF4',fontSize:21}}>{x}</div>)}</div>}
      <div style={{position:'absolute',left:72,right:75,bottom:82,height:1,background:dark?'#FFFFFF25':'#173D3320'}}/>
      <div style={{position:'absolute',left:72,right:75,bottom:35,display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:20,color:muted}}>
        <div style={{display:'flex',gap:16,alignItems:'center'}}><div style={{display:'flex',gap:3,height:23,alignItems:'center'}}>{[.4,.8,1,.6,.9,.45,.7].map((gain,i)=><div key={i} style={{width:4,height:3+20*(p.levels[frame]??0)*gain,background:accent,borderRadius:3}}/>)}</div>{scene.kind==='pause'?'Düşün ve sesli cevapla':scene.kind==='reading'?'Okuma · English':'Öğretmen · Türkçe'}</div>
        <div>{p.variantTitle} <span style={{marginLeft:25,fontVariantNumeric:'tabular-nums'}}>{Math.floor(time/60)}:{String(Math.floor(time%60)).padStart(2,'0')}</span></div>
      </div>
      {p.readingLink&&!endCard&&<div style={{position:'absolute',right:74,top:22,display:'flex',alignItems:'center',gap:20}}>
        <div style={{fontSize:21,textAlign:'right',maxWidth:260}}>{p.readingLink.label}<div style={{fontSize:17,color:muted,marginTop:7}}>getfluentfast.app</div></div>
        <Img src={staticFile(p.readingLink.qrImage)} style={{width:168,height:168,background:'white'}}/>
      </div>}
      {p.readingLink&&endCard&&<AbsoluteFill style={{background:dark?'#112B2C':'#F7F3EA',padding:'90px 100px',display:'flex',flexDirection:'row',alignItems:'center',gap:95}}>
        <div style={{flex:1}}><div style={{fontSize:29,fontWeight:800,marginBottom:45}}>GetFluentFast ●</div>
          <div style={{fontSize:62,fontWeight:750,lineHeight:1.16}}>{p.readingLink.label}</div>
          <div style={{fontSize:36,marginTop:30,color:muted}}>{p.title}</div>
          <div style={{fontSize:29,marginTop:42}}>{p.readingLink.instruction}</div>
          <div style={{fontSize:25,marginTop:18,color:muted}}>getfluentfast.app</div>
        </div>
        <Img src={staticFile(p.readingLink.qrImage)} style={{width:600,height:600,background:'white'}}/>
      </AbsoluteFill>}
      <div style={{position:'absolute',bottom:0,left:0,height:5,width:`${100*frame/durationInFrames}%`,background:accent}}/>
    </div>
  </AbsoluteFill>;
};

export const readingCoachDef:TemplateDef={
  slug:'reading-coach',title:'Reading Coach',tier:'free',category:'Text',sourceContract:'overlay',
  description:'Source-aligned reading with editorial underlines, contextual artwork and a guiding-language teaching panel.',
  regions:['fullscreen'],schema:readingCoachSchema,
  demoProps:{title:'Booking a hotel room',variantTitle:'Pause & notice',treatment:'paper',scenes:[{kind:'reading',sentence:0,start:0,duration:6,text:'Sarah needs a hotel room for three nights.',image:'reading-teacher-hotel/sarah.png'}]},
  demoDurationSec:6,component:ReadingCoach,
};
