(function(){
'use strict';
const $=id=>document.getElementById(id);
const file=$('capsule-file');
const MAX=4*1024*1024;
function shown(id,s){$(id).textContent=String(s);}
function add(parent,tag,text){const el=document.createElement(tag);el.textContent=String(text);parent.appendChild(el);return el;}
function dl(id, data){const parent=$(id);parent.replaceChildren();Object.entries(data).forEach(([k,v])=>{add(parent,'dt',k);add(parent,'dd',v==null?'UNKNOWN':v)});}
function safeJSON(text){return JSON.parse(text);}
function stable(value){
 if(value===null)return 'null';
 if(typeof value==='string'||typeof value==='number'||typeof value==='boolean'){
   if(typeof value==='number'&&!Number.isFinite(value))throw Error('NONFINITE_VALUE');
   return JSON.stringify(value);
 }
 if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
 if(typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
 throw Error('UNSUPPORTED_VALUE');
}
async function hash(value){
 if(!crypto || !crypto.subtle)throw Error('SHA256_UNAVAILABLE');
 const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(stable(value)));
 return Array.from(new Uint8Array(digest)).map(x=>x.toString(16).padStart(2,'0')).join('');
}
async function inspect(c){
 if(!c||typeof c!=='object'||Array.isArray(c)||c.schemaVersion!=='gnome.reactor.evidence.v3')throw Error('UNSUPPORTED_CAPSULE_SCHEMA');
 for(const key of ['campaign','interventions','execution','evaluation','findings','integrity']){
   if(!c[key]||typeof c[key]!=='object'||Array.isArray(c[key]))throw Error('INVALID_SECTION:'+key);
 }
 const checks=c.integrity.checksums, manifest=c.integrity.manifest;
 if(!checks||typeof checks!=='object'||!manifest||typeof manifest!=='object')throw Error('MISSING_CHECKSUMS');
 const states=[];
 for(const key of ['campaign','interventions','execution','evaluation','findings','manifest']){
   const actual=await hash(key==='manifest'?manifest:c[key]);
   const expected=checks[key];
   states.push({part:key,valid:typeof expected==='string'&&expected===actual});
 }
 const ok=states.every(x=>x.valid);
 const title=ok?'CHECKSUMS MATCH — NOT A SCIENTIFIC VERIFICATION':'REJECTED: INTEGRITY CHECK FAILED';
 shown('status',title);
 $('status').className=ok?'ok':'fail';
 shown('integrity-result',states.map(x=>`${x.valid?'PASS':'FAIL'}  ${x.part}`).join('\n'));
 if(!ok){clearData();return;}
 const camp=c.campaign,plan=camp.plan||{},exec=c.execution,evalData=c.evaluation;
 shown('run-state',exec.status||'UNKNOWN');
 shown('pairs',evalData.counts?.validPairedTrials??'—');
 shown('induced',evalData.counts?.variantInducedFailures??'—');
 dl('source-meta',{'Campaign ID':camp.campaignId||'UNKNOWN', 'Family':camp.family||'UNKNOWN',
      'Manual body status':plan.sourceRef?.bodyStatus||'UNKNOWN',
      'Source SHA-256':plan.sourceRef?.sourceSha256||'UNKNOWN',
      'Synthetic fixture':camp.isSyntheticDemo===true?'YES — NOT EMPIRICAL':'DECLARED NO — NOT AUTHENTICATED',
      'References recorded':Array.isArray(camp.references)?camp.references.length:'UNKNOWN'});
 const it=c.interventions;
 dl('intervention-meta',{'Type':it.type||'UNKNOWN','ID':it.interventionId||'UNKNOWN',
    'Mutation SHA-256':it.mutationHash||'NOT APPLICABLE','Task SHA-256':it.fixedTaskHash||'UNKNOWN',
    'Reference authority':'NOT INDEPENDENTLY AUTHENTICATED'});
 const tbody=$('trial-rows');tbody.replaceChildren();
 const records=Array.isArray(exec.observations)?exec.observations:[];
 if(!records.length){const tr=document.createElement('tr');const td=add(tr,'td','NO RECORDED OUTPUTS');td.colSpan=4;tbody.appendChild(tr);}
 records.slice(0,1024).forEach(o=>{const tr=document.createElement('tr');
   [o.inputId+' / '+o.trialId,o.condition,o.model,String(o.outputText||'').slice(0,260)].forEach(s=>add(tr,'td',s??'UNKNOWN'));
   tbody.appendChild(tr);
 });
 const p=$('claims');p.replaceChildren();
 const claims=Array.isArray(c.findings.claims)?c.findings.claims:[];
 if(!claims.length)add(p,'p','No recorded claims');
 claims.forEach(cl=>{const div=add(p,'p',`${cl.claimId||'NO ID'} — ${cl.status||'UNKNOWN'}: ${cl.statement||'No statement'}`);div.className='meta';});
}
function clearData(){
 shown('run-state','—');shown('pairs','—');shown('induced','—');
 dl('source-meta',{'Origin':'No valid capsule'});
 dl('intervention-meta',{'Binding':'No valid capsule'});
 const tbody=$('trial-rows');tbody.replaceChildren();
 const tr=document.createElement('tr');const td=add(tr,'td','No verified capsule');td.colSpan=4;tbody.appendChild(tr);
 $('claims').replaceChildren();add($('claims'),'p','No valid capsule loaded');
}
file.addEventListener('change',async function(){
 clearData();
 const f=file.files&&file.files[0];if(!f)return;
 if(f.size>MAX){shown('status','REJECTED: FILE TOO LARGE');return;}
 shown('status','Inspecting local JSON and hashes…');
 try{await inspect(safeJSON(await f.text()));}
 catch(e){shown('status','REJECTED: '+String(e.message||e));$('status').className='fail';shown('integrity-result','Not verified');clearData();}
});
})();
