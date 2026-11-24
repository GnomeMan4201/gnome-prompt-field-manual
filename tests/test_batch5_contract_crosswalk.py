"""Batch 5 contract/crosswalk review. HOLD: no ID promotion or body verification."""
from __future__ import annotations

import hashlib
import html
import json
import re
import tempfile
import unittest
from pathlib import Path

from tools.audit_editorial_lineage import audit, canonical_surface
from tools.reconcile_entry_lineage import reconcile

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CROSSWALK = ROOT / "workbench/data/batch5_identity_crosswalk.json"
CARDS = re.compile(r'<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>', re.S)
RISK_MAPPING = {
    "DATA COMPATIBILITY RISK": ("COMPATIBILITY RISK", "SCHEMA / CONTRACT RISK"),
    "BEHAVIORAL RISK": ("COMPATIBILITY RISK", "USER / DOWNSTREAM IMPACT", "DETECTABILITY"),
    "INTEGRATION RISK": ("SCHEMA / CONTRACT RISK", "DEPENDENCY RISK", "ORDERING / SEQUENCING RISK"),
    "ROLLBACK COMPLEXITY RISK": ("ROLLBACK RISK", "ORDERING / SEQUENCING RISK", "OBSERVABILITY RISK", "DETECTABILITY"),
}


class Batch5ContractCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = INDEX.read_text()
        cls.cards = {int(m.group(1)): m.group(0) for m in CARDS.finditer(cls.source)}
        cls.crosswalk = json.loads(CROSSWALK.read_text())
        cls.index = json.loads((ROOT / "workbench/data/current_entry_identity_index.json").read_text())

    def page_text(self, page: int) -> str:
        raw = re.search(r"<pre>(.*?)</pre>", self.cards[page], re.S).group(1)
        return canonical_surface(html.unescape(raw))

    def test_separate_planned_and_canonical_ids_fail_closed(self):
        x = self.crosswalk
        self.assertEqual(x["schemaVersion"], "gnome.batch5.crosswalk.v1")
        digest = hashlib.sha256(INDEX.read_bytes()).hexdigest()
        self.assertEqual(x["sourceIndexSha256"], digest)
        self.assertEqual(self.index["sourceIndexSha256"], digest)
        self.assertEqual(x["disposition"], "REVISE_HOLD")
        self.assertEqual(x["planned"], {
            "briefId": "b-s10",
            "entryId": "S-10",
            "title": "Migration Risk Classifier",
            "status": "PENDING",
        })
        self.assertEqual(x["canonicalSubject"]["entryId"], "S-07")
        self.assertEqual(x["canonicalSubject"]["title"], "Migration Risk Classifier")
        self.assertEqual(x["canonicalSubject"]["pages"], list(range(129, 136)))
        self.assertEqual(x["canonicalCollision"]["entryId"], "S-10")
        self.assertEqual(x["canonicalCollision"]["title"], "Architecture Decision Record Generator")
        self.assertEqual(x["canonicalCollision"]["firstPage"], 140)
        self.assertIn("s-07 migration risk classifier", self.page_text(129))
        self.assertIn("s-10 architecture decision record generator", self.page_text(140))
        self.assertFalse(x["promotionAuthorized"])
        self.assertFalse(x["canonicalIdReuseResolved"])
        self.assertEqual(x["canonicalBodyVerification"], "UNVERIFIED")

    def test_all_four_categories_and_risk_scale_required_in_standard_prompt(self):
        x = self.crosswalk
        observed = {
            row["name"]: tuple(row["sourceDimensions"])
            for row in x["riskCategories"]
        }
        self.assertEqual(observed, RISK_MAPPING)
        p130 = self.page_text(130)
        p133 = self.page_text(133)
        for category in RISK_MAPPING:
            with self.subTest(category=category):
                self.assertIn(category.casefold(), p130)
                self.assertIn(category.casefold(), p133)
        for dimension in set(sum((list(items) for items in RISK_MAPPING.values()), [])):
            with self.subTest(dimension=dimension):
                self.assertIn(dimension.removesuffix(" RISK").casefold(), p130)
        for field in (
            "mandatory four-category risk summary",
            "critical / high / medium / low",
            "specific evidence",
            "source dimensions",
            "unassessed",
            "do not migrate yet",
        ):
            with self.subTest(field=field):
                self.assertIn(field, p130)
        self.assertIn("mandatory four-category risk summary", p133)
        self.assertIn("rollback trigger conditions", p133)
        self.assertEqual(x["categoryRatingLevels"], ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
        self.assertEqual(x["dimensionRatingLevels"], ["CRITICAL", "HIGH", "MODERATE", "LOW"])
        self.assertEqual(x["labelReconciliation"], {"MEDIUM": "MODERATE", "scope": "SUMMARY_ONLY"})
        self.assertEqual(x["missingEvidenceDecision"], "UNASSESSED_AND_DO_NOT_MIGRATE_YET")

    def test_current_counts_and_provenance_remain_unpromoted(self):
        x = self.crosswalk
        self.assertEqual(x["countsUnaffected"], {"pending": 11, "drafted": 80, "total": 91, "pages": 315})
        r = reconcile(INDEX)
        self.assertEqual(r.summary.pending_inventory_rows, 11)
        self.assertEqual(r.summary.drafting_briefs, 11)
        self.assertIn("S-10", {e.entry_id for e in r.pending_entries})
        self.assertEqual(self.index["bodyCoverage"], 0)
        self.assertEqual(sorted(self.cards), list(range(1, 316)))
        self.assertIn('id="b-s10"', self.source)
        self.assertEqual(
            hashlib.sha256((ROOT / "tests/fixtures/batch3-canonical-1f06445e.html").read_bytes()).hexdigest(),
            "1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19",
        )

    def test_four_category_semantic_rule_fails_if_both_text_surfaces_rewrite_requirement(self):
        source_card = self.cards[130]
        altered = source_card.replace("data compatibility risk", "generic risk", 1).replace(
            "DATA COMPATIBILITY RISK", "GENERIC RISK", 1
        )
        self.assertNotEqual(altered, source_card)
        broken = self.source.replace(source_card, altered, 1)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.html"
            path.write_text(broken)
            result = audit(path, ROOT)
        failures = {check.name for check in result.checks if not check.passed}
        self.assertIn("manual-page-130:semantic-rules", failures)


if __name__ == "__main__":
    unittest.main()
