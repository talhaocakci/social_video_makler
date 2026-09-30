#!/usr/bin/env python3
"""Loopback-only preview server with byte ranges for reliable video seeking."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import re

class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        self.byte_range=None
        path=Path(self.translate_path(self.path))
        if not path.is_file():return super().send_head()
        file=path.open('rb');size=path.stat().st_size
        header=self.headers.get('Range');start=0;end=size-1
        if header:
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',header.strip())
            if not match or not any(match.groups()):
                file.close();self.send_error(416);return None
            a,b=match.groups()
            if a:start=int(a);end=min(size-1,int(b))if b else size-1
            else:start=max(0,size-int(b))
            if start>end or start>=size:
                file.close();self.send_error(416);return None
            self.byte_range=(start,end);file.seek(start);self.send_response(206)
            self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        else:self.send_response(200)
        self.send_header('Content-Type',self.guess_type(str(path)))
        self.send_header('Accept-Ranges','bytes')
        self.send_header('Content-Length',str(end-start+1))
        self.send_header('Cache-Control','no-cache')
        self.end_headers();return file

    def copyfile(self,source,outputfile):
        if self.byte_range is None:return super().copyfile(source,outputfile)
        remaining=self.byte_range[1]-self.byte_range[0]+1
        while remaining:
            data=source.read(min(remaining,64*1024))
            if not data:break
            outputfile.write(data);remaining-=len(data)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8766);p.add_argument('--directory',type=Path);args=p.parse_args()
    directory=args.directory or Path(__file__).resolve().parents[1]/'renders/reading-teacher-hotel'
    print(f'Local reading previews: http://127.0.0.1:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(directory))).serve_forever()
