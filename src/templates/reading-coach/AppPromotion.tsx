import {Img, staticFile} from 'remotion';

export type AppPromo = {start:number; duration:number; mode:'spoken'|'silent'; headline:string; instruction:string; qrImage:string; screens:{src:string;caption:string;tap?:{x:number;y:number}}[]};
export function promoAmount(promo:AppPromo|undefined,time:number){
 if(!promo)return 0;
 const t=time-promo.start;
 const x=Math.max(0,Math.min(1,t/.8,(promo.duration-t)/.8));
 return x*x*(3-2*x);
}
/** Actual application captures, never a reconstructed product UI. */
export function AppPromotion({promo,time}:{promo:AppPromo;time:number}){
 const amount=promoAmount(promo,time);
 const local=time-promo.start;
 const index=Math.min(promo.screens.length-1,Math.max(0,Math.floor((local-.8)/((promo.duration-1.6)/promo.screens.length))));
 const screen=promo.screens[index];
 const screenDuration=(promo.duration-1.6)/promo.screens.length;
 const tapProgress=(local-.8-index*screenDuration-(screenDuration-.65))/.65;
 return <div style={{position:'absolute',left:1280,top:120,width:600,height:900,opacity:amount,transform:`translateX(${(1-amount)*640}px)`,color:'#173E32',fontFamily:"'Avenir Next',system-ui,sans-serif"}}>
  <div style={{fontSize:32,fontWeight:750,lineHeight:1.2,marginBottom:16}}>{promo.headline}</div>
  <div style={{display:'flex',alignItems:'center',gap:22}}>
   <div style={{position:'relative',width:306,height:650,border:'9px solid #173E32',borderRadius:42,overflow:'hidden',background:'#fff',flexShrink:0}}>
    <Img src={staticFile(screen.src)} style={{width:'100%',height:'100%',objectFit:'contain'}}/>
    {screen.tap&&tapProgress>=0&&tapProgress<=1&&<div style={{position:'absolute',left:`${screen.tap.x*100}%`,top:`${screen.tap.y*100}%`,width:34,height:34,border:'4px solid #E2A342',borderRadius:'50%',background:'#E2A34233',opacity:Math.sin(tapProgress*Math.PI),transform:`translate(-50%,-50%) scale(${.7+tapProgress*.7})`}}/>}
   </div>
   <div style={{width:240}}><Img src={staticFile(promo.qrImage)} style={{width:230,height:230,background:'#fff'}}/><div style={{fontSize:24,lineHeight:1.35,marginTop:20}}>{promo.instruction}</div><div style={{fontSize:20,marginTop:16}}>getfluentfast.app</div></div>
  </div>
  <div style={{fontSize:28,fontWeight:650,marginTop:22}}>{screen.caption}</div>
 </div>;
}
