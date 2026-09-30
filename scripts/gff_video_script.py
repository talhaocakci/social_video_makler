#!/usr/bin/env python3
"""Export ordered video script + translatable strings; materialize another locale."""
import argparse,copy,hashlib,json,re
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def write(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def export(work,out):
 lesson=read(work/'lesson.json');rows=read(work/'source/persisted-pedagogy-en.json')['sentences']
 from elternabend_teacher import chapter
 strings={};bindings=[]
 def text(value,key,path):
  strings[key]=value;bindings.append({'path':path,'string_id':key});return value
 script=copy.deepcopy(lesson);script['schema_version']=1;script['timing_policy']='Regenerate speech, measure clips, then rebuild timings; never reuse timings from another language.'
 script['ui']={
 'targetLabel':'German','guidingLabel':'English','readingLabel':'reading','guidanceLabel':'guidance','listenLabel':'LISTEN','closerLabel':'LET’S LOOK CLOSER','thinkLabel':'THINK ABOUT THE MEANING','teacherLabel':'TEACHER NOTE','yourTurnLabel':'YOUR TURN','readingHint':'Take your time. Let the meaning come together.','sceneCaption':'Feel more at home at your next parents’ evening. Let’s make the school’s plans and requests easier to follow.','illustrationCaption':'Listen together · One sentence at a time','narrationLabel':'narration','thinkingLabel':'Thinking time','teacherRoleLabel':'teacher','continueLabel':'Continue in the app','domain':'getfluentfast.app','endTitle':'Continue with\nElternabend','endBody':'Read, listen and practise in the app.','qrInstruction':'Scan with your phone camera'}
 for k,v in script['ui'].items():
  if k!='domain':text(v,'ui.'+k,['ui',k])
 script['video_title']='Elternabend: Our first school year together';text(script['video_title'],'video.title',['video_title'])
 for vi,v in enumerate(script['variants']):
  text(v['title'],v['id']+'.title',['variants',vi,'title'])
  for si,s in enumerate(v['scenes']):
   base=['variants',vi,'scenes',si];i=s['sentence'];s['scene_id']=f"{v['id']}.{si:04d}";s['source_text']=rows[i]['sentence_text'];s['chapter']=chapter(i)[1];s['image']='reading-teacher-elternabend/'+chapter(i)[2]
   text(s['chapter'],'chapter.'+str(chapter(i)[0]),base+['chapter'])
   for field in ['title','body','sentence_meaning','note','pass_label']:
    if s.get(field):text(s[field],f"scene.{s.get('key',s['scene_id'])}.{field}",base+[field])
   for bi,b in enumerate(s.get('speech_beats',[])):
    b['language_role']='target' if b['language']=='German' else 'guiding'
    if b['language_role']=='guiding':text(b['text'],f"speech.{s['key']}.{bi}",base+['speech_beats',bi,'text'])
   for ni,n in enumerate(s.get('teaching_notes',[])):
    for field in ['meaning','explanation']:
     text(n[field],f"pedagogy.{n['point_id']}.{field}",base+['teaching_notes',ni,field])
   for ni,n in enumerate(s.get('lexical_pairs',[])):
    text(n['meaning'],f"lexical.{s['key']}.{ni}.meaning",base+['lexical_pairs',ni,'meaning'])
 script['assets']=[]
 for p in sorted((ROOT/'public/reading-teacher-elternabend').glob('*.svg')):
  if 'reading-teacher-elternabend/'+p.name not in {s['image'] for v in script['variants'] for s in v['scenes']}:continue
  xml=ET.parse(p);nodes=[n for n in xml.iter() if n.tag.endswith('}text') or n.tag=='text'];asset={'path':'reading-teacher-elternabend/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'text_strings':[]}
  for i,n in enumerate(nodes):
   key=f'asset.{p.stem}.text.{i}';strings[key]=''.join(n.itertext());asset['text_strings'].append(key)
  script['assets'].append(asset)
 script['reading_link']={'app_deep_link':'getfluentfast://reading/reading_elternabend_seed_de','url':'https://getfluentfast.app/reading/reading_elternabend_seed_de/','qrImage':'reading-teacher-elternabend/reading-qr.png','hold_seconds':10}
 if (work/'narrator-mature-qwen/manifest.json').exists():script['voice_roles']={'target':read(work/'narrator-mature-qwen/manifest.json'),'guiding':script['teacher_voice']}
 script['localization_bindings']=bindings
 write(out/'video-script.json',script);write(out/'guiding-en.json',{'language':'en','tts_language':'English','strings':strings})
 write(out/'guiding-translation-template.json',{'language':'CHANGE_ME','tts_language':'CHANGE_ME','strings':strings})
 md=['# Complete ordered video script','Target reading, speech order, pauses, panels, pedagogy and visuals are stored in video-script.json. Translate guiding-translation-template.json. German speech/source spans stay unchanged.']
 for v in script['variants']:
  md.append('\n## '+v['title'])
  for s in v['scenes']:
   md.append(f"\n### {s['scene_id']} · {s['kind']} · sentence {s['sentence']+1}\nGerman: {s['source_text']}\nVisual: {s['image']} · Chapter: {s['chapter']}\nUnderline: {s.get('focus','')}")
   if s['kind']=='reading':md.append('Audio: exact German reading sentence.')
   for b in s.get('speech_beats',[]):md.append(f"Speak [{b['language_role']}]: {b['text']}\nPause after: {b['pause_after_seconds']}s · Delivery: {b['direction']}")
   if s['kind']=='pause':md.append(f"Thinking pause: {s['duration']}s")
   if s.get('body'):md.append(f"Panel: {s['title']}\n{s['body']}")
   for n in s.get('teaching_notes',[]):md.append(f"{n['kind']}: {n['term']} · {n['meaning']}\n{n['explanation']}")
 (out/'video-script.md').write_text('\n\n'.join(md)+'\n');print('Exported',len(strings),'translatable strings,',sum(len(v['scenes']) for v in script['variants']),'ordered scenes')
def materialize(script_path,locale_path,out):
 script=read(script_path);loc=read(locale_path);assert loc['language']!='CHANGE_ME' and loc['tts_language']!='CHANGE_ME'
 strings=loc['strings'];expected={b['string_id'] for b in script['localization_bindings']}|{k for a in script['assets'] for k in a['text_strings']}
 assert expected<=strings.keys(),f'Missing translations: {sorted(expected-strings.keys())}'
 for b in script['localization_bindings']:
  obj=script
  for key in b['path'][:-1]:obj=obj[key]
  obj[b['path'][-1]]=strings[b['string_id']]
 for v in script['variants']:
  for s in v['scenes']:
   for b in s.get('speech_beats',[]):
    if b['language_role']=='guiding':b['language']=loc['tts_language']
   if s.get('speech_beats'):s['text']=' '.join(b['text'] for b in s['speech_beats'])
 prefix='reading-teacher-elternabend-'+loc['language'];assert re.fullmatch(r'[a-zA-Z0-9_-]+',prefix)
 for a in script['assets']:
  source=ROOT/'public'/a['path'];assert hashlib.sha256(source.read_bytes()).hexdigest()==a['sha256']
  xml=ET.parse(source);nodes=[n for n in xml.iter() if n.tag.endswith('}text') or n.tag=='text']
  for n,key in zip(nodes,a['text_strings']):
   assert len(n)==0,'Nested SVG text needs explicit localization support';n.text=strings[key]
  dest=ROOT/'public'/prefix/source.name;dest.parent.mkdir(parents=True,exist_ok=True);xml.write(dest,encoding='unicode')
  for v in script['variants']:
   for s in v['scenes']:
    if s['image']==a['path']:s['image']=prefix+'/'+source.name
 script['guiding_language']=loc['language'];script['teacher_voice']['status']='select guiding-language reference before synthesis';script['teacher_voice']['user_approved_sample']=False
 script['localization_provenance']={'source_script_sha256':hashlib.sha256(Path(script_path).read_bytes()).hexdigest(),'locale_sha256':hashlib.sha256(Path(locale_path).read_bytes()).hexdigest()}
 write(out,script);print('Materialized',out,'— regenerate audio and measure timings before rendering.')
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
e=sub.add_parser('export');e.add_argument('--work',type=Path,required=True);e.add_argument('--out',type=Path,required=True)
m=sub.add_parser('materialize');m.add_argument('--script',type=Path,required=True);m.add_argument('--locale',type=Path,required=True);m.add_argument('--out',type=Path,required=True)
if __name__=='__main__':
 a=p.parse_args();export(a.work,a.out) if a.cmd=='export' else materialize(a.script,a.locale,a.out)
