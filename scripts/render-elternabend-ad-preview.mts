import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {parseSpec} from '../src/spec/validate';
const root=process.cwd(),work=path.join(root,'work/reading-teacher-elternabend-promo'),id=process.argv[3]??'ueberblick-ad-transition-preview';
const inputProps=JSON.parse(fs.readFileSync(path.join(work,id+'.props.json'),'utf8'));parseSpec(inputProps.spec);
const url=await bundle({entryPoint:path.join(root,'remotion/index.ts'),publicDir:path.join(root,'public')});
const composition=await selectComposition({serveUrl:url,id:'custom',inputProps});
const promo=inputProps.spec.overlays[0].props.promotions[0];
const checkpoints={before:promo.start-.5,enter:promo.start+.4,stable:promo.start+2,quiz:promo.start+promo.duration*.7,exit:promo.start+promo.duration-.4,after:promo.start+promo.duration+.5};
if(process.argv[2]==='stills'){
 for(const [name,time] of Object.entries(checkpoints)){
  await renderStill({serveUrl:url,composition,inputProps,output:path.join(work,id+'-'+name+'.png'),frame:Math.round(time*30),logLevel:'error'});console.log(name);
 }
}else{
 let last=-1;
 await renderMedia({serveUrl:url,composition,inputProps,outputLocation:path.join(root,'renders/reading-teacher-elternabend',id+'.mp4'),codec:'h264',crf:19,concurrency:8,logLevel:'error',onProgress:({progress})=>{const n=Math.floor(progress*10);if(n!==last){console.log(n*10+'%');last=n}}});
 console.log('DONE',composition.durationInFrames/30);
}
