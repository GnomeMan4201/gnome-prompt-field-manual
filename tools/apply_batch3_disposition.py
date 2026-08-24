from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EXPECTED_PRE_SHA = "e0d88f80a6f14e90732a7f0765794ffe348bf526aaa3225fe3b87c8acb073bac"
BASE_COMMIT = "5893ce77993e7362b276e4b486733a6ec220286a"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    out, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return out


def edit_page(source: str, page_no: int, fn) -> str:
    pid = f"manual-page-{page_no:03d}"
    pattern = rf'(<article class="manual-page-card" id="{pid}"[^>]*>.*?</article>)'
    match = re.search(pattern, source, re.S)
    if not match:
        raise SystemExit(f"missing {pid}")
    old = match.group(1)
    new = fn(old)
    if new == old:
        raise SystemExit(f"{pid}: edit produced no change")
    return source[:match.start(1)] + new + source[match.end(1):]

if sha256(INDEX) != EXPECTED_PRE_SHA:
    raise SystemExit(f"index hash mismatch: expected {EXPECTED_PRE_SHA}, got {sha256(INDEX)}")

text = INDEX.read_text(encoding="utf-8")

# Production-state surfaces.
text = once(text, "16 pending entries · 8 remaining batches · drafting authority", "14 pending entries · 7 remaining batches · drafting authority", "header state")
text = once(text, "Production state: 75 drafted · 0 restore · 16 pending", "Production state: 77 drafted · 0 restore · 14 pending", "production state")
text = once(text, '<div class="stat"><div class="stat-num sn-pending">16</div><div class="stat-label">Pending Entries</div></div>', '<div class="stat"><div class="stat-num sn-pending">14</div><div class="stat-label">Pending Entries</div></div>', "pending stat")
text = once(text, '<div class="stat"><div class="stat-num sn-drafted">75</div><div class="stat-label">Drafted</div></div>', '<div class="stat"><div class="stat-num sn-drafted">77</div><div class="stat-label">Drafted</div></div>', "drafted stat")
text = once(text, '<div class="stat"><div class="stat-num sn-batch">8</div><div class="stat-label">Remaining Batches</div></div>', '<div class="stat"><div class="stat-num sn-batch">7</div><div class="stat-label">Remaining Batches</div></div>', "batch stat")
text = once(text, '<span class="section-count">16 entries · 4 parts</span>', '<span class="section-count">14 entries · 3 parts</span>', "pending section count")
text = once(text, '<span class="section-count">16 entries</span>', '<span class="section-count">14 entries</span>', "brief count")

# Remove Part III pending inventory only.
text = regex_once(text, r'\n  <div class="part-block">\n    <div class="part-label">Part III — Raw Work to Evidence · 2 pending</div>.*?(?=\n  <div class="part-block">\n    <div class="part-label">Part IV)', '', "Part III inventory")
# Remove R-01/R-03 briefs only.
text = regex_once(text, r'\n  <!-- R-01 -->.*?(?=\n  <!-- S-01 -->)', '', "Batch 3 briefs")
# Remove Batch 3 row, preserve numbering 4-10.
text = regex_once(text, r'\n\s*<tr><td class="batch-num">3</td><td class="batch-entries">R-01, R-03</td>.*?</tr>', '', "Batch 3 row")

text = once(text,
    "Batches 1 and 2 are complete. Remaining drafting proceeds part-by-part beginning with Batch 3 / Part III, using the adjudicated Part I and Part II bodies as the entry-level quality bar.",
    "Batches 1 through 3 are complete. Remaining drafting proceeds part-by-part beginning with Batch 4 / Part IV, using the adjudicated Parts I through III as the entry-level quality bar.",
    "drafting order prose")
text = once(text,
    '<strong>Batches 1 and 2 completed 2026-08-24:</strong> T-01/T-02 and W-01/W-02/W-03 passed bounded disposition and were promoted from pending to drafted state. The table below contains the eight remaining production batches; the original Batch 1 drafting prompt remains preserved in Section 6 as historical provenance.',
    '<strong>Batches 1 through 3 completed 2026-08-24:</strong> T-01/T-02, W-01/W-02/W-03, and R-01/R-03 passed bounded disposition and were promoted from pending to drafted state. The table below contains the seven remaining production batches; the original Batch 1 drafting prompt remains preserved in Section 6 as historical provenance.',
    "completion callout")

