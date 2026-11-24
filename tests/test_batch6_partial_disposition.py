"""Source-bound gates for closing only SEC-02 while Batch 6 remains open."""
from collections import Counter
import base64
import json
import re
import subprocess
from pathlib import Path
import tempfile
import unittest

from batch6_baseline import (
    FINAL_SOURCE_SHA, PARTIAL_SOURCE_SHA, PR40_MERGE, ROOT, adjudication_bytes,
)
from batch7_baseline import merged_disposition_bytes
from test_batch6_correction import (
    ADAPTER_PATH, EXPECTED_PDF_SHA256, HISTORICAL_ROOTS, INDEX_PATH, canonical_surface,
    cards, contract_errors, digest, visible,
)
from test_batch6_final_adjudication import canary_errors
from tools.reconcile_entry_lineage import TreeParser, field_text, reconcile, validate_expectations

INITIAL_DISPOSITION = "029dc88e95ddf39dd357208b4548f0aacdb1baa9"
UNSUPPORTED_CAUSATION = re.compile(
    r"\b(?:signals|proves|confirms|establishes) (?:an? )?(?:successful )?injection\b", re.I
)
ARCHIVE = "tests/fixtures/batch6-sec02-frozen-brief.html"
DISPOSITION = "docs/BATCH6_SEC02_DISPOSITION_2026-11-24.md"
AMENDMENT = "docs/BATCH6_ADJUDICATION_AMENDMENT_2026-11-24.md"
UNRESOLVED = "docs/BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md"
REQUIRED_ARTIFACT = (
    "Two outputs: (1) Refactored code/prompt with annotations at each separation point "
    "explaining the change. (2) Test suite: at minimum, normal-input passing test, "
    "delimiter-escape attempt that should fail, injection attempt that should be blocked. "
    "The test suite must be copy-paste executable."
)


def extract_brief(source, subject):
    pattern = rb'^  <div class="brief" id="b-' + subject + rb'">\n.*?^  </div>\n'
    return re.search(pattern, source, re.M | re.S)[0]


def sec02_caution(source):
    parser = TreeParser()
    parser.feed(source.decode())
    parser.close()
    section = next(node for node in parser.root.walk() if node.element_id == "caution")
    card = next(node for node in section.walk()
                if "caution-card" in node.classes and field_text(node, "caution-id") == "SEC-02")
    return field_text(card, "caution-body")


