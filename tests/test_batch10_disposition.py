"""Source-bound regressions for the three Batch 10 editorial closures."""
import base64
import json
import re
import subprocess
import unittest

from test_reader_decision_contracts import previous
from batch10_baseline import (
    BATCH10_DISPOSITION_SOURCE_SHA, BATCH10_SOURCE_SHA, PR47_MERGE, PR48_MERGE, ROOT,
    batch10_base_bytes, batch10_correction_bytes,
)
from test_batch6_correction import (
    ADAPTER_PATH, EXPECTED_PDF_SHA256, HISTORICAL_ROOTS, INDEX_PATH, cards, digest, visible,
)
from test_batch6_partial_disposition import UNRESOLVED, extract_brief
from tools.reconcile_entry_lineage import TreeParser, field_text, reconcile, validate_expectations


SOURCE = ROOT / "index.html"
READER = "GNOME-Field-Manual.html"
APPROVED_HEAD = "4b90f644044f4b17de884b99ca8b3f47cce49b6c"
ADJUDICATION = "docs/BATCH10_P08_P09_P10_ADJUDICATION_2026-11-24.md"
DISPOSITION = "docs/BATCH10_DISPOSITION_2026-11-24.md"
CLOSEOUT = "docs/FINAL_EDITORIAL_CLOSEOUT_2026-11-24.md"
CANONICAL_PAGES_SHA = "065835de3c87b4e87af32d883f4460de0c819470e6ff0ee34cde012c9e506f67"
SUBJECTS = {
    "P-08": ("Peer Review Responder", 238),
    "P-09": ("Correction/Retraction Writer", 242),
    "P-10": ("Open Source Contribution Guide Generator", 247),
}


