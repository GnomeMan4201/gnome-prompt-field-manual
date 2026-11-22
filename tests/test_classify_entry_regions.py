"""Regression tests for Phase V lossless source-region proposals."""
import sys, unittest, tempfile, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from classify_entry_regions import classify,source_fragments,report
class RegionClassTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.r=report(ROOT/"index.html",ROOT/"workbench/data/entry_identity_index.json",ROOT/"workbench/data/entry_declaration_candidates.json")
 def test_real_counts_and_not_verified(self):
  self.assertEqual(self.r["counts"]["entries"],91)
  self.assertEqual(self.r["counts"]["VERIFIED"],0)
  self.assertEqual(self.r["counts"]["PARTIAL"],91)
  self.assertTrue(all(e["regionRoundTrip"] and e["reviewRequired"] for e in self.r["entries"]))
 def test_all_exact_spans_nonoverlapping(self):
  for entry in self.r["entries"]:
   reg=entry["regions"]
   self.assertTrue(reg)
   self.assertEqual(len([x for x in reg if x["regionType"]=="ENTRY_DECLARATION_CANDIDATE"]),1)
   for x,y in zip(reg,reg[1:]):
    self.assertLessEqual((x["page"],x["endOffsetCodepoints"]),(y["page"],y["startOffsetCodepoints"]))
 def test_running_header_only_at_page_top(self):
  source="\nGNOME Prompt Field Manual\nOther content\n"
  a=source.index("GNOME")
  self.assertEqual(classify(10,a,a,a+len("GNOME Prompt Field Manual\n"),source[a:a+len("GNOME Prompt Field Manual\n")],source,"T-01 Title")[0],"PAGE_HEADER")
  body="Some body text\nGNOME Prompt Field Manual\n"
  a=body.index("GNOME")
  self.assertNotEqual(classify(10,a,a,len(body),body[a:],body,"T-01 Title")[0],"PAGE_HEADER")
 def test_numeric_footer_only_matching_page_end(self):
  full="text\n 25\n";i=full.index(" 25")
  self.assertEqual(classify(25,i,i,len(full),full[i:],full,"T-01 Title")[0],"PAGE_FOOTER")
  self.assertNotEqual(classify(24,i,i,len(full),full[i:],full,"T-01 Title")[0],"PAGE_FOOTER")
 def test_code_or_body_mentions_not_declaration(self):
  text="Example: T-01 Idea Stress-Test"
  self.assertEqual(classify(1,0,0,len(text),text,text,"T-01 Idea Stress-Test")[0],"ENTRY_TEXT_CANDIDATE")
 def test_cross_page_source_is_lossless(self):
  x=list(source_fragments({1:"abc",2:"xyz"},(1,1),(2,2)))
  self.assertEqual("".join(y[3] for y in x),"bcxy")
 def test_modified_html_fails(self):
  with tempfile.TemporaryDirectory() as td:
   altered=Path(td)/"index.html";altered.write_bytes((ROOT/"index.html").read_bytes()+b" ")
   with self.assertRaisesRegex(ValueError,"Source hash mismatch"):
    report(altered,ROOT/"workbench/data/entry_identity_index.json",ROOT/"workbench/data/entry_declaration_candidates.json")
if __name__=="__main__":unittest.main()
