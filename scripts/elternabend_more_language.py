"""A separate, fuller vocabulary variation; preserves the accepted lesson."""
import copy, os, shutil, sys
from pathlib import Path
import elternabend_teacher as compiler
import elternabend_radio as radio
from elternabend_audio_first import PAIRS
from elternabend_two_pass import author as base_author
from gff_reading_teacher import load, save, digest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'work/reading-teacher-elternabend'
WORK=ROOT/'work/reading-teacher-elternabend-more-language'
ID='04-more-language'
# Meanings belong to the exact source sentence, never an unrelated dictionary sense.
EXTRA={
 5:[('Zusammenarbeit.','Working together: here, parents and school supporting the children.'),('Elternvertretung.','The parent representatives, elected to speak for the parents.')],
 9:[('Unterstützen.','To support or help someone.'),('Jemandem etwas zutrauen.','To believe someone can manage something. Here, the teacher offers help while trusting each child’s abilities.')],
 10:[('Erzieherin.','An educator who looks after and supports the children.'),('Eng zusammenarbeiten.','To work closely together. The educator and teacher work as a team.')],
 11:[('Auffallen.','To catch someone’s attention. If something catches your attention, you notice it.'),('Sprechen Sie uns bitte an.','Please come and speak to us. You can bring up a question or something you’ve noticed.')],
 12:[('Sich zurechtfinden.','To find your way and get used to a new situation. At first, everyone needs time to settle in.')],
 17:[('Beachten.','To pay attention to something, or take it into account.'),('Vorher bestellt werden.','To be ordered in advance. The food needs to be ordered beforehand.')],
 18:[('Anmelden.','To register or sign someone up.'),('Mahlzeiten auswählen.','To choose the meals. Registering your child and actually selecting the food are two separate steps.')],
 20:[('Abrechnen.','To calculate and bill the cost. Scanning the card lets the meal provider charge for the food.')],
 24:[('Mitteilen.','To let someone know. Here, please tell the school about a food allergy.'),('Speiseplan.','The menu or meal plan, where you can check what food is offered.')],
 27:[('Nicht weiterkommen.','To get stuck and be unable to make progress. Here, children can ask for help with their tasks.')],
 30:[('Davon ausgehen.','To assume something is the case. Please don’t assume the homework will always be finished and free of mistakes.')],
 32:[('Vorgesehen.','Planned or intended for a particular purpose.'),('Frühbetreuung.','Early-morning childcare, for children who arrive before their lessons start.')],
 34:[('Gut aufgehoben sein.','To be in good hands: somewhere safe, with someone looking after you.')],
 40:[('Vorgegeben.','Provided in advance. The children use the supplied words to check their spelling.'),('Vergleichen.','To compare: look at two things and check how they match.')],
 41:[('Sich mit etwas beschäftigen.','To work on or spend time exploring something. Everyone works on the same topic, in different ways.')],
 44:[('Nach und nach.','Gradually, little by little.'),('Zuordnen.','To match one thing to another. Here, the children match sounds with letters.')],
 51:[('Sicher sitzen.','To be firmly learned. The basics need to be secure.'),('Darauf aufbauen.','To build on that foundation, using what the children already understand.')],
 58:[('Bescheid geben.','To let someone know. The teacher will contact you if your child is being considered for extra support.')],
 70:[('Überfordert.','Overwhelmed: finding a task too much to manage. Let the teacher know if your child is struggling like this.')],
 72:[('Federtasche.','A pencil case. This is a quick reminder to check your child’s writing supplies.')],
 76:[('Beschriften.','To label something with writing. Put your child’s name on their materials so they’re easier to identify.')],
 78:[('Miteinander umgehen.','To treat and interact with one another. Here, the children practise being kind to each other.')],
 88:[('Fortschritte machen.','To make progress. Over time, the children can see how their writing is improving.')],
 92:[('Klassenrat.','A class meeting where children talk about shared concerns.'),('Stattfinden.','To take place. This meeting happens regularly.')],
 101:[('Postmappe.','The folder for letters and messages between school and home. That’s the place to check for school notices.')],
 111:[('In Kopie setzen.','To copy someone into an email. Include the teacher as well, so they know what’s happening.')],
 117:[('Vertretung.','Cover or a replacement while someone is away. Here, another person will cover the teacher’s absence.')],
 119:[('Arbeitsgemeinschaften.','School activity groups or clubs. Here, examples include sport and theatre.')],
 124:[('Die Verwaltung übernehmen.','To take responsibility for managing something: here, looking after the class fund.'),('Einverstanden sein.','To agree or be happy with a proposal. The teacher offers to manage the money if the parents agree.')],
 129:[('Sich verzögern.','To be delayed. If the class gets back later than planned, the parent representatives can pass the news on.')],
 132:[('Im Gespräch bleiben.','To keep talking and stay in touch. The teacher wants communication with parents to continue throughout the year.')],
}
def author():
 WORK.mkdir(exist_ok=True)
 for name in ['source','narrator-mature-qwen','qwen-radio-sample']:
  if not (WORK/name).exists():(WORK/name).symlink_to(BASE/name,target_is_directory=True)
 for name in ['teacher-audio-qwen','teacher-qa-qwen']:
  if not (WORK/name).exists():shutil.copytree(BASE/name,WORK/name)
 rows=load(BASE/'source/persisted-pedagogy-en.json')['sentences']
 lesson=base_author(rows,load(BASE/'source/persisted-pedagogy-en.json'))
 v=lesson['variants'][0];v['id']=ID;v['title']='Words for your next parents’ evening'
 scenes=[]
 for s in v['scenes']:
  if s['kind']=='reading':s['pass_label']=''
  if s.get('key')=='regular-pass-bridge':s['title']='Listen once more';s['body']='Let the whole meeting come together.'
  if s.get('key')=='01-close-reading-intro':s['key']=ID+'-intro';s['title']='Let’s listen together'
  scenes.append(s)
  if s['kind']=='reading' and s['pace']=='slow' and s['sentence'] in EXTRA:
   i=s['sentence'];pairs=EXTRA[i]
   beats=[b for term,meaning in pairs for b in [radio.beat(term,'German',.12),radio.beat(meaning,pause=.2)]]
   # First pair always has a literal source anchor; inflection is stored separately.
   anchors={5:'Zusammenarbeit',9:'unterstützen',10:'Erzieherin',11:'auffällt',12:'zurechtfinden',17:'beachten',18:'Mahlzeiten',20:'abrechnen',24:'teilen Sie uns das bitte mit',27:'nicht weiterkommen',30:'davon aus',32:'vorgesehene',34:'gut aufgehoben',40:'vorgegebenen',41:'beschäftigen',44:'nach und nach',51:'sicher sitzen',58:'Bescheid',70:'überfordert',72:'Federtasche',76:'Beschriften',78:'miteinander umgehen',88:'Fortschritte',92:'Klassenrat',101:'Postmappe',111:'in Kopie',117:'Vertretung',119:'Arbeitsgemeinschaften',124:'Verwaltung übernehmen',129:'verzögert',132:'im Gespräch bleiben'}
   focus=anchors[i];assert focus in rows[i]['sentence_text']
   scenes.append(dict(kind='teacher',key=f'more-words-{i}',sentence=i,text=' '.join(b['text'] for b in beats),speech_beats=beats,title=' · '.join(t.rstrip('.') for t,m in pairs),body=' '.join(m for t,m in pairs),focus=focus,pedagogy_refs=[],teaching_notes=[],teaching_basis='additional source-bound vocabulary; independently reviewed',lexical_pairs=[dict(term=t,meaning=m,source_sentence=rows[i]['sentence_text']) for t,m in pairs]))
 v['scenes']=scenes
 lesson['presentation']=dict(showLevel=False,showChapter=False,showPassLabel=False)
 lesson['scope']=f'Two complete passes; first .88x, second1.0x; {26+len(EXTRA)} useful teaching stops; existing26 plus{len(EXTRA)} concise vocabulary stops; one paper layout; no second-pass interruptions'
 lesson['variation_parent']=dict(path=str(BASE/'lesson.json'),sha256=digest(BASE/'lesson.json'),preserve_parent_video=True)
 save(WORK/'lesson.json',lesson);compiler.validate(lesson)
 save(WORK/'edit-plan.json',dict(template='reading-coach',family='reading-teacher',source_id=lesson['source_id'],source_hash=lesson['source_hash'],clarifications=[],preserved_video_sha256=digest(ROOT/'renders/reading-teacher-elternabend/01-close-reading.mp4'),extra_stops=len(EXTRA),total_stops=26+len(EXTRA),presentation=lesson['presentation']))
 print('Authored',26+len(EXTRA),'stops',flush=True)
def configure():
 compiler.WORK=WORK;radio.WORK=WORK;radio.OUT=WORK/'teacher-audio-qwen'
if __name__=='__main__':
 configure();action=sys.argv[1]
 if action=='author':author()
 elif action=='audio':compiler.audio(load(WORK/'lesson.json'))
 elif action=='compile':compiler.compile(load(WORK/'lesson.json'))
