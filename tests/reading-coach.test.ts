import test from 'node:test';
import assert from 'node:assert/strict';
import {readingCoachSchema,sentenceFragments} from '../src/templates/reading-coach';

test('highlighted fragments reconstruct exact punctuated source',()=>{
  const p=readingCoachSchema.parse({title:'Pilot',variantTitle:'Test',treatment:'paper',scenes:[{
    kind:'reading',sentence:1,start:0,duration:3,text:'Is a room available?',image:'source.png',focus:'a room',
    words:[{start:0,end:2,t0:0,t1:.4},{start:3,end:4,t0:.4,t1:.4},{start:5,end:9,t0:.4,t1:1},{start:10,end:19,t0:1,t1:2}],
  }]});
  const parts=sentenceFragments(p.scenes[0],.5);
  assert.equal(parts.map(x=>x.text).join(''),'Is a room available?');
  assert.equal(parts.filter(x=>x.current).map(x=>x.text).join(''),'room');
  assert.equal(parts.filter(x=>x.focus).map(x=>x.text).join(''),'a room');
});

test('reading continuation only accepts canonical web reading destinations',()=>{
  const base={title:'Test',variantTitle:'Test',treatment:'paper',scenes:[{kind:'reading',sentence:0,start:0,duration:1,text:'Test',image:'test.png'}]};
  const link={url:'https://getfluentfast.app/reading/reading-1/',qrImage:'qr.png',endCardStart:1,label:'Continue',instruction:'Scan'};
  assert.equal(readingCoachSchema.parse({...base,readingLink:link}).readingLink?.url,link.url);
  for(const url of ['getfluentfast://reading/reading-1','https://evil.test/reading/x/','https://getfluentfast.app/reading/../']){
    assert.equal(readingCoachSchema.safeParse({...base,readingLink:{...link,url}}).success,false);
  }
});
