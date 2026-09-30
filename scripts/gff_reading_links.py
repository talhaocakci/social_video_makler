#!/usr/bin/env python3
"""Build an explicit Reading landing page and QR assets; never deploys.
Dependency: qrcode[pil]==8.2. Only pass an approved public source snapshot.
"""
import argparse
import html
import json
import re
from pathlib import Path
import qrcode
from qrcode.image.svg import SvgPathImage


def reading_url(content_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,159}', content_id):
        raise ValueError('Invalid Reading ID')
    return f'https://getfluentfast.app/reading/{content_id}/'


def build(content_id, title, excerpt, output):
    url = reading_url(content_id)
    app_url = f'getfluentfast://reading/{content_id}'
    destination = Path(output) / 'reading' / content_id
    destination.mkdir(parents=True, exist_ok=True)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    qr.make_image(fill_color='black', back_color='white').save(destination / 'qr.png')
    qr.make_image(image_factory=SvgPathImage).save(destination / 'qr.svg')
    esc = html.escape
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ · GetFluentFast</title><meta name="description" content="Read, listen and practise this lesson in GetFluentFast.">
<link rel="canonical" href="__URL__">
<style>*{box-sizing:border-box}body{margin:0;background:#f5f2e9;color:#173d33;font:18px/1.65 system-ui,sans-serif}main{max-width:760px;margin:auto;padding:48px 24px}header{font-weight:800;margin-bottom:64px}small{letter-spacing:.12em;color:#536d60}h1{font-size:clamp(36px,7vw,58px);line-height:1.1;letter-spacing:-.045em;margin:18px 0 28px}article{background:white;border-radius:24px;padding:26px;margin:30px 0}a.button{display:block;text-align:center;background:#176c50;color:white;padding:17px 20px;border-radius:14px;text-decoration:none;font-weight:700}a{color:#176c50}aside{margin-top:38px;padding-top:28px;border-top:1px solid #cbd6c8;display:flex;gap:24px;align-items:center}aside img{width:160px;height:160px}p{margin:12px 0}.hint{font-size:15px;color:#536d60}#status{min-height:24px}@media(max-width:450px){aside{display:block}header{margin-bottom:40px}}</style>
<main><header>GetFluentFast ●</header><small>CONTINUE YOUR READING</small><h1>__TITLE__</h1>
<p>Pick up the reading from the video. Listen, explore the words and practise in the app.</p>
<a class="button" id="open-app" href="__APP__">Open in GetFluentFast</a>
<p class="hint">Sign in if asked. The app will then open this reading.</p>
<p id="status" class="hint" role="status"></p>
<article><p>__EXCERPT__</p></article>
<details><summary>The app didn’t open?</summary><p>Open this page on the phone where GetFluentFast is installed, then tap the button again. If you don’t have the app yet, keep this page and return after installing it.</p></details>
<aside><img src="qr.png" alt="QR code for this reading page" width="160" height="160"><div><strong>Watching on a larger screen?</strong><p class="hint">Scan with your phone camera to continue with this same reading.</p></div></aside>
</main><script>document.getElementById('open-app').addEventListener('click',function(){document.getElementById('status').textContent='If the app does not open, use the help below. This page will stay available.';});</script></html>'''
    for key, value in {'__TITLE__': title, '__EXCERPT__': excerpt, '__URL__': url, '__APP__': app_url}.items():
        page = page.replace(key, esc(value, quote=True))
    (destination / 'index.html').write_text(page)
    manifest = {'schema_version': 1, 'content_id': content_id, 'web_url': url, 'app_url': app_url,
                'qr_payload': url, 'qr_error_correction': 'M', 'quiet_zone_modules': 4,
                'deployment_status': 'local_only', 'title': title}
    (destination / 'link.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return destination

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content-id', required=True)
    parser.add_argument('--title', required=True)
    parser.add_argument('--excerpt', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(build(args.content_id, args.title, args.excerpt, args.output))
