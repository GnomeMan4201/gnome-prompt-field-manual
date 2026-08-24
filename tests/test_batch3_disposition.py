from __future__ import annotations

import html
import re
import unittest
from pathlib import Path

from tools.reconcile_entry_lineage import reconcile, validate_expectations

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
FIELDS = (
    "WHAT IT DOES",
    "WHEN TO USE",
    "THE PROMPT",
    "INPUTS NEEDED",
    "EXPECTED OUTPUT",
    "KNOBS",
    "FAILURE MODE",
    "FOLLOW-UP",
    "SAFETY NOTES",
)


def page(n: int) -> str:
    source = INDEX.read_text(encoding="utf-8")
    match = re.search(
        rf'<article class="manual-page-card" id="manual-page-{n:03d}"[^>]*>.*?</article>',
        source,
        re.S,
    )
    if not match:
        raise AssertionError(f"missing page {n}")
    return match.group(0)


def visible(card: str) -> str:
    match = re.search(r"<pre>(.*?)</pre>", card, re.S)
    if not match:
        raise AssertionError("page has no visible <pre> surface")
    return html.unescape(re.sub(r"<[^>]+>", "", match.group(1)))


def metadata(card: str) -> str:
    match = re.search(r'data-manual-text="([^"]*)"', card, re.S)
    if not match:
        raise AssertionError("page has no data-manual-text surface")
    return html.unescape(match.group(1))


class Batch3DispositionTests(unittest.TestCase):
    def test_state(self) -> None:
        result = reconcile(INDEX)
        self.assertEqual(
            validate_expectations(
                result,
                expected_pending=14,
                expected_drafted=77,
                expected_total=91,
                expected_pages=315,
            ),
            [],
        )
        pending = {entry.entry_id for entry in result.pending_entries}
        briefs = {entry.entry_id for entry in result.briefs}
        for entry_id in ("R-01", "R-03"):
            self.assertNotIn(entry_id, pending)
            self.assertNotIn(entry_id, briefs)

    def test_bodies_retain_all_nine_fields(self) -> None:
        bodies = {
            "R-01": "\n".join(visible(page(n)) for n in range(71, 78)),
            "R-03": "\n".join(visible(page(n)) for n in range(79, 87)),
        }
        self.assertEqual(bodies["R-01"].count("R-01 Source Map with Contested Zones"), 1)
        self.assertEqual(bodies["R-03"].count("R-03 Replication Risk Auditor"), 1)
        for entry_id, body in bodies.items():
            for field in FIELDS:
                self.assertIn(field, body, f"{entry_id} missing {field}")

    def test_r01_frozen_properties_and_metadata_order(self) -> None:
        cards = [page(n) for n in range(71, 77)]
        body = " ".join(visible(card) for card in cards)
        search = " ".join(metadata(card) for card in cards)

        for token in (
            "INSTITUTIONAL INTEREST MAP",
            "CONTESTED ZONES",
            "KNOWN GAPS",
            "SOURCE FLATTENING WARNINGS",
        ):
            self.assertIn(token, body)
        self.assertIn("Six components:", body)

        page73_meta = metadata(page(73))
        self.assertEqual(page73_meta.count("institutional interest map"), 1)
        self.assertIn("if no contested zones are identified on a mature research topic", page73_meta)
        self.assertNotIn("if no institutional interest map", page73_meta)
        self.assertLess(page73_meta.index("institutional interest map"), page73_meta.index("contested zones"))
        self.assertLess(
            page73_meta.index("contested zones"),
            page73_meta.index("if no contested zones are identified on a mature research topic"),
        )
        self.assertLess(
            page73_meta.index("if no contested zones are identified on a mature research topic"),
            page73_meta.index("known gaps"),
        )
        self.assertIn("institutional interest map", search)

    def test_r03_frozen_properties(self) -> None:
        cards = [page(n) for n in range(79, 87)]
        body = " ".join(visible(card) for card in cards)
        search = " ".join(metadata(card) for card in cards)
        for token in (
            "VERY HIGH RISK",
            "NOT REPLICATION-READY",
            "R-05 (Failure-to-Test Converter)",
            "HARKING FLAGS",
        ):
            self.assertIn(token, body)
        self.assertIn("very high risk", search)
        self.assertIn("separate assessment-status outcome", search)
        self.assertIn("r-05 (failure-to-test converter)", search)

    def test_startup_targets_first_two_remaining_briefs(self) -> None:
        source = INDEX.read_text(encoding="utf-8")
        self.assertIn("document.getElementById('b-s01').classList.add('open');", source)
        self.assertIn("document.getElementById('b-s02').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-r01').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-r03').classList.add('open');", source)
        self.assertNotIn('<td class="batch-entries">R-01, R-03</td>', source)


if __name__ == "__main__":
    unittest.main()
