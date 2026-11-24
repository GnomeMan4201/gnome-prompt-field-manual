"""Fail-closed regression for the source-bound S-01/S-02/S-03 Batch 4 disposition.

No tests confer independently verified canonical-body status.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import unittest
from pathlib import Path

from batch6_baseline import baseline_bytes
from batch9_baseline import BATCH9_SOURCE_SHA
from tools.reconcile_entry_lineage import reconcile, validate_expectations

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DOC = ROOT / "docs/BATCH4_DISPOSITION_2026-11-23.md"
IDENTITY = ROOT / "workbench/data/current_entry_identity_index.json"
HISTORICAL_QUEUE = ROOT / "workbench/data/adjudication_queue.json"
HISTORICAL_INDEX = ROOT / "workbench/data/entry_identity_index.json"
HISTORICAL_HTML = ROOT / "tests/fixtures/batch3-canonical-1f06445e.html"

BATCH5_POST_STATE_SHA = "d5c0f82c33ab228166225972d7de0945b819c7d9a424451916fb5c2efca97e7d"
BASELINE_SHA = "1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19"
BATCH4_PAGE_SHA = "145b5fe00fedfa43d2a098f3bca1e59e6a9d7ffef8e4a378bc0852626a2d9a1a"
ALL_PAGE_SHA = "e4019358cb80de25706f983ab1eb2fb66e71dfcded70b94a8bddfe80c5eb14eb"
CARD_PATTERN = re.compile(
    r'<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>',
    re.S,
)


def cards(source: str) -> dict[int, str]:
    rows = [(int(m.group(1)), m.group(0)) for m in CARD_PATTERN.finditer(source)]
    if len(rows) != len({number for number, _ in rows}):
        raise AssertionError("Duplicate physical page")
    return dict(rows)


def fingerprint(items: dict[int, str], numbers: range | list[int]) -> str:
    return hashlib.sha256("\0".join(items[n] for n in numbers).encode()).hexdigest()


def display(cards_by_number: dict[int, str], numbers: range) -> str:
    chunks = []
    for n in numbers:
        match = re.search(r"<pre>(.*?)</pre>", cards_by_number[n], re.S)
        if not match:
            raise AssertionError(f"Page {n} has no canonical text")
        chunks.append(html.unescape(re.sub(r"<[^>]+>", "", match.group(1))))
    return " ".join(chunks).replace("\n", " ")


class Batch4DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = INDEX.read_text(encoding="utf-8")
        cls.cards = cards(cls.source)

    def test_current_source_hash_and_frozen_batch4_doc_binding(self):
        self.assertEqual(hashlib.sha256(baseline_bytes("index.html")).hexdigest(), BATCH5_POST_STATE_SHA)
        self.assertEqual(hashlib.sha256(INDEX.read_bytes()).hexdigest(), BATCH9_SOURCE_SHA)
        self.assertIn("Final `index.html` SHA-256: `8c7a56dc0687809e691ee09030f2a028c290c3ab81a64e63f4b58b6d809df3bd`", DOC.read_text())

    def test_315_canonical_pages_and_frozen_batch4_pages(self):
        self.assertEqual(len(self.cards), 315)
        self.assertEqual(sorted(self.cards), list(range(1, 316)))
        self.assertEqual(fingerprint(cards(baseline_bytes("index.html").decode()), list(range(1, 316))), ALL_PAGE_SHA)
        self.assertEqual(fingerprint(self.cards, range(107, 122)), BATCH4_PAGE_SHA)

    def test_reconciles_6_85_91_315_without_missing_inventory(self):
        r = reconcile(INDEX)
        self.assertEqual(validate_expectations(r,
            expected_pending=6, expected_drafted=85, expected_total=91, expected_pages=315), [])
        self.assertEqual(r.summary.pending_missing_from_embedded, 0)
        self.assertEqual(r.summary.pending_present_in_embedded, 6)
        self.assertEqual(r.summary.drafting_briefs, 6)

    def test_s01_frozen_brief_requirement(self):
        body = display(self.cards, range(107, 112)).upper()
        for required in ("WHO CAN INJECT", "SPECIFIC ACTOR TYPE", "OBSERVABILITY STATUS"):
            self.assertIn(required, body)

    def test_s02_frozen_brief_requirement(self):
        body = display(self.cards, range(112, 117)).upper()
        for required in ("HIDDEN STATE DEPENDENCIES", "SAFE MODIFICATION", "ACTUAL BEHAVIOR"):
            self.assertIn(required, body)

    def test_s03_frozen_brief_requirement(self):
        body = display(self.cards, range(117, 122)).upper()
        for required in ("DETECTABILITY", "MANDATORY", "EARLIEST OBSERVABLE SIGNAL"):
            self.assertIn(required, body)

    def test_no_active_pending_rows_or_briefs_for_promoted_ids(self):
        r = reconcile(INDEX)
        pending = {entry.entry_id for entry in r.pending_entries}
        briefs = {entry.entry_id for entry in r.briefs}
        for entry_id, brief_id in (("S-01", "b-s01"), ("S-02", "b-s02"), ("S-03", "b-s03")):
            self.assertNotIn(entry_id, pending)
            self.assertNotIn(entry_id, briefs)
            self.assertNotRegex(self.source, rf'<div class="brief" id="{brief_id}"')
        self.assertNotIn('<td class="batch-entries">S-01, S-02, S-03</td>', self.source)
        self.assertIn("document.getElementById('b-sec05').classList.add('open');", self.source)
        self.assertNotIn("document.getElementById('b-sec02').classList.add('open');", self.source)

    def test_identity_is_current_but_historical_review_queue_is_not_rewritten(self):
        identity = json.loads(IDENTITY.read_text())
        queue = json.loads(HISTORICAL_QUEUE.read_text())
        self.assertEqual(identity["sourceIndexSha256"], BATCH9_SOURCE_SHA)
        self.assertEqual(identity["counts"], {"pending": 6, "drafted": 85, "total": 91, "pages": 315})
        self.assertEqual(identity["bodyCoverage"], 0)
        self.assertEqual(queue["sourceHtmlSha256"], BASELINE_SHA)
        self.assertEqual(json.loads(HISTORICAL_INDEX.read_text())["sourceIndexSha256"], BASELINE_SHA)
        self.assertEqual(hashlib.sha256(HISTORICAL_HTML.read_bytes()).hexdigest(), BASELINE_SHA)
        self.assertIn("../../tests/fixtures/batch3-canonical-1f06445e.html", (ROOT / "workbench/adjudication/app.js").read_text())
        self.assertEqual(len(queue["entries"]), 91)


if __name__ == "__main__":
    unittest.main()
