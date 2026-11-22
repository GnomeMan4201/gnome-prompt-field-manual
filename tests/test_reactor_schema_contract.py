import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from reactor_engine import validate_experiment,validate_observations
from reactor_fixtures import experiment,observation
try:
 import jsonschema
except ImportError:
 jsonschema=None

@unittest.skipUnless(jsonschema,'jsonschema unavailable')
class SchemaContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.exp_schema=json.loads((ROOT/'schemas/reactor-experiment.schema.json').read_text())
  cls.obs_schema=json.loads((ROOT/'schemas/reactor-observation.schema.json').read_text())
 def test_valid_experiment(self):
  e=experiment();jsonschema.validate(e,self.exp_schema)
  self.assertEqual(validate_experiment(e),[])
 def test_missing_hash_rejected_by_both(self):
  e=experiment();del e['variantPromptHash']
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(e,self.exp_schema)
  self.assertTrue(validate_experiment(e))
 def test_invalid_observation_rejected_by_both(self):
  o=observation('CONTROL');o['inputHash']='not-sha256'
  with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(o,self.obs_schema)
  self.assertTrue(validate_observations([o],experiment()))
 def test_valid_observation(self):
  o=observation('CONTROL');jsonschema.validate(o,self.obs_schema)
  self.assertEqual(validate_observations([o],experiment()),[])
