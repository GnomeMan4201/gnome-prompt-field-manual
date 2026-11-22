import sys,copy,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reactor_engine import classify_paired_trial,evaluate_comparability,build_capsule,verify_and_replay_capsule,validate_observations,validate_experiment,canonical_json,sha256_text
from reactor_fixtures import observation,experiment
class TestHardening(unittest.TestCase):
 def test_mismatched_inputs_are_unattributable(self):
  self.assertEqual(classify_paired_trial(observation('CONTROL',True),observation('VARIANT',False,inputHash='c'*64)),'UNATTRIBUTABLE')
 def test_mismatched_temperature_seed_tools(self):
  for changes in ({'temperature':1},{'seed':17},{'tools':['search']}):
   self.assertEqual(classify_paired_trial(observation('CONTROL'),observation('VARIANT',False,**changes)),'UNATTRIBUTABLE')
 def test_missing_metadata_unattributable(self):
  for key in ('seed','tools','inputHash','evaluator','rubricHash'):
   o=observation('VARIANT',False);del o[key]
   self.assertEqual(classify_paired_trial(observation('CONTROL'),o),'UNATTRIBUTABLE',key)
 def test_repeated_trials_not_overwritten(self):
  ex=experiment();obs=[observation('CONTROL',False),observation('VARIANT',True),observation('CONTROL',True,trial_id='trial-2'),observation('VARIANT',False,trial_id='trial-2')]
  c=build_capsule({},ex,'Control','Variant',ex['dataset'],obs,{},[],[])
  result=verify_and_replay_capsule(c)
  self.assertTrue(result['valid'],result['errors']);self.assertEqual(result['replay']['totalInputs'],2)
  self.assertEqual(result['replay']['classifications']['VARIANT_IMPROVEMENT'],1)
  self.assertEqual(result['replay']['classifications']['VARIANT_INDUCED_FAILURE'],1)
 def test_duplicate_slot_rejected_even_with_different_run_id(self):
  x=observation('CONTROL');y=observation('CONTROL',runId='another')
  self.assertTrue(any('DUPLICATE_OBSERVATION' in e for e in validate_observations([x,y],experiment())))
 def test_bad_schema_hash_rejected(self):
  ex=experiment();del ex['controlPromptHash']
  self.assertIn('INVALID_CONTROLPROMPTHASH',validate_experiment(ex))
 def test_prompt_mismatch_observation_rejected(self):
  self.assertTrue(any('PROMPT_HASH_MISMATCH' in e for e in validate_observations([observation('VARIANT',promptHash='e'*64)],experiment())))
 def test_missing_seed_both_is_disclosed(self):
  a,b=observation('CONTROL'),observation('VARIANT');del a['seed'];del b['seed']
  self.assertIn('seed',evaluate_comparability(a,b)['missingMetadata'])
 def test_capsule_cannot_replay_after_checksum_failure(self):
  ex=experiment();c=build_capsule({},ex,'Control','Variant',ex['dataset'],[observation('CONTROL')],{},[],[])
  c['runs']['observations'][0]['outputText']='tampered'
  r=verify_and_replay_capsule(c)
  self.assertFalse(r['valid']);self.assertIsNone(r['replay'])
