"""New native German Qwen identity + measured 12%-slower first-pass derivatives."""
import sys,json,os,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper');import gff_tts_pipeline as t
from gff_reading_teacher import load,save,digest,ffmpeg_path
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/reading-teacher-elternabend';OUT=WORK/'narrator-mature-qwen';OUT.mkdir(exist_ok=True)
TEXT='Guten Abend, liebe Eltern. Schön, dass Sie heute da sind. Ich möchte Ihnen einen Überblick darüber geben, wie wir in unserer Klasse lernen und was für den Schulalltag wichtig ist.'
STYLE='Eine erfahrene deutsche Lehrerin, etwa fünfzig Jahre alt, mit einer deutlich reifen, tiefen Altstimme. Muttersprachliches Hochdeutsch. Voller, geerdeter Brustklang, dunkle warme Resonanz, leicht raue natürliche Stimmtextur. Erwachsen, souverän, freundlich und sachlich interessiert. Sie erklärt Eltern etwas im ruhigen Gespräch, mit klarer natürlicher Betonung und normalem Sprechtempo. Keine hohe, helle, mädchenhafte oder kindliche Stimme. Keine künstlich fröhliche singende Satzmelodie, keine Cartoonstimme, kein Flüstern, kein übertriebenes Lächeln. Natürliches erwachsenes Gespräch, wach und engagiert, nicht schläfrig. Saubere Nahaufnahme ohne Hall.'
ref=OUT/'reference.wav'
if not ref.exists():
 model=t.load_model(str(t.VOICE_DESIGN_SNAPSHOT));t.mx.random.seed(4518);np.random.seed(4518)
 info=t.save_generation(model,ref,text=TEXT,lang_code='German',instruct=STYLE,temperature=.7,top_k=50,top_p=.95,repetition_penalty=1.1);t.release_model(model)
 save(OUT/'reference.json',dict(text=TEXT,style=STYLE,synthetic=True,human_approved=False,**info))
rows=load(WORK/'source/persisted-pedagogy-en.json')['sentences'];model=t.load_model(str(t.BASE_SNAPSHOT))
try:
 for row in ([rows[i] for i in [15,16,17,18]] if '--sample' in sys.argv else rows):
  i=row['sentence_index'];path=OUT/'regular'/f'{i:03d}.wav';path.parent.mkdir(exist_ok=True);receipt=path.with_suffix('.json');text=row['sentence_text']
  if not(path.exists() and receipt.exists() and load(receipt)['reference_sha256']==digest(ref) and load(receipt)['text']==text and load(receipt)['audio_sha256']==digest(path)):
   seed=4510+i;t.mx.random.seed(seed);np.random.seed(seed)
   info=t.save_generation(model,path,text=text,lang_code='German',ref_audio=str(ref),split_pattern='',temperature=.7,top_k=50,top_p=.95,repetition_penalty=1.5)
   info['conditioning']='approved reference speaker embedding'
   save(receipt,dict(text=text,reference_sha256=digest(ref),audio_sha256=digest(path),generation=info))
  slow=OUT/'slow'/path.name;slow.parent.mkdir(exist_ok=True);ffmpeg=ffmpeg_path()
  subprocess.run([str(ffmpeg),'-v','error','-y','-i',str(path),'-af','atempo=0.88','-ar','24000','-ac','1','-c:a','pcm_s16le',str(slow)],check=True,env=dict(os.environ,DYLD_LIBRARY_PATH=str(ffmpeg.parent)))
  save(slow.with_suffix('.json'),dict(text=text,source_audio_sha256=digest(path),audio_sha256=digest(slow),rate=.88,method='pitch-preserving atempo'))
  print('German narrator',i,flush=True)
finally:t.release_model(model)
save(OUT/('sample-manifest.json' if '--sample' in sys.argv else 'manifest.json'),dict(source_id='reading_elternabend_seed_de',source_hash=load(WORK/'lesson.json')['source_hash'],reference_sha256=digest(ref),model_revision=str(t.BASE_SNAPSHOT),voice_design_revision=str(t.VOICE_DESIGN_SNAPSHOT),synthetic=True,reference_human_approved=True,full_audio_human_audition=False,approved_sample="mature-voice-sample.mp4",sentences=4 if '--sample' in sys.argv else 137,rate_first=.88,rate_second=1.0))
