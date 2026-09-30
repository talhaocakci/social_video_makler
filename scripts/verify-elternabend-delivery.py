#!/usr/bin/env python3
"""Finish QR pilot delivery from exact WAVs, then measure decoded audio/QR frames."""
import json,os,subprocess,sys,tempfile,wave,hashlib
from pathlib import Path
import numpy as np
from scipy.signal import correlate
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from gff_reading_teacher import ffmpeg_path
ffmpeg=ffmpeg_path();env=dict(os.environ,DYLD_LIBRARY_PATH=str(ffmpeg.parent))
def run(args): return subprocess.run([str(ffmpeg),'-v','error',*args],check=True,env=env,stdout=subprocess.PIPE).stdout
report=[]
for name in (sys.argv[1:] or ['01-close-reading','02-story-first','03-predict-recall']):
 work=Path(os.environ.get('GFF_READING_WORK',str(ROOT/'work/reading-teacher-elternabend')))
 props=json.loads((work/f'{name}.props.json').read_text())
 duration=props['spec']['durationSec'];wav=ROOT/f'public/reading-teacher-elternabend/{name}.wav'
 video=ROOT/f'renders/reading-teacher-elternabend/{name}.mp4';tmp=video.with_suffix('.delivery.mp4')
 run(['-y','-i',str(video),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(duration),'-movflags','+faststart',str(tmp)])
 tmp.replace(video)
 def samples(path):
  with tempfile.TemporaryDirectory() as directory:
   decoded=Path(directory)/'decoded.wav'
   run(['-y','-i',str(path),'-vn','-ar','16000','-ac','1','-c:a','pcm_s16le',str(decoded)])
   with wave.open(str(decoded),'rb') as handle:
    return np.frombuffer(handle.readframes(handle.getnframes()),dtype=np.int16).astype(np.float32)/32768

 original=samples(wav);encoded=samples(video);offsets=[]
 speech_end=props['spec']['overlays'][0]['props']['readingLink']['endCardStart']
 for anchor in [5,speech_end/2,speech_end-6]:
  start=int(anchor*16000);template=original[start:start+16000];margin=1600
  signal=encoded[start-margin:start+16000+margin]
  offset=(int(np.argmax(correlate(signal,template,mode='valid',method='fft')))-margin)/16
  assert abs(offset)<=2, (name,offset)
  offsets.append(offset)
 frame=work/f'{name}-encoded-qr.png'
 run(['-y','-ss',str(duration-5),'-i',str(video),'-frames:v','1',str(frame)])
 run(['-i',str(video),'-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-'])
 report.append({'variant':name,'duration_seconds':duration,'decoded_audio_anchor_offsets_ms':offsets,'encoded_qr_frame':str(frame),'full_decode':'passed','video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'assembled_audio_sha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'lesson_sha256':hashlib.sha256((work/'lesson.json').read_bytes()).hexdigest()})
 print(name,offsets,flush=True)
receipt=ROOT/'renders/reading-teacher-elternabend'/os.environ.get('GFF_DELIVERY_RECEIPT','delivery-qa.json')
previous=json.loads(receipt.read_text()) if receipt.exists() else []
replaced={r['variant'] for r in report}
active={v['id'] for v in json.loads((work/'lesson.json').read_text())['variants']}
receipt.write_text(json.dumps([r for r in previous if r['variant'] not in replaced and r['variant'] in active]+report,indent=2))
