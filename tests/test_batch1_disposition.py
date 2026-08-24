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


def page(page_no: int) -> str:
    source = INDEX.read_text(encoding="utf-8")
    page_id = f"manual-page-{page_no:03d}"
    match = re.search(
        rf'<article class="manual-page-card" id="{page_id}"[^>]*>.*?</article>',
        source,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"missing {page_id}")
    return match.group(0)


def visible_text(fragment: str) -> str:
    pre = re.search(r"<pre>(.*?)</pre>", fragment, re.DOTALL)
    if not pre:
        raise AssertionError("page card missing <pre>")
    return html.unescape(re.sub(r"<[^>]+>", "", pre.group(1)))


def metadata_text(fragment: str) -> str:
    match = re.search(r'data-manual-text="([^"]*)"', fragment, re.DOTALL)
    if not match:
        raise AssertionError("page card missing data-manual-text")
    return html.unescape(match.group(1))


class Batch1DispositionTests(unittest.TestCase):
    def test_t01_t02_promoted_out_of_pending_state(self) -> None:
        result = reconcile(INDEX)
        failures = validate_expectations(
            result,
            expected_pending=19,
            expected_drafted=72,
            expected_total=91,
            expected_pages=315,
        )
        self.assertEqual(failures, [])
        pending = {item.entry_id for item in result.pending_entries}
        briefs = {item.entry_id for item in result.briefs}
        self.assertNotIn("T-01", pending)
        self.assertNotIn("T-02", pending)
        self.assertNotIn("T-01", briefs)
        self.assertNotIn("T-02", briefs)

    def test_exactly_one_canonical_body_for_each_entry(self) -> None:
        t01 = "\n".join(visible_text(page(n)) for n in range(9, 13))
        t02 = "\n".join(visible_text(page(n)) for n in range(13, 18))
        self.assertEqual(t01.count("T-01 Idea Stress-Test"), 1)
        self.assertEqual(t02.count("T-02 Claim Dissection"), 1)

    def test_both_entries_retain_all_nine_fields(self) -> None:
        t01 = "\n".join(visible_text(page(n)) for n in range(9, 13))
        t02 = "\n".join(visible_text(page(n)) for n in range(13, 18))
        for field in FIELDS:
            self.assertIn(field, t01, f"T-01 missing {field}")
            self.assertIn(field, t02, f"T-02 missing {field}")

    def test_t01_frozen_clauses_and_metadata_parity(self) -> None:
        p10 = page(10)
        p11 = page(11)
        p12 = page(12)
        visible = "\n".join(visible_text(x) for x in (p10, p11, p12))
        metadata = " ".join(metadata_text(x) for x in (p10, p11, p12))
        self.assertIn("LENS 6 — CONSTRAINT LENS", visible)
        self.assertIn("highest-severity finding", visible)
        self.assertIn("VERDICT JUSTIFICATION", visible)
        self.assertIn("T-02 (Claim Dissection)", visible)
        self.assertIn("Assume a competent adversary knows this idea is being de-", visible)
        self.assertIn("Historical analog must be from", visible)
        self.assertIn("Weight lenses by:", visible)
        self.assertIn("run the weakest-link selection twice", visible)
        self.assertIn("lens 6 — constraint lens", metadata)
        self.assertIn("highest-severity finding", metadata)
        self.assertIn("verdict justification", metadata)
        self.assertIn("t-02 (claim dissection)", metadata)
        self.assertIn("assume a competent adversary knows this idea is being de-", metadata)
        self.assertIn("historical analog must be from", metadata)
        self.assertIn("weight lenses by:", metadata)
        self.assertIn("run the weakest-link selection twice", metadata)
        self.assertNotIn("LENS 6 — WEAKEST LINK LENS", visible)

    def test_t02_frozen_clauses_and_metadata_parity(self) -> None:
        cards = [page(n) for n in range(13, 18)]
        visible = "\n".join(visible_text(x) for x in cards)
        metadata = " ".join(metadata_text(x) for x in cards)
        self.assertIn("DISSECTION VERDICT: DEFENSIBLE / PARTIALLY DEFENSIBLE / COLLAPSE", visible)
        self.assertIn("RATIONALE: [One sentence explaining the rating", visible)
        self.assertIn("eight-item claim dissection", visible)
        self.assertNotIn("COLLAPSES", visible)
        self.assertIn("dissection verdict: defensible / partially defensible / collapse", metadata)
        self.assertIn("rationale: [one sentence explaining the rating", metadata)
        self.assertIn("eight-item claim dissection", metadata)
        self.assertNotIn("dissection verdict: defensible / partially defensible / collapses", metadata)
        self.assertNotIn("collapses: the claim relies", metadata)
        self.assertNotIn("partially defensible or collapses", metadata)
        self.assertNotIn("a collapses verdict", metadata)
        self.assertNotIn("dissue", metadata)
        self.assertIn("dis- section does not change what you understand about the claim", metadata)

    def test_batch1_prompt_is_historical_not_active(self) -> None:
        source = INDEX.read_text(encoding="utf-8")
        self.assertIn("Batch 1 Drafting Prompt — Completed Historical Provenance", source)
        self.assertIn("do not execute the block below as a current drafting instruction", source)
        self.assertNotIn('<td class="batch-entries">T-01, T-02</td>', source)

    def test_default_open_briefs_follow_remaining_pending_inventory(self) -> None:
        source = INDEX.read_text(encoding="utf-8")
        self.assertNotIn("document.getElementById('b-t01').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-t02').classList.add('open');", source)
        self.assertIn("document.getElementById('b-w01').classList.add('open');", source)
        self.assertIn("document.getElementById('b-w02').classList.add('open');", source)


if __name__ == "__main__":
    unittest.main()