# R-01 page 073: add cross-source institutional interest map while preserving per-source disclosure.
def r01_p73(card: str) -> str:
    card = once(card, "none identified] contested zones", "none identified] institutional interest map aggregate the source-level disclosures above by conclusion or outcome. for each identified interest: conclusion / outcome: [the conclusion or outcome an institution has a stake in] sources with an identified stake: [named sources] nature of interest: [funding / regulatory / commercial / organizational / other] evidentiary implication: [what must be disclosed or independently verified; interest alone is not evidence the source is wrong] if none are identified, state: none identified. contested zones", "R01 metadata institutional map")
    marker = "explicitly, or state: NONE IDENTIFIED]\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━CONTESTED ZONES"
    replacement = "explicitly, or state: NONE IDENTIFIED]\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━INSTITUTIONAL INTEREST MAP\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nAggregate the source-level disclosures above by conclusion or outcome.\n\nFor each identified interest: CONCLUSION / OUTCOME: [The conclusion or\n\noutcome an institution has a stake in] SOURCES WITH AN IDENTIFIED\n\nSTAKE: [Named sources] NATURE OF INTEREST: [Funding / regulatory /\n\ncommercial / organizational / other] EVIDENTIARY IMPLICATION: [What\n\nmust be disclosed or independently verified; interest alone is not\n\nevidence the source is wrong]\n\nIf none are identified, state: NONE IDENTIFIED.\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━CONTESTED ZONES"
    return once(card, marker, replacement, "R01 visible institutional map")
text = edit_page(text, 73, r01_p73)

# R-01 page 074: expected artifact is now six components and names the map.
def r01_p74(card: str) -> str:
    card = once(card, "five components:", "six components:", "R01 metadata component count")
    card = once(card, "institutional position;", "institutional position; institutional interest map aggregating sources by the conclusions or outcomes they have an identified stake in;", "R01 metadata expected map")
    card = once(card, "Five components:", "Six components:", "R01 visible component count")
    card = once(card, "institutional position;", "institutional position; INSTITUTIONAL INTEREST MAP aggregating sources by the conclusions or outcomes they have an identified stake in;", "R01 visible expected map")
    return card
text = edit_page(text, 74, r01_p74)

# R-03 page 083: restore VERY HIGH as a risk level; keep NOT REPLICATION-READY as insufficiency status.
def r03_p83(card: str) -> str:
    meta_marker = "independent replication should be attempted before acting on this result. not replication-ready:"
    meta_repl = "independent replication should be attempted before acting on this result. very high risk: severe or compounding threats across core design and reporting dimensions. the result should not be load-bearing before independent replication. not replication-ready:"
    card = once(card, meta_marker, meta_repl, "R03 metadata very high")
    vis_marker = "Independent replication should be attempted before\n\nacting on this result. NOT REPLICATION-READY:"
    vis_repl = "Independent replication should be attempted before\n\nacting on this result. VERY HIGH RISK: Severe or compounding threats\n\nacross core design and reporting dimensions. The result should not be\n\nload-bearing before independent replication. NOT REPLICATION-READY:"
    return once(card, vis_marker, vis_repl, "R03 visible very high")
text = edit_page(text, 83, r03_p83)

# R-03 page 084: clarify four risk levels plus separate insufficiency status.
def r03_p84(card: str) -> str:
    card = once(card, "one of four levels:", "one of four risk levels:", "R03 metadata taxonomy wording")
    card = once(card, "low risk, moderate risk, high risk, or not replication-ready.", "low risk, moderate risk, high risk, or very high risk. if critical information is missing, report not replication-ready as a separate assessment-status outcome rather than forcing a risk level.", "R03 metadata taxonomy")
    card = once(card, "one of four levels:", "one of four risk levels:", "R03 visible taxonomy wording")
    card = once(card, "LOW\nRISK, MODERATE RISK, HIGH RISK, or NOT REPLICATION-READY.", "LOW\nRISK, MODERATE RISK, HIGH RISK, or VERY HIGH RISK. If critical information is missing, report NOT REPLICATION-READY as a separate assessment-status outcome rather than forcing a risk level.", "R03 visible taxonomy")
    return card
text = edit_page(text, 84, r03_p84)

