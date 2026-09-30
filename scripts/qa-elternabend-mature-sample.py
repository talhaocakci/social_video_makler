import sys,json,time
from pathlib import Path
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper');import validate_gff_audio as v
from gff_reading_teacher import load,save,digest
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/reading-teacher-elternabend';OUT=WORK/'narrator-mature-qwen';QA=OUT/'qa';QA.mkdir(exist_ok=True)
model=v.WhisperModel(str(v.MODELS['large-v3']['path']),device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True);secondary=None;results=[]
for row in [load(WORK/'source/persisted-pedagogy-en.json')['sentences'][i] for i in [15,16,17,18]]:
 i=row['sentence_index'];p=OUT/'regular'/f'{i:03d}.wav';report=QA/f'{i:03d}.json'
 while not p.with_suffix('.json').exists():time.sleep(3)
 if report.exists() and load(report)['audio_sha256']==digest(p):r=load(report)
 else:
  r=v.transcribe(model,str(p),'de');r.update(v.score(row['sentence_text'],r['text'],language='de'));r['audio_quality']=v.inspect_audio(str(p),str(i),source_word_count=len(row['sentence_text'].split()));r.update(sentence=i,source_text=row['sentence_text'],audio_sha256=digest(p))
  if not r['passed']:
   if secondary is None:secondary=v.WhisperModel(str(v.MODELS['large-v3-turbo']['path']),device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
   q=v.transcribe(secondary,str(p),'de');q.update(v.score(row['sentence_text'],q['text'],language='de'));r['secondary']=q;r['passed']=r['passed'] or q['passed']
  r['passed']=r['passed'] and r['audio_quality']['passed'];save(report,r)
 results.append(r);print('Narrator QA',i,r['passed'],flush=True)
save(OUT/('qa-tail.json' if len(sys.argv)>1 else 'sample-qa.json'),dict(passed=all(x['passed'] for x in results),reference_sha256=digest(OUT/'reference.wav'),source_hash=load(WORK/'lesson.json')['source_hash'],clips=results,human_audition=False))
print('Narrator QA DONE',all(x['passed'] for x in results),flush=True)
