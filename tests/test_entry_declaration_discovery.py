"""Regression gates for actual-heading and cross-reference-safe discovery."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from discover_entry_boundaries import discover,find_declarations,parse_cards
def card(t):
 return parse_cards('<article class="manual-page-card" id="manual-page-001"><pre>'+t+'</pre></article>')
class TestDeclarationDiscovery(unittest.TestCase):
 def test_real_source_91_unique(self):
  d=discover(ROOT/'index.html',ROOT/'workbench/data/entry_identity_index.json')
  self.assertEqual(d['status'],'DECLARATIONS_COMPLETE_CANDIDATE_ONLY')
  self.assertEqual(d['counts']['declarationCandidates'],91)
  self.assertEqual(d['counts']['verifiedEntryBodies'],0)
  names={x['id']:x['titleCandidate'] for x in d['candidates']}
  self.assertEqual(names['W-04'],'Over-Smoothing Detector')
  self.assertEqual(names['R-07'],'Competing Hypotheses Table')
  self.assertEqual(names['R-10'],'Source-of-Truth Conflict Resolver')
 def test_natural_heading_no_separator(self):
  c,_=find_declarations(card('\n  S-01 Real Title\n\n Criteria: 1, 2\nWHAT IT DOES\ntext'),{'S-01'})
  self.assertEqual(len(c),1)
 def test_false_heading_without_adjacent_criteria(self):
  c,r=find_declarations(card('S-01 Real Title\nnot a declaration\nCriteria: 1\n'),{'S-01'})
  self.assertEqual(c,[]);self.assertEqual(len(r),1)
 def test_phantom_unknown_id_excluded(self):
  c,_=find_declarations(card('S-99 Fake\nCriteria: 1\n'),{'S-01'})
  self.assertEqual(c,[])
 def test_appendix_not_a_new_entry(self):
  c,_=find_declarations([{'page':312,'htmlId':'manual-page-312','text':'S-01 Entry\nCriteria: 1'}],{'S-01'})
  self.assertEqual(c,[])
 def test_duplicate_detected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);s=p/'index.html';s.write_text('<article class="manual-page-card"><pre>S-01 One\nCriteria: 1\nS-01 Two\nCriteria: 2</pre></article>');idx=p/'id.json';idx.write_text(json.dumps({'sourceIndexSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'entries':[{'id':'S-01'}]}))
   d=discover(s,idx,expected_pages=1,expected_entries=1)
   self.assertEqual(d['status'],'INCOMPLETE_FAIL_CLOSED');self.assertEqual(d['duplicateIds'],['S-01'])
 def test_source_hash_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);s=p/'index.html';s.write_text('<article class="manual-page-card"><pre>S-01 One\nCriteria: 1</pre></article>');idx=p/'id.json';idx.write_text(json.dumps({'sourceIndexSha256':'wrong','entries':[{'id':'S-01'}]}))
   with self.assertRaisesRegex(ValueError,'SOURCE_SHA_MISMATCH'):discover(s,idx,expected_pages=1,expected_entries=1)
if __name__=='__main__':unittest.main()
