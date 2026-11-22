(function(root){'use strict';
const hex=/^[a-f0-9]{64}$/;
function validateExperiment(e){const errors=[];if(!e||e.schemaVersion!=='gnome.reactor.experiment.v1')errors.push('INVALID_SCHEMA_VERSION');if(!e||!e.experimentId||!e.hypothesis||!hex.test(e.controlPromptHash)||!hex.test(e.variantPromptHash)||!e.dataset||!e.dataset.datasetId||!Array.isArray(e.dataset.inputs)||!e.dataset.inputs.length||!e.rubric||!Array.isArray(e.rubric.criteria)||!e.rubric.criteria.length||!e.modelConfig||!e.modelConfig.provider||!e.modelConfig.model)errors.push('INVALID_EXPERIMENT');if(e?.dataset?.inputs){const ids=e.dataset.inputs.map(x=>x.inputId);if(new Set(ids).size!==ids.length)errors.push('DUPLICATE_INPUT_ID');}return errors;}
async function validateObservations(arr,e){const errors=[];if(!Array.isArray(arr))return ['OBSERVATIONS_NOT_ARRAY'];if(!e||!e.dataset||!Array.isArray(e.dataset.inputs))return ['INVALID_EXPERIMENT'];
const core=root.ReactorExperimentCore;const runIds=new Set(),slots=new Set(),inputIds=new Set(e.dataset.inputs.map(x=>x.inputId));
const rubricHash=await core.sha256Hex(root.ReactorEvidenceCapsule.stableStringify(e.rubric));
for(let i=0;i<arr.length;i++){const o=arr[i],pre='OBSERVATION_'+i;if(!o||o.schemaVersion!=='gnome.reactor.observation.v1'||!o.runId||!o.experimentId||!o.inputId||!['CONTROL','VARIANT'].includes(o.condition)||!hex.test(o.inputHash)||!hex.test(o.promptHash)||!Object.hasOwn(o,'outputText')||o.outputText!==null&&typeof o.outputText!=='string'||o.passed!=null&&typeof o.passed!=='boolean'){errors.push(pre+':INVALID_OBSERVATION');continue;}
const key=JSON.stringify([o.experimentId,o.inputId,o.trialId??'trial-1',o.condition]);if(runIds.has(o.runId)||slots.has(key))errors.push(pre+':DUPLICATE_OBSERVATION');runIds.add(o.runId);slots.add(key);
if(o.experimentId!==e.experimentId||!inputIds.has(o.inputId)||o.promptHash!==(o.condition==='CONTROL'?e.controlPromptHash:e.variantPromptHash))errors.push(pre+':EXPERIMENT_OR_PROMPT_MISMATCH');
if(o.datasetId!=null&&o.datasetId!==e.dataset.datasetId)errors.push(pre+':DATASET_MISMATCH');
const input=e.dataset.inputs.find(x=>x.inputId===o.inputId);if(input&&typeof input.text==='string'&&o.inputHash!==await core.sha256Hex(input.text))errors.push(pre+':INPUT_CONTENT_HASH_MISMATCH');
if(o.rubricHash!=null&&o.rubricHash!==rubricHash)errors.push(pre+':RUBRIC_HASH_MISMATCH');
const model=e.modelConfig||{};for(const k of ['provider','model','temperature','seed','tools']){if(model[k]!=null&&o[k]!=null&&JSON.stringify(model[k])!==JSON.stringify(o[k]))errors.push(pre+':MODEL_CONFIG_MISMATCH:'+k);}}
return errors;}
root.ReactorObservationValidator={validateExperiment,validateObservations};
})(typeof window!=='undefined'?window:globalThis);
