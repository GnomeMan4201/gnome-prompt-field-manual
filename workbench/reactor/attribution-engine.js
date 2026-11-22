(function(root){'use strict';
// The Phase VIII-A comparable-pair classifier is authoritative for metadata.
function supported(e){
 if(!e||typeof e!=='object')return null;
 if(e.deterministic==='PASS'&&e.grounded==='SUPPORTED')return true;
 if(e.deterministic==='FAIL'&&e.grounded==='CONTRADICTED')return false;
 return null;
}
function attributeTrials(pairs){
 if(!Array.isArray(pairs))throw Error('PAIRS_NOT_ARRAY');
 const counts={validPairedTrials:0,missingTrials:0,baselineFailures:0,variantInducedFailures:0,sharedFailures:0,variantImprovements:0,bothPass:0,evaluatorDisagreements:0,unattributableCount:0};
 const seen=new Set(),outcomes=[];
 for(const p of pairs){
  if(!p||typeof p!=='object')throw Error('INVALID_PAIR');
  const key=JSON.stringify([p.trialId,p.inputId]);
  if(!p.trialId||seen.has(key))throw Error('DUPLICATE_OR_MISSING_PAIR_ID');seen.add(key);
  const c=p.control,v=p.variant;
  let reason=null;
  if(!c||!v||c.outputText==null||v.outputText==null){counts.missingTrials++;reason='MISSING_OBSERVATION';}
  else {
   const cs=supported(p.controlEvaluation),vs=supported(p.variantEvaluation);
   if(cs===null||vs===null)reason='INSUFFICIENT_INDEPENDENT_SCORING';
   else if((c.trialId||'trial-1')!==(v.trialId||'trial-1')||(c.trialId||'trial-1')!==p.trialId||c.inputId!==v.inputId||c.inputId!==p.inputId)reason='TRIAL_ID_MISMATCH';
   else if(c.condition!=='CONTROL'||v.condition!=='VARIANT')reason='INVALID_CONDITIONS';
   else if(root.ReactorComparisonEngine.evaluateComparability(c,v).status!=='COMPARABLE')reason='NOT_STRICTLY_COMPARABLE';
   else {
    const cls=root.ReactorComparisonEngine.classifyPairedTrial({...c,passed:cs},{...v,passed:vs});
    if(cls==='UNATTRIBUTABLE')reason='STRICT_CLASSIFIER_REJECTED';
    else{
     counts.validPairedTrials++;
     const bucket={SHARED_FAILURE:'sharedFailures',VARIANT_INDUCED_FAILURE:'variantInducedFailures',VARIANT_IMPROVEMENT:'variantImprovements',BOTH_PASS:'bothPass'};
     counts[bucket[cls]]++;
     if(cls==='SHARED_FAILURE'||cls==='VARIANT_IMPROVEMENT')counts.baselineFailures++;
     outcomes.push({trialId:p.trialId,attribution:cls});
    }
   }
  }
  if(reason){counts.unattributableCount++;outcomes.push({trialId:p.trialId,attribution:'UNATTRIBUTABLE',reason});}
 }
 return {counts,observedVariantInducedFailureProportion:counts.validPairedTrials?counts.variantInducedFailures/counts.validPairedTrials:null,outcomes};
}
root.ReactorAttributionEngine={attributeTrials,supported};
})(typeof window!=='undefined'?window:globalThis);
