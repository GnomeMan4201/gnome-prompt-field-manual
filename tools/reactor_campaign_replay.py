#!/usr/bin/env python3
"""Strict v3 computational replay, building on the existing v2 scoring engine.

Checksums establish internal consistency only; they are not signatures, execution
attestations, or guarantees that reference facts are authentic.
"""
from __future__ import annotations
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from reactor_evidence_v2 import (validate_plan, validate_run_records, analyze,
    stable_json, EvidenceError, require, MAX_FILE_BYTES)
from reactor_campaign_runner import validate_intervention,validate_intervention_observations
from reactor_reference_registry import checked_reference_eligible, verify_reference_bytes
from reactor_empirical_evaluator import wilson_interval

CAPSULE_VERSION='gnome.reactor.evidence.v3'
CAMPAIGN_VERSION='gnome.reactor.campaign.v3'
SECTION_KEYS=('campaign','interventions','execution','evaluation','findings')
VALID_CLAIM_STATES=frozenset({'INCONCLUSIVE','NOT_SUPPORTED','CONTRADICTED',
                            'CANDIDATE_REQUIRES_REVIEW','SUPPORTED_WITHIN_RECORDED_CONDITIONS'})


def canonical_json(obj:Any)->str:
    """Restricted stable JSON. This is not full RFC-8785 canonicalization."""
    return stable_json(obj)


def sha256_text(text:str)->str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _strict_fields(obj:Any, required:set, allow:set,code:str):
    require(isinstance(obj,dict),code+':NOT_OBJECT')
    require(required<=set(obj),code+':MISSING_FIELDS')
    require(set(obj)<=allow,code+':UNKNOWN_FIELDS')


def validate_campaign(campaign:Any,intervention:Any)->None:
    _strict_fields(campaign,{'schemaVersion','campaignId','family','plan','references','protocol'},
                   {'schemaVersion','campaignId','family','plan','references','protocol','isSyntheticDemo'},'CAMPAIGN')
    require(campaign['schemaVersion']==CAMPAIGN_VERSION,'INVALID_CAMPAIGN_VERSION')
    require(isinstance(campaign['campaignId'],str) and 0<len(campaign['campaignId'])<=128,'INVALID_CAMPAIGN_ID')
    require(campaign['family'] in ('A_EVIDENCE_BOUNDARY','B_LOWER_TRUST_INJECTION','C_EVALUATOR_CONTAMINATION'),
            'INVALID_CAMPAIGN_FAMILY')
    require(type(campaign.get('isSyntheticDemo',False)) is bool,'INVALID_SYNTHETIC_FLAG')
    require(isinstance(campaign['protocol'],dict) and campaign['protocol'].get('researchMode') in ('EXPLORATORY','CONFIRMATORY'),
            'INVALID_CAMPAIGN_PROTOCOL')
    plan=campaign['plan'];validate_plan(plan)
    validate_intervention(intervention,plan)
    if campaign['family']=='B_LOWER_TRUST_INJECTION':
        require(intervention['type']=='LOWER_TRUST_DOCUMENT','DOCUMENT_INTERVENTION_REQUIRED')
    require(isinstance(campaign['references'],list) and 0<len(campaign['references'])<=512,'INVALID_REFERENCE_REGISTRY')
    registry={}
    for ref in campaign['references']:
        errors=verify_reference_bytes(ref)
        require(not errors,'INVALID_REFERENCE:'+','.join(errors[:3]))
        rid=ref['referenceId']
        require(rid not in registry,'DUPLICATE_REFERENCE_ID')
        registry[rid]=ref
    for item in plan['inputs']:
        wanted=item['reference']
        for rid in wanted['evidenceRefs']:
            require(rid in registry,'UNRESOLVED_EVIDENCE_REFERENCE:'+rid)
            require('expectedJson' in registry[rid] and
                    canonical_json(registry[rid]['expectedJson'])==canonical_json(wanted['expectedJson']),
                    'REFERENCE_EXPECTED_JSON_MISMATCH:'+rid)


