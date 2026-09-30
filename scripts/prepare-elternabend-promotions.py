"""Prepare source-word-bound ads; full assembly requires each word's real captures."""
import copy,sys,math
from pathlib import Path
from gff_reading_teacher import load,save,digest,pcm,wav,RATE,normalize
from reading_ad_schedule import plan_ads
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'work/reading-teacher-elternabend-more-language'
WORK=ROOT/'work/reading-teacher-elternabend-promo'
PUBLIC=ROOT/'public/reading-teacher-elternabend'
ID='05-app-promotion'

def prepare(plan_only=False):
 props=load(BASE/'04-more-language.props.json');spec=props['spec'];p=spec['overlays'][0]['props']
 receipt=load(WORK/'promotion-audio.json');audio=WORK/'promotion.wav'
 assert receipt['audio_sha256']==digest(audio)
 # Exclude the old "listen again" sign-off; resume the same first pass.
 speech,gain=normalize(pcm(audio)[:round(12.3*RATE)*2])
 duration=max(15,math.ceil((len(speech)/(2*RATE)+1.3)*30)/30)
 speech+=b'\0'*(round(duration*RATE)*2-len(speech))
 events=plan_ads(p['scenes'],spoken_duration=duration,end_card_start=p['readingLink']['endCardStart'])
 assert events,'No eligible word explanation for first ad'
 captures=[load(WORK/'app-captures-en.json')]
 registry=WORK/'app-captures-by-word.json'
 if registry.exists():captures+=load(registry)['captures']
 missing=[]
 for e in events:
  c=next((c for c in captures if c['word']==e['word'] and c['source_sentence_index']==e['source_sentence_index'] and c['ui_guiding_language']=='en'),None)
  if not c:missing.append(dict(word=e['word'],source_sentence_index=e['source_sentence_index'],after_scene_key=e['after_scene_key']));continue
  for screen in c['screens']:assert digest(ROOT/'public'/screen['src'])==screen['sha256']
  e['capture_manifest']=c
 plan=dict(parent_props_sha256=digest(BASE/'04-more-language.props.json'),guiding_language='en',min_interval_seconds=360,first_sentence_floor=3,events=events,missing_captures=missing,render_ready=not missing)
 save(WORK/'promotion-plan.json',plan)
 if plan_only:return
 if missing:raise ValueError('Capture each scheduled word in English before full rendering; see promotion-plan.json. Never reuse unrelated word screens.')
 first=events[0];insert=first['source_time']
 explanation=copy.deepcopy(next(s for s in p['scenes'] if s.get('key')==first['after_scene_key']))
 for s in p['scenes']:
  if s['start']>=insert-1e-6:s['start']+=duration
 explanation.update(start=insert,duration=duration,key='app-promotion',teacherText=receipt['text'].split(' Now,')[0])
 p['scenes'].append(explanation);p['scenes'].sort(key=lambda s:s['start'])
 p['readingLink']['endCardStart']+=duration;spec['durationSec']+=duration
 spec['overlays'][0]['time']['duration']=f"{spec['durationSec']}s"
 original=pcm(PUBLIC/'04-more-language.wav');cut=round(insert*RATE)*2
 wav(PUBLIC/(ID+'.wav'),original[:cut]+speech+original[cut:])
 spec['source']['src']='reading-teacher-elternabend/'+ID+'.wav'
 p['promotions']=[dict(start=e['start'],duration=e['duration'],mode=e['mode'],headline='Keep learning with us',instruction='Scan to open this reading',qrImage=p['readingLink']['qrImage'],screens=[{k:s[k] for k in ('src','caption','tap') if k in s} for s in e['capture_manifest']['screens']]) for e in events]
 save(WORK/(ID+'.props.json'),props)
 print('Prepared',ID,spec['durationSec'],'seconds',len(events),'source-bound ads')
if __name__=='__main__':prepare('--plan-only' in sys.argv)
