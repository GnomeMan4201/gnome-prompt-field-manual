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


class Batch2DispositionTests(unittest.TestCase):
    def test_w01_w02_w03_promoted_out_of_pending_state(self) -> None:
        result = reconcile(INDEX)
        failures = validate_expectations(
            result,
            expected_pending=14,
            expected_drafted=77,
            expected_total=91,
            expected_pages=315,
        )
        self.assertEqual(failures, [])
        pending = {item.entry_id for item in result.pending_entries}
        briefs = {item.entry_id for item in result.briefs}
        for entry_id in ("W-01", "W-02", "W-03"):
            self.assertNotIn(entry_id, pending)
            self.assertNotIn(entry_id, briefs)

    def test_exactly_one_canonical_body_for_each_entry(self) -> None:
        w01 = "\n".join(visible_text(page(n)) for n in range(35, 40))
        w02 = "\n".join(visible_text(page(n)) for n in range(39, 44))
        w03 = "\n".join(visible_text(page(n)) for n in range(43, 49))
        self.assertEqual(w01.count("W-01 Dense-to-Clear (Rule-Based)"), 1)
        self.assertEqual(w02.count("W-02 Argument Skeleton Extractor"), 1)
        self.assertEqual(w03.count("W-03 Adversarial Reader (Persona-Specific)"), 1)

    def test_all_three_entries_retain_all_nine_fields(self) -> None:
        bodies = {
            "W-01": "\n".join(visible_text(page(n)) for n in range(35, 40)),
            "W-02": "\n".join(visible_text(page(n)) for n in range(39, 44)),
            "W-03": "\n".join(visible_text(page(n)) for n in range(43, 49)),
        }
        for entry_id, body in bodies.items():
            for field in FIELDS:
                self.assertIn(field, body, f"{entry_id} missing {field}")

    def test_w01_w11_prerequisite_is_in_inputs_needed_and_metadata(self) -> None:
        cards = [page(n) for n in range(36, 39)]
        visible = "\n".join(visible_text(x) for x in cards)
        metadata = " ".join(metadata_text(x) for x in cards)
        required_visible = (
            "If the source may not be summarizable without losing load-bearing content, "
            "run W-11 (The Anti-Summary) first to determine whether rewriting is appropriate."
        )
        self.assertIn(required_visible, visible.replace("\n", " "))
        self.assertIn(
            "if the source may not be summarizable without losing load-bearing content, run w-11 (the anti-summary) first to determine whether rewriting is appropriate.",
            metadata,
        )
        self.assertIn("rule-application log", metadata)
        self.assertIn("run w-04 (over-smoothing detector)", metadata)

    def test_w02_pass_properties_remain_intact(self) -> None:
        cards = [page(n) for n in range(39, 44)]
        visible = "\n".join(visible_text(x) for x in cards)
        metadata = " ".join(metadata_text(x) for x in cards)
        for required in (
            "INFERENCE GAP REGISTER",
            "HIDDEN PREMISES",
            "STRUCTURAL VERDICT: VALID / VALID WITH GAPS / FALLACIOUS",
            "Toulmin mode",
            "CLAIM:",
            "GROUNDS:",
            "WARRANT:",
            "BACKING:",
            "QUALIFIER:",
            "REBUTTAL:",
        ):
            self.assertIn(required, visible)
        self.assertIn("inference gap register", metadata)
        self.assertIn("structural verdict: valid / valid with gaps / fallacious", metadata)
        self.assertIn("toulmin mode", metadata)

    def test_w03_requires_at_least_three_specific_objections(self) -> None:
        cards = [page(n) for n in range(43, 48)]
        visible = "\n".join(visible_text(x) for x in cards)
        metadata = " ".join(metadata_text(x) for x in cards)
        self.assertIn("SPECIFIC OBJECTIONS A numbered list of at least three distinct objections", visible.replace("\n", " "))
        self.assertIn("specific objections a numbered list of at least three distinct objections", metadata)
        self.assertIn("<em>SPECIFIC OBJECTIONS A numbered list of at least three distinct objections this</em>", page(45))
        self.assertIn("WHAT THIS DRAFT AVOIDS", visible)
        self.assertIn("CONFIDENCE LAUNDERING FLAGS", visible)
        self.assertIn("ADVERSARIAL VERDICT: SURVIVES ATTACK / NEEDS REVISION / FAILS UNDER", visible)

    def test_remaining_batch_and_startup_state(self) -> None:
        source = INDEX.read_text(encoding="utf-8")
        self.assertNotIn('<td class="batch-entries">W-01, W-02, W-03</td>', source)
        self.assertIn("14 pending entries · 7 remaining batches · drafting authority", source)
        self.assertIn("Production state: 77 drafted · 0 restore · 14 pending", source)
        self.assertIn("document.getElementById('b-s01').classList.add('open');", source)
        self.assertIn("document.getElementById('b-s02').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-w01').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-w02').classList.add('open');", source)


if __name__ == "__main__":
    unittest.main()
