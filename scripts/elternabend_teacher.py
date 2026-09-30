#!/usr/bin/env python3
"""Source-bound Elternabend variants; local only, no provider calls or publication."""
import json,hashlib,subprocess,sys,shutil,math
from pathlib import Path
from array import array
from gff_reading_teacher import pcm,wav,normalize,RATE,FPS,digest,save,load
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work/reading-teacher-elternabend'
PUBLIC=ROOT/'public/reading-teacher-elternabend'
SOURCE=Path('/Users/talhaocakci/Projects/contentpub_io_react_native/outputs/elternabend-seed-de')
CHAPTERS=[(0,'Welcome and overview','classroom.png'),(10,'Care and lunch','classroom.png'),(24,'Homework support','classroom.png'),(31,'Learning together','classroom.png'),(59,'Homework at home','classroom.png'),(75,'Classroom routines','classroom.png'),(93,'Community and celebrations','classroom.png'),(102,'Communication and absences','classroom.png'),(119,'Activities and class fund','classroom.png')]
def chapter(i):return next(x for x in reversed(CHAPTERS) if i>=x[0])
def author():
 ped=load(WORK/'source/persisted-pedagogy-en.json');rows=ped['sentences']
 from elternabend_two_pass import author as create
 lesson=create(rows,ped);save(WORK/'lesson.json',lesson);validate(lesson);return lesson

def validate(lesson):
 rows=load(WORK/'source/persisted-pedagogy-en.json')['sentences'];manifest=load(WORK/'source/audio-manifest.json')
 primary=load(WORK/'source/primary-published.json')
 assert primary['content_id']==lesson['source_id']
 assert primary['payload']['reading_audio']['text_hash']==lesson['source_hash'][:24]
 assert [s['text'] for s in primary['payload']['reading_audio']['sentences']]==[r['sentence_text'] for r in rows]
 assert len(rows)==len(manifest['artifacts'])==137
 for r,clip in zip(rows,manifest['artifacts']):
  assert r['sentence_text']==clip['text'] and r['sentence_text_hash']==clip['text_sha256']
  assert digest(SOURCE/'audio/sentences'/f"{r['sentence_index']:03d}.wav")==clip['checksum_sha256']
 for v in lesson['variants']:
  reads=[s['sentence'] for s in v['scenes'] if s['kind']=='reading'];assert reads[:137]==list(range(137))
  for s in v['scenes']:
   assert not s.get('focus') or s['focus'] in rows[s['sentence']]['sentence_text']
   refs={p['point_id'] for k in ['important_words','important_phrases','grammar'] for p in rows[s['sentence']]['pedagogic'][k]}
   assert set(s.get('pedagogy_refs',[]))<=refs
 print('PASS source text, audio hashes, coverage and pedagogy references',flush=True)

def audio(lesson):
 from elternabend_radio import audio as generate
 generate(lesson)

