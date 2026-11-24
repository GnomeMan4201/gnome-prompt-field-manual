"""Verify that only SEC-06 is closed and that the workspace follows the correction."""
import base64
from collections import Counter
import json
import re
import subprocess
import unittest

from batch7_baseline import (
    BATCH7_DISPOSITION_SOURCE_SHA, BATCH7_SOURCE_SHA, PR42_MERGE, ROOT,
    corrected_sec06_bytes, merged_disposition_bytes,
)
from test_batch6_correction import (
    ADAPTER_PATH, EXPECTED_PDF_SHA256, HISTORICAL_ROOTS, INDEX_PATH, cards, digest,
)
from test_batch6_partial_disposition import extract_brief
from tools.reconcile_entry_lineage import TreeParser, field_text, reconcile, validate_expectations

SOURCE = ROOT / "index.html"
ARCHIVE = "tests/fixtures/batch7-sec06-frozen-brief.html"
ADJUDICATION = "docs/BATCH7_SEC06_ADJUDICATION_2026-11-24.md"
DISPOSITION = "docs/BATCH7_SEC06_DISPOSITION_2026-11-24.md"
SEC05_EVIDENCE = "docs/BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md"
SUPERSEDED = re.compile(r"drafts? alone|drafting alone|before DOCX insertion|specific control that blocks each one", re.I)


def parse_workspace(source):
    parser = TreeParser()
    parser.feed(source.decode())
    parser.close()
    return parser.root


def sec06_caution(root):
    section = next(node for node in root.walk() if node.element_id == "caution")
    return next(node for node in section.walk()
                if "caution-card" in node.classes and field_text(node, "caution-id") == "SEC-06")


class Batch7DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.base = corrected_sec06_bytes("index.html")
        cls.workspace = parse_workspace(cls.raw)
        cls.lineage = reconcile(SOURCE)

    def test_inventory_and_schedule(self):
        self.assertEqual(validate_expectations(
            self.lineage, expected_pending=8, expected_drafted=83, expected_total=91, expected_pages=315
        ), [])
        pending = {entry.entry_id for entry in self.lineage.pending_entries}
        self.assertEqual(pending, {entry.entry_id for entry in self.lineage.briefs})
        schedule = {}
        for row in self.workspace.walk():
            if row.tag == "tr" and (number := field_text(row, "batch-num")):
                self.assertNotIn(int(number), schedule)
                subjects = tuple(name.strip() for name in field_text(row, "batch-entries").split(","))
                self.assertEqual(int(field_text(row, "batch-size")), len(subjects))
                schedule[int(number)] = subjects
        self.assertEqual(schedule, {
            6: ("SEC-05",), 8: ("P-01", "P-02"), 9: ("P-06", "P-07"), 10: ("P-08", "P-09", "P-10")
        })
        self.assertEqual(Counter(name for names in schedule.values() for name in names), Counter(pending))
        self.assertEqual(self.lineage.summary.source_counts.batches, len(schedule))
        self.assertEqual(extract_brief(self.raw, b"sec05"), extract_brief(self.base, b"sec05"))
        self.assertIn(f'href="{SEC05_EVIDENCE}"'.encode(), self.raw)

    def test_only_sec06_editorial_flags_change(self):
        identity = json.loads((ROOT / INDEX_PATH).read_bytes())
        expected = json.loads(corrected_sec06_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), BATCH7_DISPOSITION_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH7_DISPOSITION_SOURCE_SHA}';", (ROOT / ADAPTER_PATH).read_text())
        expected["sourceIndexSha256"] = BATCH7_DISPOSITION_SOURCE_SHA
        expected["counts"].update(pending=8, drafted=83)
        sec06 = next(row for row in expected["entries"] if row["id"] == "SEC-06")
        self.assertEqual((sec06["status"], sec06["pendingInventory"], sec06["draftingBrief"]),
                         ("PENDING", True, True))
        self.assertEqual(sec06["titleCandidate"], "Tool-Agent Offense Probe")
        sec06.update(status="NON_PENDING", pendingInventory=False, draftingBrief=False)
        self.assertEqual(identity, expected)
        self.assertEqual(identity["bodyCoverage"], 0)
        self.assertTrue(all(row["canonicalBody"] is None for row in identity["entries"]))

    def test_active_guidance_uses_corrected_contract(self):
        self.assertRegex(sec06_caution(parse_workspace(self.base)).text(), SUPERSEDED)
        caution = sec06_caution(self.workspace).text()
        self.assertNotRegex(caution, SUPERSEDED)
        self.assertNotIn(b'id="b-sec06"', self.raw)
        for phrase in (
            "written authorization and scope", "isolated synthetic fixtures", "observed runtime evidence",
            "distinguish detection from prevention", "every HIGH finding", "before deploying remediation",
        ):
            self.assertIn(phrase, caution)
        for element_id in ("order", "batches", "sec06-reader-guidance"):
            section = next(node for node in self.workspace.walk() if node.element_id == element_id)
            self.assertNotRegex(section.text(), SUPERSEDED)
        self.assertIn(b'older probe wording on pages 121, 261, and 271 is preserved for provenance', self.raw)
        self.assertIn(f'href="{DISPOSITION}"'.encode(), self.raw)
        readme = (ROOT / "README.md").read_text()
        self.assertIn("current defensive evaluation contract on pages 187–197", readme)
        self.assertIn("archived brief and older probe wording serve as provenance", readme)
        self.assertNotRegex(readme, SUPERSEDED)

    def test_frozen_brief_and_report_bindings(self):
        archived = (ROOT / ARCHIVE).read_bytes()
        self.assertEqual(archived, extract_brief(self.base, b"sec06"))
        original = merged_disposition_bytes("index.html")
        self.assertEqual(archived, extract_brief(original, b"sec06"))
        self.assertEqual(digest(self.base), BATCH7_SOURCE_SHA)
        report = (ROOT / ADJUDICATION).read_bytes()
        self.assertEqual(report, corrected_sec06_bytes(ADJUDICATION))
        record = (ROOT / DISPOSITION).read_text()
        for binding in (
            PR42_MERGE, digest(original), digest(archived), digest(report), BATCH7_SOURCE_SHA,
            BATCH7_DISPOSITION_SOURCE_SHA, digest((ROOT / INDEX_PATH).read_bytes()),
        ):
            self.assertIn(binding, record)

    def test_pages_standalone_pdf_and_historical_files_are_preserved(self):
        actual = cards(self.raw)
        self.assertEqual(list(actual), list(range(1, 316)))
        self.assertEqual(actual, cards(self.base))
        self.assertEqual((ROOT / "GNOME-Field-Manual.html").read_bytes(),
                         corrected_sec06_bytes("GNOME-Field-Manual.html"))
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf, validate=True)), EXPECTED_PDF_SHA256)
        protected = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR42_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        protected.remove(INDEX_PATH)
        for path in protected:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), corrected_sec06_bytes(path))
