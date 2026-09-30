"""Expose the new variation alongside the checksum-preserved accepted video."""
import hashlib, html, json, re, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'renders/reading-teacher-elternabend'
BASE=ROOT/'work/reading-teacher-elternabend';NEW=ROOT/'work/reading-teacher-elternabend-more-language'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(OUT/'01-close-reading.mp4')==json.loads((NEW/'edit-plan.json').read_text())['preserved_video_sha256']
old=(OUT/'index.html').read_text();style=re.search(r'<style>(.*?)</style>',old,re.S).group(1)
cards=[]
for work,id,title,desc,script in [
 (NEW,'04-more-language','Let’s unpack a little more German','More useful words, verbs and expressions, explained briefly as they come up. Then hear the whole meeting again without interruptions.','script-more-language'),
 (BASE,'01-close-reading','The earlier lesson','The version you liked, kept exactly as it was.','script')]:
 p=json.loads((work/f'{id}.props.json').read_text())['spec'];scenes=p['overlays'][0]['props']['scenes'];duration=p['durationSec'];rev=digest(OUT/f'{id}.mp4')[:12]
 markers=[]
 if id=='04-more-language':
  for label,key in [('Settling in','more-words-12'),('In good hands','more-words-34'),('School messages','more-words-101'),('Copying someone into an email','more-words-111'),('Listen once more','regular-pass-bridge')]:
   markers.append(f'<button data-video="{id}" data-time="{next(s["start"] for s in scenes if s.get("key")==key)}">{label}</button>')
 cards.append(f'<article><video id="{id}" aria-label="{html.escape(title)}" controls playsinline preload="metadata" src="{id}.mp4?v={rev}" poster="{id}.png?v={rev}"></video><div class="copy"><small>{int(duration)//60}:{int(duration)%60:02d}</small><h2>{title}</h2><p>{desc}</p>{"".join(markers)}<br><a href="{id}.mp4" download>Download video</a> · <a href="{script}/video-script.md">Complete ordered script</a> · <a href="{script}/guiding-translation-template.json">Translation file</a></div></article>')
page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Feel at home at your next parents’ evening</title><style>{style}</style><main><header>GetFluentFast ●</header><h1>Feel more at home<br>at your next parents’ evening.</h1><p class="lead">Picking up your child, reading a school notice, keeping in touch with the teacher: let’s make the German easier to follow. Listen together, with short English explanations of useful words and expressions.</p><div class="grid">{"".join(cards)}</div><p class="note">You don’t need to understand every word at once. We’ll make room for helpful meanings as the meeting unfolds. On the next listen, let the whole conversation come together. You can follow through headphones too.</p><p>The QR takes you to the original reading. Public website hosting is still pending; these videos are local previews.</p></main><script>const videos=[...document.querySelectorAll('video')];videos.forEach(v=>v.addEventListener('play',()=>videos.forEach(o=>{{if(o!==v)o.pause()}})));document.querySelectorAll('[data-video]').forEach(b=>b.addEventListener('click',()=>{{const v=document.getElementById(b.dataset.video);v.currentTime=Number(b.dataset.time);v.play();}}));</script></html>'''
(OUT/'index.html').write_text(page)
shutil.copytree(NEW/'script',OUT/'script-more-language',dirs_exist_ok=True)
for name in ['04-more-language.manifest.json','editorial-audit.json','teacher-audio-qa-qwen.json','teacher-waveform-qa-qwen.json','teacher-speaker-qa-qwen.json']:
 shutil.copy2(NEW/name,OUT/('more-language-'+name if not name.startswith('04-') else name))
print('Gallery ready; accepted original checksum preserved')
