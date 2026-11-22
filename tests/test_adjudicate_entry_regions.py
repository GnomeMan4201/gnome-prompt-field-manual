"""Phase VI adjudication queue invariants and fail-closed human review."""
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from adjudicate_entry_regions import build_queue, validate
class AdjudicationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads((ROOT/"workbench/data/region_review_summary.json").read_text())
  cls.queue=build_queue(cls.manifest)
 def test_91_entries_and_all_unreviewed(self):
  q=self.queue
  self.assertEqual(len(q["entries"]),91)
  self.assertEqual(sum(len(x["exclusions"]) for x in q["entries"]),447)
  r=validate(self.manifest,q)
  self.assertTrue(r["valid"]);self.assertFalse(r["reviewComplete"])
  self.assertEqual(r["pendingDecisions"],629);self.assertEqual(r["approvedBodies"],0)
 def test_source_hash_mutation_fails_closed(self):
  q=copy.deepcopy(self.queue);q["sourceHtmlSha256"]="0"*64
  self.assertFalse(validate(self.manifest,q)["valid"])
 def test_manifest_hash_mutation_fails_closed(self):
  q=copy.deepcopy(self.queue);q["manifestSha256"]="0"*64
  self.assertFalse(validate(self.manifest,q)["valid"])
 def test_added_removed_entry_fails_closed(self):
  q=copy.deepcopy(self.queue);q["entries"].pop()
  self.assertFalse(validate(self.manifest,q)["valid"])
 def test_reordered_entries_fails_closed(self):
  q=copy.deepcopy(self.queue);q["entries"][0],q["entries"][1]=q["entries"][1],q["entries"][0]
  self.assertFalse(validate(self.manifest,q)["valid"])
 def test_changed_span_fails_closed(self):
  q=copy.deepcopy(self.queue)
  item=next(x for x in q["entries"] if x["exclusions"])
  item["exclusions"][0]["span"][1]+=1
  self.assertFalse(validate(self.manifest,q)["valid"])
 def test_claim_without_reviewer_and_evidence_fails(self):
  q=copy.deepcopy(self.queue)
  item=next(x for x in q["entries"] if x["exclusions"])
  item["exclusions"][0]["decision"]="ACCEPT_EXCLUSION"
  r=validate(self.manifest,q)
  self.assertFalse(r["valid"]);self.assertFalse(r["reviewComplete"])
 def test_completed_record_does_not_verify_body(self):
  q=copy.deepcopy(self.queue)
  x=next(x for x in q["entries"] if x["exclusions"])
  e=x["exclusions"][0];e.update(decision="ACCEPT_EXCLUSION",reviewer="Reviewer",rationale="Checked printed page",evidence=["printed-page:10"],reviewedAt="2026-11-22T21:00:00Z")
  r=validate(self.manifest,q)
  self.assertTrue(r["valid"]);self.assertEqual(r["completedDecisions"],1)
  self.assertEqual(r["approvedBodies"],0)
 def test_pending_metadata_must_be_empty(self):
  q=copy.deepcopy(self.queue);q["entries"][0]["endBoundary"]["reviewer"]="somebody"
  self.assertFalse(validate(self.manifest,q)["valid"])
if __name__=="__main__":unittest.main()
