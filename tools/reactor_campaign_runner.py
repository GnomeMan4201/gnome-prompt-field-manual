#!/usr/bin/env python3
"""Phase VIII-C controlled campaign definitions and opt-in numeric-loopback runner.

No arbitrary external network contact. The existing hardened Ollama runner owns all
inference; this module never executes model-generated code or confuses mock runs
with empirical model observations.
"""
from __future__ import annotations
from copy import deepcopy
import http.client
import json
from pathlib import Path
import socket
import urllib.parse
from typing import Any

from reactor_engine import sha256_text
from reactor_evidence_v2 import stable_json, validate_plan, EvidenceError, require
from reactor_local_runner import is_localhost_url, run_local_ollama_trial
from reactor_pair_runner import run_pairs

INTERVENTION_VERSION = 'gnome.reactor.intervention.v1'


def fixed_task_hash(plan:dict)->str:
    return sha256_text(stable_json([{'inputId':x['inputId'],'text':x['text']} for x in plan['inputs']]))


def fixed_config_hash(plan:dict)->str:
    return sha256_text(stable_json({k:plan[k] for k in ('provider','model','temperature','seed','tools','evaluator','datasetId')}))


def build_lower_trust_intervention(task_text:str,config_json:str,baseline_doc:str,
                                    mutated_doc:str,intervention_span:str)->dict[str,Any]:
    """Legacy declaration API; string hashes alone do not establish a valid insertion.

    For a verifiable experiment use build_bound_intervention(plan, template, ...).
    """
    return {'schemaVersion':INTERVENTION_VERSION,'type':'LOWER_TRUST_DOCUMENT',
            'fixedTaskHash':sha256_text(task_text),'fixedConfigHash':sha256_text(config_json),
            'baselineDocHash':sha256_text(baseline_doc),
            'mutatedDocHash':sha256_text(mutated_doc),
            'interventionSpan':intervention_span,'mutationHash':sha256_text(intervention_span),
            'provenanceStatus':'DECLARATION_ONLY_UNVERIFIED'}


def build_bound_intervention(plan:dict,template:str,baseline_doc:str,
                             inserted_text:str,offset:int, intervention_id:str='INT-1')->dict[str,Any]:
    validate_plan(plan)
    if (not isinstance(template,str) or template.count('{{DOCUMENT}}')!=1
        or not isinstance(baseline_doc,str) or not isinstance(inserted_text,str)
        or not inserted_text or type(offset) is not int or not 0<=offset<=len(baseline_doc)):
        raise EvidenceError('INVALID_DOCUMENT_INTERVENTION')
    mutated=baseline_doc[:offset]+inserted_text+baseline_doc[offset:]
    expected_control=template.replace('{{DOCUMENT}}',baseline_doc)
    expected_variant=template.replace('{{DOCUMENT}}',mutated)
    require(plan['prompts']['control']==expected_control and plan['prompts']['variant']==expected_variant,
            'INTERVENTION_PROMPT_BINDING_MISMATCH')
    require(isinstance(intervention_id,str) and bool(intervention_id.strip()), 'INVALID_INTERVENTION_ID')
    return {'schemaVersion':INTERVENTION_VERSION,'interventionId':intervention_id,
            'type':'LOWER_TRUST_DOCUMENT','provenanceStatus':'DECLARED_CONTENT_VERIFIED',
            'template':template,'templateHash':sha256_text(template),
            'baselineDocument':baseline_doc,'mutatedDocument':mutated,
            'baselineDocHash':sha256_text(baseline_doc),'mutatedDocHash':sha256_text(mutated),
            'insertionOffset':offset,'interventionSpan':inserted_text,
            'mutationHash':sha256_text(inserted_text),
            'fixedTaskHash':fixed_task_hash(plan),'fixedConfigHash':fixed_config_hash(plan),
            'controlPromptHash':sha256_text(expected_control),
            'variantPromptHash':sha256_text(expected_variant)}


