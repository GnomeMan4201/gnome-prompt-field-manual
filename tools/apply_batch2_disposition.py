from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
AUDIT = ROOT / "docs" / "BATCH2_DISPOSITION_2026-08-24.md"
EXPECTED_PRE_SHA256 = "92d4e6c395c620bb9eb08a6df798ff1d1685b7c091a5ffd910e8fd996d9c9559"
BASE_COMMIT = "8591c9f7ed4dbdeb5ed83de96e33c4dfbfedc324"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return result


raw = INDEX.read_bytes()
pre_sha = sha256(raw)
if pre_sha != EXPECTED_PRE_SHA256:
    raise SystemExit(f"index hash mismatch: expected {EXPECTED_PRE_SHA256}, got {pre_sha}")

text = raw.decode("utf-8")

# Current production-state metadata.
text = replace_once(text, "19 pending entries · 9 remaining batches · drafting authority", "16 pending entries · 8 remaining batches · drafting authority", "header pending/batch count")
text = replace_once(text, "Production state: 72 drafted · 0 restore · 19 pending", "Production state: 75 drafted · 0 restore · 16 pending", "header production state")
text = replace_once(text, '<div class="stat"><div class="stat-num sn-pending">19</div><div class="stat-label">Pending Entries</div></div>', '<div class="stat"><div class="stat-num sn-pending">16</div><div class="stat-label">Pending Entries</div></div>', "pending stat")
text = replace_once(text, '<div class="stat"><div class="stat-num sn-drafted">72</div><div class="stat-label">Drafted</div></div>', '<div class="stat"><div class="stat-num sn-drafted">75</div><div class="stat-label">Drafted</div></div>', "drafted stat")
text = replace_once(text, '<div class="stat"><div class="stat-num sn-batch">9</div><div class="stat-label">Remaining Batches</div></div>', '<div class="stat"><div class="stat-num sn-batch">8</div><div class="stat-label">Remaining Batches</div></div>', "batch stat")
text = replace_once(text, '<span class="section-count">19 entries · 5 parts</span>', '<span class="section-count">16 entries · 4 parts</span>', "pending inventory count")
text = replace_once(text, '<span class="section-count">19 entries</span>', '<span class="section-count">16 entries</span>', "brief count")

# Remove Batch 2 entries from the pending inventory only.
text = regex_replace_once(
    text,
    r'\n  <div class="part-block">\n    <div class="part-label">Part II — Dense-to-Clear · 3 pending</div>.*?\n  </div>\n\n  <div class="part-block">\n    <div class="part-label">Part III — Raw Work to Evidence · 2 pending</div>',
    '\n  <div class="part-block">\n    <div class="part-label">Part III — Raw Work to Evidence · 2 pending</div>',
    "Part II pending inventory block",
)

# Remove W-01/W-02/W-03 active drafting briefs, preserving R-01 onward.
text = regex_replace_once(
    text,
    r'\n  <!-- W-01 -->.*?(?=\n  <!-- R-01 -->)',
    '',
    "Batch 2 drafting briefs",
)

# Remove Batch 2 from remaining-batch table; retain historical numbering 3-10.
text = regex_replace_once(
    text,
    r'\n\s*<tr><td class="batch-num">2</td><td class="batch-entries">W-01, W-02, W-03</td><td class="batch-size">3</td><td class="batch-rationale">Part II completion\. Completes the part with the most daily-use prompts\. W-01 carries the highest generic risk — draft first, review hardest\.</td></tr>',
    '',
    "Batch 2 table row",
)

# Current drafting-order prose and completion callout.
text = replace_once(
    text,
    "Batch 1 Part I openers are complete. Remaining drafting proceeds part-by-part beginning with Batch 2 / Part II, using the adjudicated T-01 and T-02 bodies as the entry-level quality bar.",
    "Batches 1 and 2 are complete. Remaining drafting proceeds part-by-part beginning with Batch 3 / Part III, using the adjudicated Part I and Part II bodies as the entry-level quality bar.",
    "drafting order prose",
)
text = replace_once(
    text,
    '<strong>Batch 1 completed 2026-08-24:</strong> T-01 and T-02 passed bounded disposition and were promoted from pending to drafted state. The table below contains the nine remaining production batches; the original Batch 1 drafting prompt is preserved in Section 6 as historical provenance.',
    '<strong>Batches 1 and 2 completed 2026-08-24:</strong> T-01/T-02 and W-01/W-02/W-03 passed bounded disposition and were promoted from pending to drafted state. The table below contains the eight remaining production batches; the original Batch 1 drafting prompt remains preserved in Section 6 as historical provenance.',
    "batch completion callout",
)

