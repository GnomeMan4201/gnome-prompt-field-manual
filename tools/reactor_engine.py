#!/usr/bin/env python3
"""GNOME Reactor reference core: conservative comparability and deterministic offline replay.

This core makes no empirical claim about output quality. ``passed`` is a supplied
rubric observation, not a conclusion independently evaluated by this module.
"""
from __future__ import annotations
import hashlib
import json
import re
from collections import defaultdict
from typing import Any

HEX = re.compile(r'^[a-f0-9]{64}$')
EXPERIMENT_VERSION = 'gnome.reactor.experiment.v1'
OBSERVATION_VERSION = 'gnome.reactor.observation.v1'
CAPSULE_VERSION = 'gnome.reactor.capsule.v1'
# Non-prompt experimental factors; promptHash must *differ* between conditions.
MATCH_FIELDS = ('experimentId','inputId','inputHash','provider','model','evaluator',
                'temperature','seed','tools','datasetId','rubricHash')
HARD_FIELDS = ('experimentId','inputId','inputHash','provider','model','evaluator',
               'tools','datasetId','rubricHash')

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)

def _present(value):
    # Null is meaningful for explicitly unsupported seed, but not for other fields.
    return value is not None and value != ''

def _matching(a: dict, b: dict) -> dict:
    differences, missing = [], []
    for field in MATCH_FIELDS:
        va, vb = a.get(field), b.get(field)
        if field == 'seed' and field in a and field in b and va is None and vb is None:
            continue  # Explicit unsupported seed; not fabricated.
        if not _present(va) or not _present(vb):
            missing.append(field)
        elif va != vb:
            differences.append(field)
    if differences and any(k in HARD_FIELDS for k in differences):
        status = 'NOT_COMPARABLE'
    elif differences or missing:
        status = 'COMPARABLE_WITH_DISCLOSED_LIMITATIONS'
    else:
        status = 'COMPARABLE'
    return {'status':status, 'confounders':differences, 'missingMetadata':missing}

def evaluate_comparability(ctrl_cfg: dict[str, Any], var_cfg: dict[str, Any]) -> dict[str, Any]:
    return _matching(ctrl_cfg, var_cfg)

def validate_experiment(exp: dict[str, Any]) -> list[str]:
    errs=[]
    if not isinstance(exp,dict):
        return ['INVALID_EXPERIMENT']
    if exp.get('schemaVersion') != EXPERIMENT_VERSION: errs.append('INVALID_SCHEMA_VERSION')
    for key in ('experimentId','hypothesis'):
        if not isinstance(exp.get(key),str) or not exp[key].strip(): errs.append('MISSING_'+key.upper())
    for key in ('controlPromptHash','variantPromptHash'):
        if not isinstance(exp.get(key),str) or not HEX.fullmatch(exp[key]):errs.append('INVALID_'+key.upper())
    model=exp.get('modelConfig')
    if not isinstance(model,dict) or any(not isinstance(model.get(k),str) or not model[k].strip() for k in ('provider','model')):
        errs.append('INVALID_MODEL_CONFIG')
    rubric=exp.get('rubric')
    if not isinstance(rubric,dict) or not isinstance(rubric.get('criteria'),list) or not rubric['criteria'] or any(not isinstance(x,str) or not x.strip() for x in rubric['criteria']):
        errs.append('INVALID_SCORING_RUBRIC')
    dataset=exp.get('dataset')
    if not isinstance(dataset,dict) or not isinstance(dataset.get('datasetId'),str) or not dataset['datasetId'].strip():
        errs.append('INVALID_DATASET_ID')
    inputs=dataset.get('inputs',[]) if isinstance(dataset,dict) else []
    if not isinstance(inputs,list) or not inputs:errs.append('EMPTY_INPUT_SET');inputs=[]
    seen=set()
    for inp in inputs:
        if not isinstance(inp,dict) or not isinstance(inp.get('inputId'),str) or not inp['inputId'].strip():
            errs.append('INVALID_INPUT_ID');continue
        iid=inp['inputId']
        if iid in seen:errs.append('DUPLICATE_INPUT_ID:'+iid)
        seen.add(iid)
    return errs

