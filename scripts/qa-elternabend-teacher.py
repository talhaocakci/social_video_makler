"""Checksum-bound native-language ASR checks for local Qwen teaching beats."""
import sys,json,time,os
os.environ["OPENBLAS_NUM_THREADS"]="1"
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper')
import validate_gff_audio as v
from gff_reading_teacher import digest
from elternabend_radio import identity
ROOT=Path(__file__).resolve().parents[1];WORK=Path(os.environ.get('GFF_READING_WORK',str(ROOT/'work/reading-teacher-elternabend')));OUT=WORK/'teacher-audio-qwen/beats';QA=WORK/'teacher-qa-qwen';QA.mkdir(exist_ok=True)
lesson=json.loads((WORK/'lesson.json').read_text());beats={identity(b):b for variant in lesson['variants'] for s in variant['scenes'] if s['kind']=='teacher' for b in s['speech_beats']}
model=v.WhisperModel(str(v.MODELS['large-v3-turbo']['path']),device='cpu',compute_type='int8',cpu_threads=3,num_workers=2,local_files_only=True);secondary=None;secondary_lock=Lock()
def one(item):
 global secondary
 h,b=item;audio=OUT/(h+'.wav');target=QA/(h+'.json')
 while not audio.with_suffix('.json').exists():time.sleep(3)
 lang='de' if b['language']=='German' else 'en'
 if target.exists() and json.loads(target.read_text())['audio_sha256']==digest(audio) and json.loads(target.read_text())['passed']:return json.loads(target.read_text())
 r=v.transcribe(model,str(audio),lang);r['transcription_model']='large-v3-turbo';r.update(v.score(b['text'],r['text'],language=lang));
 if not r['passed'] and lang=='en':
  expected=b['text'].replace('Get Fluent Fast','GetFluentFast').replace('practise','practice')
  canonical=v.score(expected,r['text'],language=lang)
  if canonical['passed']:r['orthographic_reconciliation']=dict(expected=expected,score=canonical,reason='brand spacing and British/American spelling');r['passed']=True
 if not r['passed']:
  with secondary_lock:
   if secondary is None:secondary=v.WhisperModel(str(v.MODELS['large-v3']['path']),device='cpu',compute_type='int8',cpu_threads=3,num_workers=2,local_files_only=True)
  q=v.transcribe(secondary,str(audio),lang);q.update(v.score(b['text'],q['text'],language=lang));q['transcription_model']='large-v3';r['secondary']=q;r['passed']=r['passed'] or q['passed']
 r.update(identity=h,source_text=b['text'],language=lang,audio_sha256=digest(audio));target.write_text(json.dumps(r,indent=2));print(b['text'][:50],r['passed'],flush=True);return r
with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,beats.items()))
(WORK/'teacher-audio-qa-qwen.json').write_text(json.dumps(dict(passed=all(x['passed'] for x in results),lesson_sha256=digest(WORK/'lesson.json'),model='checksum-cached large-v3 and large-v3-turbo; per-clip provenance',clips=results,human_audition=False),indent=2));print('DONE',all(x['passed'] for x in results),flush=True)
