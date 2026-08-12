from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.reconcile_entry_lineage import (
    exclusion_reason,
    markdown_report,
    reconcile,
    validate_expectations,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


FIXTURE = """<!doctype html>
<html><body>
<div class="stat"><span class="stat-num">2</span><span class="stat-label">Pending</span></div>
<div class="stat"><span class="stat-num">1</span><span class="stat-label">Drafted</span></div>
<div class="stat"><span class="stat-num">3</span><span class="stat-label">Total Entries</span></div>
<div class="stat"><span class="stat-num">1</span><span class="stat-label">Batches</span></div>
<div class="entry-row">
  <span class="er-id">T-01</span><span class="er-name">Timeline Probe</span>
  <span class="er-badge">pending</span><span class="er-why">Needs measured example.</span>
</div>
<div class="entry-row">
  <span class="er-id">T-02</span><span class="er-name">Source Split</span>
  <span class="er-badge">pending</span><span class="er-why">Needs counterexample.</span>
</div>
<div class="brief" id="b-t-01">
  <span class="brief-id">T-01</span><span class="brief-name">Timeline Probe</span>
  <span class="audit-chip">audit A</span>
</div>
<div class="brief" id="b-t-02">
  <span class="brief-id">T-02</span><span class="brief-name">Source Split</span>
  <span class="audit-chip">audit B</span>
</div>
<div class="manual-page-card">
  <div class="manual-page-head">Page 1</div>
  <pre>D-01: Existing Draft\nContent.\nAP-00 [Anti-Prompt Name]\nX-00 [Prompt Name]</pre>
</div>
<div class="manual-page-card">
  <div class="manual-page-head">Page 2</div>
  <pre>T-01 — Timeline Probe\nLegacy occurrence.\nTEST ID: EDT-01</pre>
</div>
</body></html>
"""


class LineageTests(unittest.TestCase):
    def write(self, content: str = FIXTURE) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "index.html"
        path.write_text(content, encoding="utf-8")
        return path

    def test_extracts_source_counts_and_components(self) -> None:
        result = reconcile(self.write())
        self.assertEqual(result.summary.source_counts.pending, 2)
        self.assertEqual(result.summary.source_counts.drafted, 1)
        self.assertEqual(result.summary.source_counts.total, 3)
        self.assertEqual(result.summary.pending_inventory_rows, 2)
        self.assertEqual(result.summary.drafting_briefs, 2)
        self.assertEqual(result.summary.embedded_page_cards, 2)

    def test_builds_reconciled_universe(self) -> None:
        result = reconcile(self.write())
        self.assertEqual(
            [entry.entry_id for entry in result.entries],
            ["D-01", "T-01", "T-02"],
        )
        self.assertEqual(result.summary.reconciled_universe_ids, 3)
        self.assertEqual(result.summary.drafted_embedded_not_pending, 1)
        by_id = {entry.entry_id: entry for entry in result.entries}
        self.assertEqual(by_id["D-01"].status, "embedded-not-listed-pending")
        self.assertEqual(by_id["T-01"].status, "pending-listed-and-present-in-embedded")
        self.assertEqual(by_id["T-02"].status, "pending-listed-not-found-in-embedded")

    def test_non_entry_tokens_are_retained_but_excluded(self) -> None:
        result = reconcile(self.write())
        self.assertEqual(result.summary.candidate_embedded_ids, 5)
        self.assertEqual(result.summary.excluded_non_entry_ids, 3)
        self.assertEqual(
            [item.token for item in result.excluded_tokens],
            ["AP-00", "EDT-01", "X-00"],
        )
        self.assertEqual(
            exclusion_reason("EDT-06"),
            "embedded test-case identifier used inside an entry",
        )
        self.assertNotIn("AP-00", [entry.entry_id for entry in result.entries])

    def test_conflict_sets_are_explicit(self) -> None:
        result = reconcile(self.write())
        self.assertEqual(result.conflicts["pending_present_in_embedded"], ["T-01"])
        self.assertEqual(result.conflicts["pending_missing_from_embedded"], ["T-02"])
        self.assertEqual(result.conflicts["drafted_embedded_not_pending"], ["D-01"])
        self.assertEqual(result.conflicts["inventory_without_brief"], [])
        self.assertEqual(result.conflicts["brief_without_inventory"], [])

    def test_expectations_pass_for_fixture(self) -> None:
        result = reconcile(self.write())
        self.assertEqual(
            validate_expectations(
                result,
                expected_pending=2,
                expected_drafted=1,
                expected_total=3,
                expected_pages=2,
            ),
            [],
        )

    def test_expectations_fail_closed_on_missing_ids(self) -> None:
        broken = FIXTURE.replace("<span class=\"er-id\">T-02</span>", "")
        result = reconcile(self.write(broken))
        failures = validate_expectations(
            result,
            expected_pending=2,
            expected_drafted=1,
            expected_total=3,
            expected_pages=2,
        )
        self.assertIn("one or more pending inventory rows lack an entry ID", failures)
        self.assertTrue(any(item.startswith("unique pending IDs:") for item in failures))

    def test_report_is_deterministic_and_hash_bound(self) -> None:
        result = reconcile(self.write())
        failures = validate_expectations(
            result,
            expected_pending=2,
            expected_drafted=1,
            expected_total=3,
            expected_pages=2,
        )
        first = markdown_report(result, failures)
        second = markdown_report(result, failures)
        self.assertEqual(first, second)
        self.assertIn(result.summary.source_sha256, first)
        self.assertIn("T-01", first)
        self.assertIn("AP-00", first)
        self.assertNotIn("Generated:", first)

    def test_repository_post_state_reconciles_to_21_70_91(self) -> None:
        result = reconcile(REPOSITORY_ROOT / "index.html")
        failures = validate_expectations(
            result,
            expected_pending=21,
            expected_drafted=70,
            expected_total=91,
            expected_pages=315,
        )
        self.assertEqual(failures, [])
        self.assertEqual(result.summary.pending_missing_from_embedded, 0)
        self.assertEqual(result.summary.pending_present_in_embedded, 21)
        self.assertEqual(result.conflicts["pending_missing_with_numbering_rationale"], [])


if __name__ == "__main__":
    unittest.main()
