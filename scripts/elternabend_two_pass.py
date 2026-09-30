"""Teach new useful language once, then listen again at regular speed."""
from gff_reading_teacher import load,save,digest
from elternabend_radio import beat,REFERENCE,STYLE,REF_TEXT,APPROVED
from elternabend_audio_first import speech
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WORK=ROOT/'work/reading-teacher-elternabend'
SELECTED=[2,4,13,14,15,16,23,28,35,53,60,61,69,71,87,95,99,100,105,112,113,114,115,118,123,125]
def author(rows,ped):
 def t(key,i,beats,title,body,focus='',refs=[],notes=[]):return dict(kind='teacher',key=key,sentence=i,text=' '.join(b['text'] for b in beats),speech_beats=beats,title=title,body=body,focus=focus,pedagogy_refs=refs,teaching_notes=notes)
 def read(i,pace):return dict(kind='reading',sentence=i,pace=pace,pass_label='First pass · 12% slower' if pace=='slow' else 'Second pass · Regular speed')
 def note(i):
  p=rows[i]['pedagogic'];points=sum((p[k] for k in ['important_words','important_phrases','grammar']),[])
  beats=speech(i)
  notes=[dict(kind=x['kind'],term=x['term'],meaning=x['meaning'],explanation=x['explanation'],point_id=x['point_id'],form=x['form_in_sentence']) for x in points]
  focus=next((x['form_in_sentence'] for x in points if x['form_in_sentence'] in rows[i]['sentence_text']),'')
  return t(f'first-use-{i}',i,beats,points[0]['term'],p['sentence_meaning'],focus,[x['point_id'] for x in points],notes)
 variants=[]
 for id,title,treatment in [('01-close-reading','Guided reading · Two listens','paper')]:
  intro='Walking into a parents’ evening in German can feel like a lot to take in. Let’s listen together, so the school’s plans and requests feel easier to follow. We’ll start a little more gently, with short explanations when a useful word or structure comes up. Then you can enjoy the whole meeting again at its usual pace.'
  if treatment=='cinema':intro='First, listen to the complete German parents’ evening at a slightly gentler pace. Then we’ll briefly revisit useful new language. Finally, listen again at regular speed, without interruptions.'
  if treatment=='workshop':intro='Let’s join a German parents’ evening. I’ll explain useful new language as it appears, with a few short practice checks after the explanation. Our first listen is slightly gentler. The second is at regular speed, without interruptions.'
  scenes=[t(id+'-intro',0,[beat(intro)],title,'Feel more at home at your next parents’ evening')]
  for i in range(137):
   scenes.append(read(i,'slow'))
   if treatment!='cinema' and i in SELECTED:
    scenes.append(note(i))
    if treatment=='workshop' and i in [15,60,105]:
     questions={15:'Try the same passive pattern with an application: the application must be submitted by Friday. How would you say that in German?',60:'If something happens occasionally, can you infer a fixed weekly schedule?',105:'Suppose you sign to confirm that you have read a message. Does that alone establish agreement with its contents?'}
     answers={15:[beat('Der Antrag muss bis Freitag eingereicht werden.','German',.15),beat('The modal verb comes early; the past participle and werden finish the clause. It is the same passive pattern for a different requirement.')],60:[beat('No fixed schedule is specified. Occasionally tells you that it happens from time to time.')],105:[beat('No. Reading and agreement are different. You need to check exactly what the signature is confirming.')]}
     scenes.append(t(f'apply-question-{i}',i,[beat(questions[i])],'Try the pattern' if i==15 else 'Check the implication',questions[i]))
     scenes.append(dict(kind='pause',sentence=i,duration=3,title='Take a moment',body=questions[i],focus='',pedagogy_refs=[]))
     scenes.append(t(f'apply-answer-{i}',i,answers[i],'Practice check','Same structure · new context' if i==15 else 'Check what the sentence actually establishes'))
  if treatment=='cinema':
   scenes.append(t('story-language-bridge',2,[beat('Let’s revisit the useful language now. You’ll hear the relevant sentences again, then a brief explanation of each new word or structure.')],'Useful new language','Brief contextual explanations'))
   for i in SELECTED:scenes += [read(i,'slow'),note(i)]
  scenes.append(t('regular-pass-bridge',0,[beat('Now listen to the whole reading again at regular speed. Let the sentences connect into the meeting. I’ll leave this pass uninterrupted.')],'Second pass','Regular speed · complete reading'))
  scenes += [read(i,'regular') for i in range(137)]
  scenes.append(t('two-pass-outro',136,[beat('That’s our second listen. You can continue with the original Elternabend reading in Get Fluent Fast and practise the sentences there. Use the lesson link, or scan the QR if you’re watching. Thanks for listening!')],'Continue in the app','Read, listen and practise'))
  variants.append(dict(id=id,title=title,treatment=treatment,scenes=scenes))
 lesson=dict(source_id=ped['reading_id'],source_hash=ped['source_hash'],source_revision=load(WORK/'source/primary-published.json')['updated_at'],target_language='de',guiding_language='en',cefr='B2',audio_first_policy='Each teaching stop speaks a native German anchor, gives its English meaning, and briefly connects it to the sentence; understandable without looking at the video.',scope='Two complete passes; first at 0.88x normal narration speed, second at 1.0x; 26 first-use teaching stops between relevant sentences; one paper layout; no questions or separate teaching review',word_timing='none; measured sentence audio; editorial underlines',teacher_voice=dict(engine='local Qwen3-TTS-12Hz-1.7B-Base-bf16',synthetic=True,reference_audio=str(REFERENCE),reference_sha256=digest(REFERENCE),approved_sample_sha256=APPROVED['sample_sha256'],user_approved_sample=True,full_audio_human_audition=False,style=STYLE,reference_text=REF_TEXT,tempo_processing='none'),narrator_voice=dict(engine='local Qwen3-TTS',synthetic=True,status='mature German reference approved by user in sample',human_approved=True,reference_audio=str(WORK/'narrator-mature-qwen/reference.wav'),reference_sha256=digest(WORK/'narrator-mature-qwen/reference.wav'),approved_sample='renders/reading-teacher-elternabend/mature-voice-sample.mp4'),pacing=dict(first_pass_rate=.88,second_pass_rate=1.0,method='same new German master; pitch-preserving 0.88x first-pass derivative'),variants=variants)
 return lesson