def validate_observations(observations:list[dict], experiment:dict|None=None) -> list[str]:
    errors=[];seen=set()
    if not isinstance(observations,list):return ['OBSERVATIONS_NOT_ARRAY']
    valid_inputs={i.get('inputId') for i in (experiment or {}).get('dataset',{}).get('inputs',[]) if isinstance(i,dict)} if experiment else None
    for n,o in enumerate(observations):
        pre=f'OBSERVATION_{n}'
        if not isinstance(o,dict):errors.append(pre+':NOT_OBJECT');continue
        if o.get('schemaVersion')!=OBSERVATION_VERSION:errors.append(pre+':INVALID_SCHEMA_VERSION')
        for k in ('runId','experimentId','inputId','condition','inputHash','promptHash'):
            if not isinstance(o.get(k),str) or not o[k].strip():errors.append(pre+':MISSING_'+k)
        if o.get('condition') not in ('CONTROL','VARIANT'):errors.append(pre+':INVALID_CONDITION')
        for k in ('inputHash','promptHash'):
            if not isinstance(o.get(k),str) or not HEX.fullmatch(o[k]):errors.append(pre+':INVALID_'+k)
        if o.get('outputText') is not None and not isinstance(o.get('outputText'),str):errors.append(pre+':INVALID_OUTPUT')
        if 'outputText' not in o:errors.append(pre+':MISSING_OUTPUT')
        if o.get('passed') is not None and type(o.get('passed')) is not bool:errors.append(pre+':INVALID_PASS_FLAG')
        run=o.get('runId');key=(o.get('experimentId'),o.get('inputId'),o.get('trialId','trial-1'),o.get('condition'))
        if run in seen or key in seen:errors.append(pre+':DUPLICATE_OBSERVATION')
        seen.add(run);seen.add(key)
        if experiment:
            if o.get('experimentId')!=experiment.get('experimentId'):errors.append(pre+':EXPERIMENT_MISMATCH')
            if valid_inputs is not None and o.get('inputId') not in valid_inputs:errors.append(pre+':UNKNOWN_INPUT')
            wanted=experiment.get('controlPromptHash') if o.get('condition')=='CONTROL' else experiment.get('variantPromptHash')
            if o.get('promptHash')!=wanted:errors.append(pre+':PROMPT_HASH_MISMATCH')
            dataset=experiment.get('dataset',{})
            if o.get('datasetId') not in (None,dataset.get('datasetId')):
                errors.append(pre+':DATASET_MISMATCH')
            record=next((i for i in dataset.get('inputs',[]) if isinstance(i,dict) and i.get('inputId')==o.get('inputId')),None)
            if record is not None and isinstance(record.get('text'),str) and o.get('inputHash')!=sha256_text(record['text']):
                errors.append(pre+':INPUT_CONTENT_HASH_MISMATCH')
            if o.get('rubricHash') not in (None,sha256_text(canonical_json(experiment.get('rubric')))):
                errors.append(pre+':RUBRIC_HASH_MISMATCH')
            model=experiment.get('modelConfig',{})
            for field in ('provider','model','temperature','seed','tools'):
                if field in model and model[field] is not None and o.get(field) is not None and o.get(field)!=model[field]:
                    errors.append(pre+':MODEL_CONFIG_MISMATCH:'+field)

    return errors

def classify_paired_trial(ctrl:dict|None,var:dict|None)->str:
    if not isinstance(ctrl,dict) or not isinstance(var,dict):return 'UNATTRIBUTABLE'
    if ctrl.get('condition')!='CONTROL' or var.get('condition')!='VARIANT':return 'UNATTRIBUTABLE'
    if ctrl.get('outputText') is None or var.get('outputText') is None:return 'UNATTRIBUTABLE'
    if type(ctrl.get('passed')) is not bool or type(var.get('passed')) is not bool:return 'UNATTRIBUTABLE'
    if ctrl.get('promptHash')==var.get('promptHash') or any(not isinstance(o.get('promptHash'),str) or not HEX.fullmatch(o['promptHash']) for o in (ctrl,var)):
        return 'UNATTRIBUTABLE'
    if _matching(ctrl,var)['status']!='COMPARABLE':return 'UNATTRIBUTABLE'
    if not ctrl['passed'] and not var['passed']:return 'SHARED_FAILURE'
    if not ctrl['passed'] and var['passed']:return 'VARIANT_IMPROVEMENT'
    if ctrl['passed'] and not var['passed']:return 'VARIANT_INDUCED_FAILURE'
    return 'BOTH_PASS'

def build_capsule(source_refs,experiment,control_prompt,variant_prompt,dataset,observations,scores,claims,challenges):
    files={'source/references.json':canonical_json(source_refs),'experiments/experiment.json':canonical_json(experiment),
    'prompts/control.txt':control_prompt,'prompts/variant.txt':variant_prompt,'datasets/inputs.json':canonical_json(dataset),
    'runs/observations.json':canonical_json(observations),'evaluations/scores.json':canonical_json(scores),
    'claims/findings.json':canonical_json(claims),'challenges/challenges.json':canonical_json(challenges)}
    manifest={'capsuleId':experiment.get('experimentId',''), 'schemaVersion':CAPSULE_VERSION}
    files['manifest.json']=canonical_json(manifest)
    return {'schemaVersion':CAPSULE_VERSION,'manifest':manifest,
    'source':source_refs,'experiments':experiment,'prompts':{'control':control_prompt,'variant':variant_prompt},
    'datasets':dataset,'runs':{'observations':observations},'evaluations':scores,'claims':{'findings':claims},
    'challenges':{'items':challenges},'integrity':{'checksums':{k:sha256_text(v) for k,v in files.items()}}}

