(function(root){'use strict';
const KEYS=['experimentId','inputId','inputHash','provider','model','evaluator','temperature','seed','tools','datasetId','rubricHash'];
const HARD=['experimentId','inputId','inputHash','provider','model','evaluator','tools','datasetId','rubricHash'];
function present(x){return x!==null&&x!==undefined&&x!=='';}
function same(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function evaluateComparability(a,b){let diffs=[],missing=[];a=a||{};b=b||{};for(const k of KEYS){const x=a[k],y=b[k];if(k==='seed'&&Object.hasOwn(a,k)&&Object.hasOwn(b,k)&&x===null&&y===null)continue;if(!present(x)||!present(y))missing.push(k);else if(!same(x,y))diffs.push(k);}return {status:diffs.some(k=>HARD.includes(k))?'NOT_COMPARABLE':diffs.length||missing.length?'COMPARABLE_WITH_DISCLOSED_LIMITATIONS':'COMPARABLE',confounders:diffs,missingMetadata:missing};}
function classifyPairedTrial(c,v){if(!c||!v||c.condition!=='CONTROL'||v.condition!=='VARIANT'||c.outputText==null||v.outputText==null)return 'UNATTRIBUTABLE';if(typeof c.passed!=='boolean'||typeof v.passed!=='boolean')return 'UNATTRIBUTABLE';const hex=/^[a-f0-9]{64}$/;if(!hex.test(c.promptHash)||!hex.test(v.promptHash)||c.promptHash===v.promptHash)return 'UNATTRIBUTABLE';if(evaluateComparability(c,v).status!=='COMPARABLE')return 'UNATTRIBUTABLE';return !c.passed&&!v.passed?'SHARED_FAILURE':!c.passed&&v.passed?'VARIANT_IMPROVEMENT':c.passed&&!v.passed?'VARIANT_INDUCED_FAILURE':'BOTH_PASS';}
function summarizeTrials(obs){
 const groups=new Map(),issues=[];if(!Array.isArray(obs))return {classifications:{},pairs:[],issues:['OBSERVATIONS_NOT_ARRAY']};
 for(const o of obs){const key=JSON.stringify([o.inputId,o.trialId??'trial-1']);if(!groups.has(key))groups.set(key,{inputId:o.inputId,trialId:o.trialId??'trial-1'});const p=groups.get(key);if(p[o.condition])issues.push('DUPLICATE_PAIR_SLOT:'+key);else p[o.condition]=o;}
 const counts={BASELINE_FAILURE:0,SHARED_FAILURE:0,VARIANT_INDUCED_FAILURE:0,VARIANT_IMPROVEMENT:0,BOTH_PASS:0,UNATTRIBUTABLE:0};
 const pairs=[];for(const p of groups.values()){const cls=classifyPairedTrial(p.CONTROL,p.VARIANT);counts[cls]++;if(['SHARED_FAILURE','VARIANT_IMPROVEMENT'].includes(cls)&&p.CONTROL.passed===false)counts.BASELINE_FAILURE++;pairs.push({inputId:p.inputId,trialId:p.trialId,classification:cls,comparability:p.CONTROL&&p.VARIANT?evaluateComparability(p.CONTROL,p.VARIANT):null});}
 return {classifications:counts,pairs,issues};
}
root.ReactorComparisonEngine={classifyPairedTrial,evaluateComparability,summarizeTrials};
})(typeof window!=='undefined'?window:globalThis);
