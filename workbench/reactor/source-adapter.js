(function(root){'use strict';
const EXPECTED_SOURCE='1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19';
async function loadIndex(path){
 const response=await fetch(path||'../data/entry_identity_index.json',{cache:'no-store'});
 if(!response.ok)throw Error('SOURCE_INDEX_FETCH_FAILED:'+response.status);
 const data=await response.json();
 if(data.schemaVersion!=='gnome.manual.identity-index.v1'||data.sourceIndexSha256!==EXPECTED_SOURCE||data.entries?.length!==91||data.counts?.total!==91||data.bodyCoverage!==0||new Set(data.entries.map(e=>e.id)).size!==91)throw Error('INVALID_SOURCE_INDEX');
 return {canonicalPages:data.counts.pages,reconciledIdentities:data.entries.length,verifiedBodies:0,sourceHtmlSha256:data.sourceIndexSha256,entries:data.entries.map(e=>({id:e.id,title:e.titleCandidate,titleAuthority:e.titleAuthority,editorialStatus:e.status,bodyStatus:'UNVERIFIED_SOURCE_CANDIDATE',sourceRef:'index.html sha256:'+data.sourceIndexSha256,occurrencePages:e.occurrencePages}))};
}
function buildSourceReference(entry,isUserTranscription){return {entryId:entry.id,titleCandidate:entry.title,titleAuthority:entry.titleAuthority,editorialStatus:entry.editorialStatus,bodyStatus:isUserTranscription?'EXPERIMENTAL_TRANSCRIPTION':entry.bodyStatus,sourceRef:entry.sourceRef,inheritsCanonicalVerification:false};}
root.ReactorSourceAdapter={loadIndex,buildSourceReference};
})(typeof window!=='undefined'?window:globalThis);