# R-03 page 085: add frozen R-05 follow-up.
def r03_p85(card: str) -> str:
    meta_marker = "→if a replication attempt proceeds and produces a result"
    meta_insert = "→run r-05 (failure-to-test converter) on the highest-severity replication risks or blockers to convert them into concrete test specifications before attempting replication. " + meta_marker
    card = once(card, meta_marker, meta_insert, "R03 metadata R05 follow-up")
    vis_marker = "→If a replication attempt proceeds\n"
    vis_insert = "→Run R-05 (Failure-to-Test Converter) on the highest-severity replication risks or blockers to convert them into concrete test specifications before attempting replication. " + vis_marker
    return once(card, vis_marker, vis_insert, "R03 visible R05 follow-up")
text = edit_page(text, 85, r03_p85)

# Startup must not dereference removed briefs.
text = once(text, "document.getElementById('b-r01').classList.add('open');", "document.getElementById('b-s01').classList.add('open');", "startup first")
text = once(text, "document.getElementById('b-r03').classList.add('open');", "document.getElementById('b-s02').classList.add('open');", "startup second")

for forbidden in ('id="b-r01"', 'id="b-r03"', '<td class="batch-entries">R-01, R-03</td>'):
    if forbidden in text:
        raise SystemExit(f"forbidden pending residue: {forbidden}")
if text.count("R-01 Source Map with Contested Zones") != 1:
    raise SystemExit("R-01 canonical title count not exactly one")
if text.count("R-03 Replication Risk Auditor") != 1:
    raise SystemExit("R-03 canonical title count not exactly one")

INDEX.write_text(text, encoding="utf-8", newline="")
post_sha = sha256(INDEX)

# Current-state tests from earlier batches track the repository's current reconciled state/startup.
for rel in ("tests/test_batch2_disposition.py", "tests/test_reconcile_entry_lineage.py"):
    p = ROOT / rel
    s = p.read_text(encoding="utf-8")
    s = s.replace("expected_pending=16", "expected_pending=14").replace("expected_drafted=75", "expected_drafted=77")
    s = s.replace("16 pending entries · 8 remaining batches · drafting authority", "14 pending entries · 7 remaining batches · drafting authority")
    s = s.replace("Production state: 75 drafted · 0 restore · 16 pending", "Production state: 77 drafted · 0 restore · 14 pending")
    s = s.replace("document.getElementById('b-r01').classList.add('open');", "document.getElementById('b-s01').classList.add('open');")
    s = s.replace("document.getElementById('b-r03').classList.add('open');", "document.getElementById('b-s02').classList.add('open');")
    s = s.replace("test_repository_post_state_reconciles_to_16_75_91", "test_repository_post_state_reconciles_to_14_77_91")
    p.write_text(s, encoding="utf-8")