class Batch10DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = previous("index.html")
        cls.original = batch10_base_bytes("index.html")
        cls.approved = batch10_correction_bytes("index.html")
        cls.pages = cards(cls.raw)
        cls.identity = json.loads(previous(INDEX_PATH))

    def test_only_sec05_remains_in_the_inventory_and_schedule(self):
        result = reconcile(SOURCE)
        self.assertEqual(validate_expectations(
            result, expected_pending=1, expected_drafted=90, expected_total=91, expected_pages=315
        ), [])
        self.assertEqual([entry.entry_id for entry in result.pending_entries], ["SEC-05"])
        self.assertEqual([brief.entry_id for brief in result.briefs], ["SEC-05"])
        self.assertEqual(result.summary.source_counts.batches, 1)
        self.assertEqual(extract_brief(self.raw, b"sec05"), extract_brief(self.approved, b"sec05"))
        self.assertEqual(extract_brief(self.raw, b"sec05"), extract_brief(self.original, b"sec05"))

        parser = TreeParser()
        parser.feed(self.raw.decode())
        parser.close()
        schedule = [
            (field_text(row, "batch-num"), field_text(row, "batch-entries"), field_text(row, "batch-size"))
            for row in parser.root.walk()
            if row.tag == "tr" and field_text(row, "batch-num")
        ]
        self.assertEqual(schedule, [("6", "SEC-05", "1")])

    def test_title_candidates_match_headings_without_promoting_bodies(self):
        expected = json.loads(batch10_correction_bytes(INDEX_PATH))
        expected["sourceIndexSha256"] = BATCH10_DISPOSITION_SOURCE_SHA
        expected["counts"].update(pending=1, drafted=90)
        changed = set()
        for row in expected["entries"]:
            entry_id = row["id"]
            if entry_id not in SUBJECTS:
                continue
            with self.subTest(entry=entry_id):
                title, page = SUBJECTS[entry_id]
                self.assertRegex(visible(self.pages[page]), rf"(?m)^\s*{re.escape(entry_id + ' ' + title)}\s*$")
                self.assertEqual((row["status"], row["pendingInventory"], row["draftingBrief"]),
                                 ("PENDING", True, True))
                prior_title = "Correction / Retraction Writer" if entry_id == "P-09" else title
                self.assertEqual(row["titleCandidate"], prior_title)
                self.assertEqual(row["titleAuthority"], "reconciler-candidate-not-verified-heading")
                row.update(titleCandidate=title, status="NON_PENDING", pendingInventory=False, draftingBrief=False)
                changed.add(entry_id)
        self.assertEqual(changed, set(SUBJECTS))
        self.assertEqual(self.identity, expected)
        self.assertEqual(self.identity["bodyCoverage"], 0)
        self.assertTrue(all(row["canonicalBody"] is None for row in self.identity["entries"]))

    def test_approved_adjudication_and_original_brief_bytes_are_bound(self):
        record = (ROOT / DISPOSITION).read_text()
        matrix = (ROOT / ADJUDICATION).read_bytes()
        self.assertEqual(matrix, batch10_correction_bytes(ADJUDICATION))
        self.assertEqual(digest(self.approved), BATCH10_SOURCE_SHA)
        for binding in (APPROVED_HEAD, PR48_MERGE, PR47_MERGE, digest(self.original),
                        BATCH10_SOURCE_SHA, digest(matrix)):
            self.assertIn(binding, record)
        for entry_id in SUBJECTS:
            short = entry_id.lower().replace("-", "")
            with self.subTest(entry=entry_id):
                archive = (ROOT / f"tests/fixtures/batch10-{short}-frozen-brief.html").read_bytes()
                self.assertEqual(archive, extract_brief(self.original, short.encode()))
                self.assertEqual(archive, extract_brief(self.approved, short.encode()))
                self.assertNotIn(f'id="b-{short}"'.encode(), self.raw)
                self.assertIn(digest(archive), record)

    def test_current_source_bindings_and_unchanged_reader_artifacts(self):
        record = (ROOT / DISPOSITION).read_text()
        self.assertEqual(digest(self.raw), BATCH10_DISPOSITION_SOURCE_SHA)
        self.assertEqual(self.identity["sourceIndexSha256"], BATCH10_DISPOSITION_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH10_DISPOSITION_SOURCE_SHA}';", previous(ADAPTER_PATH).decode())
        self.assertEqual(list(self.pages), list(range(1, 316)))
        self.assertEqual(self.pages, cards(self.approved))
        self.assertEqual(digest(b"\0".join(self.pages.values())), CANONICAL_PAGES_SHA)
        reader = previous(READER)
        self.assertEqual(reader, batch10_correction_bytes(READER))
        pdf_pattern = rb'data="data:application/pdf;base64,([^"]+)"'
        pdf = base64.b64decode(re.search(pdf_pattern, self.raw)[1], validate=True)
        approved_pdf = base64.b64decode(re.search(pdf_pattern, self.approved)[1], validate=True)
        self.assertEqual(pdf, approved_pdf)
        self.assertEqual(digest(pdf), EXPECTED_PDF_SHA256)
        for binding in (BATCH10_DISPOSITION_SOURCE_SHA, digest(previous(INDEX_PATH)),
                        CANONICAL_PAGES_SHA, digest(reader), EXPECTED_PDF_SHA256):
            self.assertIn(binding, record)

    def test_previous_dispositions_crosswalks_and_research_files_are_unchanged(self):
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR48_MERGE, "--", *HISTORICAL_ROOTS], cwd=ROOT, text=True,
        ).splitlines()
        paths.remove(INDEX_PATH)
        for path in paths:
            with self.subTest(path=path):
                approved_file = subprocess.check_output(["git", "show", f"{PR48_MERGE}:{path}"], cwd=ROOT)
                self.assertEqual((ROOT / path).read_bytes(), approved_file)

    def test_notice_links_to_canonical_headings_and_closeout_records(self):
        parser = TreeParser()
        parser.feed(self.raw.decode())
        parser.close()
        workspace = parser.root
        notice = next(node for node in workspace.walk() if node.element_id == "batch10-disposition")
        links = {node.attrs["href"]: node.text() for node in notice.walk() if node.tag == "a"}
        for entry_id, (title, page) in SUBJECTS.items():
            self.assertIn(f"{entry_id} {title}", links[f"#manual-page-{page}"])
        readme = (ROOT / "README.md").read_text()
        for path in (DISPOSITION, CLOSEOUT):
            self.assertIn(path, links)
            self.assertTrue((ROOT / path).is_file())
            self.assertIn(f"]({path})", readme)

        inventory = next(node for node in workspace.walk() if node.element_id == "inventory")
        inventory_links = {node.attrs["href"] for node in inventory.walk() if node.tag == "a"}
        self.assertIn("#b-sec05", inventory_links)
        self.assertIn(UNRESOLVED, inventory_links)
        self.assertIn(f"]({UNRESOLVED})", readme)