# W-01: frozen brief requires W-11 prerequisite specifically in INPUTS NEEDED.
text = replace_once(
    text,
    "inputs needed any prose document — technical writing, research summaries, reports, internal memos, draft analysis. the denser and more hedge-laden, the more rules will fire.",
    "inputs needed any prose document — technical writing, research summaries, reports, internal memos, draft analysis. if the source may not be summarizable without losing load-bearing content, run w-11 (the anti-summary) first to determine whether rewriting is appropriate. the denser and more hedge-laden, the more rules will fire.",
    "W-01 metadata INPUTS prerequisite",
)
text = replace_once(
    text,
    "Any prose document — technical writing, research summaries,\nreports, internal memos, draft analysis. The denser and more\nhedge-laden, the more rules will fire.",
    "Any prose document — technical writing, research summaries,\nreports, internal memos, draft analysis. If the source may not be summarizable without losing load-bearing content,\nrun W-11 (The Anti-Summary) first to determine whether rewriting is appropriate. The denser and more\nhedge-laden, the more rules will fire.",
    "W-01 visible INPUTS prerequisite",
)

# W-03: frozen brief requires a minimum of three specific objections.
text = replace_once(
    text,
    "specific objections a numbered list of distinct objections this persona raises. each objection must:",
    "specific objections a numbered list of at least three distinct objections this persona raises. each objection must:",
    "W-03 metadata minimum objections",
)
text = replace_once(
    text,
    "SPECIFIC OBJECTIONS A numbered list of distinct objections this\npersona raises. Each objection must:",
    "SPECIFIC OBJECTIONS A numbered list of at least three distinct objections this\npersona raises. Each objection must:",
    "W-03 visible minimum objections",
)

# Removed W-01/W-02 briefs must no longer be startup targets.
text = replace_once(text, "document.getElementById('b-w01').classList.add('open');", "document.getElementById('b-r01').classList.add('open');", "first default brief")
text = replace_once(text, "document.getElementById('b-w02').classList.add('open');", "document.getElementById('b-r03').classList.add('open');", "second default brief")

# Fail closed on forbidden leftovers / unintended duplication.
for forbidden in (
    '<td class="batch-entries">W-01, W-02, W-03</td>',
    'id="b-w01"',
    'id="b-w02"',
    'id="b-w03"',
    "document.getElementById('b-w01').classList.add('open');",
    "document.getElementById('b-w02').classList.add('open');",
):
    if forbidden in text:
        raise SystemExit(f"forbidden Batch 2 pending residue remains: {forbidden}")

if text.count("W-01 Dense-to-Clear (Rule-Based)") != 1:
    raise SystemExit("W-01 canonical visible body count is not exactly one")
if text.count("W-02 Argument Skeleton Extractor") != 1:
    raise SystemExit("W-02 canonical visible body count is not exactly one")
if text.count("W-03 Adversarial Reader (Persona-Specific)") != 1:
    raise SystemExit("W-03 canonical visible body count is not exactly one")

INDEX.write_text(text, encoding="utf-8", newline="")
post_sha = sha256(INDEX.read_bytes())

audit = f"""# Batch 2 Disposition Record — 2026-08-24

Bounded editorial disposition of the existing canonical bodies for `W-01 Dense-to-Clear (Rule-Based)`, `W-02 Argument Skeleton Extractor`, and `W-03 Adversarial Reader (Persona-Specific)`.

## Artifact binding

- Base commit: `{BASE_COMMIT}`
- Pre-mutation `index.html` SHA-256: `{EXPECTED_PRE_SHA256}`
- Post-mutation `index.html` SHA-256: `{post_sha}`
- Pre-state: 19 pending / 72 drafted / 91 semantic entries / 315 pages / 9 remaining batches
- Post-state: 16 pending / 75 drafted / 91 semantic entries / 315 pages / 8 remaining batches
- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`

## Frozen audit matrix

| Entry | Frozen classification | Demonstrated gap | Disposition |
|---|---|---|---|
| W-01 | PARTIAL | `INPUTS NEEDED` omitted the frozen W-11 prerequisite for source material that may not be safely summarizable. | Added only that prerequisite in visible text and mirrored search metadata. Existing numbered rules, per-change rule log, W-04 follow-up, and other prose remain authoritative. |
| W-02 | PASS | None demonstrated. | No manuscript content rewrite. Promoted from pending based on existing body satisfying the frozen brief. |
| W-03 | PARTIAL | `SPECIFIC OBJECTIONS` did not explicitly require the frozen minimum of three. | Added only the minimum-three requirement in visible text and mirrored search metadata. Existing persona constraints, avoidance analysis, confidence-laundering checks, verdict, and routing remain authoritative. |

## Production-state actions

- Removed W-01/W-02/W-03 from the active pending inventory and per-entry drafting briefs.
- Removed Batch 2 from the remaining production-batch table without renumbering historical batches 3-10.
- Updated current state to 16 pending / 75 drafted / 91 total / 315 pages / 8 remaining batches.
- Retargeted default-open drafting briefs from removed W-01/W-02 to the first two remaining briefs, R-01/R-03, preventing startup abort on missing elements.
- Preserved the historical PDF and dated historical baseline records unchanged.

## Verification contract

The Batch 2 change is acceptable only if the repository's complete Python suite, strict structural validator, 16/75/91 lineage reconciliation, frozen editorial-classifier comparison, editorial-lineage audit, `git diff --check`, and Chromium/Firefox/WebKit reader smoke all pass on the exact cleaned PR head, followed by human review of the final `index.html` patch.
"""
AUDIT.write_text(audit, encoding="utf-8")

print(f"Batch 2 disposition staged: {pre_sha} -> {post_sha}")
