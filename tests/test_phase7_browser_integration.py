"""Phase VII integration tests grounded in merged Phase VI queue schema."""
import json,sys,tempfile,unittest
from pathlib import Path
from frozen_source import BASELINE_SHA, materialize_batch3_source
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from adjudicate_entry_regions import build_queue,validate
from discover_entry_boundaries import parse_cards
class TestPhaseVIIIntegration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads((ROOT/"workbench/data/region_review_summary.json").read_text())
  cls.expected=build_queue(cls.manifest)
  cls.queue=json.loads((ROOT/"workbench/data/adjudication_queue.json").read_text())
 def test_queue_is_byte_semantics_identical_to_authoritative_generator(self):
  self.assertEqual(self.queue,self.expected)
 def test_nested_schema_and_629_decisions(self):
  self.assertEqual(self.queue["schemaVersion"],"gnome.manual.adjudication.v1")
  self.assertEqual(len(self.queue["entries"]),91)
  self.assertEqual(sum(len(e["exclusions"]) for e in self.queue["entries"]),447)
  self.assertEqual(447+91+91,629)
 def test_python_rejects_unreviewed_queue(self):
  report=validate(self.manifest,self.queue)
  self.assertTrue(report["valid"])
  self.assertFalse(report["reviewComplete"])
  self.assertEqual(report["pendingDecisions"],629)
  self.assertEqual(report["approvedBodies"],0)
 def test_page_source_offsets_match_original(self):
  self.assertEqual(self.queue["sourceHtmlSha256"], BASELINE_SHA)
  with tempfile.TemporaryDirectory() as directory:
   source=materialize_batch3_source(Path(directory))
   pages={i+1:c["text"] for i,c in enumerate(parse_cards(source.read_text()))}
  self.assertEqual(len(pages),315)
  for e in self.queue["entries"]:
   for x in e["exclusions"]:
    p,a,b,_=x["span"];self.assertLess(a,b);self.assertLessEqual(b,len(pages[p]))
    frag=pages[p][a:b]
    self.assertTrue(frag.strip())
 def test_web_sources_use_canonical_queue_not_synthetic(self):
  app=(ROOT/"workbench/adjudication/app.js").read_text()
  html=(ROOT/"workbench/adjudication/index.html").read_text()
  self.assertIn("../data/adjudication_queue.json",app)
  self.assertNotIn("sample_unreviewed_queue.json",html)
  self.assertNotIn("sourceHtmlLoaded = true",app)
  self.assertIn("crypto.subtle.digest",app)
  self.assertIn("SOURCE_HASH_MISMATCH",app)
 def test_source_map_pages_have_separate_coordinates(self):
  src=(ROOT/"workbench/adjudication/source-map.js").read_text()
  self.assertIn("for(let p=start.page;p<=end.page;p++)",src)
  self.assertIn("size=Array.from(raw).length",src)
 def test_queue_export_has_no_flat_decisions_root(self):
  self.assertNotIn("decisions",self.queue)
  self.assertIn("entries",self.queue)
if __name__=="__main__":unittest.main()