def build_prompt_intervention(plan:dict, intervention_id:str='INT-1')->dict[str,Any]:
    validate_plan(plan)
    return {'schemaVersion':INTERVENTION_VERSION,'interventionId':intervention_id,
            'type':'PROMPT_VARIANT',
            'controlPromptHash':sha256_text(plan['prompts']['control']),
            'variantPromptHash':sha256_text(plan['prompts']['variant']),
            'fixedTaskHash':fixed_task_hash(plan),'fixedConfigHash':fixed_config_hash(plan),
            'provenanceStatus':'DECLARED_PROMPT_VARIANT'}


def validate_intervention(intervention:dict, plan:dict)->None:
    validate_plan(plan)
    require(isinstance(intervention,dict),'INTERVENTION_NOT_OBJECT')
    require(intervention.get('schemaVersion')==INTERVENTION_VERSION,'INVALID_INTERVENTION_SCHEMA')
    require(isinstance(intervention.get('interventionId'),str) and bool(intervention['interventionId'].strip()),'MISSING_INTERVENTION_ID')
    for key,wanted in (
        ('controlPromptHash',sha256_text(plan['prompts']['control'])),
        ('variantPromptHash',sha256_text(plan['prompts']['variant'])),
        ('fixedTaskHash',fixed_task_hash(plan)),('fixedConfigHash',fixed_config_hash(plan))):
        require(intervention.get(key)==wanted,'INTERVENTION_BINDING_MISMATCH:'+key)
    kind=intervention.get('type')
    require(kind in ('PROMPT_VARIANT','LOWER_TRUST_DOCUMENT'),'UNKNOWN_INTERVENTION_TYPE')
    if kind=='LOWER_TRUST_DOCUMENT':
        baseline=intervention.get('baselineDocument');mutated=intervention.get('mutatedDocument')
        span=intervention.get('interventionSpan');offset=intervention.get('insertionOffset')
        template=intervention.get('template')
        require(isinstance(baseline,str) and isinstance(mutated,str) and isinstance(span,str) and bool(span), 'INVALID_DOCUMENT_BYTES')
        require(type(offset) is int and 0<=offset<=len(baseline),'INVALID_INSERTION_OFFSET')
        require(isinstance(template,str) and template.count('{{DOCUMENT}}')==1,'INVALID_DOCUMENT_TEMPLATE')
        require(mutated==baseline[:offset]+span+baseline[offset:],'UNDECLARED_DOCUMENT_MUTATION')
        for key,wanted in (('baselineDocHash',sha256_text(baseline)),
                           ('mutatedDocHash',sha256_text(mutated)),
                           ('mutationHash',sha256_text(span)),
                           ('templateHash',sha256_text(template))):
            require(intervention.get(key)==wanted,'INTERVENTION_HASH_MISMATCH:'+key)
        require(plan['prompts']['control']==template.replace('{{DOCUMENT}}',baseline) and
                plan['prompts']['variant']==template.replace('{{DOCUMENT}}',mutated),
                'INTERVENTION_PROMPT_BINDING_MISMATCH')
    else:
        require(intervention.get('provenanceStatus')=='DECLARED_PROMPT_VARIANT', 'INVALID_PROMPT_VARIANT_PROVENANCE')


def intervention_observation_binding(intervention:dict,condition:str)->dict:
    return {'interventionId':intervention['interventionId'],
            'fixedTaskHash':intervention['fixedTaskHash'],
            'fixedConfigHash':intervention['fixedConfigHash'],
            'documentHash':(intervention.get('baselineDocHash') if condition=='CONTROL'
                            else intervention.get('mutatedDocHash')) if intervention['type']=='LOWER_TRUST_DOCUMENT' else None,
            'mutationHash':intervention.get('mutationHash')}