def calculate(campaign:dict, intervention:dict,execution:dict)->dict:
    validate_campaign(campaign,intervention)
    _strict_fields(execution,{'status','observations','errors','modelProvenance'},
                   {'schemaVersion','status','observations','errors','modelProvenance','claimsVerified'},'EXECUTION')
    require(execution['status'] in ('NOT_EXECUTED','PARTIAL','COMPLETED'),'INVALID_EXECUTION_STATUS')
    require(isinstance(execution['observations'],list) and isinstance(execution['errors'],list),'INVALID_EXECUTION_RECORDS')
    require(execution['modelProvenance'] in ('PROVIDER_REPORTED_UNAUTHENTICATED','SYNTHETIC_MOCK_TEST_ONLY','NOT_AVAILABLE'),
            'INVALID_EXECUTION_PROVENANCE')
    obs=execution['observations']
    if execution['status']=='NOT_EXECUTED':
        require(not obs,'NOT_EXECUTED_WITH_OBSERVATIONS')
        return {'schemaVersion':'gnome.reactor.analysis.v3','executionStatus':'NOT_EXECUTED',
                'replayMode':'COMPUTATIONAL_REPLAY_ONLY',
                'counts':{'validPairedTrials':0,'variantInducedFailures':0,'unattributableCount':0},
                'observedVariantInducedFailureProportion':None,'wilson95':None,
                'referenceAuthority':'NOT_INDEPENDENTLY_AUTHENTICATED','outcomes':[]}
    require(bool(obs),'EXECUTION_MARKED_RUN_WITHOUT_OBSERVATIONS')
    if execution['status']=='COMPLETED':
        require(not execution['errors'],'COMPLETED_WITH_FAILURES')
    if execution['status']=='PARTIAL':
        require(bool(execution['errors']),'PARTIAL_WITHOUT_FAILURES')
    plan=campaign['plan']
    validate_run_records(plan,obs)      # Rejects imported pass/evaluation/disposition assertions.
    validate_intervention_observations(intervention,plan,obs)
    result=analyze(plan,obs)             # Recompute all scores from raw output text and references.
    counts=result['counts']
    ratio=result['observedVariantInducedFailureProportion']
    lower_upper=wilson_interval(counts['variantInducedFailures'],counts['validPairedTrials'])
    return {'schemaVersion':'gnome.reactor.analysis.v3','executionStatus':execution['status'],
            'replayMode':'COMPUTATIONAL_REPLAY_ONLY',
            'counts':counts,'observedVariantInducedFailureProportion':ratio,
            'wilson95':list(lower_upper) if lower_upper is not None else None,
            'referenceAuthority':'NOT_INDEPENDENTLY_AUTHENTICATED',
            'outcomes':result['outcomes']}


