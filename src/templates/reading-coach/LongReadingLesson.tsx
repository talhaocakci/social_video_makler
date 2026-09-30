import {AppPromotion,promoAmount} from './AppPromotion';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {videoCanvasStyle,videoLayerStyle} from '../video-layout';

/** Full-length reading layout; sentence display never implies word timing. */
export function LongReadingLesson({p,time,width,height}:{p:any;time:number;width:number;height:number}) {
 const scene=p.scenes.find((s:any)=>time>=s.start&&time<s.start+s.duration)??p.scenes.at(-1);
 const ui=p.ui??{};const tr=(key:string,fallback:string)=>ui[key]??fallback;
 const promo=p.promotions?.find((x:any)=>time>=x.start&&time<x.start+x.duration);
 const amount=promoAmount(promo,time);
 const lessonScale=1-.36*amount;
 const dark=p.treatment==='cinema',workshop=p.treatment==='workshop';
 const ink=dark?'#F8F3E8':'#173E32',muted=dark?'#B9D0C4':'#587364',accent=dark?'#F5CE8C':'#187451';
 const teaching=scene.kind!=='reading';const end=p.readingLink&&time>=p.readingLink.endCardStart;
 const readingPhase=scene.pace?.includes('natural')?'NATURAL SPEED':scene.pace?.includes('full sentence')?'FULL SENTENCE · SLOW':'SHORT PART · SLOW';
 const readingHint=scene.pace?.includes('natural')?'Follow the complete thought at natural speed.':scene.pace?.includes('full sentence')?'Now connect the parts in the complete sentence.':tr('readingHint','Take your time. Let the meaning come together.');
 const focus=scene.focus?scene.text.indexOf(scene.focus):-1;
 const text=<>{focus<0?scene.text:<>{scene.text.slice(0,focus)}<span style={{color:accent,textDecoration:'underline',textDecorationColor:'#D5954C',textUnderlineOffset:9,textDecorationThickness:4}}>{scene.focus}</span>{scene.text.slice(focus+scene.focus.length)}</>}</>;
 const font=!dark&&!workshop&&scene.teaching_notes?.length>1?42:scene.text.length>200?43:scene.text.length>130?49:58;
 const progress=Math.min(1,(time-scene.start)/.35);
 const L=(name:any,fallback:any)=>videoLayerStyle(p.layout,name,fallback);
 return <AbsoluteFill style={videoCanvasStyle(p.layout,{background:dark?'#102D2D':'#F5F2E8',color:ink,fontFamily:"'Avenir Next',system-ui,sans-serif"})}>
 <div style={{position:'absolute',width:1920,height:1080,transform:`scale(${width/1920},${height/1080})`,transformOrigin:'top left'}}>
 <div style={{position:'absolute',width:1920,height:1080,transform:`translate(${28*amount}px,${194*amount}px) scale(${lessonScale})`,transformOrigin:'top left'}}>
 {dark&&<><Img src={staticFile('reading-teacher-elternabend/classroom.png')} style={{position:'absolute',width:1920,height:1080,objectFit:'cover',opacity:.18}}/><AbsoluteFill style={{background:'linear-gradient(90deg,#102D2DEB,#102D2D99)'}}/></>}
 <div style={L('logo',{position:'absolute',left:72,top:46,fontSize:29,fontWeight:800})}>GetFluentFast ●</div>
 <div style={L('meta',{position:'absolute',left:72,top:106,fontSize:22,color:muted})}>{p.lessonUI.targetLabel} {tr('readingLabel','reading')} · {p.lessonUI.guidingLabel} {tr('guidanceLabel','guidance')}{p.presentation?.showLevel!==false&&<> · {p.lessonUI.cefr}</>}</div>
 <div style={{position:'absolute',left:72,top:165,fontSize:25,fontWeight:600}}>{p.presentation?.showChapter!==false&&scene.chapter}{p.presentation?.showPassLabel!==false&&<span style={{marginLeft:30,fontSize:20,color:muted}}>{scene.pass_label}</span>}</div>
 {p.readingLink&&<div style={{position:'absolute',right:72,top:24,display:'flex',alignItems:'center',gap:22,opacity:1-amount}}><div style={{textAlign:'right',fontSize:21}}>{tr('continueLabel','Continue in the app')}<div style={{fontSize:17,color:muted,marginTop:7}}>getfluentfast.app</div></div><Img src={staticFile(p.readingLink.qrImage)} style={L('qr',{width:162,height:162,background:'white',objectFit:'contain'})}/></div>}
 {!dark&&!workshop&&<Img src={staticFile(scene.image)} style={L('media',{position:'absolute',left:72,top:260,width:650,height:510,objectFit:'cover',borderRadius:26})}/>}
 {!dark&&!workshop&&<div style={{position:'absolute',left:78,top:825,width:620,fontSize:24,lineHeight:1.5,color:muted}}>{tr('sceneCaption','Feel more at home at your next parents’ evening. Let’s make the school’s plans and requests easier to follow.')}<div style={{fontSize:17,marginTop:18}}>{tr('illustrationCaption','Listen together · One sentence at a time')}</div></div>}
 <div style={L('content',{position:'absolute',left:!dark&&!workshop?795:80,top:255,width:!dark&&!workshop?1045:teaching?965:1370})}>
 <div style={{fontSize:19,color:muted,letterSpacing:2,marginBottom:24}}>{scene.kind==='reading'?readingPhase+' · '+p.lessonUI.targetLabel:scene.kind==='pause'?tr('thinkLabel','THINK ABOUT THE MEANING'):tr('closerLabel','LET’S LOOK CLOSER')} <span style={{marginLeft:20}}>{scene.sentence+1} / {p.lessonUI.sentenceCount}</span></div>
 <div style={{fontSize:font,lineHeight:1.38,fontWeight:500,letterSpacing:-1}}>{text}</div>
 {!teaching&&<div style={{fontSize:23,color:muted,marginTop:34}}>{readingHint}</div>}
 </div>
 {teaching&&<div style={L('teaching',{position:'absolute',left:!dark&&!workshop?795:1120,top:!dark&&!workshop?(scene.lexical_pairs?.length?590:scene.teaching_notes?.length>1?520:630):260,width:!dark&&!workshop?1045:720,padding:32,borderRadius:24,background:dark?'#1A3A35F5':'#FFFFFFEE',border:`1px solid ${dark?'#547565':'#CCD7C8'}`,opacity:progress,transform:`translateY(${(1-progress)*12}px)`})}>
 <div style={{fontSize:18,letterSpacing:2,color:muted,marginBottom:18}}>{scene.kind==='pause'?tr('yourTurnLabel','YOUR TURN'):tr('teacherLabel','TEACHER NOTE')+' · '+p.lessonUI.guidingLabel}</div>
 <div style={{fontSize:scene.lexical_pairs?.length?30:36,lineHeight:1.22,fontWeight:750,color:accent}}>{scene.title}</div>
 <div style={{fontSize:scene.lexical_pairs?.length?24:scene.teaching_notes?.length?23:29,lineHeight:1.35,marginTop:16,whiteSpace:'pre-line'}}>{scene.body}</div>
 {scene.teaching_notes?.map((n:any)=><div key={n.point_id} style={{fontSize:21,lineHeight:1.35,marginTop:14,borderTop:`1px solid ${dark?'#547565':'#CCD7C8'}`,paddingTop:10}}><strong style={{color:accent}}>{n.term} · {n.meaning}</strong><div style={{marginTop:5}}>{n.explanation}</div></div>)}
 {scene.kind==='pause'&&<div style={{marginTop:25,height:7,background:dark?'#35554A':'#DEE8D8',borderRadius:8}}><div style={{height:7,width:`${100*Math.max(0,1-(time-scene.start)/scene.duration)}%`,background:accent,borderRadius:8}}/></div>}
 </div>}
 {workshop&&<Img src={staticFile(scene.image)} style={{position:'absolute',right:80,top:700,width:teaching?460:660,height:teaching?235:250,objectFit:scene.image.endsWith('.svg')?'contain':'cover',borderRadius:20}}/>}
 <div style={L('footer',{position:'absolute',left:72,right:72,bottom:40,borderTop:`1px solid ${dark?'#FFFFFF30':'#CED8C8'}`,paddingTop:22,display:'flex',justifyContent:'space-between',fontSize:20,color:muted})}><span>{p.variantTitle} · {scene.kind==='reading'?p.lessonUI.targetLabel+' '+tr('narrationLabel','narration'):scene.kind==='pause'?tr('thinkingLabel','Thinking time'):p.lessonUI.guidingLabel+' '+tr('teacherRoleLabel','teacher')}</span><span>{Math.floor(time/60)}:{String(Math.floor(time%60)).padStart(2,'0')}</span></div>
 {end&&<AbsoluteFill style={videoCanvasStyle(p.layout,{background:dark?'#102D2D':'#F5F2E8'})}><div style={L('endText',{position:'absolute',left:100,top:90,width:950,height:900,display:'flex',flexDirection:'column',justifyContent:'center'})}><div style={{fontSize:30,fontWeight:800,marginBottom:40}}>GetFluentFast ●</div><div style={{fontSize:65,fontWeight:750,lineHeight:1.15}}>{tr('endTitle','Continue with\nElternabend').split('\n').map((line:string,i:number)=><div key={i}>{line}</div>)}</div><div style={{fontSize:30,marginTop:35}}>{tr('endBody','Read, listen and practise in the app.')}</div><div style={{fontSize:28,color:muted,marginTop:40}}>{tr('qrInstruction','Scan with your phone camera')}</div><div style={{fontSize:24,color:muted,marginTop:15}}>getfluentfast.app</div></div><Img src={staticFile(p.readingLink.qrImage)} style={L('endQr',{position:'absolute',left:1210,top:230,width:600,height:600,background:'white',objectFit:'contain'})}/></AbsoluteFill>}
 </div>
 {promo&&<AppPromotion promo={promo} time={time}/>}
 <div style={L('progress',{position:'absolute',left:0,bottom:0,height:7,width:'100%',background:dark?'#35554A':'#D8E2D9',overflow:'hidden'})}><div style={{width:`${100*time/(p.scenes.at(-1).start+p.scenes.at(-1).duration)}%`,height:'100%',background:accent}}/></div>
 </div></AbsoluteFill>;
}
