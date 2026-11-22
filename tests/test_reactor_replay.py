import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reactor_engine import build_capsule,verify_and_replay_capsule
from reactor_fixtures import observation,experiment
class TestReactorReplay(unittest.TestCase):
 def test_replay_and_claim_promotion(self):
  ex=experiment([{'inputId':'I-1'},{'inputId':'I-2'}])
  cap=build_capsule({'entryId':'R-03'},ex,'Control','Variant',ex['dataset'],[
   observation('CONTROL',False),observation('VARIANT',True),observation('CONTROL',False,input_id='I-2')],{},
   [{'claimId':'CL-UNSUP','status':'REPRODUCED','evidenceRefs':[]}],[])
  res=verify_and_replay_capsule(cap)
  self.assertFalse(res['valid']);self.assertIn('UNSUPPORTED_CLAIM_PROMOTION:CL-UNSUP',res['errors'])
  self.assertIsNone(res['replay'])
  cap['claims']['findings'][0]['status']='EVALUATED'
  from reactor_engine import canonical_json,sha256_text
  cap['integrity']['checksums']['claims/findings.json']=sha256_text(canonical_json(cap['claims']['findings']))
  res=verify_and_replay_capsule(cap)
  self.assertTrue(res['valid'],res['errors']);self.assertEqual(res['replay']['classifications']['VARIANT_IMPROVEMENT'],1)
  self.assertEqual(res['replay']['classifications']['UNATTRIBUTABLE'],1)