def validate_findings(findings:Any,campaign:dict,execution:dict,derived:dict)->None:
    _strict_fields(findings,{'claims'}, {'claims','challenges'},'FINDINGS')
    require(isinstance(findings['claims'],list),'INVALID_CLAIMS')
    require(isinstance(findings.get('challenges',[]),list),'INVALID_CHALLENGES')
    valid_trials={f"{o['inputId']}:{o['trialId']}" for o in derived['outcomes']}
    ids=set()
    for claim in findings['claims']:
        _strict_fields(claim,{'claimId','status','trialRefs','statement'},
                       {'claimId','status','trialRefs','statement','limitations'},'CLAIM')
        require(isinstance(claim['claimId'],str) and bool(claim['claimId'].strip()),'INVALID_CLAIM_ID')
        require(claim['claimId'] not in ids,'DUPLICATE_CLAIM_ID')
        ids.add(claim['claimId'])
        require(claim['status'] in VALID_CLAIM_STATES,'UNKNOWN_CLAIM_STATUS')
        require(isinstance(claim['statement'],str) and bool(claim['statement'].strip()),'INVALID_CLAIM_TEXT')
        require(isinstance(claim['trialRefs'],list) and all(isinstance(x,str) and x in valid_trials for x in claim['trialRefs']),
                'CLAIM_WITHOUT_VALID_TRIAL_EVIDENCE')
        if execution['status']=='NOT_EXECUTED':
            require(claim['status'] in ('INCONCLUSIVE','NOT_SUPPORTED'), 'EMPIRICAL_CLAIM_WITHOUT_EXECUTION')
            require(not claim['trialRefs'],'NOT_EXECUTED_WITH_TRIAL_REFS')
        if claim['status']=='SUPPORTED_WITHIN_RECORDED_CONDITIONS':
            require(execution['status']=='COMPLETED','SUPPORTED_CLAIM_REQUIRES_COMPLETE_EXECUTION')
            require(execution['modelProvenance']=='PROVIDER_REPORTED_UNAUTHENTICATED' and not campaign.get('isSyntheticDemo',False),
                    'SYNTHETIC_OR_UNVERIFIED_RUN_NOT_EMPIRICAL')
            require(all(checked_reference_eligible(r) for r in campaign['references']),
                    'REFERENCES_NOT_SOURCE_CHECKED')
            induced={f"{o['inputId']}:{o['trialId']}" for o in derived['outcomes']
                     if o['attribution']=='VARIANT_INDUCED_FAILURE'}
            require(bool(set(claim['trialRefs']) & induced),'CLAIM_NOT_SUPPORTED_BY_INDUCED_FAILURE')
    for challenge in findings.get('challenges',[]):
        require(isinstance(challenge,dict) and challenge.get('claimId') in ids and
                isinstance(challenge.get('rationale'),str) and bool(challenge['rationale'].strip()),
                'INVALID_CLAIM_CHALLENGE')


def build_evidence_capsule_v3(campaign:dict,interventions:dict,
                              execution:dict,evaluation:dict,findings:dict)->dict:
    sections={'campaign':deepcopy(campaign),'interventions':deepcopy(interventions),
              'execution':deepcopy(execution),'evaluation':deepcopy(evaluation),
              'findings':deepcopy(findings)}
    manifest={'schemaVersion':CAPSULE_VERSION,
              'authentication':'UNAUTHENTICATED_CONTENT_CHECKSUMS_ONLY',
              'replayMode':'COMPUTATIONAL_REPLAY_ONLY',
              'isSyntheticDemo':bool(campaign.get('isSyntheticDemo',False)) if isinstance(campaign,dict) else False}
    checksums={key:sha256_text(canonical_json(value)) for key,value in sections.items()}
    checksums['manifest']=sha256_text(canonical_json(manifest))
    return {'schemaVersion':CAPSULE_VERSION,**sections,'integrity':{'manifest':manifest,'checksums':checksums}}


def build_checked_capsule_v3(campaign:dict,interventions:dict,execution:dict,findings:dict)->dict:
    calculated=calculate(campaign,interventions,execution)
    validate_findings(findings,campaign,execution,calculated)
    capsule=build_evidence_capsule_v3(campaign,interventions,execution,calculated,findings)
    result=replay_evidence_capsule_v3(capsule)
    require(result['valid'],'CAPSULE_BUILD_VALIDATION_FAILED:'+str(result['errors']))
    return capsule