def validate_intervention_observations(intervention:dict,plan:dict,observations:list)->None:
    validate_intervention(intervention,plan)
    require(isinstance(observations,list),'OBSERVATIONS_NOT_ARRAY')
    for i,o in enumerate(observations):
        require(isinstance(o,dict) and o.get('condition') in ('CONTROL','VARIANT'),f'INVALID_INTERVENTION_OBSERVATION:{i}')
        wanted=intervention_observation_binding(intervention,o['condition'])
        bound=o.get('interventionProvenance')
        require(isinstance(bound,dict),f'MISSING_INTERVENTION_PROVENANCE:{i}')
        require(set(bound)==set(wanted),f'INTERVENTION_PROVENANCE_FIELD_MISMATCH:{i}')
        for k,v in wanted.items():
            require(bound[k]==v,f'OBSERVATION_INTERVENTION_MISMATCH:{i}:{k}')
        require(o.get('promptHash')==intervention['controlPromptHash' if o['condition']=='CONTROL' else 'variantPromptHash'],
                f'OBSERVATION_PROMPT_BINDING_MISMATCH:{i}')


def check_loopback_endpoint(endpoint:str)->dict[str,Any]:
    """No redirects, hostnames, environment proxies, or non-loopback hops."""
    if not is_localhost_url(endpoint):
        return {'status':'NOT_EXECUTED','reason':'NON_LOOPBACK_BLOCKED'}
    p=urllib.parse.urlsplit(endpoint)
    conn=http.client.HTTPConnection(p.hostname,p.port,timeout=2.0)
    try:
        conn.request('GET','/api/tags',headers={'Accept':'application/json'})
        resp=conn.getresponse()
        if 300<=resp.status<400:
            return {'status':'NOT_EXECUTED','reason':'REDIRECT_BLOCKED','httpStatus':resp.status}
        if resp.status!=200:
            return {'status':'NOT_EXECUTED','reason':'HTTP_ERROR','httpStatus':resp.status}
        if resp.length is not None and resp.length>65536:
            return {'status':'NOT_EXECUTED','reason':'RESPONSE_TOO_LARGE'}
        data=resp.read(65537)
        if len(data)>65536:
            return {'status':'NOT_EXECUTED','reason':'RESPONSE_TOO_LARGE'}
        decoded=json.loads(data.decode('utf-8'))
        if not isinstance(decoded,dict) or not isinstance(decoded.get('models'),list):
            return {'status':'NOT_EXECUTED','reason':'INVALID_PROVIDER_RESPONSE'}
        return {'status':'ENDPOINT_REACHABLE','reportedModels':len(decoded['models']),
                'authentication':'UNVERIFIED_LOOPBACK_ONLY'}
    except (OSError,ValueError,UnicodeError,http.client.HTTPException) as exc:
        return {'status':'NOT_EXECUTED','reason':'NO_MODEL_ENDPOINT_AVAILABLE:'+type(exc).__name__}
    finally:
        conn.close()


def attempt_falsification(finding:dict[str,Any])->dict[str,Any]:
    """Never promotes a claim on absent fields or self-declared reviewer identity."""
    reasons=[]
    if not isinstance(finding,dict):
        return {'survived':False,'disposition':'INCONCLUSIVE','falsificationReasons':['MISSING_FINDING']}
    if finding.get('baselineFailed') is True:reasons.append('BASELINE_ALREADY_FAILED')
    if finding.get('evaluatorDisagreement') is True:reasons.append('EVALUATOR_DISAGREEMENT')
    if finding.get('uncontrolledVariable') is True:reasons.append('CONFOUNDED')
    if finding.get('modelConfigDrifted') is True:reasons.append('MODEL_CONFIG_DRIFT')
    if finding.get('exploratoryCherryPicked') is True:reasons.append('EXPLORATORY_SELECTION')
    # No conclusion based on selectively absent flags.
    gates=('recomputedScoring','validPairedObservations','sourceChecked','rawObservationsPresent')
    for gate in gates:
        if finding.get(gate) is not True:reasons.append('UNVERIFIED_GATE:'+gate)
    if finding.get('referenceAuthority') not in ('SOURCE_CHECKED',):
        reasons.append('REFERENCE_NOT_SOURCE_CHECKED')
    return {'survived':not reasons,'disposition':'PROVISIONAL_WITHIN_RECORDED_CONDITIONS' if not reasons else 'INCONCLUSIVE',
            'falsificationReasons':reasons,
            'independentReplication':'NOT_ESTABLISHED'}


