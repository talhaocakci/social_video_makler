import assert from "node:assert/strict";
import test from "node:test";
import {highlightShortSchema} from "../src/templates/highlight-short";

const sample={excerpt:"Ich brauche etwas mehr Zeit.",sourceLabel:"Reading",targetLabel:"German",guidingLabel:"English",introLabel:"Listen to this useful line.",listenLabel:"Listen",repeatLabel:"Now say it again.",turnLabel:"Your turn",continueLabel:"Continue in Get Fluent Fast",qrInstruction:"Scan with your phone camera",reason:"A useful way to ask for time.",tags:["daily-life"],qrDomain:"getfluentfast.app",qrImage:"qr.png",excerptStart:2,repeatStart:5,endCardStart:8};

test("highlight short accepts ordered listen, repeat and QR phases",()=>{
  assert.equal(highlightShortSchema.parse(sample).excerpt,"Ich brauche etwas mehr Zeit.");
});

test("highlight short rejects overlapping phase order",()=>{
  assert.throws(()=>highlightShortSchema.parse({...sample,repeatStart:9}));
});
