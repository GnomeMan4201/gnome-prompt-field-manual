"""Phase VIII-B conservative chamber attribution; depends on the Phase VIII-A core.

No assertion of independent judge correctness or causality is made here.
Both deterministic and reference-grounded evaluations must agree; a judge is advisory.
"""
from __future__ import annotations
from collections import Counter
from typing import Any
from reactor_engine import classify_paired_trial, validate_observations, evaluate_comparability

ACCEPTED = {'Supported pass':True, 'Supported failure':False}

def independently_scored(disposition:dict|None)->bool|None:
    if not isinstance(disposition,dict):return None
    deterministic=disposition.get('deterministic')
    grounded=disposition.get('grounded')
    # Both mechanisms must provide actual positive evidence, NOT_ASSESSABLE is not a failure.
    if deterministic=='PASS' and grounded=='SUPPORTED':return True
    if deterministic=='FAIL' and grounded=='CONTRADICTED':return False
    return None

def attribute_chamber_trials(pairs:list[dict[str,Any]])->dict[str,Any]:
    counts=Counter({k:0 for k in ('validPairedTrials','missingTrials','baselineFailures','variantInducedFailures','sharedFailures','variantImprovements','bothPass','evaluatorDisagreements','unattributableCount')})
    outcomes=[];seen=set()
    if not isinstance(pairs,list):raise ValueError('PAIRS_NOT_ARRAY')
    for p in pairs:
        if not isinstance(p,dict):raise ValueError('INVALID_PAIR')
        c,v=p.get('control'),p.get('variant')
        key=(p.get('trialId'),p.get('inputId'))
        if not key[0] or key in seen:raise ValueError('DUPLICATE_OR_MISSING_PAIR_ID')
        seen.add(key)
        reason=None
        if not isinstance(c,dict) or not isinstance(v,dict) or c.get('outputText') is None or v.get('outputText') is None:
            counts['missingTrials']+=1;reason='MISSING_OBSERVATION'
        else:
            # Never use p.comparable or caller-supplied dispositions as trusted evidence.
            scores=(independently_scored(p.get('controlEvaluation')),independently_scored(p.get('variantEvaluation')))
            if None in scores:reason='INSUFFICIENT_INDEPENDENT_SCORING'
            elif (c.get('trialId','trial-1')!=v.get('trialId','trial-1') or c.get('trialId','trial-1')!=key[0] or c.get('inputId')!=v.get('inputId') or c.get('inputId')!=p.get('inputId')):
                reason='TRIAL_ID_MISMATCH'
            elif c.get('condition')!='CONTROL' or v.get('condition')!='VARIANT':reason='INVALID_CONDITIONS'
            elif evaluate_comparability(c,v)['status']!='COMPARABLE':reason='NOT_STRICTLY_COMPARABLE'
            else:
                trial_c={**c,'passed':scores[0]};trial_v={**v,'passed':scores[1]}
                cls=classify_paired_trial(trial_c,trial_v)
                if cls=='UNATTRIBUTABLE':reason='STRICT_CLASSIFIER_REJECTED'
        if reason:
            counts['unattributableCount']+=1
            outcomes.append({'trialId':key[0],'attribution':'UNATTRIBUTABLE','reason':reason});continue
        counts['validPairedTrials']+=1
        mapping={'SHARED_FAILURE':'sharedFailures','VARIANT_INDUCED_FAILURE':'variantInducedFailures','VARIANT_IMPROVEMENT':'variantImprovements','BOTH_PASS':'bothPass'}
        counts[mapping[cls]]+=1
        if cls in ('SHARED_FAILURE','VARIANT_IMPROVEMENT'):counts['baselineFailures']+=1
        outcomes.append({'trialId':key[0],'attribution':cls})
    # Denominator excludes pairs that lack independently substantiated PASS/FAIL on both sides.
    denom=counts['validPairedTrials']
    return {'counts':dict(counts),'observedVariantInducedFailureProportion':counts['variantInducedFailures']/denom if denom else None,'outcomes':outcomes}
