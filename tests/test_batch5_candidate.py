"""Regression of the source-bound Batch 5 manuscript correction candidate.

This is not a Batch 5 PASS or independent body verification.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import tempfile
import unittest
from pathlib import Path

from batch6_baseline import baseline_bytes
from tools.audit_editorial_lineage import audit, canonical_surface
from tools.reconcile_entry_lineage import reconcile, validate_expectations

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "index.html"
EXPECTED_SOURCE_SHA = "d5c0f82c33ab228166225972d7de0945b819c7d9a424451916fb5c2efca97e7d"
EXPECTED_STANDALONE_SHA = "558fec69b1dc5f2ceb3821d7918a1601d017e93b289c97c4f8e6afcb35895fb3"
UNCHANGED_313_SHA = "31f9f2d953c9bc5c8392f4010cc80eb26524cff54e92ff2fc633f2f67cf918e0"
PAGE140_SHA = "66a08d8d367d91ae61221fa48865e5f217247e2af8aab7003a43be6bd4b32276"
BATCH4_SHA = "145b5fe00fedfa43d2a098f3bca1e59e6a9d7ffef8e4a378bc0852626a2d9a1a"
CARD = re.compile(r'<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>', re.S)
REQUIRED = (
    "rollback trigger conditions",
    "observable failure signal",
    "measurable threshold or condition",
    "evaluation window",
    "evidence source or monitoring mechanism",
    "responsible decision owner",
    "immediate halt or rollback action",
    "escalation procedure",
    "[requires operational confirmation]",
    "does not monitor production",
)


def fingerprint(pages: dict[int, str], numbers: list[int]) -> str:
    return hashlib.sha256("\0".join(pages[n] for n in numbers).encode()).hexdigest()


class Batch5CorrectionCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        matches = [(int(m.group(1)), m.group(0)) for m in CARD.finditer(cls.source)]
        cls.pages = dict(matches)
        if len(matches) != len(cls.pages):
            raise AssertionError("Duplicate page card")

    def test_source_and_preservation_are_hash_bound(self):
        historical = baseline_bytes("index.html")
        self.assertEqual(hashlib.sha256(historical).hexdigest(), EXPECTED_SOURCE_SHA)
        baseline_pages = {int(m[1]): m[0] for m in CARD.finditer(historical.decode())}
        self.assertEqual(sorted(baseline_pages), list(range(1, 316)))
        self.assertEqual(fingerprint(baseline_pages, [n for n in range(1, 316) if n not in (130, 133)]), UNCHANGED_313_SHA)
        self.assertEqual(sorted(self.pages), list(range(1, 316)))
        self.assertEqual(hashlib.sha256(self.pages[140].encode()).hexdigest(), PAGE140_SHA)
        self.assertEqual(fingerprint(self.pages, list(range(107, 122))), BATCH4_SHA)

    def test_required_fields_present_in_metadata_and_visible_text(self):
        page = self.pages[133]
        metadata = html.unescape(re.search(r'data-manual-text="([^"]*)"', page).group(1))
        visible = re.search(r'<pre>(.*?)</pre>', page, re.S).group(1)
        meta, shown = canonical_surface(metadata), canonical_surface(visible)
        self.assertEqual(meta, shown)
        for requirement in REQUIRED:
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, meta)
                self.assertIn(requirement, shown)

    def test_regression_fails_even_if_metadata_and_visible_text_drift_together(self):
        original = self.pages[133]
        altered = original.replace("observable failure signal", "generic symptom", 1).replace(
            "OBSERVABLE FAILURE SIGNAL", "GENERIC SYMPTOM", 1
        )
        self.assertNotEqual(altered, original)
        broken = self.source.replace(original, altered, 1)
        with tempfile.TemporaryDirectory() as directory:
            test_source = Path(directory) / "index.html"
            test_source.write_text(broken)
            result = audit(test_source, ROOT)
        failed = {check.name for check in result.checks if not check.passed}
        self.assertIn("manual-page-133:semantic-rules", failed)

    def test_standalone_reader_is_source_identical_for_all_315_pages(self):
        standalone = ROOT / "GNOME-Field-Manual.html"
        self.assertEqual(hashlib.sha256(baseline_bytes("GNOME-Field-Manual.html")).hexdigest(), EXPECTED_STANDALONE_SHA)
        html_source = standalone.read_text(encoding="utf-8")
        match = re.search(r"(?m)^\s*var BOOK_PAGES = (.+);$", html_source)
        self.assertIsNotNone(match)
        pages = json.loads(match.group(1))
        self.assertEqual(len(pages), 315)
        for i, row in enumerate(pages, 1):
            with self.subTest(page=i):
                card = self.pages[i]
                pre = html.unescape(re.search(r"<pre>(.*?)</pre>", card, re.S).group(1))
                self.assertEqual(row["cardId"], f"manual-page-{i:03d}")
                self.assertEqual(row["pageNumber"], i)
                self.assertEqual(row["text"], pre)
                self.assertEqual(row["textSha256"], hashlib.sha256(pre.encode()).hexdigest())
        static130 = re.search(r'<article class="book-page" id="page-130">.*?</article>', html_source, re.S)
        self.assertIsNotNone(static130)
        self.assertIn("MANDATORY FOUR-CATEGORY RISK SUMMARY", static130.group(0))
        self.assertIn("DATA COMPATIBILITY RISK", static130.group(0))
        self.assertIn("ROLLBACK COMPLEXITY RISK", static130.group(0))
        self.assertIn("MEDIUM", static130.group(0))
        static133 = re.search(r'<article class="book-page" id="page-133">.*?</article>', html_source, re.S)
        self.assertIsNotNone(static133)
        self.assertIn("ROLLBACK TRIGGER CONDITIONS", static133.group(0))
        self.assertIn("REQUIRES OPERATIONAL", static133.group(0))

    def test_identity_crosswalk_is_not_a_promotion(self):
        self.assertIn("S-10 Architecture Decision Record Generator", self.pages[140])
        self.assertIn("S-07 Migration Risk Classifier", self.pages[129])
        reconciled = reconcile(SOURCE)
        self.assertEqual(validate_expectations(
            reconciled, expected_pending=6, expected_drafted=85,
            expected_total=91, expected_pages=315
        ), [])
        self.assertNotIn("S-10", {item.entry_id for item in reconciled.pending_entries})
        self.assertNotIn("S-10", {item.entry_id for item in reconciled.briefs})
        self.assertNotIn('id="b-s10"', self.source)
        self.assertIn('id="b-s10"', (ROOT / "tests/fixtures/batch5-frozen-planned-s10.html").read_text())


if __name__ == "__main__":
    unittest.main()
