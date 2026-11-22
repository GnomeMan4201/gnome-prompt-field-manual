#!/usr/bin/env python3
"""Adversarial acceptance gates for the uploaded GNOME Phase VIII-C candidate.

Expected: candidate currently FAILS these tests. They are specification tests,
not results that should be presented as passed project tests.

Run with: GNOME_PHASE8C_DIR=/path/to/extracted/gnome-phase8c-empirical \
  python3 -m unittest -v test_phase8c_audit_regressions.py
"""
import json
import os
from pathlib import Path
import sys
import threading
import http.server
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from reactor_empirical_evaluator import attribute_campaign_pair, score_raw_observation
from reactor_reference_registry import create_reference, blind_verify_reference
from reactor_campaign_replay import build_evidence_capsule_v3, replay_evidence_capsule_v3
from reactor_campaign_runner import check_loopback_endpoint, attempt_falsification, build_lower_trust_intervention

class ExpectedSecurityGates(unittest.TestCase):
    def test_missing_comparability_is_unattributable(self):
        a = {'outputText':'CONTROL','passed':True}
        b = {'outputText':'ATTACK','passed':False}
        self.assertEqual('UNATTRIBUTABLE',attribute_campaign_pair(a,b)['disposition'])

    def test_missing_model_config_is_unattributable(self):
        a = {'inputHash':'SAME','outputText':'CONTROL','passed':True}
        b = {'inputHash':'SAME','outputText':'ATTACK','passed':False}
        self.assertEqual('UNATTRIBUTABLE',attribute_campaign_pair(a,b)['disposition'])

    def test_lower_trust_document_hashes_are_required(self):
        mutation = build_lower_trust_intervention('task','cfg','baseline','mutated','payload')
        a = {'taskHash':mutation['fixedTaskHash'], 'configHash':mutation['fixedConfigHash'], 'outputText':'ok', 'passed':True}
        b = {'taskHash':mutation['fixedTaskHash'], 'configHash':mutation['fixedConfigHash'], 'outputText':'bad', 'passed':False}
        self.assertEqual('UNATTRIBUTABLE',attribute_campaign_pair(a,b,mutation)['disposition'])

    def test_contradictory_answer_is_not_supported(self):
        reference = {'expectedAnswer':'18ms','authorityLevel':'SOURCE_CHECKED'}
        result = score_raw_observation('The answer was NOT 18ms. It was 99ms.',reference)
        self.assertFalse(result['passed'])

    def test_second_reviewer_cannot_be_first_reviewer(self):
        ref = create_reference('REF','DOC','log','Q2: 18ms','18ms','18ms', reviewer_id='rev1')
        result = blind_verify_reference(ref,'rev1','18ms',model_output_hidden=True)
        self.assertNotEqual('INDEPENDENTLY_CHECKED',result['authorityLevel'])

    def test_not_executed_capsule_cannot_support_empirical_success(self):
        capsule = build_evidence_capsule_v3({'campaignId':'C'}, {'family':'B'},
                    {'status':'NOT_EXECUTED','observations':[]}, {},
                    {'claims':[{'status':'SUPPORTED','claim':'Attack success'}]})
        self.assertFalse(replay_evidence_capsule_v3(capsule)['valid'])

    def test_falsification_cannot_promote_unknown_evidence(self):
        finding = {'referenceAuthority':'REVIEWER_ASSERTED'}
        self.assertFalse(attempt_falsification(finding)['survived'])

    def test_schema_rejects_wrong_typed_capsules(self):
        import jsonschema
        schema=json.loads((ROOT/'schemas/reactor-evidence-v3.schema.json').read_text())
        obj={'schemaVersion':'gnome.reactor.evidence.v3','campaign':None,
             'interventions':False,'execution':'NOT_EXECUTED','evaluation':0,
             'findings':'forged','integrity':[]}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(obj, schema)

    def test_local_endpoint_check_must_not_follow_redirects(self):
        hits=[]
        class Target(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path);self.send_response(200);self.end_headers()
            def log_message(self,*args):pass
        target=http.server.ThreadingHTTPServer(('127.0.0.1',0),Target)
        class Redirect(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header('Location',f'http://127.0.0.1:{target.server_port}/api/tags')
                self.end_headers()
            def log_message(self,*args):pass
        redirect=http.server.ThreadingHTTPServer(('127.0.0.1',0),Redirect)
        try:
            for server in (target,redirect):threading.Thread(target=server.serve_forever,daemon=True).start()
            result=check_loopback_endpoint(f'http://127.0.0.1:{redirect.server_port}')
            self.assertEqual([],hits,'Unexpected redirect target was contacted')
            self.assertNotEqual('ENDPOINT_REACHABLE',result['status'])
        finally:
            for server in (redirect,target):server.shutdown();server.server_close()

if __name__ == '__main__':
    unittest.main(verbosity=2)
