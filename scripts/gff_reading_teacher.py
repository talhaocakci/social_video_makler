#!/usr/bin/env python3
"""Compile a reviewed reading-teacher storyboard to the existing motion engine.

All output is local. Reading speech is cut from the checksum-verified original
master. Teacher notes are synthetic prototype audio, never canonical content.
"""
from __future__ import annotations
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import wave

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work/reading-teacher-hotel'
PUBLIC=ROOT/'public/reading-teacher-hotel'
RATE=24000
FPS=30

def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
def save(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def ffmpeg_path():
    candidates=list((ROOT/'node_modules/.pnpm').glob('@remotion+compositor-*/node_modules/@remotion/compositor-*/ffmpeg'))
    if not candidates: raise RuntimeError('Remotion ffmpeg missing')
    return candidates[0]

def convert(src,dst):
    ffmpeg=ffmpeg_path();env=dict(os.environ, DYLD_LIBRARY_PATH=str(ffmpeg.parent))
    subprocess.run([str(ffmpeg),'-v','error','-y','-i',str(src),'-ar',str(RATE),'-ac','1','-c:a','pcm_s16le',str(dst)],env=env,check=True)

def pcm(p):
    with wave.open(str(p),'rb') as f:
        assert (f.getframerate(),f.getnchannels(),f.getsampwidth())==(RATE,1,2)
        return f.readframes(f.getnframes())

def wav(p,b):
    with wave.open(str(p),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(b)

def normalize(b):
    samples=array('h');samples.frombytes(b)
    rms=math.sqrt(sum(x*x for x in samples)/max(1,len(samples)))
    peak=max(map(abs,samples),default=1)
    gain=min(32767*.85/max(1,peak),32767*(10**(-21/20))/max(1,rms))
    result=array('h',(round(x*gain) for x in samples))
    return result.tobytes(),round(gain,5)

def word_spans(text,words,clip_start_ms):
    # The aligner collapses internal hyphens (check-in -> checkin). Match its
    # normalized token while retaining exact original character positions.
    positions=[i for i,c in enumerate(text) if c.isalnum()]
    normalized=''.join(text[i].lower() for i in positions)
    cursor=0;out=[]
    for w in words:
        token=''.join(c.lower() for c in w['text'] if c.isalnum())
        at=normalized.find(token,cursor)
        if at!=cursor or not token: raise ValueError(f'Cannot locate aligned word {token!r} at expected source position')
        start=positions[at];end=positions[at+len(token)-1]+1;cursor=at+len(token)
        out.append(dict(start=start,end=end,t0=(w['start_ms']-clip_start_ms)/1000,
                        t1=(w['end_ms']-clip_start_ms)/1000))
    assert cursor==len(normalized),'Alignment does not cover all source text'
    return out

def validate(lesson):
    source=load(WORK/'source/reading.json');ped=load(WORK/'source/pedagogy.json')
    alignment=load(WORK/'source/reading_alignment.json')
    assert source['content_id']==lesson['source_id']
    assert source['list_summary']['cefr']=='B1' and source['list_summary']['target_language']=='en'
    assert alignment['source_text_sha256']==lesson['source_text_sha256']==ped['head']['source_hash']
    assert digest(WORK/'source/reading_full.wav')==alignment['full']['audio_checksum']
    assert ped['head']['bundle_checksum']==lesson['source_pedagogy_checksum']
    refs={p['point_id'] for r in ped['sentences'] for k in ['important_words','important_phrases','grammar'] for p in r.get('authoring_pedagogic',r['pedagogic'])[k]}
    texts=[s['text'] for s in alignment['sentences']]
    assert texts==[s['text'] for s in source['payload']['reading_audio']['sentences']]
    for variant in lesson['variants']:
        reads=[s['sentence'] for s in variant['scenes'] if s['kind']=='reading']
        assert reads[:5]==list(range(5)),reads
        for scene in variant['scenes']:
            assert 0<=scene['sentence']<len(texts)
            assert not scene.get('focus') or scene['focus'] in texts[scene['sentence']]
            assert set(scene.get('pedagogy_refs',[]))<=refs
    return alignment

def generate(lesson):
    voice_dir=WORK/'teacher-audio';voice_dir.mkdir(exist_ok=True)
    manifest=[]
    for variant in lesson['variants']:
        for scene in variant['scenes']:
            if scene['kind']!='teacher':continue
            key=scene['key'];text=scene['text'];txt=voice_dir/f'{key}.txt';target=voice_dir/f'{key}.wav'
            spoken_text=text.replace('Sarah','Sara')
            identity=hashlib.sha256(f"Yelda|{variant['voice_rate']}|{text}|{spoken_text}".encode()).hexdigest()
            receipt=voice_dir/f'{key}.json'
            if not target.exists() or not receipt.exists() or load(receipt).get('identity')!=identity:
                txt.write_text(spoken_text+'\n');aiff=voice_dir/f'{key}.aiff'
                subprocess.run(['say','-v','Yelda','-r',str(variant['voice_rate']),'-f',str(txt),'-o',str(aiff)],check=True)
                subprocess.run(['afconvert','-f','WAVE','-d','LEI16@24000','-c','1',str(aiff),str(target)],check=True)
                save(receipt,dict(identity=identity,engine='macOS Speech Synthesis',voice='Yelda',rate=variant['voice_rate'],text=text,spoken_text=spoken_text,pronunciation_mapping={'Sarah':'Sara'},text_sha256=hashlib.sha256(text.encode()).hexdigest(),audio_sha256=digest(target),language='tr',synthetic=True))
            manifest.append(dict(key=key,path=str(target),**load(receipt)))
            print('audio',key,round(len(pcm(target))/2/RATE,2),flush=True)
    save(WORK/'teacher-audio-manifest.json',manifest)

def compile(lesson,alignment):
    PUBLIC.mkdir(exist_ok=True,parents=True)
    master=pcm(WORK/'source/reading_full.wav');sentences=alignment['sentences']
    theme=load(ROOT/'brand/getfluentfast.theme.json')
    for variant in lesson['variants']:
        buffer=bytearray();scenes=[];gains=[]
        for i,raw in enumerate(variant['scenes']):
            sentence=sentences[raw['sentence']];scene=dict(raw,text=sentence['text'],words=[])
            scene['teacherText']=raw.get('text','') if raw['kind']=='teacher' else ''
            if raw['kind']=='reading':
                start=round(sentence['master_clip_start_ms']*RATE/1000);end=round(sentence['master_clip_end_ms']*RATE/1000)
                audio=master[start*2:end*2]
                scene['words']=word_spans(sentence['text'],sentence['words'],sentence['master_clip_start_ms'])
                scene['source_audio_clip_ms']=[sentence['master_clip_start_ms'],sentence['master_clip_end_ms']]
            elif raw['kind']=='teacher': audio=pcm(WORK/'teacher-audio'/f"{raw['key']}.wav")
            else: audio=b'\0'*(round(raw['duration']*RATE)*2)
            if raw['kind']!='pause':
                audio,gain=normalize(audio);gains.append(dict(scene=i,gain=gain,kind=raw['kind']))
            # Quiet visual settle before teacher / opening; no inserted gaps inside
            # consecutive narration, preserving the original reading rhythm.
            lead=.22 if i==0 or raw['kind']=='teacher' else 0
            tail=.32 if raw['kind']=='teacher' else .22 if raw['kind']=='reading' and (i+1==len(variant['scenes']) or variant['scenes'][i+1]['kind']!='reading') else 0
            if lead:audio=b'\0'*(round(lead*RATE)*2)+audio
            if tail:audio+=b'\0'*(round(tail*RATE)*2)
            # Align scene boundaries to exact rendered frames using silence only.
            frame_samples=RATE//FPS;pad=(-len(audio)//2)%frame_samples;audio+=b'\0'*(pad*2)
            scene['start']=len(buffer)/2/RATE;scene['duration']=len(audio)/2/RATE
            for w in scene['words']:w['t0']+=lead;w['t1']+=lead
            scene['image']='reading-teacher-hotel/'+{0:'sarah.png',1:'sarah.png',2:'reception.png',3:'cancellation.svg',4:'booking.svg'}[raw['sentence']]
            scenes.append(scene);buffer.extend(audio)
        duration=len(buffer)/2/RATE;audio_out=PUBLIC/f"{variant['id']}.wav";wav(audio_out,buffer)
        samples=array('h');samples.frombytes(buffer)
        levels=[]
        for j in range(math.ceil(duration*FPS)):
            block=samples[j*(RATE//FPS):(j+1)*(RATE//FPS)]
            rms=math.sqrt(sum(x*x for x in block)/max(1,len(block)))
            levels.append(round(min(1,rms/4500),3))
        props=dict(spec=dict(version=1,format='horizontal',fps=FPS,durationSec=duration,
                   source=dict(type='audio',src=f"reading-teacher-hotel/{variant['id']}.wav"),
                   sound=dict(enabled=False,volume=0,sounds={}),overlays=[
                     dict(template='reading-coach',region='fullscreen',time=dict(start='0s',duration=f'{duration}s'),
                          props=dict(title='Booking a hotel room',variantTitle=variant['title'],treatment=variant['treatment'],scenes=scenes,levels=levels))]),theme=theme)
        save(WORK/f"{variant['id']}.props.json",props)
        save(WORK/f"{variant['id']}.manifest.json",dict(schema_version=1,source_id=lesson['source_id'],source_revision=lesson['source_revision'],source_text_sha256=lesson['source_text_sha256'],source_pedagogy_checksum=lesson['source_pedagogy_checksum'],lesson_sha256=digest(WORK/'lesson.json'),template_family='reading-teacher',motion_templates=['reading-coach'],variant=variant['id'],source_sentence_count=5,narration='reused source-aligned Qwen master',teacher_voice=lesson['teacher_audio'],word_sync=alignment['alignment_model'],audio_sha256=digest(audio_out),audio_gain_changes=gains,duration_seconds=duration,publication='local_only',human_audition=False,scenes=scenes))
        print('compiled',variant['id'],duration,'seconds',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['validate','audio','compile']);args=p.parse_args()
    lesson=load(WORK/'lesson.json');alignment=validate(lesson)
    if args.action=='audio':generate(lesson)
    if args.action=='compile':compile(lesson,alignment)
    print('PASS',args.action)
