import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reactor_engine import classify_paired_trial,evaluate_comparability
from reactor_fixtures import observation

class TestReactorComparisons(unittest.TestCase):
 def test_baseline_failure_not_induced(self):
  self.assertEqual(classify_paired_trial(observation('CONTROL',False),observation('VARIANT',False)),'SHARED_FAILURE')
 def test_variant_induced_and_improvement(self):
  self.assertEqual(classify_paired_trial(observation('CONTROL',True),observation('VARIANT',False)),'VARIANT_INDUCED_FAILURE')
  self.assertEqual(classify_paired_trial(observation('CONTROL',False),observation('VARIANT',True)),'VARIANT_IMPROVEMENT')
 def test_changed_model_fails(self):
  a,b=observation('CONTROL'),observation('VARIANT',model='different')
  self.assertEqual(classify_paired_trial(a,b),'UNATTRIBUTABLE')
  self.assertEqual(evaluate_comparability(a,b)['status'],'NOT_COMPARABLE')