def compile(lesson):
 audit=load(WORK/'editorial-audit.json')
 assert audit['status']=='PASS' and audit['bindings']['lesson.json']==digest(WORK/'lesson.json'), 'A passing audit for this exact lesson is required'
 qa=load(WORK/'teacher-audio-qa-qwen.json')
 assert qa['passed'] and qa['lesson_sha256']==digest(WORK/'lesson.json'), 'Current teacher audio must pass ASR'
 assert load(WORK/'teacher-waveform-qa-qwen.json')['passed']
 assert load(WORK/'teacher-speaker-qa-qwen.json')['speaker_consistency_audit']['passed']
 narrator=load(WORK/'narrator-mature-qwen/qa.json')
 assert narrator['passed'] and narrator['source_hash']==lesson['source_hash']
 assert narrator['reference_sha256']==digest(WORK/'narrator-mature-qwen/reference.wav')
 assert load(WORK/'narrator-mature-qwen/speaker-qa.json')['speaker_consistency_audit']['passed']
 rows=load(WORK/'source/persisted-pedagogy-en.json')['sentences'];theme=load(ROOT/'brand/getfluentfast.theme.json')
 for v in lesson['variants']:
  data=bytearray();scenes=[]
  for raw in v['scenes']:
   i=raw['sentence'];s=dict(raw,text=rows[i]['sentence_text'],words=[]);s['teacherText']=raw.get('text','')
   if raw['kind']=='reading':
    path=WORK/'narrator-mature-qwen'/raw.get('pace','regular')/f'{i:03d}.wav';receipt=load(path.with_suffix('.json'))
    assert receipt['text']==rows[i]['sentence_text'] and receipt['audio_sha256']==digest(path)
    b=pcm(path)
   elif raw['kind']=='teacher':
    path=WORK/'teacher-audio-qwen'/f"{raw['key']}.wav";receipt=load(path.with_suffix('.json'))
    assert receipt['text']==raw['text'] and receipt['audio_sha256']==digest(path)
    assert receipt['reference_sha256']==lesson['teacher_voice']['reference_sha256']
    b=pcm(path)
   else:b=b'\0'*(round(raw['duration']*RATE)*2)
   if raw['kind']!='pause':b,_=normalize(b)
   b+=b'\0'*(round((.2 if raw['kind']=='reading' else .4)*RATE)*2)
   b+=b'\0'*(((-len(b)//2)%(RATE//FPS))*2)
   s['start']=len(data)/2/RATE;s['duration']=len(b)/2/RATE;s['chapter']=raw.get('chapter',chapter(i)[1]);s['image']=raw.get('image','reading-teacher-elternabend/'+chapter(i)[2])
   scenes.append(s);data.extend(b)
  end=len(data)/2/RATE;data.extend(b'\0'*(RATE*2*10));duration=len(data)/2/RATE
  output=PUBLIC/(v['id']+'.wav');wav(output,data)
  p=dict(presentation=lesson.get('presentation',{}),ui=lesson.get('ui',{}),title=lesson.get('video_title','Elternabend: Our first school year together'),variantTitle=v['title'],treatment=v['treatment'],scenes=scenes,lessonUI=dict(targetLabel=lesson.get('ui',{}).get('targetLabel','German'),guidingLabel=lesson.get('ui',{}).get('guidingLabel','English'),cefr=lesson['cefr'],sentenceCount=137),readingLink=dict(url='https://getfluentfast.app/reading/reading_elternabend_seed_de/',qrImage='reading-teacher-elternabend/reading-qr.png',endCardStart=end,label=lesson.get('ui',{}).get('continueLabel','Continue in the app'),instruction=lesson.get('ui',{}).get('qrInstruction','Scan with your phone camera')))
  spec=dict(version=1,format='horizontal',fps=FPS,durationSec=duration,source=dict(type='audio',src='reading-teacher-elternabend/'+v['id']+'.wav'),sound=dict(enabled=False,volume=0,sounds={}),overlays=[dict(template='reading-coach',region='fullscreen',time=dict(start='0s',duration=f'{duration}s'),props=p)])
  save(WORK/(v['id']+'.props.json'),dict(spec=spec,theme=theme));save(WORK/(v['id']+'.manifest.json'),dict(variant=v['id'],source_id=lesson['source_id'],source_hash=lesson['source_hash'],lesson_sha256=digest(WORK/'lesson.json'),audio_sha256=digest(output),duration_seconds=duration,sentence_count=137,word_timing='none',teacher_voice=lesson['teacher_voice'],narrator_provenance=load(WORK/'narrator-mature-qwen/manifest.json'),pacing=lesson['pacing'],motion_template='reading-coach',family='reading-teacher',publication='local_only'))
  print('compiled',v['id'],round(duration,2),flush=True)

if __name__=='__main__':
 action=sys.argv[1];lesson=author() if action=='author' else load(WORK/'lesson.json')
 if action!='author':validate(lesson)
 if action=='audio':audio(lesson)
 if action=='compile':compile(lesson)
