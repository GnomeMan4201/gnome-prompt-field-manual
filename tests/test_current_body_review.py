"""Current-source verification is deliberately distinct from independent approval."""
import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_current_body_review import build,verify,entry_packet,OUTPUT,SOURCE,IDENTITY,HISTORICAL,sha
from adjudicate_entry_regions import validate
BASE='cce15ddb8981a4b4a160d4d2caf1c5e91aad659b'
class CurrentBodyReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.packet=json.loads((ROOT/OUTPUT).read_text());cls.generated,cls.manifest,cls.queue=build(ROOT)
 def test_exact_reproducible_candidate_inventory(self):
  self.assertEqual(self.generated,self.packet)
  c=self.packet['counts'];self.assertEqual((c['entries'],c['pages'],c['VERIFIED'],c['PARTIAL']),(91,315,0,91))
  self.assertEqual((c['titleMismatches'],c['entriesWithMissingSectionMarkers'],c['entriesWithRepeatedSectionMarkers']),(31,0,1))
  self.assertEqual((c['proposedExclusions'],c['pendingLegacyQueueDecisions'],c['unassignedRegions']),(447,629,9))
  self.assertEqual({x['entryId'] for x in self.packet['entries'] if x['editorialStatus']=='PENDING'},{'SEC-05'})
 def test_shared_page_and_subject_boundaries(self):
  by={x['entryId']:x for x in self.packet['entries']}
  for a,b in [('SEC-05','SEC-06'),('P-05','P-06'),('P-06','P-07'),('P-08','P-09'),('P-09','P-10')]:
   self.assertEqual(by[a]['endExclusive'],by[b]['start']);self.assertEqual(by[a]['nextEntry'],b)
  self.assertEqual(by['S-07']['canonicalHeadingCandidate'],'Migration Risk Classifier')
  self.assertEqual(by['S-10']['canonicalHeadingCandidate'],'Architecture Decision Record Generator')
  self.assertEqual(by['P-07']['canonicalHeadingCandidate'],'RFC Draft Generator')
  self.assertEqual(by['SEC-05']['start'],{'page':179,'offset':0})
  self.assertEqual(by['SEC-05']['endExclusive'],{'page':187,'offset':683})
  self.assertEqual(by['AP-20']['endExclusive'],{'page':307,'offset':0})
 def test_pagewise_sections_and_queue(self):
  self.assertTrue(all(not x['missingSectionLabels'] for x in self.packet['entries']))
  self.assertEqual([x['entryId'] for x in self.packet['entries'] if x['repeatedSectionLabels']],['SEC-06'])
  v=validate(self.manifest,self.queue);self.assertTrue(v['valid']);self.assertFalse(v['reviewComplete']);self.assertEqual(v['approvedBodies'],0);self.assertEqual(v['pendingDecisions'],629)
  self.assertEqual(self.packet['reviewQueueManifestSha256'],self.queue['manifestSha256'])
 def test_packet_mutations_fail(self):
  mutations=[lambda x:x.update(sourceHtmlSha256='0'*64),lambda x:x['entries'][0]['start'].update(offset=0),
   lambda x:x['entries'][0].update(endExclusive=x['entries'][1]['endExclusive']),
   lambda x:x['entries'][0].update(entryId='T-02'),lambda x:x['entries'][0]['sectionMarkers'].pop(),
   lambda x:x['entries'][0].update(bodyStatus='VERIFIED'),lambda x:x['entries'][0]['proposedExclusions'].pop(),
   lambda x:x['historicalBindings'].update({HISTORICAL[0]:'0'*64}),lambda x:x['unassignedRegions'].pop()]
  for i,mutate in enumerate(mutations):
   with self.subTest(mutation=i):
    bad=copy.deepcopy(self.packet);mutate(bad)
    with self.assertRaisesRegex(ValueError,'differs'):verify(ROOT,bad)
 def test_source_digest_mismatch(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/SOURCE).write_bytes((ROOT/SOURCE).read_bytes()+b' ');(p/IDENTITY).parent.mkdir(parents=True);(p/IDENTITY).write_bytes((ROOT/IDENTITY).read_bytes())
   with self.assertRaisesRegex(ValueError,'SOURCE_SHA_MISMATCH'):build(p)
 def test_read_only_entry_packet(self):
  p=entry_packet(ROOT,self.packet,'T-01');self.assertEqual(p['entry']['bodyStatus'],'PARTIAL')
  raw=''.join(x['text'] for x in p['rawPageSlices']);self.assertEqual(sha(raw.encode()),p['entry']['rawSpanSha256'])
  for item in p['rawPageSlices']:self.assertEqual(sha(item['text'].encode()),item['sha256'])
  self.assertTrue(all(e['decision']=='NEEDS_REVIEW' for e in p['exclusionEvidence']))
 def test_immutable_history_and_readers(self):
  paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines()
  # Entire baseline data/evidence + readers; not only the seven named inputs.
  protected=[p for p in paths if p in (SOURCE,'GNOME-Field-Manual.html') or p.startswith(('workbench/data/','workbench/adjudication/','research/','examples/','tests/fixtures/','docs/'))]
  for p in protected:
   with self.subTest(path=p):self.assertEqual((ROOT/p).read_bytes(),subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
 def test_existing_output_refused(self):
  r=subprocess.run([sys.executable,'tools/build_current_body_review.py'],cwd=ROOT,capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0);self.assertIn('Refusing to overwrite',r.stderr)
if __name__=='__main__':unittest.main()
