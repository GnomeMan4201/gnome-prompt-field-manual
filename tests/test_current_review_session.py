"""Review session validation checks decisions without verifying bodies."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate_current_review_session import blank_session,load_basis,validate_session,compatible_queue
from adjudicate_entry_regions import validate

class CurrentReviewSessionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet,cls.manifest,cls.queue=load_basis(ROOT);cls.blank=blank_session(cls.packet)
 def completed(self,key='T-01:exclusion:0',decision='ACCEPT'):
  session=copy.deepcopy(self.blank);r=next(r for r in session['records'] if r['key']==key)
  r.update(decision=decision,reviewer='synthetic-test-reviewer',rationale='Test-only review record',evidence=['fixture:page-9'],reviewedAt='2026-11-24T15:00:00.000Z');return session
 def test_all_669_keys_and_pending_state(self):
  r=validate_session(self.blank,self.packet);self.assertEqual((r['records'],r['pending'],r['independentlyVerifiedBodies']),(669,669,0))
  self.assertEqual(len({x['key'] for x in self.blank['records']}),669)
  self.assertEqual(sum(x['key'].endswith(':title') for x in self.blank['records']),31)
  self.assertEqual(sum(x['key'].startswith('region:') for x in self.blank['records']),9)
 def test_accept_reject_and_defer(self):
  for d in ('ACCEPT','REJECT'):
   r=validate_session(self.completed(decision=d),self.packet);self.assertEqual(r['completedReviewRecords'],1);self.assertEqual(r['independentlyVerifiedBodies'],0)
  self.assertEqual(validate_session(self.blank,self.packet)['completedReviewRecords'],0)
 def test_source_and_identity_mutations_rejected(self):
  mutations=[lambda x:x.update(sourceHtmlSha256='0'*64),lambda x:x.update(packetSha256='0'*64),lambda x:x.update(reviewQueueManifestSha256='0'*64),lambda x:x.update(independentlyVerifiedBodies=91),lambda x:x['records'].pop(),lambda x:x['records'][0].update(key='T-02:owner'),lambda x:x['records'][0].update(decision='VERIFIED'),lambda x:x['records'][0].update(evidence=['fake'])]
  for i,f in enumerate(mutations):
   with self.subTest(mutation=i):
    s=copy.deepcopy(self.blank);f(s)
    with self.assertRaises(ValueError):validate_session(s,self.packet)
 def test_completed_metadata_required_and_timestamp_valid(self):
  for field,bad in [('reviewer',''),('rationale',' '),('evidence',[]),('evidence',[None]),('reviewedAt','2026-02-30T00:00:00.000Z'),('reviewedAt','yesterday')]:
   with self.subTest(field=field,bad=bad):
    s=self.completed();s['records'][0][field]=bad
    with self.assertRaises(ValueError):validate_session(s,self.packet)
 def test_compatible_queue_and_extra_decisions_separate(self):
  s=self.completed();title=next(x for x in s['records'] if x['key'].endswith(':title'));title.update({k:v for k,v in s['records'][0].items() if k!='key'})
  q=compatible_queue(s,self.packet,self.manifest,self.queue);r=validate(self.manifest,q)
  self.assertTrue(r['valid']);self.assertEqual(r['completedDecisions'],1);self.assertEqual(r['pendingDecisions'],628);self.assertEqual(r['approvedBodies'],0)
  self.assertEqual(validate_session(s,self.packet)['completedReviewRecords'],2)
  self.assertEqual(q['entries'][0]['exclusions'][0]['decision'],'ACCEPT_EXCLUSION')
  self.assertEqual(self.queue['entries'][0]['exclusions'][0]['decision'],'NEEDS_REVIEW')
 def test_cli_read_only_and_exclusive_export(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'session.json';p.write_text(json.dumps(self.completed()));out=Path(td)/'queue.json'
   cmd=[sys.executable,'tools/validate_current_review_session.py',str(p),'--queue-out',str(out)]
   r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['independentlyVerifiedBodies'],0)
   first=out.read_bytes();r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);self.assertEqual(r.returncode,2);self.assertEqual(out.read_bytes(),first)
if __name__=='__main__':unittest.main()
