import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {parseSpec} from '../src/spec/validate';
const root=process.cwd(),work=process.env.GFF_READING_WORK??path.join(root,'work/reading-teacher-elternabend'),out=path.join(root,'renders/reading-teacher-elternabend');
const mode=process.argv[2]??'stills';
const url=await bundle({entryPoint:path.join(root,'remotion/index.ts'),publicDir:path.join(root,'public')});
const ids=process.argv.slice(3);
for(const id of (ids.length?ids:JSON.parse(fs.readFileSync(path.join(work,'lesson.json'),'utf8')).variants.map((v:any)=>v.id))){
 const inputProps=JSON.parse(fs.readFileSync(path.join(work,id+'.props.json'),'utf8'));parseSpec(inputProps.spec);
 const composition=await selectComposition({serveUrl:url,id:'custom',inputProps});const scenes=inputProps.spec.overlays[0].props.scenes;
 const longest=scenes.filter((s:any)=>s.kind==='reading').sort((a:any,b:any)=>b.text.length-a.text.length)[0];
 const points=[{name:'opening',time:3},{name:'teaching',time:scenes.find((s:any)=>s.kind==='teacher'&&(s.focus==='Hort'||s.sentence===15)).start+2},{name:'longest',time:longest.start+1},{name:'late',time:(scenes.find((s:any)=>s.kind==='teacher'&&s.sentence===113)??scenes.find((s:any)=>s.kind==='teacher'&&s.sentence===16)).start+2},{name:'passive',time:scenes.find((s:any)=>s.kind==='teacher'&&s.sentence===15).start+2},{name:'two-notes',time:(scenes.find((s:any)=>s.kind==='teacher'&&s.sentence===100)??scenes.find((s:any)=>s.kind==='teacher'&&s.sentence===16)).start+2},{name:'regular-pass',time:scenes.find((s:any)=>s.kind==='reading'&&s.pace==='regular').start+2},{name:'qr',time:composition.durationInFrames/30-5}];
 if(scenes.some((s:any)=>s.lexical_pairs?.length)){
  const vocabulary=scenes.filter((s:any)=>s.lexical_pairs?.length);
  const dense=vocabulary.sort((a:any,b:any)=>(b.title.length+b.body.length)-(a.title.length+a.body.length))[0];
  points.push({name:'vocabulary-dense',time:dense.start+2});
  for(const i of [12,34,111])points.push({name:'vocabulary-'+i,time:scenes.find((s:any)=>s.key==='more-words-'+i).start+2});
 }
 if(mode==='stills'){
  for(const p of points){await renderStill({serveUrl:url,composition,inputProps,output:path.join(work,`${id}-${p.name}.png`),frame:Math.round(p.time*30),logLevel:'error'});console.log('still',id,p.name)}
 }else{
  const output=path.join(out,id+'.mp4');let last=-1;
  await renderMedia({serveUrl:url,composition,inputProps,outputLocation:output,codec:'h264',crf:23,concurrency:12,onProgress:({progress})=>{const n=Math.floor(progress*10);if(n!==last){console.log(id,n*10+'%');last=n}},logLevel:'error'});
  await renderStill({serveUrl:url,composition,inputProps,output:path.join(out,id+'.png'),frame:90,logLevel:'error'});
  console.log('DONE',id,composition.durationInFrames/30);
 }
}
