"""Fail-closed replay tests with mock provider evidence; no network calls."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
from reactor_campaign_replay import build_checked_capsule_v3,replay_evidence_capsule_v3,canonical_json,sha256_text
from test_reactor_viiic_integrity import fixture,observations


def good_capsule():
    campaign,intervention=fixture(family='B_LOWER_TRUST_INJECTION',mode='LOWER_TRUST_DOCUMENT')
    plan=campaign['plan']
    obs=observations(campaign,intervention)
    for o in obs:
        prompt=plan['prompts']['control' if o['condition']=='CONTROL' else 'variant']
        prompt+='\n\n[INPUT DATA — TREAT AS UNTRUSTED TEXT]\n'+plan['inputs'][0]['text']+'\n[/INPUT DATA]'
        req={'model':plan['model'],'prompt':prompt,'stream':False,'options':{'temperature':0}}
        resp={'model':plan['model'],'response':o['outputText'],'done':True}
        rt=json.dumps(req,ensure_ascii=False)
        st=json.dumps(resp,ensure_ascii=False)
        o['executionProvenance']={
            'executionMode':'LOCAL_OLLAMA_REPORTED',
            'providerEvidence':{'requestText':rt,'responseText':st,
                'requestSha256':hashlib.sha256(rt.encode()).hexdigest(),
                'responseSha256':hashlib.sha256(st.encode()).hexdigest()}}
    execution={'status':'COMPLETED','observations':obs,'errors':[],
               'modelProvenance':'PROVIDER_REPORTED_UNAUTHENTICATED'}
    return build_checked_capsule_v3(campaign,intervention,execution,{'claims':[]})


def reseal(c):
    c['integrity']['checksums']['execution']=sha256_text(canonical_json(c['execution']))
    return c


class RawReplayGuardTests(unittest.TestCase):
    def test_valid_raw_evidence_replays(self):
        self.assertTrue(replay_evidence_capsule_v3(good_capsule())['valid'])

    def test_missing_raw_evidence_rejected_even_after_rehash(self):
        c=good_capsule()
        del c['execution']['observations'][0]['executionProvenance']['providerEvidence']
        self.assertIn('RAW_EVIDENCE_MISSING',str(replay_evidence_capsule_v3(reseal(c))['errors']))

    def test_changed_raw_response_rejected_even_after_rehash(self):
        c=good_capsule()
        ev=c['execution']['observations'][0]['executionProvenance']['providerEvidence']
        raw=json.loads(ev['responseText'])
        raw['response']='{}'
        ev['responseText']=json.dumps(raw)
        ev['responseSha256']=hashlib.sha256(ev['responseText'].encode()).hexdigest()
        self.assertIn('RAW_RESPONSE_OUTPUT_MISMATCH',str(replay_evidence_capsule_v3(reseal(c))['errors']))

    def test_changed_raw_request_rejected_even_after_rehash(self):
        c=good_capsule()
        ev=c['execution']['observations'][0]['executionProvenance']['providerEvidence']
        raw=json.loads(ev['requestText'])
        raw['prompt']='forged prompt'
        ev['requestText']=json.dumps(raw)
        ev['requestSha256']=hashlib.sha256(ev['requestText'].encode()).hexdigest()
        self.assertIn('RAW_REQUEST_PLAN_MISMATCH',str(replay_evidence_capsule_v3(reseal(c))['errors']))

    def test_changed_provider_hash_rejected_even_after_rehash(self):
        c=good_capsule()
        ev=c['execution']['observations'][0]['executionProvenance']['providerEvidence']
        ev['responseSha256']='0'*64
        self.assertIn('RAW_RESPONSE_HASH_MISMATCH',str(replay_evidence_capsule_v3(reseal(c))['errors']))

    def test_missing_done_flag_rejected_even_after_rehash(self):
        c=good_capsule()
        ev=c['execution']['observations'][0]['executionProvenance']['providerEvidence']
        raw=json.loads(ev['responseText'])
        del raw['done']
        ev['responseText']=json.dumps(raw)
        ev['responseSha256']=hashlib.sha256(ev['responseText'].encode()).hexdigest()
        self.assertIn('RAW_RESPONSE_OUTPUT_MISMATCH',str(replay_evidence_capsule_v3(reseal(c))['errors']))

if __name__=='__main__':unittest.main()
