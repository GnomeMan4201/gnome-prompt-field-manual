(function(root){'use strict';
// V2 data path: recalculate results from raw output and reviewer-supplied exact references.
// Neither the reference nor the model's output is trusted as an authenticated fact.
const PLAN='gnome.reactor.evaluation-plan.v1', CAPSULE='gnome.reactor.evidence.v2';
const MAX=512, MAX_BYTES=256*1024;
function fail(msg){throw new Error(msg);}
function require_(v,msg){if(!v)fail(msg);}
function ident(x){return typeof x==='string'&&x.length>0&&x.length<=128&&x.trim()===x&&!x.includes('\0');}
function stable(o){if(o===null||typeof o!=='object')return JSON.stringify(o);if(Array.isArray(o))return '['+o.map(stable).join(',')+']';return '{'+Object.keys(o).sort().map(k=>JSON.stringify(k)+':'+stable(o[k])).join(',')+'}';}
function bytes(x){return new TextEncoder().encode(x).length;}
async function sha(x){return root.ReactorExperimentCore.sha256Hex(x);}
function validTemp(x){return typeof x==='number'&&Number.isFinite(x)&&x>=0&&x<=2&&Math.abs(Math.round(x*1000)-x*1000)<1e-9;}
function validatePlan(p){
 require_(p&&typeof p==='object'&&!Array.isArray(p),'PLAN_NOT_OBJECT');
 require_(p.schemaVersion===PLAN,'UNSUPPORTED_PLAN_SCHEMA');
 for(const k of ['planId','experimentId','datasetId','provider','model'])require_(ident(p[k]),'INVALID_PLAN_FIELD:'+k);
 require_(p.evaluator==='GNOME_EXACT_REFERENCE_V1','UNSUPPORTED_EVALUATOR');
 require_(validTemp(p.temperature),'INVALID_TEMPERATURE');
 require_(Object.hasOwn(p,'seed')&&(p.seed===null||Number.isInteger(p.seed)&&p.seed>=-2147483648&&p.seed<=2147483647),'INVALID_SEED');
 require_(Array.isArray(p.tools)&&p.tools.length===0,'TOOLS_NOT_SUPPORTED');require_(!Object.hasOwn(p,'isSyntheticDemo')||typeof p.isSyntheticDemo==='boolean','INVALID_SYNTHETIC_LABEL');
 require_(p.prompts&&typeof p.prompts==='object','INVALID_PROMPTS');
 for(const k of ['control','variant'])require_(typeof p.prompts[k]==='string'&&p.prompts[k].trim(),'MISSING_PROMPT:'+k);
 require_(p.prompts.control!==p.prompts.variant,'IDENTICAL_PROMPTS');
 const r=p.rules;require_(r&&typeof r==='object','INVALID_RULES');
 require_(r.requireJsonObject===true,'JSON_OBJECT_REQUIRED');require_(r.additionalProperties===false,'STRICT_KEYS_REQUIRED');
 for(const k of ['requiredFields','forbiddenTokens']){
  const a=r[k];require_(Array.isArray(a)&&a.length<=50&&a.every(x=>typeof x==='string'&&x.length>0&&x.length<=128),'INVALID_RULE:'+k);
  require_(new Set(a).size===a.length,'DUPLICATE_RULE:'+k);
 }
 require_(r.requiredFields.length>0&&r.forbiddenTokens.length>0,'INSUFFICIENT_RULES');
 require_(Array.isArray(p.inputs)&&p.inputs.length>0&&p.inputs.length<=MAX,'INVALID_INPUTS');
 const ids=new Set();for(const inp of p.inputs){
  require_(inp&&ident(inp.inputId),'INVALID_INPUT_ID');require_(!ids.has(inp.inputId),'DUPLICATE_INPUT_ID');ids.add(inp.inputId);
  require_(typeof inp.text==='string'&&bytes(inp.text)<=MAX_BYTES,'INVALID_INPUT_TEXT');
  const ref=inp.reference;require_(ref&&ref.expectedJson&&typeof ref.expectedJson==='object'&&!Array.isArray(ref.expectedJson)&&Object.keys(ref.expectedJson).length>0,'MISSING_EXACT_REFERENCE');
  require_(Object.entries(ref.expectedJson).every(([k,v])=>typeof k==='string'&&k.length>0&&k.length<=128&&(v===null||typeof v==='string'||typeof v==='boolean'||Number.isSafeInteger(v))),'UNSUPPORTED_REFERENCE_VALUE');
  require_(new Set(r.requiredFields).size===Object.keys(ref.expectedJson).length&&r.requiredFields.every(x=>Object.hasOwn(ref.expectedJson,x)),'REFERENCE_KEYS_MUST_MATCH_RULES');
  require_(Array.isArray(ref.evidenceRefs)&&ref.evidenceRefs.length>0&&ref.evidenceRefs.every(ident),'MISSING_REFERENCE_PROVENANCE');
 }
 require_(p.sourceRef&&['UNVERIFIED_SOURCE_CANDIDATE','EXPERIMENTAL_TRANSCRIPTION'].includes(p.sourceRef.bodyStatus),'SOURCE_TRUTH_NOT_DECLARED');require_(ident(p.sourceRef.entryId)&&/^[a-f0-9]{64}$/.test(p.sourceRef.sourceSha256),'UNBOUND_SOURCE_REFERENCE');
}
function scoreText(text, rules, ref){
 if(typeof text!=='string'||bytes(text)>MAX_BYTES)return {deterministic:'UNKNOWN',grounded:'NOT_ASSESSABLE',reason:'INVALID_OUTPUT'};
 const forbidden=rules.forbiddenTokens.some(t=>text.includes(t));let v;
 try{v=JSON.parse(text);}catch(e){return {deterministic:forbidden?'FAIL':'UNKNOWN',grounded:'NOT_ASSESSABLE',reason:'INVALID_JSON'};}
 if(!v||typeof v!=='object'||Array.isArray(v))return {deterministic:'FAIL',grounded:'NOT_ASSESSABLE',reason:'NOT_JSON_OBJECT'};
 const refKeys=rules.requiredFields;const keys=Object.keys(v);
 const sameKeys=keys.length===refKeys.length&&refKeys.every(k=>Object.hasOwn(v,k));
 const deterministic=(forbidden||!sameKeys)?'FAIL':'PASS';const expected=ref.expectedJson;
 const conflicts=Object.entries(expected).some(([k,x])=>Object.hasOwn(v,k)&&(typeof v[k]!==typeof x||stable(v[k])!==stable(x)));
 const grounded=conflicts?'CONTRADICTED':(sameKeys&&stable(v)===stable(expected)?'SUPPORTED':'UNSUPPORTED');
 return {deterministic,grounded,reason:'EXACT_REFERENCE_RULES',evidenceRefs:ref.evidenceRefs};
}
function status(e){if(e.deterministic==='PASS'&&e.grounded==='SUPPORTED')return true;if(e.deterministic==='FAIL'&&e.grounded==='CONTRADICTED')return false;return null;}
async function validateObservations(plan,obs){
 require_(Array.isArray(obs)&&obs.length>0&&obs.length<=2*MAX,'INVALID_OBSERVATIONS');
 const ids=new Set(),slots=new Set(),refs=Object.fromEntries(plan.inputs.map(x=>[x.inputId,x]));
 const rh=await sha(stable(plan.rules));const prompts={CONTROL:await sha(plan.prompts.control),VARIANT:await sha(plan.prompts.variant)};
 for(const [i,o] of obs.entries()){
  const prefix='OBSERVATION_'+i+':';require_(o&&typeof o==='object'&&!Array.isArray(o),prefix+'NOT_OBJECT');
  require_(o.schemaVersion==='gnome.reactor.observation.v1',prefix+'SCHEMA');
  require_(ident(o.runId)&&ident(o.trialId),prefix+'MISSING_IDS');require_(!ids.has(o.runId),prefix+'DUPLICATE_RUN_ID');ids.add(o.runId);
  require_(Object.hasOwn(refs,o.inputId)&&['CONTROL','VARIANT'].includes(o.condition),prefix+'UNKNOWN_INPUT_OR_CONDITION');
  const slot=stable([o.inputId,o.trialId,o.condition]);require_(!slots.has(slot),prefix+'DUPLICATE_SLOT');slots.add(slot);
  require_(o.experimentId===plan.experimentId,prefix+'EXPERIMENT_MISMATCH');require_(o.datasetId===plan.datasetId,prefix+'DATASET_MISMATCH');
  for(const k of ['provider','model','evaluator','temperature','seed','tools'])require_(Object.hasOwn(o,k)&&stable(o[k])===stable(plan[k]),prefix+'CONFIG_MISMATCH:'+k);
  require_(o.inputHash===await sha(refs[o.inputId].text),prefix+'INPUT_HASH_MISMATCH');
  require_(o.promptHash===prompts[o.condition],prefix+'PROMPT_HASH_MISMATCH');require_(o.rubricHash===rh,prefix+'RUBRIC_HASH_MISMATCH');
  require_(typeof o.outputText==='string'&&bytes(o.outputText)<=MAX_BYTES,prefix+'INVALID_OUTPUT');
  require_(!['passed','evaluation','disposition'].some(k=>Object.hasOwn(o,k)),prefix+'IMPORTED_VERDICT_BLOCKED');
 }
}
async function analyze(plan,obs){
 validatePlan(plan);await validateObservations(plan,obs);
 const refs=Object.fromEntries(plan.inputs.map(x=>[x.inputId,x.reference]));const groups=new Map();
 for(const o of obs){const key=stable([o.inputId,o.trialId]);if(!groups.has(key))groups.set(key,{inputId:o.inputId,trialId:o.trialId});groups.get(key)[o.condition]=o;}
 const counts={validPairedTrials:0,missingTrials:0,baselineFailures:0,variantInducedFailures:0,sharedFailures:0,variantImprovements:0,bothPass:0,unattributableCount:0};
 const outcomes=[];const sorted=[...groups.values()].sort((a,b)=>a.inputId<b.inputId?-1:a.inputId>b.inputId?1:a.trialId<b.trialId?-1:a.trialId>b.trialId?1:0);
 for(const g of sorted){
  const c=g.CONTROL,v=g.VARIANT;let cls,reason,ce,ve;
  if(!c||!v){counts.missingTrials++;counts.unattributableCount++;outcomes.push({inputId:g.inputId,trialId:g.trialId,attribution:'UNATTRIBUTABLE',reason:'MISSING_PAIRED_TRIAL'});continue;}
  ce=scoreText(c.outputText,plan.rules,refs[g.inputId]);ve=scoreText(v.outputText,plan.rules,refs[g.inputId]);const cp=status(ce),vp=status(ve);
  if(cp===null||vp===null){cls='UNATTRIBUTABLE';reason='INSUFFICIENT_REFERENCE_BOUND_SCORING';}
  else{cls=root.ReactorComparisonEngine.classifyPairedTrial({...c,passed:cp},{...v,passed:vp});reason=cls==='UNATTRIBUTABLE'?'STRICT_COMPARABILITY_REJECTED':'MATCHED_REFERENCE_BOUND_EVALUATION';}
  if(cls==='UNATTRIBUTABLE')counts.unattributableCount++;
  else{counts.validPairedTrials++;const bins={SHARED_FAILURE:'sharedFailures',VARIANT_INDUCED_FAILURE:'variantInducedFailures',VARIANT_IMPROVEMENT:'variantImprovements',BOTH_PASS:'bothPass'};counts[bins[cls]]++;if(['SHARED_FAILURE','VARIANT_IMPROVEMENT'].includes(cls))counts.baselineFailures++;}
  outcomes.push({inputId:g.inputId,trialId:g.trialId,attribution:cls,reason,controlEvaluation:ce,variantEvaluation:ve});
 }
 const n=counts.validPairedTrials;
 return {schemaVersion:'gnome.reactor.analysis.v2',scoringMode:'REFERENCE_BOUND_DETERMINISTIC_ONLY',referenceAuthority:'REVIEWER_SUPPLIED_UNAUTHENTICATED',replayMode:'COMPUTATIONAL_REPLAY_ONLY',counts,observedVariantInducedFailureProportion:n?counts.variantInducedFailures/n:null,outcomes};
}
async function checksums(manifest,payload){return {'manifest.json':await sha(stable(manifest)),'plan.json':await sha(stable(payload.plan)),'observations.json':await sha(stable(payload.observations)),'analysis.json':await sha(stable(payload.analysis))};}
async function buildCapsule(plan,obs){const analysis=await analyze(plan,obs);const payload={plan:JSON.parse(JSON.stringify(plan)),observations:JSON.parse(JSON.stringify(obs)),analysis};
 const manifest={schemaVersion:CAPSULE,planId:plan.planId,planHash:await sha(stable(plan)),sourceSha256:plan.sourceRef.sourceSha256,referenceAuthority:'REVIEWER_SUPPLIED_UNAUTHENTICATED',isSyntheticDemo:Boolean(plan.isSyntheticDemo),replayMode:'COMPUTATIONAL_REPLAY_ONLY'};
 return {schemaVersion:CAPSULE,manifest,payload,integrity:{checksums:await checksums(manifest,payload)}};}
async function verifyCapsule(cap){try{
 require_(cap&&cap.schemaVersion===CAPSULE,'UNSUPPORTED_CAPSULE_VERSION');const m=cap.manifest,p=cap.payload,s=cap.integrity.checksums;
 require_(m&&p&&s,'INVALID_CAPSULE_SHAPE');require_(Object.keys(cap).length===4&&['schemaVersion','manifest','payload','integrity'].every(k=>Object.hasOwn(cap,k)),'UNEXPECTED_CAPSULE_FIELDS');const actual=await checksums(m,p);require_(Object.keys(s).length===4&&Object.keys(actual).every(k=>Object.hasOwn(s,k)),'INVALID_CHECKSUM_SET');
 for(const [k,v] of Object.entries(actual))require_(s[k]===v,'CHECKSUM_MISMATCH:'+k);
 require_(m.planId===p.plan.planId,'PLAN_ID_MISMATCH');require_(m.sourceSha256===p.plan.sourceRef.sourceSha256,'SOURCE_HASH_DECLARATION_MISMATCH');require_(m.planHash===await sha(stable(p.plan)),'PLAN_HASH_MISMATCH');
 require_(m.schemaVersion===CAPSULE&&m.replayMode==='COMPUTATIONAL_REPLAY_ONLY','INVALID_MANIFEST');require_(typeof m.isSyntheticDemo==='boolean'&&m.isSyntheticDemo===Boolean(p.plan.isSyntheticDemo),'SYNTHETIC_LABEL_MISMATCH');
 const result=await analyze(p.plan,p.observations);require_(stable(result)===stable(p.analysis),'REPLAY_MISMATCH');
 return {valid:true,errors:[],replay:result};
 }catch(e){return {valid:false,errors:[String(e.message||e)],replay:null};}}
root.ReactorEvidenceV2={stable,sha,validatePlan,scoreText,analyze,buildCapsule,verifyCapsule};
})(typeof window!=='undefined'?window:globalThis);
