"""Screen-independent teaching scripts and approved local Qwen delivery."""
import hashlib,json,sys
from pathlib import Path
from gff_reading_teacher import save,load,digest,pcm,wav,RATE
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/reading-teacher-elternabend';OUT=WORK/'teacher-audio-qwen'
REFERENCE=WORK/'qwen-radio-sample/teacher-reference.wav'
APPROVED=load(WORK/'qwen-radio-sample/receipt.json')
STYLE=APPROVED['style'];REF_TEXT=APPROVED['reference_text']
DIRECTION='Speak to one interested adult with warm radio-host energy. Keep a natural conversational pace. Give contrasts light emphasis and questions genuine curiosity. No drawn-out syllables.'
# English is self-contained after the explicitly spoken German expression.
NOTES={
2:("Überblick.","An overview. Imagine arriving at a parents' evening with a dozen questions. Are you about to get every tiny detail?", "No, just the main points for now. The teacher is giving you the big picture. That's a useful listening cue: follow the main topics first, then collect the details as they come.","Remember how the meeting began? An overview sets up the main points. It helps you organize what follows, without promising every detail."),
13:("Hort.","Care for schoolchildren outside lesson hours. You might hear a childcare word and think: kindergarten?", "Here, it's care for children who are already at school. And there's a practical detail: this school requires a contract for that service. So remember both parts: the care, and the paperwork.","Let's connect that childcare word to the meeting. It means supervised care outside lessons, for schoolchildren. It isn't preschool kindergarten. At this school, that service needs a contract."),
15:("Abgeholt werden.","Be collected. Who is doing the collecting here? The children?", "No, someone must collect the children. They receive the action. Add the German modal verb müssen, and it becomes an obligation: they must be collected. The time given is this school's arrangement.","The collection rule is a useful example of the passive. Someone collects the children; the children are collected. With müssen, collection is required. The time in the reading belongs to this school."),
28:("Nachhilfe.","Extra tutoring. Now, is having someone supervise homework the same as getting targeted extra teaching?", "Not necessarily. The reading makes that distinction. Homework supervision gives children working time and support. It doesn't promise systematic teaching to address learning difficulties. That's what extra tutoring would add.","Think back to homework supervision. The school draws a boundary: time and support for homework, without promising systematic extra tutoring. Those are different services, even though both can help with schoolwork."),
60:("Gelegentlich.","From time to time. So, should you put this in the diary for every Monday?", "The word doesn't give you a fixed schedule. It means occasionally. You know it happens sometimes, but not exactly how often. Small frequency words can change what you expect just as much as a date or a number.","In the homework section, this means from time to time. It leaves the frequency open. You can't turn it into a promise of something happening daily or every week."),
69:("Überschütten.","To shower someone with something. Here, the something is homework! Can you picture that?", "It's a vivid way to talk about giving someone far too much. Nobody is literally pouring anything. The image helps you feel the excessive amount, and understand the teacher's intention.","The homework image is figurative: showering someone with far too much. Connect the person receiving it with what they're receiving. In this sentence, it's an excessive amount of homework."),
95:("Einander.","One another. Let's think about listening. Is it only the children listening to the teacher?", "This word makes the action mutual: they listen to one another. Listening goes both ways. That fits the discussion circle, where everyone has a part. One small word tells you something important about the group.","In the discussion circle, listening is mutual. The participants listen to one another. It isn't just a one-way instruction to listen to the teacher. Everyone has a part in the exchange."),
100:("Keine Voraussetzung.","Not a requirement. A cake that's already cut into portions sounds helpful, doesn't it? But is it compulsory?", "No. The teacher says it isn't a requirement for a lovely celebration. Helpful and required are two different things. The little negative word, keine, removes the requirement. That's the detail to keep.","Remember the birthday cake? Already portioned is helpful, but it isn't required. The negative word removes a condition. So don't turn a helpful suggestion into an obligation."),
105:("Bestätigen.","To confirm. A familiar idea, right? But here is the interesting part: what are you confirming when you sign that message from school?", "Here, you are confirming that you have read it. Agreement? The sentence does not say that. So a signature can acknowledge a message without saying yes to its contents.","Let's return to the signature. Confirm what, exactly? That the message has been read. The sentence doesn't say you agree with it. The words after the verb tell you what the signature confirms."),
113:("Eine schriftliche Entschuldigung.","A written absence note. You may know Entschuldigung as something you say when you apologize. Is the teacher asking someone to say sorry here?", "Here, the school needs a note explaining a pupil's absence. Schriftlich means written. That adjective and the school situation help you choose the right meaning. A familiar word can do a different job in a different setting.","The school asks for a written absence note. The familiar apology word has a document meaning here. Schriftlich means written, and the context is a pupil's absence. Together, those clues make the request clear."),
123:("Klassenkasse.","The class fund. Does that mean a shop's cash register?", "Here, it means money pooled for the class. The reading gives you two examples of what it's for: materials and trips. Those examples make the compound concrete. Shared money, for shared class expenses.","Near the end, we heard about pooled money for the class. Materials and trips are the examples in the sentence. They tell us that this is a class fund, rather than a shop's till.")}
QUESTIONS={13:'Does Hort mean preschool kindergarten, or care for schoolchildren outside lessons?',15:'Are the children collecting someone, or is someone collecting the children?',28:'Does homework supervision promise Nachhilfe: systematic extra tutoring?',95:'With einander, does listening go one way, or both ways?',105:'Does the signature confirm that you have read the message, or that you agree with it?',113:'Is a schriftliche Entschuldigung a spoken apology, or a written note about an absence?'}
def beat(text,language='English',pause=.3,direction=DIRECTION):return dict(text=text,language=language,pause_after_seconds=pause,direction=direction)
def enrich(lesson):
 for variant in lesson['variants']:
  mode=variant['id'][:2]
  for s in variant['scenes']:
   if s['kind']=='pause':s['duration']=3.0;continue
   if s['kind']!='teacher':continue
   key=s['key'];i=s['sentence']
   if key.endswith('intro'):
    text={'01':"Welcome to a German parents' evening. What does the school offer, and what do parents need to do? Let's find out. You'll hear the whole reading in German, and I'll join you in English at a few useful moments. These arrangements belong to the school in this reading.", '02':"Let's join a German parents' evening. First, you'll hear the whole meeting. Keep three things in mind: daily arrangements, learning, and communication with parents. Then we'll come back to some useful expressions together. You don't need to catch every detail on the first listen.",'03':"Ready to join a German parents' evening? You'll hear the complete reading, with a few questions from me along the way. Try an answer to yourself, then we'll unpack the meaning. Listen for what's offered, what's required, and what's simply helpful."}[mode]
    beats=[beat(text)]
   elif key.endswith('outro'):beats=[beat("That's the complete reading. Before we finish, pick one school word you want to remember. Can you explain it in your own words?" ,pause=1.2),beat("You can keep practising with this Elternabend reading in Get Fluent Fast. The lesson link takes you to the reading, and if you're watching the video, you can also scan its QR code. Thanks for listening!")]
   elif key=='b-return':beats=[beat("Now we've heard the whole meeting. Let's go back to a few moments where one expression makes a real difference. You'll hear each sentence again, then we'll unpack it together.")]
   else:
    term,opening,answer,recap=NOTES[i]
    if key.startswith('c-question'):
     beats=[beat(term,'German',.18),beat(QUESTIONS[i])];s['body']=QUESTIONS[i]
    elif key.startswith('c-'):beats=[beat(term,'German',.18),beat(answer)]
    elif key.startswith('b-'):beats=[beat(term,'German',.18),beat(recap)]
    elif i==105:beats=[{k:b[k] for k in ('text','language','pause_after_seconds','direction')} for b in APPROVED['beats']]
    else:beats=[beat(term,'German',.18),beat(opening,pause=.65),beat(answer)]
   s['speech_beats']=beats;s['text']=' '.join(b['text'] for b in beats)
 lesson['teacher_voice']=dict(engine='local Qwen3-TTS-12Hz-1.7B-Base-bf16',synthetic=True,reference_audio=str(REFERENCE),reference_sha256=digest(REFERENCE),approved_sample_sha256=APPROVED['sample_sha256'],user_approved_sample=True,full_audio_human_audition=False,style=STYLE,reference_text=REF_TEXT,tempo_processing='none')
 return lesson

