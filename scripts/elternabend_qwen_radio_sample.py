"""Local Qwen teacher audition: one synthetic identity, deliberate teaching beats."""
import sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper')
import gff_tts_pipeline as t
from mlx_audio.audio_io import read,write
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'work/reading-teacher-elternabend/qwen-radio-sample';OUT.mkdir(parents=True,exist_ok=True)
ref_text="Here's an interesting distinction. You sign a message from school. Does that mean you've read it, or that you agree with it? Those are two different things! Let's listen to what the teacher actually says."
style="An adult female language teacher with a bright, warm, engaged conversational voice and a clear medium register. She sounds like an excellent educational radio host talking to one interested adult, not reading a script. Natural lively pace, varied melodic intonation, crisp consonants, curious questions, confident explanation. Give meaningful contrasts light vocal emphasis. Alert and inviting, never breathy, sleepy, solemn, exaggerated or sales-like. Clean close-mic recording."
beats=[
("Bestätigen.",.18,'German','Pronounce this German verb clearly and naturally, with lively explanatory intent.'),
("To confirm. A familiar idea, right? But here is the interesting part: what are you confirming when you sign that message from school?",.45,'English','Engaged conversational opening; genuine curiosity on the final question.'),
("That you have read it? Or that you agree with it?",1.35,'English','Two genuinely distinct alternatives. Contrast read with agree. Curious, alert, not an exam announcer.'),
("Here, you are confirming that you have read it. Agreement? The sentence does not say that. So a signature can acknowledge a message without saying yes to its contents.",.4,'English','Clear confident answer reveal. Stress read and the contrast with agreement. Friendly conversational energy.'),
("That's why the words after bestätigen matter. Don't just translate the verb and move on. Ask yourself: confirm what? In this example, that the message has been read.",.35,'English','Explain as an engaged radio teacher. German bestätigen pronounced carefully. Natural emphasis on confirm what; settle the final answer clearly.')]
ref=OUT/'teacher-reference.wav';receipt={'engine':'local Qwen3-TTS','synthetic_identity':True,'human_audition':False,'style':style,'reference_text':ref_text,'beats':[]}
if not ref.exists():
 model=t.load_model(str(t.VOICE_DESIGN_SNAPSHOT));t.mx.random.seed(931);np.random.seed(931)
 receipt['reference']=t.save_generation(model,ref,text=ref_text,lang_code='English',instruct=style,temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.1)
 t.release_model(model)
model=t.load_model(str(t.BASE_SNAPSHOT));audio=[]
source=Path('/Users/talhaocakci/Projects/contentpub_io_react_native/outputs/elternabend-seed-de/audio/sentences/105.wav')
x,sr=read(str(source));audio.extend([np.asarray(x),np.zeros(round(sr*.55),dtype=np.float32)]);receipt['opening_source_audio_sha256']=t.sha256_file(source)
for i,(text,pause,language,direction) in enumerate(beats):
 path=OUT/f'beat-{i}.wav';t.mx.random.seed(940+i);np.random.seed(940+i)
 info=t.save_generation(model,path,text=text,lang_code=language,ref_audio=str(ref),ref_text=ref_text,instruct=style+' '+direction,split_pattern='',temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.5)
 samples,sr=read(str(path));audio.append(np.asarray(samples));audio.append(np.zeros(round(sr*pause),dtype=np.float32));receipt['beats'].append(dict(text=text,language=language,pause_after_seconds=pause,direction=direction,**info));print('generated beat',i,flush=True)
t.release_model(model)
write(str(OUT/'teacher-sample.wav'),np.concatenate(audio),sr,format='wav')
receipt['sample_sha256']=t.sha256_file(OUT/'teacher-sample.wav');receipt['duration_seconds']=sum(len(x) for x in audio)/sr
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2));print('DONE',receipt['duration_seconds'],flush=True)
