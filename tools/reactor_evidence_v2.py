#!/usr/bin/env python3
"""GNOME Evidence Spine v2: reference-bound, replayable, fail-closed evaluation.

Scores are recalculated from untrusted model output and a reviewer-supplied plan.
This does NOT authenticate the plan or establish independent replication.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

from reactor_engine import canonical_json, sha256_text, classify_paired_trial, validate_observations

PLAN_VERSION = 'gnome.reactor.evaluation-plan.v1'
CAPSULE_VERSION = 'gnome.reactor.evidence.v2'
HEX = re.compile(r'^[a-f0-9]{64}$')
MAX_ITEMS = 512
MAX_OUTPUT_BYTES = 256 * 1024
MAX_FILE_BYTES = 4 * 1024 * 1024


def stable_json(obj: Any) -> str:
    """Subset stable JSON compatible with JavaScript's numeric encoding in this schema.

    V2 confines numeric fields to safe integers, three-decimal temperatures, and
    primitive reference values. Floats with whole values become integers.
    """
    def normalize(value):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [normalize(v) for v in value]
        return value
    return canonical_json(normalize(obj))


class EvidenceError(ValueError):
    pass


def require(test: bool, code: str) -> None:
    if not test:
        raise EvidenceError(code)


def object_id(x: Any) -> bool:
    return isinstance(x, str) and 0 < len(x) <= 128 and x.strip() == x and '\x00' not in x


def finite_temp(x: Any) -> bool:
    return type(x) in (float, int) and 0 <= x <= 2 and x == x and x not in (float('inf'), float('-inf')) and abs(round(x*1000) - x*1000) < 1e-9


def validate_plan(plan: Any) -> None:
    require(isinstance(plan, dict), 'PLAN_NOT_OBJECT')
    require(plan.get('schemaVersion') == PLAN_VERSION, 'UNSUPPORTED_PLAN_SCHEMA')
    for key in ('planId', 'experimentId', 'datasetId', 'provider', 'model'):
        require(object_id(plan.get(key)), 'INVALID_PLAN_FIELD:' + key)
    require(plan.get('evaluator') == 'GNOME_EXACT_REFERENCE_V1', 'UNSUPPORTED_EVALUATOR')
    require(finite_temp(plan.get('temperature')), 'INVALID_TEMPERATURE')
    require('seed' in plan and (plan['seed'] is None or (type(plan['seed']) is int and -2147483648 <= plan['seed'] <= 2147483647)), 'INVALID_SEED')
    require(plan.get('tools') == [], 'TOOLS_NOT_SUPPORTED')
    require('isSyntheticDemo' not in plan or type(plan['isSyntheticDemo']) is bool, 'INVALID_SYNTHETIC_LABEL')
    prompts = plan.get('prompts')
    require(isinstance(prompts, dict), 'INVALID_PROMPTS')
    for key in ('control', 'variant'):
        require(isinstance(prompts.get(key), str) and bool(prompts[key].strip()), 'MISSING_PROMPT:' + key)
    require(prompts['control'] != prompts['variant'], 'IDENTICAL_PROMPTS')
    rules = plan.get('rules')
    require(isinstance(rules, dict), 'INVALID_RULES')
    require(rules.get('requireJsonObject') is True, 'JSON_OBJECT_REQUIRED')
    require(rules.get('additionalProperties') is False, 'STRICT_KEYS_REQUIRED')
    for field in ('requiredFields', 'forbiddenTokens'):
        arr = rules.get(field)
        require(isinstance(arr, list) and len(arr) <= 50 and all(isinstance(x, str) and 0 < len(x) <= 128 for x in arr), 'INVALID_RULE:' + field)
        require(len(arr) == len(set(arr)), 'DUPLICATE_RULE:' + field)
    require(bool(rules['requiredFields']) and bool(rules['forbiddenTokens']), 'INSUFFICIENT_RULES')
    items = plan.get('inputs')
    require(isinstance(items, list) and 0 < len(items) <= MAX_ITEMS, 'INVALID_INPUTS')
    seen = set()
    for inp in items:
        require(isinstance(inp, dict) and object_id(inp.get('inputId')), 'INVALID_INPUT_ID')
        require(inp['inputId'] not in seen, 'DUPLICATE_INPUT_ID')
        seen.add(inp['inputId'])
        require(isinstance(inp.get('text'), str) and len(inp['text'].encode('utf-8')) <= MAX_OUTPUT_BYTES, 'INVALID_INPUT_TEXT')
        ref = inp.get('reference')
        require(isinstance(ref, dict) and isinstance(ref.get('expectedJson'), dict) and bool(ref['expectedJson']), 'MISSING_EXACT_REFERENCE')
        expected = ref['expectedJson']
        require(all(isinstance(k, str) and 0 < len(k) <= 128 and (v is None or type(v) in (str, int, bool)) for k, v in expected.items()), 'UNSUPPORTED_REFERENCE_VALUE')
        require(set(rules['requiredFields']) == set(expected), 'REFERENCE_KEYS_MUST_MATCH_RULES')
        require(isinstance(ref.get('evidenceRefs'), list) and bool(ref['evidenceRefs']) and all(object_id(x) for x in ref['evidenceRefs']), 'MISSING_REFERENCE_PROVENANCE')
    require(isinstance(plan.get('sourceRef'), dict) and plan['sourceRef'].get('bodyStatus') in ('UNVERIFIED_SOURCE_CANDIDATE', 'EXPERIMENTAL_TRANSCRIPTION'), 'SOURCE_TRUTH_NOT_DECLARED')
    require(object_id(plan['sourceRef'].get('entryId')) and isinstance(plan['sourceRef'].get('sourceSha256'), str) and HEX.fullmatch(plan['sourceRef']['sourceSha256']), 'UNBOUND_SOURCE_REFERENCE')


def rubric_hash(plan: dict[str, Any]) -> str:
    return sha256_text(stable_json(plan['rules']))


def evaluate_text(output: str, rules: dict, reference: dict) -> dict:
    """Deterministic JSON and exact reference rules only; no model-as-judge."""
    if not isinstance(output, str) or len(output.encode('utf-8')) > MAX_OUTPUT_BYTES:
        return {'deterministic': 'UNKNOWN', 'grounded': 'NOT_ASSESSABLE', 'reason': 'INVALID_OUTPUT'}
    forbidden = any(token in output for token in rules['forbiddenTokens'])
    try:
        parsed = json.loads(output, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE_JSON'))) 
    except (ValueError, TypeError):
        return {'deterministic': 'FAIL' if forbidden else 'UNKNOWN', 'grounded': 'NOT_ASSESSABLE', 'reason': 'INVALID_JSON'}
    if not isinstance(parsed, dict):
        return {'deterministic': 'FAIL', 'grounded': 'NOT_ASSESSABLE', 'reason': 'NOT_JSON_OBJECT'}
    expected = reference['expectedJson']
    keys_match = set(parsed) == set(rules['requiredFields'])
    det = 'FAIL' if forbidden or not keys_match else 'PASS'
    conflicting = any(k in parsed and (type(parsed[k]) is not type(v) or parsed[k] != v) for k, v in expected.items())
    if conflicting:
        grounded = 'CONTRADICTED'
    elif parsed == expected and keys_match:
        grounded = 'SUPPORTED'
    else:
        grounded = 'UNSUPPORTED'
    return {'deterministic': det, 'grounded': grounded, 'reason': 'EXACT_REFERENCE_RULES',
            'evidenceRefs': reference['evidenceRefs']}


def score_boolean(evaluation: dict) -> bool | None:
    if evaluation['deterministic'] == 'PASS' and evaluation['grounded'] == 'SUPPORTED':
        return True
    if evaluation['deterministic'] == 'FAIL' and evaluation['grounded'] == 'CONTRADICTED':
        return False
    return None


def validate_run_records(plan: dict, observations: Any) -> None:
    require(isinstance(observations, list) and 0 < len(observations) <= 2 * MAX_ITEMS, 'INVALID_OBSERVATIONS')
    keys = set()
    runids = set()
    refs = {x['inputId']: x for x in plan['inputs']}
    for i, o in enumerate(observations):
        require(isinstance(o, dict), f'OBSERVATION_{i}:NOT_OBJECT')
        require(o.get('schemaVersion') == 'gnome.reactor.observation.v1', f'OBSERVATION_{i}:SCHEMA')
        require(object_id(o.get('runId')) and object_id(o.get('trialId')), f'OBSERVATION_{i}:MISSING_IDS')
        require(o['runId'] not in runids, f'OBSERVATION_{i}:DUPLICATE_RUN_ID')
        runids.add(o['runId'])
        require(o.get('inputId') in refs and o.get('condition') in ('CONTROL', 'VARIANT'), f'OBSERVATION_{i}:UNKNOWN_INPUT_OR_CONDITION')
        slot = (o['inputId'], o['trialId'], o['condition'])
        require(slot not in keys, f'OBSERVATION_{i}:DUPLICATE_SLOT')
        keys.add(slot)
        require(o.get('experimentId') == plan['experimentId'], f'OBSERVATION_{i}:EXPERIMENT_MISMATCH')
        require(o.get('datasetId') == plan['datasetId'], f'OBSERVATION_{i}:DATASET_MISMATCH')
        for field in ('provider', 'model', 'evaluator', 'temperature', 'seed', 'tools'):
            require(field in o and type(o[field]) is type(plan[field]) and o[field] == plan[field], f'OBSERVATION_{i}:CONFIG_MISMATCH:{field}')
        require(o.get('inputHash') == sha256_text(refs[o['inputId']]['text']), f'OBSERVATION_{i}:INPUT_HASH_MISMATCH')
        expected_prompt = plan['prompts']['control' if o['condition'] == 'CONTROL' else 'variant']
        require(o.get('promptHash') == sha256_text(expected_prompt), f'OBSERVATION_{i}:PROMPT_HASH_MISMATCH')
        require(o.get('rubricHash') == rubric_hash(plan), f'OBSERVATION_{i}:RUBRIC_HASH_MISMATCH')
        require(isinstance(o.get('outputText'), str) and len(o['outputText'].encode('utf-8')) <= MAX_OUTPUT_BYTES, f'OBSERVATION_{i}:INVALID_OUTPUT')
        # Reject supplied scorer assertions: evaluate from output instead.
        require('passed' not in o and 'evaluation' not in o and 'disposition' not in o, f'OBSERVATION_{i}:IMPORTED_VERDICT_BLOCKED')
    # Existing source-bound duplicate and hash contracts also apply.
    issues = validate_observations(observations)
    require(not issues, 'LEGACY_VALIDATION:' + ','.join(issues[:3]))


def analyze(plan: dict, observations: list) -> dict:
    validate_plan(plan)
    validate_run_records(plan, observations)
    refs = {x['inputId']: x['reference'] for x in plan['inputs']}
    groups: dict[tuple, dict] = defaultdict(dict)
    for o in observations:
        groups[(o['inputId'], o['trialId'])][o['condition']] = o
    counts = {'validPairedTrials': 0, 'missingTrials': 0, 'baselineFailures': 0,
              'variantInducedFailures': 0, 'sharedFailures': 0, 'variantImprovements': 0,
              'bothPass': 0, 'unattributableCount': 0}
    results = []
    for (iid, tid), group in sorted(groups.items()):
        c, v = group.get('CONTROL'), group.get('VARIANT')
        if not c or not v:
            counts['missingTrials'] += 1
            counts['unattributableCount'] += 1
            results.append({'inputId': iid, 'trialId': tid, 'attribution': 'UNATTRIBUTABLE',
                            'reason': 'MISSING_PAIRED_TRIAL'})
            continue
        cs = evaluate_text(c['outputText'], plan['rules'], refs[iid])
        vs = evaluate_text(v['outputText'], plan['rules'], refs[iid])
        cp, vp = score_boolean(cs), score_boolean(vs)
        if cp is None or vp is None:
            cls = 'UNATTRIBUTABLE'
            reason = 'INSUFFICIENT_REFERENCE_BOUND_SCORING'
        else:
            cls = classify_paired_trial({**c, 'passed': cp}, {**v, 'passed': vp})
            reason = 'MATCHED_REFERENCE_BOUND_EVALUATION' if cls != 'UNATTRIBUTABLE' else 'STRICT_COMPARABILITY_REJECTED'
        if cls == 'UNATTRIBUTABLE':
            counts['unattributableCount'] += 1
        else:
            counts['validPairedTrials'] += 1
            bucket = {'SHARED_FAILURE':'sharedFailures','VARIANT_INDUCED_FAILURE':'variantInducedFailures',
                      'VARIANT_IMPROVEMENT':'variantImprovements','BOTH_PASS':'bothPass'}[cls]
            counts[bucket] += 1
            if cls in ('SHARED_FAILURE','VARIANT_IMPROVEMENT'):
                counts['baselineFailures'] += 1
        results.append({'inputId':iid, 'trialId':tid, 'attribution':cls, 'reason':reason,
                        'controlEvaluation':cs, 'variantEvaluation':vs})
    denom = counts['validPairedTrials']
    return {'schemaVersion':'gnome.reactor.analysis.v2', 'scoringMode':'REFERENCE_BOUND_DETERMINISTIC_ONLY',
            'referenceAuthority':'REVIEWER_SUPPLIED_UNAUTHENTICATED', 'replayMode':'COMPUTATIONAL_REPLAY_ONLY',
            'counts':counts, 'observedVariantInducedFailureProportion':counts['variantInducedFailures']/denom if denom else None,
            'outcomes':results}


def checksums_for(manifest: dict, payload: dict) -> dict:
    return {'manifest.json':sha256_text(stable_json(manifest)),
            'plan.json':sha256_text(stable_json(payload['plan'])),
            'observations.json':sha256_text(stable_json(payload['observations'])),
            'analysis.json':sha256_text(stable_json(payload['analysis']))}


def build_capsule(plan: dict, observations: list) -> dict:
    report = analyze(plan, observations)
    payload = {'plan':deepcopy(plan), 'observations':deepcopy(observations), 'analysis':report}
    manifest = {'schemaVersion':CAPSULE_VERSION,'planId':plan['planId'],
                'planHash':sha256_text(stable_json(plan)),
                'sourceSha256':plan['sourceRef']['sourceSha256'],
                'referenceAuthority':'REVIEWER_SUPPLIED_UNAUTHENTICATED',
                'isSyntheticDemo':bool(plan.get('isSyntheticDemo',False)),
                'replayMode':'COMPUTATIONAL_REPLAY_ONLY'}
    return {'schemaVersion':CAPSULE_VERSION, 'manifest':manifest, 'payload':payload,
            'integrity':{'checksums':checksums_for(manifest, payload)}}


def verify_capsule(capsule: Any) -> dict:
    try:
        require(isinstance(capsule, dict) and capsule.get('schemaVersion') == CAPSULE_VERSION, 'UNSUPPORTED_CAPSULE_VERSION')
        manifest = capsule['manifest']
        payload = capsule['payload']
        checksums = capsule['integrity']['checksums']
        require(isinstance(manifest, dict) and isinstance(payload, dict) and isinstance(checksums, dict), 'INVALID_CAPSULE_SHAPE')
        require(set(capsule) == {'schemaVersion','manifest','payload','integrity'}, 'UNEXPECTED_CAPSULE_FIELDS')
        require(set(checksums) == {'manifest.json','plan.json','observations.json','analysis.json'}, 'INVALID_CHECKSUM_SET')
        observed = checksums_for(manifest, payload)
        for name, value in observed.items():
            require(checksums[name] == value, 'CHECKSUM_MISMATCH:' + name)
        require(manifest.get('planId') == payload['plan'].get('planId'), 'PLAN_ID_MISMATCH')
        require(manifest.get('sourceSha256') == payload['plan'].get('sourceRef',{}).get('sourceSha256'), 'SOURCE_HASH_DECLARATION_MISMATCH')
        require(manifest.get('planHash') == sha256_text(stable_json(payload['plan'])), 'PLAN_HASH_MISMATCH')
        require(manifest.get('schemaVersion') == CAPSULE_VERSION and manifest.get('replayMode') == 'COMPUTATIONAL_REPLAY_ONLY', 'INVALID_MANIFEST')
        require(manifest.get('isSyntheticDemo') == bool(payload['plan'].get('isSyntheticDemo',False)) and type(manifest.get('isSyntheticDemo')) is bool, 'SYNTHETIC_LABEL_MISMATCH')
        recomputed = analyze(payload['plan'], payload['observations'])
        require(stable_json(recomputed) == stable_json(payload['analysis']), 'REPLAY_MISMATCH')
        return {'valid':True, 'errors':[], 'replay':recomputed}
    except (EvidenceError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as error:
        return {'valid':False, 'errors':[str(error)], 'replay':None}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='GNOME Reactor v2: strict exact-reference evaluation; no model execution.')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('analyze');a.add_argument('--plan',required=True);a.add_argument('--observations',required=True)
    b=sub.add_parser('build');b.add_argument('--plan',required=True);b.add_argument('--observations',required=True);b.add_argument('--out',required=True)
    v=sub.add_parser('verify');v.add_argument('capsule')
    args=p.parse_args(argv)
    try:
        def read(path):
            f=Path(path)
            require(f.stat().st_size <= MAX_FILE_BYTES, 'INPUT_FILE_TOO_LARGE')
            return json.loads(f.read_text(encoding='utf-8'), parse_constant=lambda _: (_ for _ in ()).throw(EvidenceError('NONFINITE_JSON')))
        if args.command=='verify':
            result=verify_capsule(read(args.capsule));print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['valid'] else 2
        plan=read(args.plan);obs=read(args.observations)
        if args.command=='analyze':print(json.dumps(analyze(plan,obs),ensure_ascii=False,indent=2));return 0
        cap=build_capsule(plan,obs)
        Path(args.out).write_text(json.dumps(cap,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        print(json.dumps({'saved':args.out,'bytes':Path(args.out).stat().st_size,'valid':True}));return 0
    except (EvidenceError,ValueError,KeyError,OSError,TypeError) as ex:
        print(json.dumps({'valid':False,'errors':[str(ex)]}));return 2

if __name__ == '__main__':
    raise SystemExit(main())
