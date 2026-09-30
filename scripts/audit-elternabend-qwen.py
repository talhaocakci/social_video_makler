"""Check decoded teacher audio and identity across nonadjacent assembled scenes."""
import os,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];WORK=Path(os.environ.get('GFF_READING_WORK',str(ROOT/'work/reading-teacher-elternabend')));OUT=WORK/'teacher-audio-qwen'
sys.path.insert(0,'/Users/talhaocakci/Projects/local_whisper')
from gff_reading_teacher import save,digest,load
if sys.argv[1] in ['speaker','narrator','anchors']:
 import gff_tts_pipeline as t
 model=t.load_model(str(t.BASE_SNAPSHOT))
 keys=['01-close-reading-intro','first-use-28','first-use-105','first-use-60','first-use-113','first-use-15','two-pass-outro']
 if (OUT/'more-words-5.json').exists():keys=['04-more-language-intro','more-words-5','more-words-34','more-words-70','more-words-111','more-words-129','two-pass-outro']
 plan={'voice_assignments':{'narrator':{'reference_audio_path':str(WORK/'qwen-radio-sample/teacher-reference.wav')}},'artifacts':[{'path':str(OUT/(key+'.wav')),'checksum_sha256':digest(OUT/(key+'.wav'))} for key in keys]}
 if sys.argv[1]=='narrator':
  plan={'voice_assignments':{'narrator':{'reference_audio_path':str(WORK/'narrator-mature-qwen/reference.wav')}},'artifacts':[{'path':str(WORK/'narrator-mature-qwen/regular'/f'{i:03d}.wav'),'checksum_sha256':digest(WORK/'narrator-mature-qwen/regular'/f'{i:03d}.wav')} for i in [0,15,35,69,95,113,136]]}
 if sys.argv[1]=='speaker':
  plan['artifacts']=[{'path':str(OUT/'beats'/(load(OUT/(key+'.json'))['beats'][-1]['identity']+'.wav'))} for key in keys]
 if sys.argv[1]=='anchors':
  plan['voice_assignments']['narrator']['reference_audio_path']=str(WORK/'narrator-mature-qwen/reference.wav')
  plan['artifacts']=[{'path':str(OUT/'beats'/(load(OUT/(key+'.json'))['beats'][0]['identity']+'.wav'))} for key in keys[1:-1]]
 t.audit_speaker_consistency(model,plan);t.release_model(model)
 plan['speaker_consistency_audit']['requires_human_audition']=False
 plan['human_audition']=False;save(WORK/('narrator-mature-qwen/speaker-qa.json' if sys.argv[1]=='narrator' else 'teacher-german-anchors-speaker-qa.json' if sys.argv[1]=='anchors' else 'teacher-speaker-qa-qwen.json'),plan);print(plan['speaker_consistency_audit'],flush=True)
else:
 import validate_gff_audio as v
 clips=[]
 from elternabend_radio import identity
 lesson=load(WORK/'lesson.json');current={identity(b) for v in lesson['variants'] for s in v['scenes'] if s['kind']=='teacher' for b in s['speech_beats']}
 for p in [OUT/'beats'/(h+'.json') for h in sorted(current)]:
  b=load(p);clips.append(v.inspect_audio(str(p.with_suffix('.wav')),p.stem,source_word_count=len(b['text'].split())))
 save(WORK/'teacher-waveform-qa-qwen.json',dict(passed=all(x['passed'] for x in clips),clips=clips));print('waveform',len(clips),all(x['passed'] for x in clips),flush=True)
