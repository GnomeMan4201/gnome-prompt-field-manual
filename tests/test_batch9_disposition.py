"""Verify the approved identity dispositions without promoting canonical bodies."""
import base64
from collections import Counter
import json
import re
import subprocess
import unittest

from batch8_baseline import PR45_MERGE, batch8_disposition_bytes
from batch9_baseline import (
    BATCH9_DISPOSITION_SOURCE_SHA, BATCH9_SOURCE_SHA, PR46_MERGE, ROOT, batch9_correction_bytes,
)
from test_batch6_correction import ADAPTER_PATH, EXPECTED_PDF_SHA256, HISTORICAL_ROOTS, INDEX_PATH, cards, digest, visible
from test_batch6_partial_disposition import UNRESOLVED, extract_brief
from tools.reconcile_entry_lineage import TreeParser, field_text, reconcile, validate_expectations

SOURCE = ROOT / "index.html"
READER = "GNOME-Field-Manual.html"
APPROVED_HEAD = "d286682a4c78e58f74d99e9f285e837a95cc6325"
ADJUDICATION = "docs/BATCH9_P06_P07_ADJUDICATION_2026-11-24.md"
CROSSWALK = "workbench/data/batch9_identity_crosswalk.json"
SCHEDULE = {6: ("SEC-05",), 10: ("P-08", "P-09", "P-10")}


