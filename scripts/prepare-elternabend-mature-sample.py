"""Reading → brief explanation → continue; then normal-speed uninterrupted replay."""
from pathlib import Path
import copy
from gff_reading_teacher import load,save,pcm,wav,normalize,RATE,FPS,digest
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/reading-teacher-elternabend';PUBLIC=ROOT/'public/reading-teacher-elternabend';OUT=WORK/'narrator-mature-qwen'
rows=load(WORK/'source/persisted-pedagogy-en.json')['sentences'];lesson=load(WORK/'lesson.json');data=bytearray();scenes=[]
def append(raw,audio):
 b=pcm(audio);b,_=normalize(b);b+=b'\0'*(round(.3*RATE)*2);b+=b'\0'*(((-len(b)//2)%(RATE//FPS))*2);i=raw['sentence'];s=dict(raw,text=rows[i]['sentence_text'],words=[],start=len(data)/2/RATE,duration=len(b)/2/RATE,chapter='Care and lunch',image='reading-teacher-elternabend/classroom.png');scenes.append(s);data.extend(b)
for i in [13,14,15,16,17,18]:
 append(dict(kind='reading',sentence=i,pace='slow',pass_label='First pass · 12% slower'),OUT/'slow'/f'{i:03d}.wav')
 if i in [13,14,15,16]:
  s=next(copy.deepcopy(s) for s in lesson['variants'][0]['scenes'] if s.get('key')==f'first-use-{i}');p=WORK/'teacher-audio-qwen'/f'first-use-{i}.wav';receipt=load(p.with_suffix('.json'));assert receipt['text']==s['text'] and receipt['audio_sha256']==digest(p);s['teacherText']=s['text'];append(s,p)
bridge=WORK/'teacher-audio-qwen/regular-pass-bridge.wav';append(dict(kind='teacher',sentence=15,title='Second pass',body='Regular speed · no explanations'),bridge)
for i in [13,14,15,16,17,18]:append(dict(kind='reading',sentence=i,pace='regular',pass_label='Second pass · Regular speed'),OUT/'regular'/f'{i:03d}.wav')
duration=len(data)/2/RATE;audio=PUBLIC/'mature-voice-sample.wav';wav(audio,data)
p=dict(title='Understanding your first parents’ evening',variantTitle='Let’s listen together',treatment='paper',scenes=scenes,lessonUI=dict(targetLabel='German',guidingLabel='English',cefr='B2',sentenceCount=137))
spec=dict(version=1,format='horizontal',fps=30,durationSec=duration,source=dict(type='audio',src='reading-teacher-elternabend/mature-voice-sample.wav'),sound=dict(enabled=False,volume=0,sounds={}),overlays=[dict(template='reading-coach',region='fullscreen',time=dict(start='0s',duration=f'{duration}s'),props=p)])
save(WORK/'mature-voice-sample.props.json',dict(spec=spec,theme=load(ROOT/'brand/getfluentfast.theme.json')));save(OUT/'sample-sequence.json',dict(duration_seconds=duration,scenes=scenes,source_id=lesson['source_id'],source_hash=lesson['source_hash'],audio_sha256=digest(audio),synthetic=True,human_audition=False));print('Sample duration',duration)
