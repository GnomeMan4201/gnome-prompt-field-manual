"""Batch 5 SUBSUMED disposition: source-bound, no new body, no silent S-10 reassignment."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from batch6_baseline import baseline_bytes
from batch8_baseline import batch8_disposition_bytes
from batch10_baseline import batch10_base_bytes
from tools.reconcile_entry_lineage import reconcile, validate_expectations

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.html"
ARCHIVE = ROOT / "tests/fixtures/batch5-frozen-planned-s10.html"
CROSSWALK = ROOT / "workbench/data/batch5_identity_crosswalk.json"
INDEX = ROOT / "workbench/data/current_entry_identity_index.json"
DOC = ROOT / "docs/BATCH5_DISPOSITION_2026-11-23.md"
SOURCE_SHA = "d5c0f82c33ab228166225972d7de0945b819c7d9a424451916fb5c2efca97e7d"
PREVIOUS_SOURCE_SHA = "dca538299e7a0a6ee74d627baa231089c051a1627a29a0364c8ff136e1b4e448"
ARCHIVE_SHA = "7861e414160693367726f8277d430274f259a7fe779ee5672a9b39003b2440a4"
ALL_CARDS_SHA = "e4019358cb80de25706f983ab1eb2fb66e71dfcded70b94a8bddfe80c5eb14eb"
CARD = re.compile(r'<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>', re.S)


class Batch5DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text()
        cls.cards = {int(m.group(1)): m.group(0) for m in CARD.finditer(cls.source)}
        cls.identity = json.loads(INDEX.read_text())
        cls.crosswalk = json.loads(CROSSWALK.read_text())

    def test_all_315_canonical_cards_were_byte_preserved_in_batch5(self):
        historical = baseline_bytes("index.html")
        self.assertEqual(hashlib.sha256(historical).hexdigest(), SOURCE_SHA)
        baseline_cards = {int(m[1]): m[0] for m in CARD.finditer(historical.decode())}
        self.assertEqual(sorted(baseline_cards), list(range(1, 316)))
        fingerprint = hashlib.sha256("\0".join(baseline_cards[n] for n in range(1, 316)).encode()).hexdigest()
        self.assertEqual(fingerprint, ALL_CARDS_SHA)
        self.assertEqual(sorted(self.cards), list(range(1, 316)))
        self.assertIn("S-07 Migration Risk Classifier", self.cards[129])
        self.assertIn("MANDATORY FOUR-CATEGORY RISK SUMMARY", self.cards[130])
        self.assertIn("ROLLBACK TRIGGER CONDITIONS", self.cards[133])
        self.assertIn("S-10 Architecture Decision Record Generator", self.cards[140])

    def test_planned_s10_is_archived_not_relabelled_as_adr(self):
        archived = ARCHIVE.read_text()
        self.assertEqual(hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(), ARCHIVE_SHA)
        self.assertIn('id="b-s10"', archived)
        self.assertIn("S-10", archived)
        self.assertIn("Migration Risk Classifier", archived)
        self.assertIn("ROLLBACK TRIGGER CONDITIONS", archived)
        self.assertNotIn('id="b-s10"', self.source)
        self.assertNotIn('<span class="er-id">S-10</span>', self.source)
        self.assertNotIn('<td class="batch-entries">S-10</td>', self.source)
        s10 = next(e for e in self.identity["entries"] if e["id"] == "S-10")
        self.assertEqual(s10["titleCandidate"], "Architecture Decision Record Generator")
        self.assertEqual(s10["status"], "NON_PENDING")
        self.assertFalse(s10["draftingBrief"])
        historical = json.loads(batch8_disposition_bytes("workbench/data/current_entry_identity_index.json"))
        historical_s10 = next(row for row in historical["entries"] if row["id"] == "S-10")
        self.assertEqual(historical_s10["occurrencePages"], [140])
        prior = json.loads(batch10_base_bytes("workbench/data/current_entry_identity_index.json"))
        self.assertEqual(next(row for row in prior["entries"] if row["id"] == "S-10")["occurrencePages"], [140, 232])
        self.assertEqual(s10["occurrencePages"], [140, 232, 251, 252, 260])
        self.assertIsNone(s10["canonicalBody"])

    def test_counts_and_next_active_brief(self):
        r = reconcile(SOURCE)
        self.assertEqual(validate_expectations(
            r, expected_pending=1, expected_drafted=90,
            expected_total=91, expected_pages=315
        ), [])
        self.assertEqual(r.summary.drafting_briefs, 1)
        self.assertEqual(r.summary.source_counts.batches, 1)
        self.assertEqual(r.summary.source_counts.caution, 5)
        self.assertEqual(self.identity["counts"], {"pending": 1, "drafted": 90, "total": 91, "pages": 315})
        self.assertEqual(self.identity["sourceIndexSha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(self.identity["bodyCoverage"], 0)
        self.assertNotIn("document.getElementById('b-sec02').classList.add('open');", self.source)
        self.assertIn("document.getElementById('b-sec05').classList.add('open');", self.source)

    def test_crosswalk_is_approved_as_subsumed_not_a_new_body(self):
        x = self.crosswalk
        self.assertEqual(x["sourceIndexSha256"], SOURCE_SHA)
        self.assertEqual(x["disposition"], "SUBSUMED_BY_CANONICAL_S07_NOT_NEW_BODY")
        self.assertEqual(x["planned"]["entryId"], "S-10")
        self.assertEqual(x["planned"]["status"], "CLOSED_AS_SUBSUMED")
        self.assertEqual(x["canonicalSubject"]["entryId"], "S-07")
        self.assertEqual(x["canonicalCollision"]["entryId"], "S-10")
        self.assertEqual(x["canonicalCollision"]["title"], "Architecture Decision Record Generator")
        self.assertTrue(x["canonicalIdReuseResolved"])
        self.assertFalse(x["promotionAuthorized"])
        self.assertEqual(x["canonicalBodyVerification"], "UNVERIFIED")
        self.assertEqual(x["frozenBriefArchive"]["sha256"], ARCHIVE_SHA)
        self.assertEqual(x["frozenBriefArchive"]["sourceIndexSha256"], PREVIOUS_SOURCE_SHA)
        self.assertEqual(x["countsAfter"], {"pending": 10, "drafted": 81, "total": 91, "pages": 315})

    def test_disposition_record_discloses_boundaries(self):
        record = DOC.read_text()
        for clause in (
            "SUBSUMED",
            "not an additional entry",
            "0/91 verified canonical bodies",
            "All **315 canonical page cards are byte-identical**",
            PREVIOUS_SOURCE_SHA,
            SOURCE_SHA,
            ARCHIVE_SHA,
            "Batch 6",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, record)


if __name__ == "__main__":
    unittest.main()
