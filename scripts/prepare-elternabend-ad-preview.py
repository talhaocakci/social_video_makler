"""An isolated, regenerable excerpt; preserves both accepted full videos."""
import copy,math
from reading_ad_schedule import plan_ads
from pathlib import Path
from gff_reading_teacher import load,save,digest,pcm,wav,normalize,RATE
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work/reading-teacher-elternabend-promo'
BASE=ROOT/'work/reading-teacher-elternabend-more-language'
PUBLIC=ROOT/'public/reading-teacher-elternabend'
ID='ueberblick-ad-transition-preview-en'
props=load(BASE/'04-more-language.props.json');spec=props['spec'];p=spec['overlays'][0]['props']
scenes=p['scenes']
schedule=plan_ads(scenes,end_card_start=p['readingLink']['endCardStart'])
save(WORK/'six-minute-ad-schedule.json',dict(min_interval_seconds=360,first_sentence_floor=3,events=schedule,assets_required_per_event=True))
explanation=next(s for s in scenes if s.get('key')==schedule[0]['after_scene_key'])
assert explanation['focus']=='Überblick'
before=[copy.deepcopy(s) for s in scenes if s['sentence']==explanation['sentence'] and s['start']<=explanation['start'] and (s.get('pace')=='slow' or s is explanation)]
after=[copy.deepcopy(next(s for s in scenes if s['kind']=='reading' and s.get('pace')=='slow' and s['sentence']==3))]
start=before[0]['start'];insert=explanation['start']+explanation['duration'];preDuration=insert-start
assert abs(after[0]['start']-insert)<1e-6
# End after "practice and quizzes", before the old second-listen invitation.
# Both local ASR passes place that phrase's end at 12.10s and "Now" at 12.46s.
speechEnd=12.3
original=pcm(PUBLIC/'04-more-language.wav');speech,gain=normalize(pcm(WORK/'promotion.wav')[:round(speechEnd*RATE)*2])
spokenText=load(WORK/'promotion-audio.json')['text'].split(' Now,')[0]
duration=max(15,math.ceil((len(speech)/(RATE*2)+1.3)*30)/30)
speech+=b'\0'*(round(duration*RATE)*2-len(speech))
postStart=after[0]['start'];postEnd=after[-1]['start']+after[-1]['duration']
def cut(a,b):return original[round(a*RATE)*2:round(b*RATE)*2]
wav(PUBLIC/(ID+'.wav'),cut(start,insert)+speech+cut(postStart,postEnd))
for s in before:s['start']-=start
hold=copy.deepcopy(before[-1]);hold.update(start=preDuration,duration=duration,key='app-invitation-context-hold')
for s in after:s['start']+=preDuration+duration-postStart
p['scenes']=before+[hold]+after
captures=load(WORK/'app-captures-en.json');screens=[]
assert captures['ui_guiding_language']=='en' and captures['word']==schedule[0]['word']
for s in captures['screens']:
 assert digest(ROOT/'public'/s['src'])==s['sha256']
 screen={k:s[k] for k in ('src','caption','tap') if k in s}
 screens.append(screen)
p['promotions']=[dict(start=preDuration,duration=duration,mode='spoken',headline='Keep learning with us',instruction='Scan to open this reading',qrImage=p['readingLink']['qrImage'],screens=screens)]
total=preDuration+duration+postEnd-postStart
p['readingLink']['endCardStart']=total+1
spec['durationSec']=round(total*30)/30;spec['source']['src']='reading-teacher-elternabend/'+ID+'.wav';spec['overlays'][0]['time']['duration']=f'{spec["durationSec"]}s'
save(WORK/(ID+'.props.json'),props)
save(WORK/(ID+'.script.json'),dict(template='reading-coach',family='reading-teacher',source_id='reading_elternabend_seed_de',source_hash=load(ROOT/'work/reading-teacher-elternabend/lesson.json')['source_hash'],parent_props_sha256=digest(BASE/'04-more-language.props.json'),guiding_language='en',target_language='de',segments=[dict(kind='reading-and-explanation',source_start=start,source_end=insert,scenes=before),dict(kind='spoken-promotion',start=preDuration,duration=duration,text=spokenText,audio_sha256=digest(WORK/'promotion.wav'),audio_source_end=speechEnd,gain=gain,promotion=p['promotions'][0]),dict(kind='reading',source_start=postStart,source_end=postEnd,scenes=after)],captures=captures,preview_duration=spec['durationSec'],anchor=dict(after_scene_key=explanation['key'],word='Überblick',source_sentence=2,source_time=insert),transition_seconds=.8,stable_qr_seconds=duration-1.6,clarifications=[],public_landing_verified=False))
print(ID,spec['durationSec'],'seconds; ad at',preDuration,'for',duration)
