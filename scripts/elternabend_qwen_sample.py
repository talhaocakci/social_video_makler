"""Local Qwen teacher audition: one synthetic identity, deliberate teaching beats."""
import sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper')
import gff_tts_pipeline as t
from mlx_audio.audio_io import read,write
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/reading-teacher-elternabend/qwen-teacher-sample'
ref_text="Let's take this one step at a time. There is a small difference here, but it matters. What is the teacher actually asking the parents to confirm? Think about that for a moment. Then we will look at the sentence together."
style="A native English-speaking adult woman, a warm experienced language teacher speaking to one adult learner. Warm low-mid register, relaxed human conversational phrasing, unhurried pace around 125 words per minute. Thoughtful pauses between ideas. Gently emphasize meaningful contrasts. Ask questions with genuine curiosity and a natural questioning intonation. Never a newsreader, sales presenter, exaggerated performer, or flat text reader. Clean close-mic audio."
beats=[
("Let's stop here for a moment. Look at the underlined word. The teacher is asking for a signature.",.9,'Calm invitation to notice something; unhurried and conversational.'),
("But what does that signature confirm? That you have read the message? Or that you agree with it?",3.5,'Ask with genuine curiosity. Give each alternative its own phrase. Stress read and agree as the contrast.'),
("Here, it confirms that you have read it. The sentence does not say you agree. That's the important distinction.",1.2,'A gentle answer reveal. Give read and agree clear contrastive stress; pause after the answer, without sounding theatrical.'),
("So, when you see a word meaning confirm, don't stop at the word itself. Look at what comes next. What, exactly, is being confirmed?",1.0,'Slow, encouraging explanation, then a thoughtful open question. Let exactly stand out naturally.')]
ref=OUT/'teacher-reference.wav';receipt={'engine':'local Qwen3-TTS','synthetic_identity':True,'human_audition':False,'style':style,'reference_text':ref_text,'beats':[]}
if not ref.exists():
 model=t.load_model(str(t.VOICE_DESIGN_SNAPSHOT));t.mx.random.seed(731);np.random.seed(731)
 receipt['reference']=t.save_generation(model,ref,text=ref_text,lang_code='English',instruct=style,temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.1)
 t.release_model(model)
model=t.load_model(str(t.BASE_SNAPSHOT));audio=[]
for i,(text,pause,direction) in enumerate(beats):
 path=OUT/f'beat-{i}.wav';t.mx.random.seed(740+i);np.random.seed(740+i)
 info=t.save_generation(model,path,text=text,lang_code='English',ref_audio=str(ref),ref_text=ref_text,instruct=style+' '+direction,split_pattern='',temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.5)
 samples,sr=read(str(path));audio.append(np.asarray(samples));audio.append(np.zeros(round(sr*pause),dtype=np.float32));receipt['beats'].append(dict(text=text,pause_after_seconds=pause,direction=direction,**info));print('generated beat',i,flush=True)
t.release_model(model)
write(str(OUT/'teacher-sample.wav'),np.concatenate(audio),sr,format='wav')
receipt['sample_sha256']=t.sha256_file(OUT/'teacher-sample.wav');receipt['duration_seconds']=sum(len(x) for x in audio)/sr
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2));print('DONE',receipt['duration_seconds'],flush=True)
