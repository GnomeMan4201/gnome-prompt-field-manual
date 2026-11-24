"""Source-bound checks for closing exactly P-01 and P-02."""
import base64
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest

from batch8_baseline import (
    BATCH8_DISPOSITION_SOURCE_SHA, BATCH8_SOURCE_SHA, PR44_MERGE, ROOT,
    batch8_base_bytes, batch8_disposition_bytes, corrected_batch8_bytes,
)
from test_batch6_correction import (
    ADAPTER_PATH, EXPECTED_PDF_SHA256, HISTORICAL_ROOTS, INDEX_PATH, cards, digest,
)
from test_batch6_partial_disposition import extract_brief
from tools.reconcile_entry_lineage import TreeParser, field_text, reconcile, validate_expectations

ADJUDICATION = "docs/BATCH8_P01_P02_ADJUDICATION_2026-11-24.md"
DISPOSITION = "docs/BATCH8_P01_P02_DISPOSITION_2026-11-24.md"
SEC05_RECORD = "docs/BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md"
ARCHIVE = "tests/fixtures/batch8-{}-frozen-brief.html"
OBSOLETE_ORDER = re.compile(r"batch 8 (?:covers|pairs|is the next)", re.I)


class Batch8DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = batch8_disposition_bytes("index.html")
        cls.base = corrected_batch8_bytes("index.html")
        parser = TreeParser()
        parser.feed(cls.raw.decode())
        parser.close()
        cls.workspace = parser.root
        with TemporaryDirectory() as directory:
            source = Path(directory) / "index.html"
            source.write_bytes(cls.raw)
            cls.lineage = reconcile(source)

    def test_pending_inventory_and_schedule(self):
        self.assertEqual(validate_expectations(
            self.lineage, expected_pending=6, expected_drafted=85, expected_total=91, expected_pages=315
        ), [])
        pending = {record.entry_id for record in self.lineage.pending_entries}
        self.assertEqual(pending, {record.entry_id for record in self.lineage.briefs})
        schedule = {}
        for row in self.workspace.walk():
            if row.tag == "tr" and (number := field_text(row, "batch-num")):
                self.assertNotIn(int(number), schedule)
                ids = tuple(entry.strip() for entry in field_text(row, "batch-entries").split(","))
                self.assertEqual(int(field_text(row, "batch-size")), len(ids))
                schedule[int(number)] = ids
        self.assertEqual(schedule, {
            6: ("SEC-05",), 9: ("P-06", "P-07"), 10: ("P-08", "P-09", "P-10"),
        })
        self.assertEqual(Counter(entry for ids in schedule.values() for entry in ids), Counter(pending))
        self.assertEqual(len(schedule), self.lineage.summary.source_counts.batches)
        self.assertEqual(extract_brief(self.raw, b"sec05"), extract_brief(self.base, b"sec05"))
        self.assertIn(f'href="{SEC05_RECORD}"'.encode(), self.raw)

    def test_only_p01_p02_editorial_flags_change(self):
        current = json.loads(batch8_disposition_bytes(INDEX_PATH))
        expected = json.loads(corrected_batch8_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), BATCH8_DISPOSITION_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH8_DISPOSITION_SOURCE_SHA}';", batch8_disposition_bytes(ADAPTER_PATH).decode())
        expected["sourceIndexSha256"] = BATCH8_DISPOSITION_SOURCE_SHA
        expected["counts"].update(pending=6, drafted=85)
        for row in expected["entries"]:
            if row["id"] in {"P-01", "P-02"}:
                self.assertEqual((row["status"], row["pendingInventory"], row["draftingBrief"]),
                                 ("PENDING", True, True))
                row.update(status="NON_PENDING", pendingInventory=False, draftingBrief=False)
        self.assertEqual(current, expected)
        self.assertEqual(current["bodyCoverage"], 0)
        self.assertTrue(all(row["canonicalBody"] is None for row in current["entries"]))

    def test_active_guidance_no_longer_schedules_batch8(self):
        # Verify the detector on the superseded source, then confine it to active workspace sections.
        self.assertRegex(self.base.decode(), OBSOLETE_ORDER)
        for element in ("order", "batches"):
            node = next(node for node in self.workspace.walk() if node.element_id == element)
            self.assertNotRegex(node.text(), OBSOLETE_ORDER)
        for entry in (b"p01", b"p02"):
            self.assertNotIn(b'id="b-' + entry + b'"', self.raw)
        self.assertIn(b'href="#manual-page-209"', self.raw)
        self.assertIn(b'href="#manual-page-213"', self.raw)
        self.assertIn(f'href="{DISPOSITION}"'.encode(), self.raw)
        readme = batch8_disposition_bytes("README.md").decode()
        self.assertNotRegex(readme, OBSOLETE_ORDER)
        self.assertIn("Batch 9 is the next manuscript review", readme)

    def test_archive_and_approved_adjudication_are_bound(self):
        original = batch8_base_bytes("index.html")
        self.assertEqual(digest(self.base), BATCH8_SOURCE_SHA)
        record = (ROOT / DISPOSITION).read_text()
        for entry in ("p01", "p02"):
            archive = (ROOT / ARCHIVE.format(entry)).read_bytes()
            self.assertEqual(archive, extract_brief(self.base, entry.encode()))
            self.assertEqual(archive, extract_brief(original, entry.encode()))
            self.assertIn(digest(archive), record)
        matrix = (ROOT / ADJUDICATION).read_bytes()
        self.assertEqual(matrix, corrected_batch8_bytes(ADJUDICATION))
        for binding in (
            PR44_MERGE, digest(original), BATCH8_SOURCE_SHA, BATCH8_DISPOSITION_SOURCE_SHA,
            digest(matrix), digest(batch8_disposition_bytes(INDEX_PATH)),
        ):
            self.assertIn(binding, record)

    def test_page_cards_reader_pdf_and_prior_evidence_are_preserved(self):
        current = cards(self.raw)
        self.assertEqual(list(current), list(range(1, 316)))
        self.assertEqual(current, cards(self.base))
        self.assertEqual(batch8_disposition_bytes("GNOME-Field-Manual.html"),
                         corrected_batch8_bytes("GNOME-Field-Manual.html"))
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf, validate=True)), EXPECTED_PDF_SHA256)
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR44_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        paths.remove(INDEX_PATH)
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), corrected_batch8_bytes(path))
