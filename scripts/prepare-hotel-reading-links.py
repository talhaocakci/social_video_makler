import sys,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from gff_reading_links import build
lesson=json.loads((root/'work/reading-teacher-hotel/lesson.json').read_text())
source=json.loads((root/'work/reading-teacher-hotel/source/reading.json').read_text())
out=build(lesson['source_id'],'Booking a hotel room',source['target_text'],root/'renders/reading-links-site')
shutil.copy2(out/'qr.png',root/'public/reading-teacher-hotel/reading-qr.png')
for variant in lesson['variants']:
 p=json.loads((root/f"work/reading-teacher-hotel/{variant['id']}.props.json").read_text())
 spec=p['spec']; end=spec['durationSec'];spec['durationSec']=end+10
 overlay=spec['overlays'][0];overlay['time']['duration']=f'{end+10}s'
 overlay['props']['readingLink']={'url':json.loads((out/'link.json').read_text())['web_url'],'qrImage':'reading-teacher-hotel/reading-qr.png','endCardStart':end,'label':'Okumaya uygulamada devam et','instruction':'Telefon kameranla QR kodu tara'}
 dest=root/'work/reading-teacher-hotel-qr';dest.mkdir(exist_ok=True)
 (dest/f"{variant['id']}.props.json").write_text(json.dumps(p,ensure_ascii=False,indent=2))

gallery=root/'renders/reading-teacher-hotel-qr'
gallery.mkdir(exist_ok=True)
original=root/'renders/reading-teacher-hotel'
for name in ('chapters.js','teacher-scripts.md'):
 shutil.copy2(original/name,gallery/name)
page=(original/'index.html').read_text().replace('Three ways to teach it.','Three ways to teach it. With QR continuation.')
page=page.replace('1:40','1:50').replace('02 / Story first · 1:50','02 / Story first · 2:00').replace('1:55','2:05')
page=page.replace('<div class="grid">','<p><strong>Local QR prototype:</strong> the public destination is awaiting hosting. <a href="http://127.0.0.1:8768/reading/'+lesson['source_id']+'/">Preview the content page</a>.</p><div class="grid">')
(gallery/'index.html').write_text(page)

for i,variant in enumerate(lesson['variants'],1):
 props=json.loads((root/f"work/reading-teacher-hotel-qr/{variant['id']}.props.json").read_text())
 start=props['spec']['overlays'][0]['props']['readingLink']['endCardStart']
 page=page.replace(f'<a class="download" href="{variant["id"]}.mp4"',f'<button data-video="v{i}" data-key="qr-{i}">QR closing card</button><a class="download" href="{variant["id"]}.mp4"')
 with (gallery/'chapters.js').open('a') as handle:
  handle.write(f'\nwindow.chapters["qr-{i}"]={start+1};\n')
(gallery/'index.html').write_text(page)
