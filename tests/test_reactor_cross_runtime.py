"""Cross-runtime strict-attribution and provenance tests, using Node when installed."""
import json, shutil,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from reactor_engine import classify_paired_trial,build_capsule,verify_and_replay_capsule
from reactor_fixtures import observation,experiment

@unittest.skipUnless(shutil.which('node'),'Node unavailable')
class CrossRuntime(unittest.TestCase):
 def node(self,script):
  return json.loads(subprocess.check_output(['node','-e',script],cwd=ROOT,text=True))
 def test_comparison_matches_python(self):
  cases=[]
  for changes in ({},{'inputHash':'3'*64},{'temperature':1},{'seed':3},{'tools':['browser']},{'model':'other'}):
   cases.append((observation('CONTROL',True),observation('VARIANT',False,**changes)))
  payload=json.dumps(cases)
  code="require('./workbench/reactor/comparison-engine.js');const vals="+payload+";console.log(JSON.stringify(vals.map(([a,b])=>globalThis.ReactorComparisonEngine.classifyPairedTrial(a,b))));"
  self.assertEqual(self.node(code),[classify_paired_trial(a,b) for a,b in cases])
 def test_capsule_python_to_javascript(self):
  exp=experiment();obs=[observation('CONTROL',False),observation('VARIANT',True)]
  c=build_capsule({'entryId':'W-04','bodyStatus':'UNVERIFIED_SOURCE_CANDIDATE'},exp,'Control','Variant',exp['dataset'],obs,{},[],[])
  self.assertTrue(verify_and_replay_capsule(c)['valid'])
  js="""const fs=require('fs');const crypto=require('crypto');globalThis.crypto=crypto.webcrypto;
require('./workbench/reactor/experiment-core.js');require('./workbench/reactor/comparison-engine.js');require('./workbench/reactor/evidence-capsule.js');require('./workbench/reactor/replay-engine.js');require('./workbench/reactor/observation-validator.js');
(async()=>{const c=JSON.parse(fs.readFileSync(0,'utf8'));const r=await globalThis.ReactorReplayEngine.replayCapsule(c);console.log(JSON.stringify(r));})().catch(e=>{console.error(e);process.exit(1)});"""
  r=json.loads(subprocess.check_output(['node','-e',js],cwd=ROOT,input=json.dumps(c),text=True))
  self.assertTrue(r['valid'],r['errors'])
  self.assertEqual(r['replay'],verify_and_replay_capsule(c)['replay'])
 def test_capsule_javascript_to_python(self):
  exp=experiment();state={'sourceRef':{'entryId':'W-04','bodyStatus':'EXPERIMENTAL_TRANSCRIPTION'},'experiment':exp,
   'controlPrompt':'Control','variantPrompt':'Variant','dataset':exp['dataset'],'observations':[observation('CONTROL',False),observation('VARIANT',True)],'scores':{},'claims':[],'challenges':[],'isSyntheticDemo':False}
  js="""const fs=require('fs');const crypto=require('crypto');globalThis.crypto=crypto.webcrypto;
require('./workbench/reactor/experiment-core.js');require('./workbench/reactor/evidence-capsule.js');
(async()=>{const s=JSON.parse(fs.readFileSync(0,'utf8'));const c=await globalThis.ReactorEvidenceCapsule.buildCapsule(s);console.log(JSON.stringify(c));})().catch(e=>{console.error(e);process.exit(1)});"""
  cap=json.loads(subprocess.check_output(['node','-e',js],cwd=ROOT,input=json.dumps(state),text=True))
  r=verify_and_replay_capsule(cap)
  self.assertTrue(r['valid'],r['errors'])
  self.assertEqual(r['replay']['classifications']['VARIANT_IMPROVEMENT'],1)
 def test_no_pseudohash_when_web_crypto_missing(self):
  script="""delete globalThis.crypto;require('./workbench/reactor/experiment-core.js');(async()=>{try {await globalThis.ReactorExperimentCore.sha256Hex('test');console.log(JSON.stringify('UNSAFE'))}catch(e){console.log(JSON.stringify(e.message));}})();"""
  self.assertIn('SHA256_UNAVAILABLE',self.node(script))
 def test_real_index_adapter_contract(self):
  data=json.loads((ROOT/'workbench/data/current_entry_identity_index.json').read_text()) if (ROOT/'workbench/data/current_entry_identity_index.json').exists() else None
  if data is None:self.skipTest('Canonical GitHub identity index not bundled with ZIP; integration must run in checkout')
  js="const data="+json.dumps(data)+";globalThis.fetch=async()=>({ok:true,json:async()=>data});require('./workbench/reactor/source-adapter.js');globalThis.ReactorSourceAdapter.loadIndex().then(x=>console.log(JSON.stringify({n:x.entries.length,verified:x.verifiedBodies}))).catch(e=>{console.error(e);process.exit(1)});"
  self.assertEqual(self.node(js),{'n':91,'verified':0})

 def test_historical_identity_rejected_by_current_adapter(self):
  data=json.loads((ROOT/'workbench/data/entry_identity_index.json').read_text())
  js="const data="+json.dumps(data)+";globalThis.fetch=async()=>({ok:true,json:async()=>data});require('./workbench/reactor/source-adapter.js');globalThis.ReactorSourceAdapter.loadIndex().then(()=>console.log(JSON.stringify('UNSAFE_ACCEPT'))).catch(e=>console.log(JSON.stringify(e.message)));"
  self.assertEqual(self.node(js),'INVALID_SOURCE_INDEX')
