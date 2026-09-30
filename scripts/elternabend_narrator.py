"""New native German Qwen identity + measured 12%-slower first-pass derivatives."""
import sys,json,os,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper');import gff_tts_pipeline as t
from gff_reading_teacher import load,save,digest,ffmpeg_path
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/reading-teacher-elternabend';OUT=WORK/'narrator-qwen';OUT.mkdir(exist_ok=True)
TEXT='Guten Abend, liebe Eltern. Schön, dass Sie heute da sind. Ich möchte Ihnen einen Überblick darüber geben, wie wir in unserer Klasse lernen und was für den Schulalltag wichtig ist.'
STYLE='Eine erwachsene deutsche Lehrerin, Muttersprachlerin mit natürlichem Hochdeutsch. Warme, klare, lebendige Stimme in mittlerer Lage. Sie spricht freundlich zu Eltern bei einem Elternabend, mit natürlichem Gesprächsfluss, abwechslungsreicher Satzmelodie und sinnvoller Betonung. Angenehmes normales Sprechtempo, präzise aber nicht überdeutliche Aussprache. Wach, interessiert und zugewandt, nicht schläfrig oder monoton. Keine Werbestimme, keine dramatische Schauspielerei. Saubere Nahaufnahme ohne Hall.'
ref=OUT/'reference.wav'
if not ref.exists():
 model=t.load_model(str(t.VOICE_DESIGN_SNAPSHOT));t.mx.random.seed(1715);np.random.seed(1715)
 info=t.save_generation(model,ref,text=TEXT,lang_code='German',instruct=STYLE,temperature=.7,top_k=50,top_p=.95,repetition_penalty=1.1);t.release_model(model)
 save(OUT/'reference.json',dict(text=TEXT,style=STYLE,synthetic=True,human_approved=False,**info))
rows=load(WORK/'source/persisted-pedagogy-en.json')['sentences'];model=t.load_model(str(t.BASE_SNAPSHOT))
try:
 for row in rows:
  i=row['sentence_index'];path=OUT/'regular'/f'{i:03d}.wav';path.parent.mkdir(exist_ok=True);receipt=path.with_suffix('.json');text=row['sentence_text']
  if not(path.exists() and receipt.exists() and load(receipt)['reference_sha256']==digest(ref) and load(receipt)['text']==text and load(receipt)['audio_sha256']==digest(path)):
   t.mx.random.seed(2000+i);np.random.seed(2000+i)
   info=t.save_generation(model,path,text=text,lang_code='German',ref_audio=str(ref),ref_text=TEXT,instruct=STYLE,split_pattern='',temperature=.7,top_k=50,top_p=.95,repetition_penalty=1.5)
   save(receipt,dict(text=text,reference_sha256=digest(ref),audio_sha256=digest(path),generation=info))
  slow=OUT/'slow'/path.name;slow.parent.mkdir(exist_ok=True);ffmpeg=ffmpeg_path()
  subprocess.run([str(ffmpeg),'-v','error','-y','-i',str(path),'-af','atempo=0.88','-ar','24000','-ac','1','-c:a','pcm_s16le',str(slow)],check=True,env=dict(os.environ,DYLD_LIBRARY_PATH=str(ffmpeg.parent)))
  save(slow.with_suffix('.json'),dict(text=text,source_audio_sha256=digest(path),audio_sha256=digest(slow),rate=.88,method='pitch-preserving atempo'))
  print('German narrator',i,flush=True)
finally:t.release_model(model)
save(OUT/'manifest.json',dict(source_id='reading_elternabend_seed_de',source_hash=load(WORK/'lesson.json')['source_hash'],reference_sha256=digest(ref),model_revision=str(t.BASE_SNAPSHOT),voice_design_revision=str(t.VOICE_DESIGN_SNAPSHOT),synthetic=True,human_approved=False,sentences=137,rate_first=.88,rate_second=1.0))
