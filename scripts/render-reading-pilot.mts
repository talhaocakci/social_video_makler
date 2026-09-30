import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {selectComposition,renderStill,renderMedia} from '@remotion/renderer';
import {parseSpec} from '../src/spec/validate';

const root=process.cwd();
const suffix=process.argv.includes('--qr')?'-qr':'';
const work=path.join(root,`work/reading-teacher-hotel${suffix}`);
const output=path.join(root,`renders/reading-teacher-hotel${suffix}`);
fs.mkdirSync(output,{recursive:true});
const mode=process.argv[2]??'stills';
const serveUrl=await bundle({entryPoint:path.join(root,'remotion/index.ts'),publicDir:path.join(root,'public')});
const report=[];
for(const id of ['01-close-reading','02-story-first','03-predict-recall']){
  const inputProps=JSON.parse(fs.readFileSync(path.join(work,`${id}.props.json`),'utf8'));
  parseSpec(inputProps.spec);
  const composition=await selectComposition({serveUrl,id:'custom',inputProps});
  const scenes=inputProps.spec.overlays[0].props.scenes;
  const checkpoints=[
    {name:'opening',time:scenes[0].start+2},
    {name:'reading',time:scenes.find((s:any)=>s.kind==='reading'&&s.sentence===1).start+1.6},
    {name:'meaning',time:scenes.find((s:any)=>s.kind==='teacher'&&s.focus==='available').start+3},
    {name:'panel',time:scenes.find((s:any)=>s.diagram==='question'||s.diagram==='confirmation').start+3},
    {name:'late',time:scenes.at(-1).start+3},
  ];
  if(suffix)checkpoints.push({name:'qr-end',time:inputProps.spec.overlays[0].props.readingLink.endCardStart+3});
  if(mode==='stills'){
    for(const c of checkpoints){
      const output=path.join(work,`${id}-${c.name}.png`);
      await renderStill({serveUrl,composition,inputProps,output,frame:Math.round(c.time*composition.fps),logLevel:'error'});
      report.push({id,...c,output});console.log('still',id,c.name);
    }
  }else{
    const out=path.join(output,`${id}.mp4`);
    let last=-1;
    await renderMedia({serveUrl,composition,inputProps,outputLocation:out,codec:'h264',crf:22,concurrency:4,
      onProgress:({progress})=>{const step=Math.floor(progress*10);if(step!==last){last=step;console.log(id,`${step*10}%`);}},logLevel:'error'});
    const cover=path.join(output,`${id}.png`);
    await renderStill({serveUrl,composition,inputProps,output:cover,frame:Math.round(checkpoints[2].time*composition.fps),logLevel:'error'});
    report.push({id,output:out,cover,duration:composition.durationInFrames/composition.fps});
    console.log('DONE',id);
  }
}
fs.writeFileSync(path.join(work,`${mode}-report.json`),JSON.stringify(report,null,2));
