from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.audit_editorial_lineage import (
    CLASSIFIER_PATH,
    HISTORICAL_RECORDS,
    audit,
    markdown,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class EditorialLineageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = (REPOSITORY_ROOT / "index.html").read_text(encoding="utf-8")

    def write_source(self, text: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "index.html"
        path.write_text(text, encoding="utf-8")
        return path

    def copy_repository_evidence(self) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        for relative in (*HISTORICAL_RECORDS, CLASSIFIER_PATH):
            source = REPOSITORY_ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        return root

    def failed_checks(self, result) -> set[str]:
        return {check.name for check in result.checks if not check.passed}

    def test_corrected_repository_passes_all_post_state_gates(self) -> None:
        result = audit(REPOSITORY_ROOT / "index.html", REPOSITORY_ROOT)
        self.assertTrue(result.passed)
        self.assertEqual(self.failed_checks(result), set())
        self.assertEqual(len(result.affected_pages), 8)
        self.assertTrue(all(item.parity for item in result.affected_pages))

    def test_field_journal_collision_fails_closed_even_with_surface_parity(self) -> None:
        broken = self.source.replace(
            "use a structured session record when no belief changes are expected",
            "use r-05 (field journal entry) for structured session records when no belief changes are expected",
            1,
        ).replace(
            "use a structured session\nrecord when no belief changes are expected",
            "use R-05 (Field Journal\nEntry) for structured session records when no belief changes are\nexpected",
            1,
        )
        result = audit(self.write_source(broken), REPOSITORY_ROOT)
        failed = self.failed_checks(result)
        self.assertFalse(result.passed)
        self.assertIn("manual-page-213:semantic-rules", failed)
        self.assertIn("no-stale-current-state-pairing", failed)
        self.assertNotIn("manual-page-213:surface-parity", failed)

    def test_partial_renumbering_fails_closed(self) -> None:
        broken = self.source.replace(
            "  R-10 Source-of-Truth Conflict Resolver",
            "  R-07 Source-of-Truth Conflict Resolver",
            1,
        )
        result = audit(self.write_source(broken), REPOSITORY_ROOT)
        self.assertFalse(result.passed)
        self.assertIn("manual-page-093:surface-parity", self.failed_checks(result))
        self.assertIn("exactly-one-source-of-truth-body", self.failed_checks(result))

    def test_duplicate_source_of_truth_body_fails_closed(self) -> None:
        marker = "</div>\n    </div>\n  </div>\n</section>"
        duplicate = (
            '<article class="manual-page-card" id="manual-page-999" '
            'data-manual-text="r-10 source-of-truth conflict resolver">'
            "<pre>R-10 Source-of-Truth Conflict Resolver</pre></article>"
        )
        broken = self.source.replace(marker, duplicate + marker, 1)
        result = audit(self.write_source(broken), REPOSITORY_ROOT)
        self.assertFalse(result.passed)
        self.assertIn("exactly-one-source-of-truth-body", self.failed_checks(result))

    def test_stale_cross_reference_fails_closed(self) -> None:
        broken = self.source.replace(
            "r-05 (failure-to-test converter)",
            "r-06 (failure-to-test converter)",
            1,
        )
        result = audit(self.write_source(broken), REPOSITORY_ROOT)
        self.assertFalse(result.passed)
        self.assertIn("no-stale-current-state-pairing", self.failed_checks(result))

    def test_stale_search_metadata_fails_parity(self) -> None:
        broken = self.source.replace(
            "step 6 →r-07 (competing hypotheses table)",
            "step 6 →r-06 (competing hypotheses table)",
            1,
        )
        result = audit(self.write_source(broken), REPOSITORY_ROOT)
        self.assertFalse(result.passed)
        self.assertIn("manual-page-267:surface-parity", self.failed_checks(result))

    def test_historical_provenance_mutation_fails_closed(self) -> None:
        root = self.copy_repository_evidence()
        record = root / "docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md"
        record.write_text(record.read_text(encoding="utf-8") + "\nmutated\n", encoding="utf-8")
        result = audit(REPOSITORY_ROOT / "index.html", root)
        self.assertFalse(result.passed)
        self.assertIn(
            "preserve:docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md",
            self.failed_checks(result),
        )

    def test_historical_pdf_mutation_fails_closed(self) -> None:
        broken = self.source.replace("JVBERi0x", "KVBERi0x", 1)
        result = audit(self.write_source(broken), REPOSITORY_ROOT)
        self.assertFalse(result.passed)
        self.assertIn("historical-pdf-byte-preservation", self.failed_checks(result))

    def test_report_is_deterministic_and_hash_bound(self) -> None:
        result = audit(REPOSITORY_ROOT / "index.html", REPOSITORY_ROOT)
        first = markdown(result)
        second = markdown(result)
        self.assertEqual(first, second)
        self.assertIn(result.source_sha256, first)
        self.assertIn(result.pdf_sha256, first)
        self.assertIn(result.text_surface_sha256, first)


if __name__ == "__main__":
    unittest.main()