def run_campaign(campaign:dict, intervention:dict,endpoint:str, trials:int=1,
                 run_call=run_local_ollama_trial, timeout:float=120.0)->dict:
    """Explicit execution path, opt-in; no model outcome is invented on failure."""
    from reactor_reference_registry import verify_reference_bytes
    plan=campaign['plan'];validate_intervention(intervention,plan)
    require(type(trials) is int and 1<=trials<=20,'INVALID_TRIAL_COUNT')
    require(type(timeout) in (int,float) and 0<timeout<=300,'INVALID_TIMEOUT')
    require(is_localhost_url(endpoint),'NON_LOOPBACK_ENDPOINT_BLOCKED')
    require(plan['provider']=='ollama-local','OLLAMA_PROVIDER_REQUIRED')
    observations=[];errors=[]
    for i in range(trials):
        result=run_pairs(plan,endpoint,f'TRIAL-{i+1:03}',run_call=run_call,timeout=timeout)
        for o in result['observations']:
            o['interventionProvenance']=intervention_observation_binding(intervention,o['condition'])
            o['executionProvenance']['executionMode']=('LOCAL_OLLAMA_REPORTED' if run_call is run_local_ollama_trial
                                                       else 'MOCK_TEST_ONLY')
            observations.append(o)
        errors.extend(result['errors'])
    status='NOT_EXECUTED' if not observations else ('PARTIAL' if errors else 'COMPLETED')
    return {'schemaVersion':'gnome.reactor.local-campaign-execution.v3',
            'status':status,'observations':observations,'errors':errors,
            'modelProvenance':'PROVIDER_REPORTED_UNAUTHENTICATED' if run_call is run_local_ollama_trial else 'SYNTHETIC_MOCK_TEST_ONLY',
            'claimsVerified':False}


def main(argv=None)->int:
    import argparse
    parser=argparse.ArgumentParser(description='GNOME v3 local campaign runner (requires explicit --endpoint; does not score)')
    parser.add_argument('--campaign',required=True)
    parser.add_argument('--intervention',required=True)
    parser.add_argument('--endpoint',required=True)
    parser.add_argument('--trials',type=int,default=1)
    parser.add_argument('--timeout',type=float,default=120.0)
    parser.add_argument('--out',required=True)
    args=parser.parse_args(argv)
    try:
        if not is_localhost_url(args.endpoint):raise EvidenceError('NON_LOOPBACK_ENDPOINT_BLOCKED')
        def read(p):
            f=Path(p);require(f.is_file() and f.stat().st_size<=4*1024*1024,'FILE_NOT_FOUND_OR_TOO_LARGE')
            return json.loads(f.read_text(encoding='utf8'))
        campaign=read(args.campaign);intv=read(args.intervention)
        result=run_campaign(campaign,intv,args.endpoint,args.trials,timeout=args.timeout)
        Path(args.out).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf8')
        print(json.dumps({'status':result['status'],'observations':len(result['observations']),
                          'failures':len(result['errors']),'scored':False}))
        return 0 if result['status']=='COMPLETED' else 2
    except (EvidenceError,OSError,KeyError,TypeError,ValueError) as exc:
        print(json.dumps({'status':'NOT_EXECUTED','error':str(exc)}));return 2

if __name__=='__main__':raise SystemExit(main())