def verify_and_replay_capsule(cap):
    if not isinstance(cap,dict) or cap.get('schemaVersion')!=CAPSULE_VERSION:
        return {'valid':False,'errors':['UNSUPPORTED_SCHEMA_VERSION'],'replay':None}
    errors=[]
    try:
        files={'manifest.json':canonical_json(cap['manifest']),'source/references.json':canonical_json(cap['source']),
        'experiments/experiment.json':canonical_json(cap['experiments']),
        'prompts/control.txt':cap['prompts']['control'], 'prompts/variant.txt':cap['prompts']['variant'],
        'datasets/inputs.json':canonical_json(cap['datasets']),
        'runs/observations.json':canonical_json(cap['runs']['observations']),
        'evaluations/scores.json':canonical_json(cap['evaluations']),
        'claims/findings.json':canonical_json(cap['claims']['findings']),
        'challenges/challenges.json':canonical_json(cap['challenges']['items'])}
        checks=cap['integrity']['checksums']
        if not isinstance(checks,dict):raise TypeError('not a checksum mapping')
    except (KeyError,TypeError,ValueError) as exc:
        return {'valid':False,'errors':['MALFORMED_CAPSULE:'+str(exc)],'replay':None}
    for path,content in files.items():
        if path not in checks:errors.append('MISSING_CHECKSUM:'+path)
        elif not isinstance(content,str) or sha256_text(content)!=checks[path]:errors.append('CHECKSUM_MISMATCH:'+path)
    if set(checks)!=set(files):errors.append('UNEXPECTED_CHECKSUM_ENTRIES')
    exp=cap['experiments'];obs=cap['runs']['observations']
    if not isinstance(exp,dict) or not isinstance(cap.get('manifest'),dict) or not isinstance(cap.get('claims',{}).get('findings'),list):
        return {'valid':False,'errors':['MALFORMED_CAPSULE:invalid_record_shape'],'replay':None}
    if cap['manifest'].get('schemaVersion')!=CAPSULE_VERSION or cap['manifest'].get('capsuleId')!=exp.get('experimentId'):
        errors.append('INVALID_MANIFEST')
    errors.extend(validate_experiment(exp))
    if exp.get('controlPromptHash')!=sha256_text(cap['prompts']['control']):errors.append('CONTROL_PROMPT_HASH_MISMATCH')
    if exp.get('variantPromptHash')!=sha256_text(cap['prompts']['variant']):errors.append('VARIANT_PROMPT_HASH_MISMATCH')
    errors.extend(validate_observations(obs,exp))
    if not isinstance(obs,list):return {'valid':False,'errors':errors,'replay':None}
    seen={} ; groups=defaultdict(dict)
    for o in obs:
        if not isinstance(o,dict):continue
        key=(o.get('inputId'),o.get('trialId','trial-1'))
        condition=o.get('condition')
        if condition in groups[key]: errors.append('DUPLICATE_PAIR_SLOT:'+str(key))
        groups[key][condition]=o
    counts=dict.fromkeys(['BASELINE_FAILURE','SHARED_FAILURE','VARIANT_INDUCED_FAILURE','VARIANT_IMPROVEMENT','BOTH_PASS','UNATTRIBUTABLE'],0)
    for pair in groups.values():
        c,v=pair.get('CONTROL'),pair.get('VARIANT')
        cls=classify_paired_trial(c,v)
        counts[cls]+=1
        if cls in ('SHARED_FAILURE','VARIANT_IMPROVEMENT') and c['passed'] is False:counts['BASELINE_FAILURE']+=1
    for cl in cap['claims']['findings']:
        if cl.get('status')=='REPRODUCED':
            refs=cl.get('evidenceRefs')
            if not isinstance(refs,list) or not refs or any(ref not in files for ref in refs):
                errors.append('UNSUPPORTED_CLAIM_PROMOTION:'+str(cl.get('claimId')))
    return {'valid':not errors,'errors':errors,'replay':{'replayMode':'COMPUTATIONAL_REPLAY_ONLY','totalInputs':len(groups),'classifications':counts} if not errors else None}
