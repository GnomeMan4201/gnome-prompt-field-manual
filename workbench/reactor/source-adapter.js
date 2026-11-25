(function(root){'use strict';
const EXPECTED_SOURCE='33fa2e969ea76969a2c82964d2c0289ec8836953e69275a5d29034b9e893b871';
const PACKET_SCHEMA='gnome.manual.current-body-review.v1';
// Display headings come from the candidate packet's source-bound declaration headings.
// They name entries; they do not verify bodies. The identity index title remains advisory.
const HEADING_SOURCE='current_body_review.json canonicalHeadingCandidate (ID+title line followed by Criteria; not body verification)';
async function fetchJson(path,code){
 const response=await fetch(path,{cache:'no-store'});
 if(!response.ok)throw Error(code+':'+response.status);
 return response.json();
}
function headingErrors(packet,data){
 if(!packet||packet.schemaVersion!==PACKET_SCHEMA)return 'PACKET_SCHEMA_INVALID';
 if(packet.sourceHtmlSha256!==EXPECTED_SOURCE)return 'PACKET_SOURCE_STALE';
 const rows=packet.entries||[];
 if(rows.length!==91||new Set(rows.map(r=>r.entryId)).size!==91)return 'PACKET_ENTRY_SET_INVALID';
 const byId=new Map(rows.map(r=>[r.entryId,r]));
 for(const e of data.entries){
  const r=byId.get(e.id);
  if(!r)return 'PACKET_MISSING_ID:'+e.id;
  // The packet records the advisory title and status it was built from; both must match this index.
  if(r.advisoryIdentityTitle!==e.titleCandidate||r.editorialStatus!==e.status)return 'PACKET_IDENTITY_MISMATCH:'+e.id;
  const heading=r.canonicalHeadingCandidate;
  if(typeof heading!=='string'||!heading.trim()||typeof r.headingRaw!=='string'||r.headingRaw.trim()!==e.id+' '+heading)return 'PACKET_HEADING_INVALID:'+e.id;
 }
 return null;
}
async function loadIndex(path,packetPath){
 const data=await fetchJson(path||'../data/current_entry_identity_index.json','SOURCE_INDEX_FETCH_FAILED');
 if(data.schemaVersion!=='gnome.manual.identity-index.v1'||data.sourceIndexSha256!==EXPECTED_SOURCE||data.entries?.length!==91||data.counts?.total!==91||data.bodyCoverage!==0||new Set(data.entries.map(e=>e.id)).size!==91)throw Error('INVALID_SOURCE_INDEX');
 let packet=null,headingStatus;
 try{packet=await fetchJson(packetPath||'../data/current_body_review.json','HEADING_SOURCE_FETCH_FAILED');headingStatus=headingErrors(packet,data);}
 catch(e){headingStatus=e.message;}
 const headings=headingStatus?null:new Map(packet.entries.map(r=>[r.entryId,r.canonicalHeadingCandidate]));
 return {canonicalPages:data.counts.pages,reconciledIdentities:data.entries.length,verifiedBodies:0,sourceHtmlSha256:data.sourceIndexSha256,
  headingSource:headings?HEADING_SOURCE:null,headingStatus:headingStatus||'BOUND',
  entries:data.entries.map(e=>({id:e.id,title:headings?headings.get(e.id):null,advisoryTitle:e.titleCandidate,titleAuthority:e.titleAuthority,editorialStatus:e.status,bodyStatus:'UNVERIFIED_SOURCE_CANDIDATE',sourceRef:'index.html sha256:'+data.sourceIndexSha256,occurrencePages:e.occurrencePages}))};
}
function displayTitle(entry){return entry.title||('heading unavailable; advisory candidate: '+(entry.advisoryTitle||'none'));}
// Exported references keep the advisory identity-index title under its existing name and authority.
function buildSourceReference(entry,isUserTranscription){return {entryId:entry.id,titleCandidate:entry.advisoryTitle,titleAuthority:entry.titleAuthority,editorialStatus:entry.editorialStatus,bodyStatus:isUserTranscription?'EXPERIMENTAL_TRANSCRIPTION':entry.bodyStatus,sourceRef:entry.sourceRef,inheritsCanonicalVerification:false};}
root.ReactorSourceAdapter={loadIndex,buildSourceReference,displayTitle,headingErrors};
})(typeof window!=='undefined'?window:globalThis);
