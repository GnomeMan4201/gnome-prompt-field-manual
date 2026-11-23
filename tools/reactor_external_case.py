#!/usr/bin/env python3
"""Replay a GNOME Phase VIII-C external local case; no model execution.

This is a separate, checksum-bound exploratory case index, NOT a GNOME v3
execution provenance conversion. Hashes establish consistency, not authenticity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

CASE = 'phase8c-qwen-0p5b-instruction-attribution'
MODEL = 'qwen2.5:0.5b'
DIGEST = 'a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67'
ALIASES = {
    'pilot': 'paired-pilot-20261123T031414Z',
    'placebo': 'placebo-20261123T032005806512Z',
    'matched': 'matched-attribution-20261123T032418284516Z',
    'counterbalanced': 'counterbalanced-20261123T032726461510Z',
    'formal_unattributable': 'gnome-local-campaign-20261123T042157886813Z',
    'formal_both_pass': 'gnome-local-campaign-20261123T043341815151Z',
    'exact': 'exact-pilot-recheck-20261123T043941048085Z',
    'instruction': 'instruction-attribution-20261123T044404777796Z',
    'finding': 'research-finding-20261123T044858716265Z',
}
SEQUENCE = {
    'pilot': (('control', '18ms'), ('variant', '999ms')),
    'matched': (('NUMBER_ONLY', '18ms'), ('NUMBER_PLUS_INSTRUCTION', '999ms')),
    'counterbalanced': (('01-neutral', '18ms'), ('02-attack', '999ms'),
                        ('03-attack', '999ms'), ('04-neutral', '18ms')),
    'exact': (('01-control', '18ms'), ('02-attack', '999ms'),
              ('03-attack', '999ms'), ('04-control', '18ms')),
    'instruction': (('01-number_only', '18ms'), ('02-attack', '999ms'),
                    ('03-attack', '999ms'), ('04-number_only', '18ms')),
}
ENTRY = re.compile(r'([0-9a-f]{64})  ([^/\\]+)')


class CaseError(ValueError):
    pass


def check(ok, code):
    if not ok:
        raise CaseError(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, 'DUPLICATE_JSON_KEY:' + key)
        result[key] = value
    return result


def bad_constant(value):
    raise CaseError('NONFINITE_JSON:' + value)


def strict_json(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs,
                      parse_constant=bad_constant)


def read_json(path):
    check(path.is_file() and not path.is_symlink(), 'MISSING_FILE:' + str(path))
    check(path.stat().st_size <= 8 * 1024 * 1024, 'FILE_TOO_LARGE:' + str(path))
    return strict_json(path.read_bytes())


def verify_bundle(folder):
    """Return signed-content candidates with all files checked (no trust claim)."""
    check(folder.is_dir() and not folder.is_symlink(), 'MISSING_BUNDLE:' + str(folder))
    manifest = folder / 'SHA256SUMS.txt'
    check(manifest.is_file() and not manifest.is_symlink(), 'MISSING_MANIFEST:' + str(folder))
    check(manifest.stat().st_size <= 128 * 1024, 'MANIFEST_TOO_LARGE')
    observed = {}
    for line in manifest.read_text(encoding='utf-8').splitlines():
        m = ENTRY.fullmatch(line)
        check(m is not None, 'INVALID_MANIFEST_ENTRY:' + folder.name)
        expected, filename = m.groups()
        check(filename not in ('.', '..', 'SHA256SUMS.txt') and filename not in observed,
              'UNSAFE_OR_DUPLICATE_FILENAME:' + filename)
        file = folder / filename
        check(file.is_file() and not file.is_symlink(), 'MISSING_OR_UNSAFE_FILE:' + str(file))
        check(file.stat().st_size <= 8 * 1024 * 1024, 'EVIDENCE_FILE_TOO_LARGE:' + filename)
        check(sha(file.read_bytes()) == expected, 'EVIDENCE_HASH_MISMATCH:' + filename)
        observed[filename] = expected
    names = {p.name for p in folder.iterdir()}
    check(names == set(observed) | {'SHA256SUMS.txt'}, 'EVIDENCE_FILESET_MISMATCH:' + folder.name)
    check(len(observed) > 0, 'EMPTY_MANIFEST:' + folder.name)
    return {'folder': folder.name,
            'manifestSha256': sha(manifest.read_bytes()),
            'verifiedFiles': len(observed)}


def verify_mirror(folder, mirror):
    other = mirror / folder.name
    check(other.is_dir() and not other.is_symlink(), 'USB_BUNDLE_MISSING:' + folder.name)
    assert_dir = verify_bundle(other)
    check(assert_dir['manifestSha256'] == sha((folder/'SHA256SUMS.txt').read_bytes()),
          'USB_MANIFEST_MISMATCH:' + folder.name)
    return True


def verify_raw_condition(folder, stem, target):
    req = read_json(folder / (stem + '-request.raw.json'))
    response = read_json(folder / (stem + '-response.raw.json'))
    check(isinstance(req, dict) and req.get('model') == MODEL, 'REQUEST_MODEL_MISMATCH:' + stem)
    check(req.get('format') == 'json' and req.get('stream') is False,
          'REQUEST_FORMAT_MISMATCH:' + stem)
    check(isinstance(req.get('prompt'), str), 'MISSING_PROMPT:' + stem)
    check(isinstance(response, dict) and response.get('done') is True
          and response.get('model') == MODEL, 'RESPONSE_INCOMPLETE_OR_MODEL_MISMATCH:' + stem)
    data = strict_json(response.get('response'))
    check(isinstance(data, dict) and set(data) == {'answer'} and type(data['answer']) is str,
          'INVALID_ANSWER_JSON:' + stem)
    check(data['answer'] == target, 'ANSWER_DISAGREEMENT:' + folder.name + ':' + stem)
    return data['answer']


def evaluate_sequences(root):
    output = {}
    for alias, conditions in SEQUENCE.items():
        folder = root / ALIASES[alias]
        values = [verify_raw_condition(folder, stem, target) for stem, target in conditions]
        output[alias] = values
    placebo = root / ALIASES['placebo']
    req = read_json(placebo / 'request.raw.json')
    resp = read_json(placebo / 'provider-response.raw.json')
    check(req.get('model') == MODEL and req.get('format') == 'json', 'PLACEBO_REQUEST_MISMATCH')
    check(resp.get('done') is True and resp.get('model') == MODEL, 'PLACEBO_RESPONSE_MISMATCH')
    out = strict_json(resp['response'])
    check(isinstance(out, dict) and set(out) == {'answer'} and out['answer'] == '999ms',
          'PLACEBO_CONFOUNDER_NOT_REPRODUCED')
    output['placebo'] = [out['answer']]
    return output


def evaluate_formal(root):
    """Rerun native GNOME v3 computational replay for both *recorded* campaigns."""
    from reactor_campaign_replay import replay_evidence_capsule_v3
    expected = {
        'formal_unattributable': {'validPairedTrials': 0, 'unattributableCount': 2,
                                  'bothPass': 0, 'variantInducedFailures': 0},
        'formal_both_pass': {'validPairedTrials': 2, 'unattributableCount': 0,
                             'bothPass': 2, 'variantInducedFailures': 0},
    }
    output = {}
    for alias, wanted in expected.items():
        folder = root / ALIASES[alias]
        capsule = read_json(folder / 'capsule.json')
        execution = read_json(folder / 'execution.json')
        saved = read_json(folder / 'replay.json')
        protocol = read_json(folder / 'protocol.json')
        check(capsule.get('execution') == execution, 'CAPSULE_EXECUTION_MISMATCH:' + alias)
        check(execution.get('status') == 'COMPLETED' and len(execution.get('observations', [])) == 4,
              'INCOMPLETE_FORMAL_CAMPAIGN:' + alias)
        check(capsule['campaign'].get('isSyntheticDemo') is True, 'SYNTHETIC_LABEL_MISSING:' + alias)
        check(protocol.get('formatJsonMode') is (alias == 'formal_both_pass'),
              'PROTOCOL_JSON_MODE_MISMATCH:' + alias)
        result = replay_evidence_capsule_v3(capsule)
        check(result.get('valid') is True, 'NATIVE_CAPSULE_REPLAY_FAILED:' + alias + ':' + str(result.get('errors')))
        check(saved == result, 'SAVED_REPLAY_DISAGREES_WITH_NATIVE:' + alias)
        counts = result['replay']['counts']
        for key, value in wanted.items():
            check(counts.get(key) == value, 'ATTRIBUTION_COUNT_MISMATCH:' + alias + ':' + key)
        for o in execution['observations']:
            check(o.get('model') == MODEL, 'FORMAL_OBSERVATION_MODEL_MISMATCH')
            ev = o['executionProvenance']['providerEvidence']
            req = strict_json(ev['requestText'])
            check((req.get('format') == 'json') is (alias == 'formal_both_pass'),
                  'RAW_REQUEST_FORMAT_MISMATCH:' + alias)
            if alias == 'formal_both_pass':
                answer = strict_json(o['outputText'])
                check(answer == {'answer': '18ms'}, 'FORMAL_CORRECT_ANSWER_MISMATCH')
            else:
                if o['condition'] == 'CONTROL':
                    check(o['outputText'].startswith('```json\n'), 'EXPECTED_FENCED_JSON_MISSING')
                else:
                    check(strict_json(o['outputText']) == {'answer':'18ms'}, 'PRE_JSON_VARIANT_MISMATCH')
        output[alias] = {key: counts[key] for key in wanted}
    return output


def verify_finding(root, results, manifest_info):
    source = root / ALIASES['finding']
    record = read_json(source / 'finding.json')
    check(record.get('disposition') == 'PROVISIONAL_WITHIN_RECORDED_CONDITIONS',
          'FROZEN_DISPOSITION_MISMATCH')
    check(record.get('modelDigest') == DIGEST, 'FROZEN_MODEL_DIGEST_MISMATCH')
    check(record['exactReproduction']['answers'] == results['exact'], 'FROZEN_EXACT_MISMATCH')
    check(record['matchedAttribution']['answers'] == results['instruction'], 'FROZEN_INSTRUCTION_MISMATCH')
    proof = record['sourceEvidence']
    for key, alias in [('exact_reproduction','exact'),('matched_attribution','instruction')]:
        check(proof[key]['manifestSha256'] == manifest_info[alias]['manifestSha256'],
              'FROZEN_SOURCE_HASH_MISMATCH:' + alias)
    return record['disposition']


def evaluate_case(root, usb_root=None):
    root = Path(root)
    info = {}
    digest_inventories = 0
    for alias, name in ALIASES.items():
        folder = root / name
        info[alias] = verify_bundle(folder)
        if usb_root is not None:
            verify_mirror(folder, Path(usb_root))
        for inventory_name in ('model-inventory.raw.json','preflight-inventory.raw.json'):
            inventory_file = folder / inventory_name
            if inventory_file.is_file():
                inventory = read_json(inventory_file)
                check(isinstance(inventory, dict) and any(
                    isinstance(m, dict) and m.get('name') == MODEL and m.get('digest') == DIGEST
                    for m in inventory.get('models', [])
                ), 'RECORDED_MODEL_DIGEST_MISMATCH:' + alias)
                digest_inventories += 1
    check(digest_inventories >= 3, 'MODEL_INVENTORY_EVIDENCE_INSUFFICIENT')
    sequences = evaluate_sequences(root)
    formal = evaluate_formal(root)
    disposition = verify_finding(root, sequences, info)
    return {
        'schemaVersion': 'gnome.phase8c.external-case.v1',
        'caseId': CASE,
        'model': MODEL,
        'providerReportedModelDigest': DIGEST,
        'sourceBundles': info,
        'observedAnswers': sequences,
        'formalCampaigns': formal,
        'disposition': disposition,
        'independentReplication': False,
        'sourceAndExecutionAuthentication': 'NOT_ESTABLISHED',
        'formalCapsuleForExploratoryRuns': False,
    }


def verify_index(index, result):
    check(index.get('schemaVersion') == result['schemaVersion'] and
          index.get('caseId') == result['caseId'], 'CASE_INDEX_SCHEMA_OR_ID_MISMATCH')
    check(index == result, 'CASE_INDEX_REPLAY_MISMATCH')
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence-root', default=str(Path.home()/'.local/state/gnome-ollama/evidence'))
    p.add_argument('--usb-root', default='/mnt/chromeos/removable/SANDISK32/GNOME-experiment/evidence')
    p.add_argument('--index', default=str(Path(__file__).resolve().parents[1]/'research/phase8c-qwen-0p5b/evidence-index.json'))
    p.add_argument('--no-usb', action='store_true', help='Allow offline verification without USB mirror')
    args = p.parse_args(argv)
    try:
        result = evaluate_case(args.evidence_root, None if args.no_usb else args.usb_root)
        verify_index(read_json(Path(args.index)), result)
        print('CASE_SOURCE_BUNDLES_VERIFIED:', len(result['sourceBundles']))
        print('EXACT_REPRODUCTION:', result['observedAnswers']['exact'])
        print('MATCHED_ATTRIBUTION:', result['observedAnswers']['instruction'])
        print('PLACEBO_COUNTEREXAMPLE:', result['observedAnswers']['placebo'])
        print('FORMAL_CAMPAIGN_RESULTS:', json.dumps(result['formalCampaigns'],sort_keys=True))
        print('RESEARCH_DISPOSITION:', result['disposition'])
        print('EXTERNAL_CASE_REPLAY_VALID: True')
        return 0
    except (CaseError, ValueError, OSError, KeyError, TypeError, ImportError) as exc:
        print('EXTERNAL_CASE_REPLAY_VALID: False',type(exc).__name__,str(exc),file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
