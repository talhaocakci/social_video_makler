"""Complete sentence-by-sentence teaching layer from persisted English pedagogy."""
from elternabend_radio import beat
NOTES={
2:('Überblick','An overview gives you the main points, without every detail. It sets out what this meeting will cover.'),
4:('Vorstellen. Stelle. Vor.','The verb means to introduce or present. In this main clause it separates: the main verb takes second position, and the prefix comes at the end.'),
13:('Hort. Im Hort.','This is care for schoolchildren outside lessons, rather than preschool kindergarten. The noun is masculine. The phrase combines in with the dative article dem.'),
14:('Zuständig. Zuständig für.','This tells you who is responsible for a matter. To name that matter, use für followed by the accusative.'),
15:('Müssen. Abgeholt werden.','The children receive the action: someone must collect them. The modal verb expresses obligation, and the passive infinitive comes at the end.'),
16:('Damit. Sein können.','Why keep to the time? So that the staff can reach their groups. The purpose clause has its own subject, and its finite modal verb comes last.'),
23:('Falls noch etwas fehlt.','This means if anything is missing. It introduces a possible situation, rather than asking whether it is true. The finite verb ends the subordinate clause.'),
28:('Nachhilfe.','This is targeted extra teaching. Homework supervision gives working time and help, but does not promise systematic tutoring.'),
35:('Die zum jeweiligen Lernstand passen.','The relative clause tells you which tasks: ones suited to the learning level. The pronoun refers to the plural tasks and is the subject. The verb comes last.'),
53:('Aufgreifen.','Here, the teacher returns to learning foundations. The topic is an accusative object. With the modal verb, the full infinitive stays together at the end.'),
60:('Gelegentlich.','From time to time. It does not mean every day, and it does not give a fixed weekly schedule.'),
61:('Zu erledigen ist.','What must be done. Here, the construction expresses necessity. In this embedded clause, the finite verb follows the infinitive phrase.'),
69:('Jemanden mit etwas überschütten.','The image is giving someone far too much homework. The person takes the accusative; the excessive thing follows mit with the dative.'),
71:('Anzupassen.','To adjust. The teacher changes the tasks based on feedback. This is a separable verb, so the infinitive marker zu goes inside it, between the prefix and the verb.'),
87:('Wer mehr erzählen möchte und kann.','Anyone who wants and is able to tell more. This is not a question. The relative clause ends with the modal verbs; the main clause then starts with its verb.'),
93:('Gesprächsrunde. In der.','A discussion circle in which something happens. The pronoun refers to the feminine noun. Because in describes the setting here, the relative pronoun takes the dative.'),
95:('Einander. Zuhören.','One another: the listening is mutual. The listening verb takes the dative, while the reciprocal word itself keeps the same form.'),
99:('Berücksichtigen.','To take into account. Here, allergies affect the food decision. The verb takes a direct accusative object, without a preposition.'),
100:('Keine Voraussetzung. Voraussetzung für.','Not a requirement. To name what requires something, use für with the accusative. The negative removes the obligation.'),
105:('Bestätigen.','To confirm. But confirm what? Here, that the message has been read, rather than agreement with it. The following clause specifies the confirmed fact.'),
112:('Reicht nicht aus.','Is not sufficient. The verb separates in the main clause. The phrase with für names the purpose, and the negative says the action does not meet that requirement.'),
113:('Schriftliche Entschuldigung.','A written absence note. Here, the familiar apology word means a document explaining a pupil’s absence. The adjective meaning written makes that clear.'),
114:('Beurlaubung.','Permission to miss lessons for a limited period. Here it is requested in advance. That is different from notifying the office that a child is ill.'),
115:('Vorübergehend.','Temporarily. The absence is limited in duration, but this word alone does not specify an end date.'),
118:('Bezugsperson.','A familiar trusted person who provides reliable support. Here it describes the educator’s relationship with the children, rather than an administrative contact.'),
121:('Werden von externen Anbietern durchgeführt.','Are run by external providers. The passive focuses on the activities. The phrase with von and the dative names who runs them; the past participle comes at the end.'),
123:('Klassenkasse.','The class fund: money pooled for shared class expenses. The sentence names materials and trips. It does not mean a shop’s till.'),
125:('Nachvollziehen.','To understand by following the details. Here, parents can follow the spending and balance. That means understandable information, rather than approval of the spending.')}
def enrich_all(lesson,rows):
 def reading(i):return dict(kind='reading',sentence=i)
 def teacher(i):
  ped=rows[i]['pedagogic'];points=sum((ped[k] for k in ['important_words','important_phrases','grammar']),[])
  meaning=ped['sentence_meaning'];beats=[beat(meaning,pause=.25)]
  if i in NOTES:
   term,explanation=NOTES[i];beats += [beat(term,'German',.15),beat(explanation)]
  if i==100:beats += [beat('Das Verteilen.','German',.15),beat('The activity of distributing. The infinitive becomes a neuter noun, with a capital letter. Here, that whole activity is the object: the cake makes distributing easier.')]
  notes=[dict(kind=p['kind'],term=p['term'],meaning=p['meaning'],explanation=p['explanation'],point_id=p['point_id'],form=p['form_in_sentence']) for p in points]
  focus=next((p['form_in_sentence'] for p in points if p['form_in_sentence'] in rows[i]['sentence_text']),'')
  return dict(kind='teacher',key=f'sentence-{i:03d}',sentence=i,text=' '.join(b['text'] for b in beats),speech_beats=beats,title='Meaning in context',body=meaning,focus=focus,pedagogy_refs=[p['point_id'] for p in points],teaching_notes=notes,sentence_meaning=meaning)
 for v in lesson['variants']:
  old=v['scenes'];intro=old[0];outro=old[-1];scenes=[intro]
  questions={s['sentence']:s for s in old if s.get('key','').startswith('c-question')}
  if v['treatment']=='cinema':
   scenes += [reading(i) for i in range(137)]
   bridge=next(s for s in old if s.get('key')=='b-return');bridge['text']='Now let’s work through the meeting sentence by sentence. We’ll check each meaning and briefly unpack the useful language notes.';bridge['speech_beats']=[beat(bridge['text'])];scenes.append(bridge)
  for i in range(137):
   scenes.append(reading(i))
   if i in questions:
    scenes.append(questions[i]);scenes.append(dict(kind='pause',sentence=i,duration=3,title='Your turn',body=questions[i]['body'],focus=questions[i]['focus'],pedagogy_refs=[]))
   scenes.append(teacher(i))
  scenes.append(outro);v['scenes']=scenes
 lesson['scope']='all 137 sentence meanings and all 29 persisted vocabulary/grammar points; brief teacher after every sentence in guided sequence'
 return lesson
