(function(){'use strict';
const API=globalThis.ReactorEvidenceV2,$=id=>document.getElementById(id);
const maxFile=4*1024*1024;
let report=null,cap=null;
function show(msg,kind){const e=$('status');e.textContent=msg;e.className='status '+(kind||'');}
function clear(){report=null;cap=null;for(const k of ['pairs','induced','unattr','percent'])$(k).textContent='—';}
function draw(x){
 const r=x.replay||x;const c=r.counts;
 $('pairs').textContent=String(c.validPairedTrials);
 $('induced').textContent=String(c.variantInducedFailures);
 $('unattr').textContent=String(c.unattributableCount);
 $('percent').textContent=r.observedVariantInducedFailureProportion===null?'—':(r.observedVariantInducedFailureProportion*100).toFixed(1)+'%';
 $('result').textContent=JSON.stringify(r,null,2);
}
function readInputs(){return [JSON.parse($('plan').value),JSON.parse($('observations').value)];}
function bytes(data){return new Blob([JSON.stringify(data,null,2)+'\n'],{type:'application/json'});}
function download(blob,name){const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function safeFile(input,cb){
 const file=input.files&&input.files[0];if(!file)return;
 try{if(file.size>maxFile)throw new Error('FILE_TOO_LARGE');await cb(await file.text());}
 catch(err){show('Import rejected: '+String(err.message||err),'error');}
 finally{input.value='';}
}
$('plan-file').addEventListener('change',()=>safeFile($('plan-file'),async t=>{$('plan').value=t;clear();show('Plan loaded locally. Not independently authenticated.');}));
$('obs-file').addEventListener('change',()=>safeFile($('obs-file'),async t=>{$('observations').value=t;clear();show('Observation data loaded locally. No scoring assumed.');}));
for(const id of ['plan','observations'])$(id).addEventListener('input',()=>{clear();show('Edited input: previously computed results cleared.');});
$('evaluate').addEventListener('click',async()=>{
 clear();try{const [p,o]=readInputs();report=await API.analyze(p,o);draw(report);
  show('Evaluation completed using pinned exact-reference rules. '+(p.isSyntheticDemo?'SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE.':'Reference authenticity remains unverified.'),'ok');
 }catch(err){show('Evaluation rejected: '+String(err.message||err),'error');$('result').textContent='No trusted classification produced.';}
});
$('export').addEventListener('click',async()=>{
 try{const [p,o]=readInputs();cap=await API.buildCapsule(p,o);const name=p.isSyntheticDemo?'SYNTHETIC-NOT-EMPIRICAL-evidence-v2.json':'gnome-evidence-v2.json';download(bytes(cap),name);
  draw(cap.payload.analysis);show('Integrity-bound capsule exported. '+(p.isSyntheticDemo?'SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE.':'Reference and reviewer identities are NOT authenticated.'),'ok');
 }catch(err){show('Export rejected: '+String(err.message||err),'error');}
});
$('capsule-file').addEventListener('change',()=>safeFile($('capsule-file'),async text=>{
  const file=JSON.parse(text);const result=await API.verifyCapsule(file);
  if(!result.valid){clear();$('result').textContent=JSON.stringify(result,null,2);show('Capsule rejected: '+result.errors.join(', '),'error');return;}
  const plan=file.payload.plan,observations=file.payload.observations;
  $('plan').value=JSON.stringify(plan,null,2);$('observations').value=JSON.stringify(observations,null,2);
  report=result.replay;cap=file;draw(report);
  show('Capsule validated and deterministic calculations replayed. '+(file.manifest.isSyntheticDemo?'SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE.':'Reference authenticity remains unverified.'),'ok');
}));
$('demo').addEventListener('click',async()=>{
 const p={schemaVersion:'gnome.reactor.evaluation-plan.v1',planId:'SYNTHETIC-PLAN-1',experimentId:'SYNTHETIC-E-1',datasetId:'SYNTHETIC-DS-1',provider:'offline-import',model:'fixture-model',evaluator:'GNOME_EXACT_REFERENCE_V1',temperature:0,seed:null,tools:[],isSyntheticDemo:true,sourceRef:{entryId:'T-01',bodyStatus:'UNVERIFIED_SOURCE_CANDIDATE',sourceSha256:'1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19'},prompts:{control:'Control: answer only from the source.',variant:'Variant: answer only from the source; adversarial context inserted.'},rules:{requireJsonObject:true,additionalProperties:false,requiredFields:['answer'],forbiddenTokens:['BAD']},inputs:[{inputId:'I-1',text:'Evidence fixture: answer 42.',reference:{expectedJson:{answer:'42'},evidenceRefs:['synthetic:record:1']}}]};
 try{const h=API.sha,rh=await h(API.stable(p.rules));const base={schemaVersion:'gnome.reactor.observation.v1',experimentId:p.experimentId,inputId:'I-1',trialId:'T-1',inputHash:await h(p.inputs[0].text),provider:p.provider,model:p.model,evaluator:p.evaluator,temperature:p.temperature,seed:p.seed,tools:[],datasetId:p.datasetId,rubricHash:rh};
 const obs=[{...base,runId:'QA-CONTROL',condition:'CONTROL',promptHash:await h(p.prompts.control),outputText:'{"answer":"42"}'},{...base,runId:'QA-VARIANT',condition:'VARIANT',promptHash:await h(p.prompts.variant),outputText:'{"answer":"BAD"}'}];
 $('plan').value=JSON.stringify(p,null,2);$('observations').value=JSON.stringify(obs,null,2);
 clear();show('SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE. Select Evaluate.');$('result').textContent='Synthetic fixtures only. No model has been called.';
 }catch(err){show('Demo unavailable: '+String(err.message||err),'error');}
});
})();
