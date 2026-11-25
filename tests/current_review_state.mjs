import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
await import('../workbench/adjudication/current/state.js');
const S=globalThis.CurrentReview;
const bytes=readFileSync('workbench/data/current_body_review.json');assert.equal(await S.hash(bytes),S.PACKET_SHA);
const packet=JSON.parse(bytes),source=readFileSync('index.html');assert.equal(await S.hash(source),packet.sourceHtmlSha256);
const pages=JSON.parse(execFileSync('python',['-c',"import json,sys;sys.path.insert(0,'tools');from discover_entry_boundaries import parse_cards;print(json.dumps({c['page']:c['text'] for c in parse_cards(open('index.html').read())}))"],{encoding:'utf8',maxBuffer:4*1024*1024}));
assert.equal(await S.verifySource(packet,pages),true);
await assert.rejects(S.verifySource(packet,{...pages,9:pages[9]+' '}),/Slice|Body/);
await assert.rejects(S.verifySource(packet,{...pages,1:pages[1]+' '}),/Unassigned/);
assert.equal(S.cp('a🧩b',1,2),'🧩');
const items=S.items(packet);assert.equal(items.length,669);assert.equal(new Set(items.map(x=>x.key)).size,669);assert.equal(items.filter(x=>x.kind==='TITLE').length,31);assert.equal(items.filter(x=>x.kind==='REGION').length,9);
const blank=S.make(packet);assert.ok(S.validate(blank,packet));assert.deepEqual(S.progress(blank),{done:0,pending:669,total:669,rejected:0});
const meta={reviewer:'synthetic-test',rationale:'Synthetic record only',evidence:['fixture:page9'],reviewedAt:'2026-11-24T15:00:00.000Z'};
const e=packet.entries[0],raw=S.candidate(pages,e,blank).map(x=>x.text).join('');assert.equal(await S.hash(raw),e.rawSpanSha256);
const accepted=S.update(blank,packet,'T-01:exclusion:0','ACCEPT',meta),removed=S.candidate(pages,e,accepted).map(x=>x.text).join('');const [p,a,b]=e.proposedExclusions[0];assert.equal(removed,raw.slice(0,a-e.start.offset)+raw.slice(b-e.start.offset));
const rejected=S.update(accepted,packet,'T-01:exclusion:0','REJECT',meta);assert.equal(S.candidate(pages,e,rejected).map(x=>x.text).join(''),raw);assert.equal(S.progress(rejected).rejected,1);assert.deepEqual(S.update(rejected,packet,'T-01:exclusion:0','NEEDS_REVIEW'),blank);
for(const mutate of [s=>s.sourceHtmlSha256='0'.repeat(64),s=>s.packetSha256='0'.repeat(64),s=>s.records.pop(),s=>s.records[0].key=s.records[1].key,s=>s.records[0].decision='VERIFIED',s=>s.records[0].evidence=['fake'],s=>s.verifiedBodies=91]){const bad=structuredClone(blank);mutate(bad);assert.throws(()=>S.validate(bad,packet));}
for(const m of [{...meta,evidence:[]},{...meta,rationale:''},{...meta,reviewedAt:'2026-02-30T00:00:00.000Z'},{...meta,reviewedAt:'0000-01-01T00:00:00.000Z'}])assert.throws(()=>S.update(blank,packet,'T-01:owner','ACCEPT',m));
const extra=S.update(accepted,packet,items.find(x=>x.kind==='TITLE').key,'REJECT',meta),dir=mkdtempSync(join(tmpdir(),'gnome-state-'));
try{const file=join(dir,'session.json');writeFileSync(file,JSON.stringify(extra));const result=JSON.parse(execFileSync('python',['tools/validate_current_review_session.py',file],{encoding:'utf8'}));assert.equal(result.completedReviewRecords,2);assert.equal(result.independentlyVerifiedBodies,0);}finally{rmSync(dir,{recursive:true,force:true});}
console.log('Current review state: exact source/packet, 669 keys, range hashes, Unicode, accept/reject/defer, tamper controls, cross-runtime validation PASS');
