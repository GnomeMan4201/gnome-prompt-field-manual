"""Conservative body-span candidate regression tests."""
import json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from reconstruct_body_candidates import produce,reconstruct,sha
class BodyCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.source=ROOT/'index.html'
  cls.ids=ROOT/'workbench/data/entry_identity_index.json'
  cls.decls=ROOT/'workbench/data/entry_declaration_candidates.json'
  cls.res=produce(cls.source,cls.ids,cls.decls)
 def test_91_contiguous_candidate_spans(self):
  rows=self.res['entryCandidates'];self.assertEqual(len(rows),91)
  self.assertEqual(self.res['counts'],{'total':91,'VERIFIED':0,'PARTIAL':91,'UNRESOLVED':0,'CONFLICT':0})
  self.assertTrue(all(r['spanRoundTrip'] and r['rawSpan'].lstrip().startswith(r['entryId']+' ') for r in rows))
 def test_active_and_renumbered(self):
  titles={r['entryId']:r['titleCandidate'] for r in self.res['entryCandidates']}
  self.assertEqual(titles['W-04'],'Over-Smoothing Detector')
  self.assertEqual(titles['R-07'],'Competing Hypotheses Table')
  self.assertEqual(titles['R-10'],'Source-of-Truth Conflict Resolver')
 def test_next_heading_not_absorbed(self):
  rows=self.res['entryCandidates']
  for cur,nxt in zip(rows,rows[1:]):
   self.assertLessEqual((cur['endPage'],cur['endOffsetCodepoints']),(nxt['startPage'],nxt['startOffsetCodepoints']))
   self.assertFalse(cur['rawSpan'].endswith(nxt['entryId']+' '+nxt['titleCandidate']))
 def test_last_ends_before_part_ix(self):
  last=self.res['entryCandidates'][-1]
  self.assertEqual(last['entryId'],'AP-20')
  self.assertEqual(last['endPage'],307)
  self.assertNotIn('Quick-reference index',last['rawSpan'])
 def test_source_hash_mismatch_fails(self):
  with tempfile.TemporaryDirectory() as t:
   other=Path(t)/'index.html';other.write_bytes(self.source.read_bytes()+b' ')
   with self.assertRaisesRegex(ValueError,'Source hash mismatch'):
    produce(other,self.ids,self.decls)
 def test_bad_declaration_offset_fails(self):
  doc=json.loads(self.decls.read_text());doc['candidates'][0]['startOffsetCodepoints']+=1
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'d.json';f.write_text(json.dumps(doc))
   with self.assertRaisesRegex(ValueError,'Offset does not point'):
    produce(self.source,self.ids,f)
 def test_roundtrip_handles_cross_page(self):
  pages={1:'abc',2:'xyz',3:'123'}
  self.assertEqual(reconstruct(pages,(1,1),(3,2)),'bcxyz12')
  self.assertEqual(sha(b'abc'),__import__('hashlib').sha256(b'abc').hexdigest())
if __name__=='__main__':unittest.main()