batch3_test = r'''from __future__ import annotations

import html
import re
import unittest
from pathlib import Path

from tools.reconcile_entry_lineage import reconcile, validate_expectations

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
FIELDS = ("WHAT IT DOES", "WHEN TO USE", "THE PROMPT", "INPUTS NEEDED", "EXPECTED OUTPUT", "KNOBS", "FAILURE MODE", "FOLLOW-UP", "SAFETY NOTES")


def page(n: int) -> str:
    source = INDEX.read_text(encoding="utf-8")
    m = re.search(rf'<article class="manual-page-card" id="manual-page-{n:03d}"[^>]*>.*?</article>', source, re.S)
    if not m:
        raise AssertionError(f"missing page {n}")
    return m.group(0)


def visible(card: str) -> str:
    m = re.search(r"<pre>(.*?)</pre>", card, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))


def metadata(card: str) -> str:
    m = re.search(r'data-manual-text="([^"]*)"', card, re.S)
    return html.unescape(m.group(1))


class Batch3DispositionTests(unittest.TestCase):
    def test_promoted_and_current_state(self):
        result = reconcile(INDEX)
        self.assertEqual(validate_expectations(result, expected_pending=14, expected_drafted=77, expected_total=91, expected_pages=315), [])
        pending = {x.entry_id for x in result.pending_entries}
        briefs = {x.entry_id for x in result.briefs}
        for eid in ("R-01", "R-03"):
            self.assertNotIn(eid, pending)
            self.assertNotIn(eid, briefs)

    def test_one_canonical_body_and_nine_fields(self):
        bodies = {
            "R-01": "\n".join(visible(page(n)) for n in range(71, 78)),
            "R-03": "\n".join(visible(page(n)) for n in range(79, 87)),
        }
        self.assertEqual(bodies["R-01"].count("R-01 Source Map with Contested Zones"), 1)
        self.assertEqual(bodies["R-03"].count("R-03 Replication Risk Auditor"), 1)
        for eid, body in bodies.items():
            for field in FIELDS:
                self.assertIn(field, body, f"{eid} missing {field}")

    def test_r01_frozen_properties_and_institutional_map(self):
        cards = [page(n) for n in range(71, 77)]
        body = "\n".join(visible(c) for c in cards)
        meta = " ".join(metadata(c) for c in cards)
        for required in ("SOURCE TABLE", "CONTESTED ZONES", "KNOWN GAPS", "SOURCE FLATTENING WARNINGS", "INSTITUTIONAL INTEREST MAP", "R-02 (Source Flattening Detector)", "R-07 (Competing Hypothe"):
            self.assertIn(required, body)
        self.assertIn("institutional interest map", meta)
        self.assertIn("sources with an identified stake", meta)
        self.assertIn("Six components:", body)

    def test_r03_frozen_properties_taxonomy_and_r05(self):
        cards = [page(n) for n in range(79, 87)]
        body = "\n".join(visible(c) for c in cards)
        meta = " ".join(metadata(c) for c in cards)
        for required in ("P-HACKING FLAGS", "HARKING FLAGS", "EFFECT SIZE VS STATISTICAL", "VERY HIGH RISK", "NOT REPLICATION-READY", "R-05 (Failure-to-Test Converter)", "R-11 (Negative Result Documenter)"):
            self.assertIn(required, body)
        self.assertIn("very high risk", meta)
        self.assertIn("not replication-ready as a separate assessment-status outcome", meta)
        self.assertIn("r-05 (failure-to-test converter)", meta)

    def test_batch_and_startup_state(self):
        source = INDEX.read_text(encoding="utf-8")
        self.assertNotIn('<td class="batch-entries">R-01, R-03</td>', source)
        self.assertIn("14 pending entries · 7 remaining batches · drafting authority", source)
        self.assertIn("Production state: 77 drafted · 0 restore · 14 pending", source)
        self.assertIn("document.getElementById('b-s01').classList.add('open');", source)
        self.assertIn("document.getElementById('b-s02').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-r01').classList.add('open');", source)
        self.assertNotIn("document.getElementById('b-r03').classList.add('open');", source)


if __name__ == "__main__":
    unittest.main()
'''
(ROOT / "tests/test_batch3_disposition.py").write_text(batch3_test, encoding="utf-8")

audit = f'''# Batch 3 Disposition Record — 2026-08-24

Bounded editorial disposition of the existing canonical bodies for `R-01 Source Map with Contested Zones` and `R-03 Replication Risk Auditor`.

## Artifact binding
- Base commit: `{BASE_COMMIT}`
- Pre-mutation `index.html` SHA-256: `{EXPECTED_PRE_SHA}`
- Post-mutation `index.html` SHA-256: `{post_sha}`
- Pre-state: 16 pending / 75 drafted / 91 semantic entries / 315 pages / 8 remaining batches
- Post-state: 14 pending / 77 drafted / 91 semantic entries / 315 pages / 7 remaining batches
- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`

## Frozen audit matrix
| Entry | Classification | Demonstrated gap | Disposition |
|---|---|---|---|
| R-01 | PARTIAL | Required cross-source INSTITUTIONAL INTEREST MAP absent; only per-source interest disclosure existed. | Added the explicit aggregate map and named it in EXPECTED OUTPUT; preserved existing per-source disclosure and all other source-map mechanics. |
| R-03 | PARTIAL | Frozen VERY HIGH risk level absent; frozen R-05 follow-up absent. | Restored VERY HIGH as the fourth risk level, retained NOT REPLICATION-READY as a separate insufficiency status, and added the R-05 test-specification follow-up. |

## Verification contract
Accept only after the complete Python suite, strict validator, 14/77/91 lineage reconciliation, frozen editorial classifier, editorial-lineage audit, `git diff --check`, Chromium/Firefox/WebKit reader smoke, and human final `index.html` diff review all pass on the exact cleaned PR head.
'''
(ROOT / "docs/BATCH3_DISPOSITION_2026-08-24.md").write_text(audit, encoding="utf-8")
print(f"Batch 3 staged: {EXPECTED_PRE_SHA} -> {post_sha}")
