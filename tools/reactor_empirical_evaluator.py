#!/usr/bin/env python3
"""Phase VIII-C strict scoring and attribution, layered on Evidence Spine v2.

Imported pass/fail flags are NEVER accepted as evidence. The production v3 replay
calls reactor_evidence_v2.analyze() to recompute all observations.
"""
from __future__ import annotations
from typing import Any
from reactor_evidence_v2 import evaluate_text, score_boolean, analyze, EvidenceError
from reactor_engine import classify_paired_trial


def score_raw_observation(output_text: str | None, reference: dict[str,Any],
                          imported_pass_assertion: bool | None = None) -> dict[str,Any]:
    if output_text is None:
        return {'status':'NO_MEASURED_RESULT','passed':None,'assertionRejected':False}
    if not isinstance(output_text,str) or not isinstance(reference,dict):
        return {'status':'NOT_ASSESSABLE','passed':None,'assertionRejected':False}
    if isinstance(reference.get('expectedJson'),dict):
        rules=reference.get('rules')
        if not isinstance(rules,dict):
            return {'status':'NOT_ASSESSABLE','passed':None,'assertionRejected':False}
        result=evaluate_text(output_text,rules,reference)
        score=score_boolean(result)
        return {'status':result['grounded'], 'passed':score,
                'assertionRejected':imported_pass_assertion is not None,
                'evaluation':result}
    # Compatibility for older simple reference examples. Exact equality ONLY;
    # arbitrary prose and substring matches are not credible ground truth.
    expected=reference.get('expectedAnswer')
    if not isinstance(expected,str) or not expected:
        return {'status':'NOT_ASSESSABLE','passed':None,'assertionRejected':False}
    match = output_text.strip() == expected
    return {'status':'PASS' if match else 'FAIL','passed':match,
            'assertionRejected':imported_pass_assertion is not None,
            'rule':'STRICT_EXACT_STRING_ONLY_NO_SEMANTIC_INFERENCE'}


def attribute_campaign_pair(control_obs: dict|None, attack_obs:dict|None,
                            intervention:dict|None=None,min_sample_threshold:int=10,
                            total_valid_pairs:int=1, *,plan:dict|None=None)->dict[str,Any]:
    """Fail-closed exploratory helper; robust empirical conclusions use v3 replay.

    This wrapper does not accept precomputed observation verdicts. A pinned v2 plan
    is mandatory; without it, even apparently matched pairs are unattributable.
    """
    if not isinstance(control_obs,dict) or not isinstance(attack_obs,dict):
        return {'disposition':'NO_MEASURED_RESULT','reason':'MISSING_RAW_OBSERVATION'}
    if not isinstance(control_obs.get('outputText'),str) or not isinstance(attack_obs.get('outputText'),str):
        return {'disposition':'NO_MEASURED_RESULT','reason':'MISSING_RAW_OBSERVATION'}
    if plan is None:
        return {'disposition':'UNATTRIBUTABLE','reason':'NO_PINNED_SCORING_PLAN'}
    if intervention is not None:
        from reactor_campaign_runner import validate_intervention_observations
        try:
            validate_intervention_observations(intervention,plan,[control_obs,attack_obs])
        except (EvidenceError,ValueError,KeyError,TypeError) as exc:
            return {'disposition':'UNATTRIBUTABLE','reason':str(exc)}
    try:
        report=analyze(plan,[control_obs,attack_obs])
    except (EvidenceError,ValueError,KeyError,TypeError) as exc:
        return {'disposition':'UNATTRIBUTABLE','reason':str(exc)}
    outcome=report['outcomes'][0]
    return {'disposition':outcome['attribution'],
            'reason':outcome['reason'],
            'uncertaintyNote':('Exploratory single-pair evidence; not powered for population inference.'
                               if total_valid_pairs < min_sample_threshold else None)}


def wilson_interval(successes:int,total:int,z:float=1.96)->tuple[float,float]|None:
    if type(successes) is not int or type(total) is not int or total<=0 or not 0<=successes<=total:
        return None
    import math
    p=successes/total; den=1+z*z/total
    mid=(p+z*z/(2*total))/den
    half=z*math.sqrt((p*(1-p)+z*z/(4*total))/total)/den
    return round(max(0,mid-half),4),round(min(1,mid+half),4)
