#!/usr/bin/env python3
"""Finish QR pilot delivery from exact WAVs, then measure decoded audio/QR frames."""
import json,os,subprocess,sys,tempfile,wave
from pathlib import Path
import numpy as np
from scipy.signal import correlate
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from gff_reading_teacher import ffmpeg_path
ffmpeg=ffmpeg_path();env=dict(os.environ,DYLD_LIBRARY_PATH=str(ffmpeg.parent))
def run(args): return subprocess.run([str(ffmpeg),'-v','error',*args],check=True,env=env,stdout=subprocess.PIPE).stdout
report=[]
for name in ['01-close-reading','02-story-first','03-predict-recall']:
 props=json.loads((ROOT/f'work/reading-teacher-hotel-qr/{name}.props.json').read_text())
 duration=props['spec']['durationSec'];wav=ROOT/f'public/reading-teacher-hotel/{name}.wav'
 video=ROOT/f'renders/reading-teacher-hotel-qr/{name}.mp4';tmp=video.with_suffix('.delivery.mp4')
 run(['-y','-i',str(video),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-af','apad','-t',str(duration),'-movflags','+faststart',str(tmp)])
 tmp.replace(video)
 def samples(path):
  with tempfile.TemporaryDirectory() as directory:
   decoded=Path(directory)/'decoded.wav'
   run(['-y','-i',str(path),'-vn','-ar','16000','-ac','1','-c:a','pcm_s16le',str(decoded)])
   with wave.open(str(decoded),'rb') as handle:
    return np.frombuffer(handle.readframes(handle.getnframes()),dtype=np.int16).astype(np.float32)/32768

 original=samples(wav);encoded=samples(video);offsets=[]
 for anchor in [5,len(original)/16000/2,len(original)/16000-6]:
  start=int(anchor*16000);template=original[start:start+16000];margin=1600
  signal=encoded[start-margin:start+16000+margin]
  offset=(int(np.argmax(correlate(signal,template,mode='valid',method='fft')))-margin)/16
  assert abs(offset)<=2, (name,offset)
  offsets.append(offset)
 frame=ROOT/f'work/reading-teacher-hotel-qr/{name}-encoded-qr.png'
 run(['-y','-ss',str(duration-5),'-i',str(video),'-frames:v','1',str(frame)])
 run(['-i',str(video),'-c:v','rawvideo','-c:a','pcm_s16le','-f','null','-'])
 report.append({'variant':name,'duration_seconds':duration,'decoded_audio_anchor_offsets_ms':offsets,'encoded_qr_frame':str(frame),'full_decode':'passed'})
 print(name,offsets,flush=True)
(ROOT/'renders/reading-teacher-hotel-qr/delivery-qa.json').write_text(json.dumps(report,indent=2))