def beat_reference(b):return WORK/'narrator-mature-qwen/reference.wav' if b['language']=='German' else REFERENCE
def identity(b):return hashlib.sha256(json.dumps(dict(beat=b,reference=digest(beat_reference(b)),style=STYLE,engine='Qwen3-TTS-12Hz-1.7B-Base-bf16',temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.5),sort_keys=True).encode()).hexdigest()
def audio(lesson):
 import numpy as np
 sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper');import gff_tts_pipeline as t
 OUT.mkdir(exist_ok=True);cache=OUT/'beats';cache.mkdir(exist_ok=True)
 model=None
 try:
  for variant in lesson['variants']:
   for s in variant['scenes']:
    if s['kind']!='teacher':continue
    chunks=[];receipts=[]
    for b in s['speech_beats']:
     h=identity(b);p=cache/(h+'.wav');r=p.with_suffix('.json')
     if not(p.exists() and r.exists() and load(r)['audio_sha256']==digest(p)):
      # Preserve the exact approved performance wherever its beat is reused.
      approved=next((x for x in APPROVED['beats'] if b['language']=='English' and all(b[k]==x[k] for k in b)),None)
      if approved:
       import shutil
       shutil.copy2(approved['path'],p);info=dict(reused_approved_sample=True)
      else:
       if model is None:model=t.load_model(str(t.BASE_SNAPSHOT))
       seed=int(h[:7],16);t.mx.random.seed(seed);np.random.seed(seed)
       ref_text=load(WORK/'narrator-mature-qwen/reference.json')['text'] if b['language']=='German' else REF_TEXT
       try:
        info=t.save_generation(model,p,text=b['text'],lang_code=b['language'],ref_audio=str(beat_reference(b)),ref_text=ref_text if b['language']=='English' else None,instruct=STYLE+' '+b['direction'],split_pattern='',temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.5)
       except RuntimeError as e:
        if b['language']!='German' or 'no audio' not in str(e):raise
        t.mx.random.seed(seed);np.random.seed(seed)
        info=t.save_generation(model,p,text=b['text'],lang_code='German',ref_audio=str(beat_reference(b)),split_pattern='',temperature=.75,top_k=50,top_p=.95,repetition_penalty=1.5)
        info['conditioning']='reference speaker embedding; empty ICL fallback'
      save(r,dict(**b,identity=h,audio_sha256=digest(p),generation=info))
     chunks.extend([pcm(p),b'\0'*(round(b['pause_after_seconds']*RATE)*2)]);receipts.append(dict(identity=h,audio_sha256=digest(p)))
    p=OUT/(s['key']+'.wav');wav(p,b''.join(chunks));save(p.with_suffix('.json'),dict(text=s['text'],beats=receipts,audio_sha256=digest(p),reference_sha256=digest(REFERENCE)))
    print('teacher Qwen complete',s['key'],flush=True)
 finally:
  if model is not None:t.release_model(model)