class Batch9DispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.approved = batch9_correction_bytes("index.html")
        cls.pages = cards(cls.raw)
        cls.lineage = reconcile(SOURCE)
        cls.identity = json.loads((ROOT / INDEX_PATH).read_bytes())
        cls.crosswalk = json.loads((ROOT / CROSSWALK).read_bytes())
        parser = TreeParser()
        parser.feed(cls.raw.decode())
        parser.close()
        cls.workspace = parser.root

    def test_schedule_covers_only_the_four_active_briefs(self):
        self.assertEqual(validate_expectations(
            self.lineage, expected_pending=4, expected_drafted=87, expected_total=91, expected_pages=315
        ), [])
        pending = Counter(entry for entries in SCHEDULE.values() for entry in entries)
        self.assertEqual(Counter(row.entry_id for row in self.lineage.pending_entries), pending)
        self.assertEqual(Counter(brief.entry_id for brief in self.lineage.briefs), pending)
        schedule_rows = []
        for row in self.workspace.walk():
            if row.tag == "tr" and (number := field_text(row, "batch-num")):
                entries = tuple(part.strip() for part in field_text(row, "batch-entries").split(","))
                self.assertEqual(int(field_text(row, "batch-size")), len(entries))
                schedule_rows.append((int(number), entries))
        self.assertEqual(schedule_rows, list(SCHEDULE.items()))
        self.assertEqual(len(schedule_rows), self.lineage.summary.source_counts.batches)
        for entry in (b"sec05", b"p08", b"p09", b"p10"):
            self.assertEqual(extract_brief(self.raw, entry), extract_brief(self.approved, entry))
        self.assertIn(f'href="{UNRESOLVED}"'.encode(), self.raw)

    def test_workspace_links_resolve_by_subject_and_candidates_keep_their_authority(self):
        expected = (
            ("P-05 Work Sample Annotator", 222),
            ("P-06 Changelog Curation Engine", 228),
            ("P-07 RFC Draft Generator", 232),
            ("S-10 Architecture Decision Record Generator", 140),
        )
        callout = next(node for node in self.workspace.walk() if node.element_id == "batch9-disposition")
        links = {node.attrs["href"]: node.text() for node in callout.walk() if node.tag == "a"}
        entries = {row["id"]: row for row in self.identity["entries"]}
        for heading, page in expected:
            with self.subTest(heading=heading):
                self.assertRegex(visible(self.pages[page]), rf"(?m)^\s*{re.escape(heading)}\s*$")
                self.assertIn(heading, links[f"#manual-page-{page}"])
                entry_id, title = heading.split(" ", 1)
                self.assertEqual(entries[entry_id]["titleCandidate"], title)
                self.assertEqual(entries[entry_id]["titleAuthority"], "reconciler-candidate-not-verified-heading")
        readme = (ROOT / "README.md").read_text()
        self.assertIn("Canonical P-07 remains RFC Draft Generator.", readme)
        self.assertIn("Batch 10 is the final scheduled manuscript review", self.raw.decode())
        for source in (self.raw.decode(), readme):
            self.assertNotIn("Batch 9 is the next manuscript review", source)

    def test_export_changes_only_authorized_inventory_flags_and_candidate_titles(self):
        previous = json.loads(batch9_correction_bytes(INDEX_PATH))
        self.assertEqual(digest(self.approved), BATCH9_SOURCE_SHA)
        self.assertEqual(digest(self.raw), BATCH9_DISPOSITION_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH9_DISPOSITION_SOURCE_SHA}';", (ROOT / ADAPTER_PATH).read_text())
        previous["sourceIndexSha256"] = BATCH9_DISPOSITION_SOURCE_SHA
        previous["counts"].update(pending=4, drafted=87)
        candidates = {"P-06": "Changelog Curation Engine", "P-07": "RFC Draft Generator"}
        for row in previous["entries"]:
            if row["id"] in candidates:
                self.assertEqual((row["status"], row["pendingInventory"], row["draftingBrief"]), ("PENDING", True, True))
                row.update(status="NON_PENDING", pendingInventory=False, draftingBrief=False,
                           titleCandidate=candidates[row["id"]])
        self.assertEqual(self.identity, previous)
        self.assertEqual(self.identity["bodyCoverage"], 0)
        self.assertTrue(all(row["canonicalBody"] is None for row in self.identity["entries"]))

    def test_crosswalk_binds_distinct_plans_subjects_collisions_and_archives(self):
        walk = self.crosswalk
        self.assertEqual(walk["schemaVersion"], "gnome.batch9.crosswalk.v1")
        self.assertEqual(walk["sourceIndexSha256"], BATCH9_DISPOSITION_SOURCE_SHA)
        adjudication = (ROOT / ADJUDICATION).read_bytes()
        self.assertEqual(adjudication, batch9_correction_bytes(ADJUDICATION))
        self.assertEqual(walk["approvedBasis"], {
            "correctionPullRequest": 46, "approvedHeadCommit": APPROVED_HEAD, "mergeCommit": PR46_MERGE,
            "sourceIndexSha256": BATCH9_SOURCE_SHA,
            "adjudication": {"path": ADJUDICATION, "sha256": digest(adjudication)},
        })
        original = batch8_disposition_bytes("index.html")
        self.assertEqual(len(walk["entries"]), 2)
        for record, (plan_id, subject_id, subject_title, first, last, collision_title) in zip(walk["entries"], (
            ("P-06", "P-05", "Work Sample Annotator", 222, 228, "Changelog Curation Engine"),
            ("P-07", "P-06", "Changelog Curation Engine", 228, 232, "RFC Draft Generator"),
        ), strict=True):
            with self.subTest(planned=plan_id):
                short = plan_id.lower().replace("-", "")
                self.assertEqual(record["disposition"], "SUBSUMED")
                self.assertEqual(record["planned"], {
                    "briefId": f"b-{short}", "entryId": plan_id, "title": subject_title, "status": "CLOSED_AS_SUBSUMED",
                })
                self.assertEqual(record["canonicalSubject"], {
                    "entryId": subject_id, "title": subject_title, "firstPage": first, "lastPage": last,
                    "endsBeforeHeading": f"{plan_id} {collision_title}",
                    "status": "ACCEPTED_AS_SUBJECT_EQUIVALENT_NOT_ID_RENAME",
                })
                self.assertEqual(record["canonicalCollision"], {
                    "entryId": plan_id, "title": collision_title, "firstPage": last, "status": "DISTINCT_BODY_PRESERVED",
                })
                self.assertEqual(record["editorialInventory"], {
                    "entryId": plan_id, "statusBefore": "PENDING", "statusAfter": "NON_PENDING",
                    "pendingInventory": False, "draftingBrief": False,
                })
                path = f"tests/fixtures/batch9-frozen-planned-{short}.html"
                archive = (ROOT / path).read_bytes()
                self.assertEqual(archive, extract_brief(original, short.encode()))
                self.assertEqual(archive, extract_brief(self.approved, short.encode()))
                self.assertNotIn(f'id="b-{short}"'.encode(), self.raw)
                self.assertEqual(record["frozenBriefArchive"], {
                    "path": path, "sha256": digest(archive), "sourceCommit": PR45_MERGE,
                    "sourceIndexSha256": digest(original),
                })
        self.assertEqual(walk["countsAfter"], self.identity["counts"])
        self.assertEqual(walk["nonemptyBatchesAfter"], 2)
        self.assertEqual(walk["independentlyVerifiedCanonicalBodies"], 0)
        self.assertEqual(walk["canonicalBodyVerification"], "UNVERIFIED")
        self.assertIs(walk["promotionAuthorized"], False)

    def test_frozen_adr_reference_resolves_by_subject(self):
        self.assertIn(b"S-09 (Architecture Decision Record Generator", extract_brief(self.approved, b"p07"))
        self.assertIn(b"S-09 (Architecture Decision Record Generator", extract_brief(self.raw, b"p10"))
        self.assertIn(b"for the ADR subject wherever frozen briefs cite S-09", self.raw)
        self.assertIn("S-09 Incident Report Scaffold", visible(self.pages[138]))
        self.assertIn("S-10 Architecture Decision Record Generator", visible(self.pages[140]))
        self.assertIn("S-10 (Architecture Decision Record Generator)", visible(self.pages[232]))
        self.assertEqual(self.crosswalk["crossReferenceResolutions"], [{
            "frozen": {"briefId": "b-p07", "entryId": "S-09", "title": "Architecture Decision Record Generator"},
            "canonicalSubject": {"entryId": "S-10", "title": "Architecture Decision Record Generator", "firstPage": 140},
            "canonicalCollision": {"entryId": "S-09", "title": "Incident Report Scaffold", "firstPage": 138},
            "resolution": "BY_SUBJECT", "correctedReferencePage": 232,
        }])

    def test_page_cards_standalone_pdf_and_frozen_evidence_are_byte_identical(self):
        self.assertEqual(list(self.pages), list(range(1, 316)))
        self.assertEqual(self.pages, cards(self.approved))
        self.assertEqual(digest(b"\0".join(self.pages.values())),
                         "9f1b71b85eeb4b3021f039bb4713ae398e37f2fa8580a64e33cff64734321a71")
        self.assertEqual((ROOT / READER).read_bytes(), batch9_correction_bytes(READER))
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf, validate=True)), EXPECTED_PDF_SHA256)
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR46_MERGE, "--", *HISTORICAL_ROOTS], cwd=ROOT, text=True,
        ).splitlines()
        paths.remove(INDEX_PATH)
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), batch9_correction_bytes(path))
