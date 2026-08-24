#!/usr/bin/env python3
"""One-shot, fail-closed Batch 1 disposition migration.

This script is intentionally temporary. It mutates only the frozen T-01/T-02
Batch 1 boundary from issue #10, updates current-state metadata/tests, writes a
SHA-bound audit record, and is deleted by the one-shot workflow after all gates
pass. Dated historical baselines and the historical v9 PDF are never touched.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EXPECTED_INDEX_SHA256 = "4ac0157df83a7deed06583da6d9f000d4ec2220490fa07e03de4bd6759d65243"
BASE_COMMIT = "0ee5a50bc1fddf86e45c9b51818b78e7c40fccfc"
DATE = "2026-08-24"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(text: str, old: str, new: str, *, count: int = 1, label: str) -> str:
    found = text.count(old)
    if found != count:
        raise SystemExit(f"{label}: expected {count} exact match(es), found {found}")
    return text.replace(old, new, count)


def regex_once(text: str, pattern: str, replacement: str, *, label: str, flags: int = 0) -> str:
    result, found = re.subn(pattern, replacement, text, count=1, flags=flags)
    if found != 1:
        raise SystemExit(f"{label}: expected one regex match, found {found}")
    return result


def mutate_page(text: str, page_id: str, transform) -> str:
    pattern = re.compile(
        rf'<article class="manual-page-card" id="{re.escape(page_id)}"[^>]*>.*?</article>',
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        raise SystemExit(f"missing page card {page_id}")
    page = match.group(0)
    changed = transform(page)
    if changed == page:
        raise SystemExit(f"{page_id}: transform made no change")
    return text[: match.start()] + changed + text[match.end() :]


def patch_index() -> tuple[str, str]:
    pre_hash = sha256(INDEX)
    if pre_hash != EXPECTED_INDEX_SHA256:
        raise SystemExit(
            f"index.html SHA-256 mismatch: expected {EXPECTED_INDEX_SHA256}, got {pre_hash}"
        )

    text = INDEX.read_text(encoding="utf-8")

    # Current production-state metadata only.
    replacements = [
        (
            "21 pending entries · 10 batches · drafting authority",
            "19 pending entries · 9 remaining batches · drafting authority",
            "header production summary",
        ),
        (
            "Production state: 70 drafted · 0 restore · 21 pending",
            "Production state: 72 drafted · 0 restore · 19 pending",
            "header production state",
        ),
        (
            '<div class="stat"><div class="stat-num sn-pending">21</div><div class="stat-label">Pending Entries</div></div>',
            '<div class="stat"><div class="stat-num sn-pending">19</div><div class="stat-label">Pending Entries</div></div>',
            "pending stat",
        ),
        (
            '<div class="stat"><div class="stat-num sn-drafted">70</div><div class="stat-label">Drafted</div></div>',
            '<div class="stat"><div class="stat-num sn-drafted">72</div><div class="stat-label">Drafted</div></div>',
            "drafted stat",
        ),
        (
            '<div class="stat"><div class="stat-num sn-batch">10</div><div class="stat-label">Batches</div></div>',
            '<div class="stat"><div class="stat-num sn-batch">9</div><div class="stat-label">Remaining Batches</div></div>',
            "batch stat",
        ),
        (
            '<span class="section-count">21 entries · 6 parts</span>',
            '<span class="section-count">19 entries · 5 parts</span>',
            "inventory section count",
        ),
        (
            '<a class="nl" href="#batch1">Batch 1 Prompt</a>',
            '<a class="nl" href="#batch1">Batch 1 Record</a>',
            "batch nav label",
        ),
        (
            '<span class="section-count">22 entries</span>',
            '<span class="section-count">19 entries</span>',
            "brief section count",
        ),
    ]
    for old, new, label in replacements:
        text = exact(text, old, new, label=label)

    # T-01/T-02 leave the active pending inventory; the canonical bodies remain.
    inventory_block = '''  <div class="part-block">\n    <div class="part-label">Part I — Idea Hardening · 2 pending</div>\n    <div class="entry-row"><span class="er-id">T-01</span><span class="er-name">Idea Stress-Test</span><span class="er-why">Part 0 audit: KEEP — six-lens audit. Never drafted in v2 body.</span><span class="er-badge badge-keep">Keep</span></div>\n    <div class="entry-row"><span class="er-id">T-02</span><span class="er-name">Claim Dissection</span><span class="er-why">Part 0 audit: KEEP — empirical/definitional/normative split is distinctive. Never drafted in v2 body.</span><span class="er-badge badge-keep">Keep</span></div>\n  </div>\n\n'''
    text = exact(text, inventory_block, "", label="remove Batch 1 pending inventory")

    # Remove only the T-01/T-02 active drafting briefs. W-01 is the next live brief.
    text = regex_once(
        text,
        r'\n  <!-- T-01 -->\n  <div class="brief" id="b-t01">.*?\n  <!-- W-01 -->',
        '\n  <!-- W-01 -->',
        label="remove T-01/T-02 drafting briefs",
        flags=re.DOTALL,
    )

    # Batch 1 is no longer in the active drafting queue; preserve its prompt below as provenance.
    batch1_row = '<tr><td class="batch-num">1</td><td class="batch-entries">T-01, T-02</td><td class="batch-size">2</td><td class="batch-rationale">Part I openers. Set the entry standard. Both have KEEP verdicts and are the first two entries a reader encounters. Must be right.</td></tr>\n'
    text = exact(text, batch1_row, "", label="remove completed Batch 1 from active batch table")

    old_order = (
        "    Drafting proceeds part-by-part, openers first. Part I and Part II openers establish the entry-level voice and quality bar before completing weaker sections. "
        "Part V security entries come before Part VI to keep the book's hardest entries out of the final pass, where fatigue risk is highest. SEC-06 drafts alone. "
        "Part VI completes last because it carries the highest generic-prompt risk — the book's voice must be fully set before attempting entries that are intrinsically closest to commodity territory."
    )
    new_order = (
        "    Batch 1 Part I openers are complete. Remaining drafting proceeds part-by-part beginning with Batch 2 / Part II, using the adjudicated T-01 and T-02 bodies as the entry-level quality bar. "
        "Part V security entries come before Part VI to keep the book's hardest entries out of the final pass, where fatigue risk is highest. SEC-06 drafts alone. "
        "Part VI completes last because it carries the highest generic-prompt risk — the book's voice must be fully set before attempting entries that are intrinsically closest to commodity territory."
    )
    text = exact(text, old_order, new_order, label="remaining drafting-order paragraph")

    table_marker = '  <table class="batch-table">'
    completed_callout = (
        '  <div class="callout" style="margin-bottom:16px;border-left-color:var(--green);">\n'
        '    <strong>Batch 1 completed 2026-08-24:</strong> T-01 and T-02 passed bounded disposition and were promoted from pending to drafted state. '
        'The table below contains the nine remaining production batches; the original Batch 1 drafting prompt is preserved in Section 6 as historical provenance.\n'
        '  </div>\n\n'
        '  <table class="batch-table">'
    )
    text = exact(text, table_marker, completed_callout, label="completed Batch 1 order callout")

    text = exact(
        text,
        '<h2 class="section-title">Batch 1 Drafting Prompt — T-01 and T-02</h2>',
        '<h2 class="section-title">Batch 1 Drafting Prompt — Completed Historical Provenance</h2>',
        label="historical Batch 1 heading",
    )
    text = exact(
        text,
        '<span class="section-count">2 entries · Part I openers</span>',
        '<span class="section-count">Completed · T-01 and T-02 promoted</span>',
        label="historical Batch 1 count label",
    )
    text = exact(
        text,
        "    Use this prompt in a fresh session with GNOME_Prompt_Field_Manual_v3_final.docx uploaded. Do not modify existing entries. Do not insert into the DOCX during drafting — review first, insert in a separate session after quality gate passes.",
        "    This original Batch 1 drafting prompt is preserved verbatim as historical provenance. T-01 and T-02 have completed disposition and are no longer pending; do not execute the block below as a current drafting instruction.",
        label="historical Batch 1 warning",
    )

    # T-01 page 010: make Lens 6 an independent attack rather than the dependent synthesis.
    def page010(page: str) -> str:
        page = exact(
            page,
            "lens 6 — weakest link lens given the five lenses above, identify the single point at which this idea is most likely to break. state it as: “this idea fails if [specific condition].” why this link and not others?",
            "lens 6 — constraint lens what hard real-world constraint can make this idea fail even if its assumptions are true and participants cooperate? test time, budget, capability, regulation, external dependencies, and coordination limits. which constraint binds first, and what evidence would show that it is actually binding?",
            label="T-01 metadata Lens 6",
        )
        page = regex_once(
            page,
            r'LENS 6 — WEAKEST LINK LENS Given the five lenses above, identify the\s+single point at which this idea is most likely to break\. State it\s+as: “This idea fails if \[specific condition\]\."? Why this link and not\s+others\?',
            "LENS 6 — CONSTRAINT LENS What hard real-world constraint can make this\n\n   idea fail even if its assumptions are true and participants cooperate?\n\n   Test time, budget, capability, regulation, external dependencies, and\n\n   coordination limits. Which constraint binds first, and what evidence\n\n   would show that it is actually binding?",
            label="T-01 visible Lens 6",
        )
        return page

    text = mutate_page(text, "manual-page-010", page010)

    # T-01 page 011: weakest-link synthesis is post-pass and chooses highest severity.
    def page011(page: str) -> str:
        page = exact(
            page,
            "weakest link: [state it as a falsifiable condition]",
            "weakest link: [select the highest-severity finding from the six lenses and state it as a falsifiable condition]",
            label="T-01 metadata weakest-link selection",
        )
        page = exact(
            page,
            "WEAKEST LINK: [State it as a falsifiable condition]",
            "WEAKEST LINK: [Select the highest-severity finding from the six lenses and state it as a falsifiable condition]",
            label="T-01 visible weakest-link selection",
        )
        page = exact(
            page,
            "stress verdict: proceed / revise / abandon idea to stress-test: [idea]",
            "stress verdict: proceed / revise / abandon verdict justification: [one sentence tying the verdict to the weakest link and evidence above] idea to stress-test: [idea]",
            label="T-01 metadata verdict justification",
        )
        page = exact(
            page,
            "STRESS VERDICT: PROCEED / REVISE / ABANDON",
            "STRESS VERDICT: PROCEED / REVISE / ABANDON\n\n   VERDICT JUSTIFICATION: [One sentence tying the verdict to the weakest link and evidence above]",
            label="T-01 visible verdict justification",
        )
        page = exact(
            page,
            "and a single verdict. the verdict is not a summary",
            "and a verdict with one-sentence justification. the verdict is not a summary",
            label="T-01 metadata expected-output verdict",
        )
        page = regex_once(
            page,
            r'and a single verdict\.\s+The\s+verdict is not a summary',
            "and a verdict with one-sentence justification. The\nverdict is not a summary",
            label="T-01 visible expected-output verdict",
        )
        page = exact(
            page,
            "add “run lens 6 twice: once before reading the other lenses, once after” to check whether the weakest link shifts under scrutiny.",
            "add “run the weakest-link selection twice: once before reading recommended actions, once after” to check whether remediation changes which highest-severity finding dominates.",
            label="T-01 metadata stale Lens 6 knob",
        )
        page = regex_once(
            page,
            r'Add “run Lens 6 twice: once before reading the other lenses, once after”\s+to check whether the weakest link shifts under scrutiny\.',
            "Add “run the weakest-link selection twice: once before reading recommended\nactions, once after” to check whether remediation changes which highest-\nseverity finding dominates.",
            label="T-01 visible stale Lens 6 knob",
        )
        return page

    text = mutate_page(text, "manual-page-011", page011)

    # T-01 page 012: repair stale Lens 6 reference and add required T-02 handoff.
    def page012(page: str) -> str:
        page = exact(
            page,
            "weakest link identified in lens 6",
            "highest-severity weakest link selected after the six-lens pass",
            label="T-01 metadata follow-up weakest-link source",
        )
        page = exact(
            page,
            "weakest link identified\nin Lens 6",
            "highest-severity weakest link selected\nafter the six-lens pass",
            label="T-01 visible follow-up weakest-link source",
        )
        page = exact(
            page,
            "→if the verdict is revise, run t-01 again on the revised idea.",
            "→if the stress-test isolates a specific claim that needs structural analysis, run t-02 (claim dissection) on that claim. →if the verdict is revise, run t-01 again on the revised idea.",
            label="T-01 metadata T-02 follow-up",
        )
        page = exact(
            page,
            "→If the verdict is REVISE, run\nT-01 again on the revised idea.",
            "→If the stress-test isolates a specific claim that needs structural analysis,\nrun T-02 (Claim Dissection) on that claim. →If the verdict is REVISE, run\nT-01 again on the revised idea.",
            label="T-01 visible T-02 follow-up",
        )
        return page

    text = mutate_page(text, "manual-page-012", page012)

    # T-02 page 014: rationale is an explicit output field and verdict token is singular.
    def page014(page: str) -> str:
        page = exact(
            page,
            "what is the selection mechanism that would allow cherry-picking here?",
            "what is the selection mechanism that would allow cherry-picking here? rationale: [one sentence explaining the rating and tying it to the selection mechanism above.]",
            label="T-02 metadata cherry-pick rationale",
        )
        page = exact(
            page,
            "What is the selection mechanism that would allow cherry-picking here?",
            "What is the selection mechanism that would allow cherry-picking here?\n\n   RATIONALE: [One sentence explaining the rating and tying it to the selection mechanism above.]",
            label="T-02 visible cherry-pick rationale",
        )
        for old, new, label in [
            ("DISSECTION VERDICT: DEFENSIBLE / PARTIALLY DEFENSIBLE / COLLAPSES", "DISSECTION VERDICT: DEFENSIBLE / PARTIALLY DEFENSIBLE / COLLAPSE", "visible verdict enum"),
            ("dissection verdict: defensible / partially defensible / collapses", "dissection verdict: defensible / partially defensible / collapse", "metadata verdict enum"),
            ("COLLAPSES: The claim relies", "COLLAPSE: The claim relies", "visible verdict definition"),
            ("collapses: the claim relies", "collapse: the claim relies", "metadata verdict definition"),
        ]:
            page = exact(page, old, new, label=f"T-02 {label}")
        return page

    text = mutate_page(text, "manual-page-014", page014)

    # T-02 page 015: the artifact has eight items, not seven, and rationale is part of output.
    def page015(page: str) -> str:
        page = exact(
            page,
            "a structured seven-section claim dissection:",
            "a structured eight-item claim dissection:",
            label="T-02 metadata artifact cardinality",
        )
        page = exact(
            page,
            "A structured seven-section claim dissection:",
            "A structured eight-item claim dissection:",
            label="T-02 visible artifact cardinality",
        )
        page = exact(
            page,
            "cherry-pick risk rating, minimum evidence requirement",
            "cherry-pick risk rating with one-sentence rationale, minimum evidence requirement",
            label="T-02 metadata expected-output rationale",
        )
        page = regex_once(
            page,
            r'cherry-pick risk rating,\s+minimum evidence\s+requirement',
            "cherry-pick risk rating with one-sentence rationale, minimum evidence\nrequirement",
            label="T-02 visible expected-output rationale",
        )
        return page

    text = mutate_page(text, "manual-page-015", page015)

    # T-02 page 016: keep the frozen singular verdict token everywhere it is referenced.
    def page016(page: str) -> str:
        for old, new, label in [
            ("issue a COLLAPSES verdict", "issue a COLLAPSE verdict", "visible failure-mode verdict"),
            ("issue a collapses verdict", "issue a collapse verdict", "metadata failure-mode verdict"),
            ("PARTIALLY DEFENSIBLE or COLLAPSES", "PARTIALLY DEFENSIBLE or COLLAPSE", "visible follow-up verdict"),
            ("partially defensible or collapses", "partially defensible or collapse", "metadata follow-up verdict"),
        ]:
            page = exact(page, old, new, label=f"T-02 {label}")
        return page

    text = mutate_page(text, "manual-page-016", page016)

    INDEX.write_text(text, encoding="utf-8")
    return pre_hash, sha256(INDEX)


def patch_file(path: str, replacements: list[tuple[str, str, str]]) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    for old, new, label in replacements:
        text = exact(text, old, new, label=f"{path}: {label}")
    target.write_text(text, encoding="utf-8")


def patch_current_state_files() -> None:
    patch_file(
        "README.md",
        [
            ("21 pending IDs, 70 embedded non-pending IDs, and 91 semantic manual entries", "19 pending IDs, 72 embedded non-pending IDs, and 91 semantic manual entries", "current counts"),
            ("deterministic 21/70/91 entry-lineage reconciler", "deterministic 19/72/91 entry-lineage reconciler", "reconciler description"),
            ("--expect-pending 21", "--expect-pending 19", "validation pending expectation"),
            ("--expect-drafted 70", "--expect-drafted 72", "validation drafted expectation"),
            ("structure, 21/70/91 inventory arithmetic", "structure, 19/72/91 inventory arithmetic", "validation interpretation"),
            ("- issue #3\n", "- issue #1 — umbrella stable-release closeout\n- [`docs/BATCH1_DISPOSITION_2026-08-24.md`](docs/BATCH1_DISPOSITION_2026-08-24.md) — SHA-bound Batch 1 disposition record\n", "authoritative records"),
            ("- `docs/FIELD_JOURNAL_IDENTIFIER_DECISION_2026-08-12.md` — evidence-backed disposition of the cut Field Journal predecessor and page-213 correction.\n", "- `docs/FIELD_JOURNAL_IDENTIFIER_DECISION_2026-08-12.md` — evidence-backed disposition of the cut Field Journal predecessor and page-213 correction.\n- `docs/BATCH1_DISPOSITION_2026-08-24.md` — adjudication record for T-01/T-02 promotion from pending to drafted.\n", "repository structure record"),
            ("Stable release remains blocked by the remaining pending-entry disposition, accessibility/browser review, and final release evidence.", "Stable release remains blocked by disposition of the 19 remaining pending entries, final regression browser/accessibility review after content closeout, independent or equivalent editorial review, and final release evidence.", "release policy"),
        ],
    )

    patch_file(
        "docs/IDENTITY_AND_SCOPE.md",
        [
            ("- 21 pending inventory IDs;", "- 19 pending inventory IDs;", "pending IDs"),
            ("- 21 matching drafting briefs;", "- 19 matching drafting briefs;", "brief IDs"),
            ("- 70 embedded non-pending entry IDs;", "- 72 embedded non-pending entry IDs;", "drafted IDs"),
            ("- 10 production batches;", "- 9 remaining production batches;", "remaining batches"),
            (
                "Issue #3 continues to track:\n\n- editorial disposition of remaining pending entries;\n- accessibility and browser validation;\n- stable-release versioning and publication evidence.",
                "Issue #1 is the umbrella stable-release closeout. Batch 1 disposition promoted T-01 and T-02 on 2026-08-24; 19 pending entries remain.\n\nRemaining blockers:\n\n- editorial disposition of the 19 remaining pending entries;\n- regression browser/accessibility validation after the final content mutation;\n- stable-release versioning, independent or documented-equivalent editorial review, and publication evidence.",
                "remaining release blockers",
            ),
        ],
    )

    changelog = ROOT / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    text = exact(
        text,
        "### Corrected\n\n",
        "### Corrected\n\n- Adjudicated T-01 Idea Stress-Test and T-02 Claim Dissection against their frozen Batch 1 briefs without drafting replacement bodies.\n- Replaced T-01's dependent weakest-link Lens 6 with an independent Constraint Lens; weakest-link synthesis now occurs after all six lenses and explicitly selects the highest-severity finding.\n- Added T-01's missing T-02 follow-up and one-sentence STRESS VERDICT justification requirement.\n- Normalized T-02's verdict token to `COLLAPSE`, added the required one-sentence CHERRY-PICK RISK rationale, and corrected the expected artifact from seven sections to eight items.\n\n",
        label="CHANGELOG Batch 1 corrected section",
    )
    text = exact(
        text,
        "### Changed\n\n",
        "### Changed\n\n- Promoted T-01 and T-02 from pending to drafted after bounded disposition; current state is 19 pending / 72 drafted / 91 semantic entries / 315 pages / 9 remaining batches.\n- Removed T-01/T-02 from active pending inventory and drafting briefs while preserving the original Batch 1 drafting prompt as explicitly completed historical provenance.\n- Added a fail-closed Batch 1 disposition regression gate and SHA-bound audit record.\n\n",
        label="CHANGELOG Batch 1 changed section",
    )
    changelog.write_text(text, encoding="utf-8")

    patch_file(
        ".github/workflows/entry-lineage.yml",
        [
            ("--expect-pending 21", "--expect-pending 19", "pending expectation"),
            ("--expect-drafted 70", "--expect-drafted 72", "drafted expectation"),
        ],
    )

    tests = ROOT / "tests/test_reconcile_entry_lineage.py"
    text = tests.read_text(encoding="utf-8")
    text = exact(
        text,
        "def test_repository_post_state_reconciles_to_21_70_91(self) -> None:",
        "def test_repository_post_state_reconciles_to_19_72_91(self) -> None:",
        label="reconcile test name",
    )
    text = exact(text, "expected_pending=21,", "expected_pending=19,", label="reconcile expected pending")
    text = exact(text, "expected_drafted=70,", "expected_drafted=72,", label="reconcile expected drafted")
    text = exact(
        text,
        "self.assertEqual(result.summary.pending_present_in_embedded, 21)",
        "self.assertEqual(result.summary.pending_present_in_embedded, 19)",
        label="reconcile pending-present assertion",
    )
    tests.write_text(text, encoding="utf-8")


def write_regression_test() -> None:
    target = ROOT / "tests/test_batch1_disposition.py"
    if target.exists():
        raise SystemExit("tests/test_batch1_disposition.py already exists")
    target.write_text(
        '''from __future__ import annotations\n\nimport html\nimport re\nimport unittest\nfrom pathlib import Path\n\nfrom tools.reconcile_entry_lineage import reconcile, validate_expectations\n\nROOT = Path(__file__).resolve().parents[1]\nINDEX = ROOT / "index.html"\nFIELDS = (\n    "WHAT IT DOES",\n    "WHY IT WORKS",\n    "THE PROMPT",\n    "INPUTS NEEDED",\n    "EXPECTED OUTPUT",\n    "KNOBS",\n    "FAILURE MODE",\n    "FOLLOW-UP",\n    "SAFETY NOTES",\n)\n\n\ndef page(page_no: int) -> str:\n    source = INDEX.read_text(encoding="utf-8")\n    page_id = f"manual-page-{page_no:03d}"\n    match = re.search(\n        rf'<article class="manual-page-card" id="{page_id}"[^>]*>.*?</article>',\n        source,\n        re.DOTALL,\n    )\n    if not match:\n        raise AssertionError(f"missing {page_id}")\n    return match.group(0)\n\n\ndef visible_text(fragment: str) -> str:\n    pre = re.search(r"<pre>(.*?)</pre>", fragment, re.DOTALL)\n    if not pre:\n        raise AssertionError("page card missing <pre>")\n    return html.unescape(re.sub(r"<[^>]+>", "", pre.group(1)))\n\n\ndef metadata_text(fragment: str) -> str:\n    match = re.search(r'data-manual-text="([^"]*)"', fragment, re.DOTALL)\n    if not match:\n        raise AssertionError("page card missing data-manual-text")\n    return html.unescape(match.group(1))\n\n\nclass Batch1DispositionTests(unittest.TestCase):\n    def test_t01_t02_promoted_out_of_pending_state(self) -> None:\n        result = reconcile(INDEX)\n        failures = validate_expectations(\n            result,\n            expected_pending=19,\n            expected_drafted=72,\n            expected_total=91,\n            expected_pages=315,\n        )\n        self.assertEqual(failures, [])\n        pending = {item.entry_id for item in result.pending_entries}\n        briefs = {item.entry_id for item in result.briefs}\n        self.assertNotIn("T-01", pending)\n        self.assertNotIn("T-02", pending)\n        self.assertNotIn("T-01", briefs)\n        self.assertNotIn("T-02", briefs)\n\n    def test_exactly_one_canonical_body_for_each_entry(self) -> None:\n        t01 = "\\n".join(visible_text(page(n)) for n in range(9, 13))\n        t02 = "\\n".join(visible_text(page(n)) for n in range(13, 18))\n        self.assertEqual(t01.count("T-01 Idea Stress-Test"), 1)\n        self.assertEqual(t02.count("T-02 Claim Dissection"), 1)\n\n    def test_both_entries_retain_all_nine_fields(self) -> None:\n        t01 = "\\n".join(visible_text(page(n)) for n in range(9, 13))\n        t02 = "\\n".join(visible_text(page(n)) for n in range(13, 18))\n        for field in FIELDS:\n            self.assertIn(field, t01, f"T-01 missing {field}")\n            self.assertIn(field, t02, f"T-02 missing {field}")\n\n    def test_t01_frozen_clauses_and_metadata_parity(self) -> None:\n        p10 = page(10)\n        p11 = page(11)\n        p12 = page(12)\n        visible = "\\n".join(visible_text(x) for x in (p10, p11, p12))\n        metadata = " ".join(metadata_text(x) for x in (p10, p11, p12))\n        self.assertIn("LENS 6 — CONSTRAINT LENS", visible)\n        self.assertIn("highest-severity finding", visible)\n        self.assertIn("VERDICT JUSTIFICATION", visible)\n        self.assertIn("T-02 (Claim Dissection)", visible)\n        self.assertIn("lens 6 — constraint lens", metadata)\n        self.assertIn("highest-severity finding", metadata)\n        self.assertIn("verdict justification", metadata)\n        self.assertIn("t-02 (claim dissection)", metadata)\n        self.assertNotIn("LENS 6 — WEAKEST LINK LENS", visible)\n\n    def test_t02_frozen_clauses_and_metadata_parity(self) -> None:\n        cards = [page(n) for n in range(13, 18)]\n        visible = "\\n".join(visible_text(x) for x in cards)\n        metadata = " ".join(metadata_text(x) for x in cards)\n        self.assertIn("DISSECTION VERDICT: DEFENSIBLE / PARTIALLY DEFENSIBLE / COLLAPSE", visible)\n        self.assertIn("RATIONALE: [One sentence explaining the rating", visible)\n        self.assertIn("eight-item claim dissection", visible)\n        self.assertNotIn("COLLAPSES", visible)\n        self.assertIn("dissection verdict: defensible / partially defensible / collapse", metadata)\n        self.assertIn("rationale: [one sentence explaining the rating", metadata)\n        self.assertIn("eight-item claim dissection", metadata)\n        self.assertNotIn("collapses", metadata)\n\n    def test_batch1_prompt_is_historical_not_active(self) -> None:\n        source = INDEX.read_text(encoding="utf-8")\n        self.assertIn("Batch 1 Drafting Prompt — Completed Historical Provenance", source)\n        self.assertIn("do not execute the block below as a current drafting instruction", source)\n        self.assertNotIn('<td class="batch-entries">T-01, T-02</td>', source)\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
        encoding="utf-8",
    )


def write_audit_record(pre_hash: str, post_hash: str) -> None:
    target = ROOT / "docs/BATCH1_DISPOSITION_2026-08-24.md"
    if target.exists():
        raise SystemExit("Batch 1 audit record already exists")
    target.write_text(
        f'''# Batch 1 Disposition Record — 2026-08-24\n\n## Scope\n\nBounded editorial disposition of the existing canonical bodies for `T-01 Idea Stress-Test` and `T-02 Claim Dissection` under issue #10. No replacement entry was drafted, no historical PDF was modified, and dated provenance baselines remain unchanged.\n\n## Artifact binding\n\n- Base commit: `{BASE_COMMIT}`\n- Pre-mutation `index.html` SHA-256: `{pre_hash}`\n- Post-mutation `index.html` SHA-256: `{post_hash}`\n- Pre-state: 21 pending / 70 drafted / 91 semantic entries / 315 pages / 10 batches\n- Post-state: 19 pending / 72 drafted / 91 semantic entries / 315 pages / 9 remaining batches\n\n## Frozen disposition matrix\n\n| Entry | Frozen classification | Demonstrated gap | Disposition |\n|---|---|---|---|\n| T-01 | PARTIAL | Lens 6 was dependent weakest-link synthesis | Replaced only Lens 6 with an independent Constraint Lens; weakest-link synthesis remains after the six-lens pass |\n| T-01 | PARTIAL | FOLLOW-UP omitted T-02 | Added a conditional T-02 Claim Dissection handoff for isolated claims |\n| T-01 | PARTIAL | Weakest-link choice did not explicitly select highest severity | Post-pass WEAKEST LINK now selects the highest-severity finding from the six lenses |\n| T-01 | PARTIAL | STRESS VERDICT lacked required one-sentence justification | Added explicit VERDICT JUSTIFICATION field and expected-output requirement |\n| T-02 | PARTIAL | Verdict token used `COLLAPSES` | Canonical T-02 body now uses frozen singular token `COLLAPSE` consistently |\n| T-02 | PARTIAL | CHERRY-PICK RISK lacked explicit one-sentence rationale | Added mandatory RATIONALE field and propagated it into expected output |\n| T-02 | PARTIAL | EXPECTED OUTPUT called an eight-item artifact “seven-section” | Corrected to “eight-item claim dissection” |\n\n## Production-state disposition\n\n- T-01 and T-02 were removed from the active pending inventory and per-entry drafting briefs.\n- The original Batch 1 drafting prompt remains byte-for-byte intact inside its prompt block and is explicitly labelled completed historical provenance.\n- Batch 1 was removed from the active drafting-order table; original batch numbering 2–10 is preserved for lineage rather than renumbered.\n- Current-state README, identity/scope, changelog, lineage CI expectations, and reconciliation tests were updated to 19/72/91.\n\n## Fail-closed regression gate\n\n`tests/test_batch1_disposition.py` proves that:\n\n- T-01/T-02 are absent from active pending inventory and drafting briefs;\n- each entry retains exactly one canonical full body;\n- both bodies retain all nine manuscript fields;\n- the frozen mandatory T-01/T-02 clauses are present in visible text and mirrored `data-manual-text`;\n- stale `COLLAPSES` and dependent “Lens 6 — Weakest Link Lens” semantics cannot silently return;\n- the Batch 1 prompt is historical provenance rather than an active instruction.\n\n## Verification policy\n\nThe one-shot migration workflow commits this record only if the complete Python unit suite, strict structural validator, 19/72/91 lineage reconciliation, frozen editorial-lineage classifier check, and editorial-lineage audit all pass. Pull-request CI then supplies the repository browser matrix before merge.\n''',
        encoding="utf-8",
    )


def main() -> None:
    pre_hash, post_hash = patch_index()
    patch_current_state_files()
    write_regression_test()
    write_audit_record(pre_hash, post_hash)
    print(f"Batch 1 migration staged: {pre_hash} -> {post_hash}")


if __name__ == "__main__":
    main()
