"""Reader regressions from the November independent evaluation."""
import json
import re
import subprocess
import unittest

from test_batch6_correction import (
    CANONICAL, DATASET, STATIC, ROOT, cards, changed_pages, dataset_rows,
    digest, parity_errors, visible,
)

BASE = "03285ac8c57bfa8c40bddd2b2c53c0692927f8d3"
CHANGED = {7, 260, 262, 265, 273, 275, 283, 284}


def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


class ReaderDecisionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "index.html").read_bytes()
        cls.pages = cards(cls.raw)
        cls.reader = (ROOT / "GNOME-Field-Manual.html").read_bytes()

    def test_edit_scope_and_reader_parity(self):
        old_source = previous("index.html")
        old_reader = previous("GNOME-Field-Manual.html")
        static = cards(self.reader, STATIC)
        rows, serialized = dataset_rows(self.reader)
        for old, new in [(cards(old_source), self.pages), (cards(old_reader, STATIC), static),
                         (dataset_rows(old_reader)[1], serialized)]:
            self.assertEqual(changed_pages(old, new), CHANGED)
        self.assertEqual(CANONICAL.sub(b"", self.raw), CANONICAL.sub(b"", old_source))
        def outside_reader_pages(raw):
            return DATASET.sub(b"", STATIC.sub(b"", raw))
        self.assertEqual(outside_reader_pages(self.reader), outside_reader_pages(old_reader))
        for n in CHANGED:
            self.assertEqual(parity_errors(n, self.pages[n], rows[n], static[n]), set())
        self.assertIn("P-07", rows[273]["idTokens"])
        self.assertNotIn("P-05", rows[273]["idTokens"])

    def test_rfc_route_reaches_its_named_entry(self):
        route = re.search(r"or (P-\d+) \(RFC Draft Generator\)", visible(self.pages[273]))
        self.assertIsNotNone(route)
        self.assertRegex(visible(self.pages[232]), rf"(?m)^\s*{route[1]} RFC Draft Generator\s*$")

    def test_exact_title_references_match_a_canonical_heading(self):
        packet = json.loads((ROOT / "workbench/data/current_body_review.json").read_text())
        def normalize(title):
            return " ".join(re.findall(r"[a-z0-9]+", title.lower()))
        titles = {}
        for entry in packet["entries"]:
            titles.setdefault(normalize(entry["canonicalHeadingCandidate"]), set()).add(entry["entryId"])
        for n, card in self.pages.items():
            refs = re.findall(r"\b([A-Z]+-\d{2})\s*\(([^()]{3,85})\)", visible(card))
            for ref, label in refs:
                matches = titles.get(normalize(label))
                if matches:
                    with self.subTest(page=n, reference=ref, label=label):
                        self.assertIn(ref, matches)
        self.assertIn("S-10 (Architecture Decision Record Generator)", visible(self.pages[260]))
        for n in (262, 265):
            self.assertIn("S-09 (Incident Report Scaffold)", visible(self.pages[n]))

    def test_quality_action_and_evidence_boundary(self):
        self.assertIn("AP-06 flags passages for a human", visible(self.pages[275]))
        self.assertIn("authorship as unknown", visible(self.pages[283]))
        action = visible(self.pages[284])
        for phrase in ("INSUFFICIENT EVIDENCE", "human reviewer", "unmet quality criterion"):
            self.assertIn(phrase, action)
        self.assertNotIn("CONFIDENT GENERATED", action)
        self.assertIn("an open research question", visible(self.pages[7]))

    def test_reactor_binds_the_current_source(self):
        adapter = (ROOT / "workbench/reactor/source-adapter.js").read_text()
        self.assertIn(f"EXPECTED_SOURCE='{digest(self.raw)}'", adapter)
