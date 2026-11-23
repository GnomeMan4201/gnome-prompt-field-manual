"""JSON mode request and replay regression tests (offline mocks only)."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
from reactor_local_runner import run_local_ollama_trial
from reactor_pair_runner import run_pairs
from reactor_campaign_replay import replay_evidence_capsule_v3
from test_reactor_evidence_v2 import plan
from test_reactor_raw_replay_guard import good_capsule,reseal
RAW=b'{"model":"fixture-model","response":"{\\"answer\\":\\"42\\"}","done":true}'

class JsonModeContractTests(unittest.TestCase):
    def test_adapter_json_mode_explicit(self):
        with patch('reactor_local_runner.http.client.HTTPConnection') as conn:
            instance=conn.return_value
            r=instance.getresponse.return_value
            r.status=200
            r.length=None
            r.read.return_value=RAW
            result=run_local_ollama_trial('http://127.0.0.1:11434','fixture-model',
                                           'Question?',format_json=True)
            self.assertTrue(result['ok'],result)
            sent=json.loads(result['rawRequest'])
            self.assertEqual(sent['format'],'json')
            self.assertEqual(json.loads(instance.request.call_args.kwargs['body']),sent)

    def test_pair_requests_json_mode_for_both_conditions(self):
        p=plan();p['provider']='ollama-local';p['model']='fixture-model'
        with patch('reactor_local_runner.http.client.HTTPConnection') as conn:
            instance=conn.return_value
            r=instance.getresponse.return_value
            r.status=200
            r.length=None
            r.read.return_value=RAW
            result=run_pairs(p,'http://127.0.0.1:11434','FMT-TEST')
            self.assertTrue(result['executionComplete'],result)
            self.assertEqual(len(result['observations']),2)
            for call in instance.request.call_args_list:
                sent=json.loads(call.kwargs['body'])
                self.assertEqual(sent['format'],'json')

    def test_replay_accepts_legacy_and_json_requests(self):
        capsule=good_capsule()
        self.assertTrue(replay_evidence_capsule_v3(capsule)['valid'])
        for obs in capsule['execution']['observations']:
            ev=obs['executionProvenance']['providerEvidence']
            req=json.loads(ev['requestText']);req['format']='json'
            ev['requestText']=json.dumps(req)
            ev['requestSha256']=hashlib.sha256(ev['requestText'].encode()).hexdigest()
        self.assertTrue(replay_evidence_capsule_v3(reseal(capsule))['valid'])

    def test_replay_rejects_format_drift_or_other_modes(self):
        capsule=good_capsule()
        ev=capsule['execution']['observations'][0]['executionProvenance']['providerEvidence']
        req=json.loads(ev['requestText']);req['format']='json'
        ev['requestText']=json.dumps(req)
        ev['requestSha256']=hashlib.sha256(ev['requestText'].encode()).hexdigest()
        result=replay_evidence_capsule_v3(reseal(capsule))
        self.assertIn('RAW_REQUEST_FORMAT_DRIFT',str(result['errors']))
        req['format']='xml'
        ev['requestText']=json.dumps(req)
        ev['requestSha256']=hashlib.sha256(ev['requestText'].encode()).hexdigest()
        result=replay_evidence_capsule_v3(reseal(capsule))
        self.assertIn('RAW_REQUEST_PLAN_MISMATCH',str(result['errors']))

if __name__=='__main__':unittest.main()