def replay_evidence_capsule_v3(capsule:Any)->dict:
    errors=[];replayed=None
    try:
        _strict_fields(capsule,{'schemaVersion',*SECTION_KEYS,'integrity'},
                       {'schemaVersion',*SECTION_KEYS,'integrity'},'CAPSULE')
        require(capsule['schemaVersion']==CAPSULE_VERSION,'UNSUPPORTED_SCHEMA_VERSION')
        for section in SECTION_KEYS:
            require(isinstance(capsule[section],dict),'INVALID_SECTION_SHAPE:'+section)
        integrity=capsule['integrity']
        _strict_fields(integrity,{'manifest','checksums'},{'manifest','checksums'},'INTEGRITY')
        manifest=integrity['manifest'];checks=integrity['checksums']
        _strict_fields(manifest,{'schemaVersion','authentication','replayMode','isSyntheticDemo'},
                       {'schemaVersion','authentication','replayMode','isSyntheticDemo'},'MANIFEST')
        require(manifest['schemaVersion']==CAPSULE_VERSION and
                manifest['authentication']=='UNAUTHENTICATED_CONTENT_CHECKSUMS_ONLY' and
                manifest['replayMode']=='COMPUTATIONAL_REPLAY_ONLY','INVALID_MANIFEST')
        require(type(manifest['isSyntheticDemo']) is bool and
                manifest['isSyntheticDemo']==bool(capsule['campaign'].get('isSyntheticDemo',False)),
                'SYNTHETIC_LABEL_MISMATCH')
        require(isinstance(checks,dict) and set(checks)==set(SECTION_KEYS)|{'manifest'},
                'INVALID_CHECKSUM_SET')
        for section in SECTION_KEYS:
            require(isinstance(capsule[section],dict),'INVALID_SECTION_SHAPE:'+section)
            require(isinstance(checks[section],str) and checks[section]==sha256_text(canonical_json(capsule[section])),
                    'CHECKSUM_MISMATCH:'+section)
        require(checks['manifest']==sha256_text(canonical_json(manifest)), 'CHECKSUM_MISMATCH:manifest')
        recomputed=calculate(capsule['campaign'],capsule['interventions'],capsule['execution'])
        require(canonical_json(capsule['evaluation'])==canonical_json(recomputed), 'REPLAY_EVALUATION_MISMATCH')
        validate_findings(capsule['findings'],capsule['campaign'],capsule['execution'],recomputed)
        replayed=recomputed
    except (EvidenceError,ValueError,KeyError,TypeError,OverflowError,RecursionError) as exc:
        errors.append(str(exc))
    return {'valid':not errors,'errors':errors,'replayLevel':'COMPUTATIONAL_REPLAY_ONLY',
            'authenticityWarning':'Checksums and replay do not authenticate source, execution or reviewers.',
            'replay':replayed if not errors else None}


def _read_json(path:str):
    p=Path(path);require(p.is_file() and p.stat().st_size<=MAX_FILE_BYTES,'FILE_TOO_LARGE_OR_NOT_FOUND')
    def unique(pairs):
        output={}
        for k,v in pairs:
            if k in output:raise EvidenceError('DUPLICATE_JSON_KEY:'+k)
            output[k]=v
        return output
    return json.loads(p.read_text(encoding='utf8'),object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(EvidenceError('NONFINITE_JSON')))


def main(argv=None)->int:
    parser=argparse.ArgumentParser(description='GNOME strict v3 campaign replay, no model inference')
    sub=parser.add_subparsers(dest='cmd',required=True)
    v=sub.add_parser('verify');v.add_argument('capsule')
    b=sub.add_parser('build');b.add_argument('--campaign',required=True);b.add_argument('--intervention',required=True)
    b.add_argument('--execution',required=True);b.add_argument('--findings',required=True);b.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    try:
        if args.cmd=='verify':
            report=replay_evidence_capsule_v3(_read_json(args.capsule));print(json.dumps(report,indent=2));return 0 if report['valid'] else 2
        cap=build_checked_capsule_v3(_read_json(args.campaign),_read_json(args.intervention),
                                     _read_json(args.execution),_read_json(args.findings))
        Path(args.out).write_text(json.dumps(cap,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf8')
        print(json.dumps({'valid':True,'saved':args.out,'authenticity':'NOT_ATTESTED'}));return 0
    except (EvidenceError,TypeError,ValueError,KeyError,OSError) as exc:
        print(json.dumps({'valid':False,'errors':[str(exc)]}));return 2

if __name__=='__main__':raise SystemExit(main())
