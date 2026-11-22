import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import jsonschema
from jsonschema import Draft202012Validator,RefResolver
from reactor_evidence_v2 import build_capsule
from test_reactor_evidence_v2 import plan,obs

class FormalV2Contracts(unittest.TestCase):
 def setUp(self):
  self.ps=json.loads((ROOT/'schemas/reactor-evaluation-plan-v2.schema.json').read_text())
  self.cs=json.loads((ROOT/'schemas/reactor-evidence-v2.schema.json').read_text())
  store={self.ps['$id']:self.ps,'reactor-evaluation-plan-v2.schema.json':self.ps}
  self.resolver=RefResolver.from_schema(self.cs,store=store)
 def test_plan_valid(self):Draft202012Validator(self.ps).validate(plan())
 def test_capsule_valid(self):Draft202012Validator(self.cs,resolver=self.resolver).validate(build_capsule(plan(),obs()))
 def test_missing_reference_fails_schema(self):
  p=plan();del p['sourceRef']['sourceSha256']
  with self.assertRaises(jsonschema.ValidationError):Draft202012Validator(self.ps).validate(p)
 def test_forged_capsule_extra_field_fails_schema(self):
  c=build_capsule(plan(),obs());c['claimedIndependentReplication']=True
  with self.assertRaises(jsonschema.ValidationError):Draft202012Validator(self.cs,resolver=self.resolver).validate(c)
if __name__=='__main__':unittest.main()