class Batch6PartialDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = merged_disposition_bytes("index.html")
        cls.before = adjudication_bytes("index.html")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "index.html"
            source.write_bytes(cls.raw)
            cls.lineage = reconcile(source)

    def test_inventory_and_schedule_agree(self):
        self.assertEqual(validate_expectations(
            self.lineage, expected_pending=9, expected_drafted=82, expected_total=91, expected_pages=315
        ), [])
        pending = {entry.entry_id for entry in self.lineage.pending_entries}
        self.assertEqual(pending, {entry.entry_id for entry in self.lineage.briefs})
        parser = TreeParser()
        parser.feed(self.raw.decode())
        parser.close()
        rows = []
        for node in parser.root.walk():
            if node.tag != "tr":
                continue
            batch = field_text(node, "batch-num")
            if batch:
                subjects = tuple(item.strip() for item in field_text(node, "batch-entries").split(","))
                self.assertEqual(int(field_text(node, "batch-size")), len(subjects))
                rows.append((int(batch), subjects))
        self.assertEqual(rows, [
            (6, ("SEC-05",)), (7, ("SEC-06",)), (8, ("P-01", "P-02")),
            (9, ("P-06", "P-07")), (10, ("P-08", "P-09", "P-10")),
        ])
        self.assertEqual(Counter(subject for _, subjects in rows for subject in subjects), Counter(pending))
        self.assertEqual(self.lineage.summary.source_counts.batches, len(rows))

    def test_only_sec02_changes_in_current_identity(self):
        actual = json.loads(merged_disposition_bytes(INDEX_PATH))
        expected = json.loads(adjudication_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), PARTIAL_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{PARTIAL_SOURCE_SHA}';", merged_disposition_bytes(ADAPTER_PATH).decode())
        expected["sourceIndexSha256"] = PARTIAL_SOURCE_SHA
        expected["counts"].update(pending=9, drafted=82)
        sec02 = next(row for row in expected["entries"] if row["id"] == "SEC-02")
        self.assertEqual((sec02["status"], sec02["pendingInventory"], sec02["draftingBrief"]),
                         ("PENDING", True, True))
        sec02.update(status="NON_PENDING", pendingInventory=False, draftingBrief=False)
        self.assertEqual(actual, expected)
        self.assertEqual(actual["bodyCoverage"], 0)
        self.assertTrue(all(row["canonicalBody"] is None for row in actual["entries"]))

    def test_frozen_sec02_brief_and_amendment_are_bound(self):
        archive = (ROOT / ARCHIVE).read_bytes()
        record = (ROOT / DISPOSITION).read_text()
        self.assertEqual(digest(self.before), FINAL_SOURCE_SHA)
        self.assertEqual(archive, extract_brief(self.before, b"sec02"))
        self.assertNotIn(b'id="b-sec02"', self.raw)
        initial_source = subprocess.check_output(
            ["git", "show", f"{INITIAL_DISPOSITION}:index.html"], cwd=ROOT
        )
        for binding in (
            PR40_MERGE, FINAL_SOURCE_SHA, digest(initial_source), digest(archive),
            digest((ROOT / AMENDMENT).read_bytes()),
        ):
            self.assertIn(binding, record)
        self.assertIn(b'href="#manual-page-156"', self.raw)
        self.assertIn(f'href="{AMENDMENT}"'.encode(), self.raw)
        self.assertIn(f'href="{DISPOSITION}"'.encode(), self.raw)

    def test_active_sec02_caution_matches_canonical_and_amended_guidance(self):
        caution = sec02_caution(self.raw)
        self.assertNotRegex(caution, UNSUPPORTED_CAUSATION)
        self.assertRegex(sec02_caution(self.before), UNSUPPORTED_CAUSATION)
        for obsolete in ("must be expanded", "Add behavioral baseline definition", "Draft this after"):
            self.assertNotIn(obsolete, caution)
        self.assertIn("Exact, fragment, and pattern-only canary matches are observations.", caution)
        self.assertIn("A match may trigger quarantine or investigation under policy.", caution)
        self.assertIn(
            "independent, trustworthy evidence links untrusted input to a policy-violating change", caution
        )

        page = canonical_surface(visible(cards(self.raw)[156]))
        self.assertIn("a match alone does not establish injection", page)
        self.assertIn("require independent, trustworthy evidence connecting untrusted input", page)
        amendment = (ROOT / AMENDMENT).read_text()
        self.assertIn("A canary match is an observation.", amendment)
        self.assertIn(
            "independent, trustworthy evidence connects untrusted input to a policy-violating change",
            amendment,
        )

    def test_initial_disposition_records_and_archive_are_unchanged(self):
        for path in (DISPOSITION, UNRESOLVED, ARCHIVE):
            with self.subTest(path=path):
                expected = subprocess.check_output(["git", "show", f"{INITIAL_DISPOSITION}:{path}"], cwd=ROOT)
                self.assertEqual((ROOT / path).read_bytes(), expected)

    def test_sec05_brief_and_original_requirement_remain_live(self):
        sec05 = extract_brief(self.raw, b"sec05")
        self.assertEqual(sec05, extract_brief(self.before, b"sec05"))
        self.assertIn(REQUIRED_ARTIFACT, sec05.decode())
        record = (ROOT / UNRESOLVED).read_text()
        for clause in (
            REQUIRED_ARTIFACT, digest(sec05), PR40_MERGE, FINAL_SOURCE_SHA,
            digest(adjudication_bytes("examples/batch6_runtime_policy.py")),
            "Independent behavioral evaluation", "actual observed results",
        ):
            self.assertIn(clause, record)
        self.assertIn(f'href="{UNRESOLVED}"'.encode(), self.raw)

    def test_all_pages_standalone_pdf_and_prior_evidence_are_unchanged(self):
        pages = cards(self.raw)
        self.assertEqual(list(pages), list(range(1, 316)))
        self.assertEqual(pages, cards(self.before))
        self.assertEqual(merged_disposition_bytes("GNOME-Field-Manual.html"),
                         adjudication_bytes("GNOME-Field-Manual.html"))
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf, validate=True)), EXPECTED_PDF_SHA256)
        self.assertEqual(canary_errors(pages), set())
        self.assertEqual(contract_errors(pages), set())
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR40_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        paths.remove(INDEX_PATH)
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), adjudication_bytes(path))
