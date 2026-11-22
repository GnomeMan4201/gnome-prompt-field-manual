import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reactor_engine import build_capsule,verify_and_replay_capsule
from reactor_fixtures import observation,experiment

class TestReactorCapsules(unittest.TestCase):
 def sample(self):
  return build_capsule({'entryId':'S-01','bodyStatus':'UNVERIFIED_SOURCE_CANDIDATE'},experiment(),
   'Control','Variant',experiment()['dataset'],[observation('CONTROL',False),observation('VARIANT',True)],
   {},[{'claimId':'CL-1','status':'EVALUATED','evidenceRefs':['runs/observations.json']}],[])
 def test_valid_tampered(self):
  c=self.sample();self.assertTrue(verify_and_replay_capsule(c)['valid'])
  c['prompts']['variant']='tampered';self.assertIn('CHECKSUM_MISMATCH:prompts/variant.txt',verify_and_replay_capsule(c)['errors'])
 def test_missing_checksum_schema(self):
  c=self.sample();del c['integrity']['checksums']['runs/observations.json']
  self.assertIn('MISSING_CHECKSUM:runs/observations.json',verify_and_replay_capsule(c)['errors'])
  c['schemaVersion']='invalid'
  self.assertIn('UNSUPPORTED_SCHEMA_VERSION',verify_and_replay_capsule(c)['errors'])
