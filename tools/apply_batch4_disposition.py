from __future__ import annotations

import hashlib
import html
import re
from pathlib import Path

from tools.reconcile_entry_lineage import reconcile, validate_expectations

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
DOC = ROOT / "docs" / "BATCH4_DISPOSITION_2026-09-17.md"
TARGETS = ("S-01", "S-02", "S-03")
TARGET_BRIEFS = tuple(f"b-{entry.lower()}" for entry in TARGETS)


def visible(fragment: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", fragment))


def normalized(fragment: str) -> str:
    return re.sub(r"\s+", " ", visible(fragment)).strip()


def balanced_div_span(source: str, start: int) -> tuple[int, int]:
    token_re = re.compile(r"<div\b[^>]*>|</div>", re.I)
    depth = 0
    first = True
    for token in token_re.finditer(source, start):
        if first:
            if token.start() != start or token.group(0).lower().startswith("</"):
                raise RuntimeError("balanced div scan did not start on an opening div")
            first = False
        if token.group(0).lower().startswith("</"):
            depth -= 1
            if depth == 0:
                return start, token.end()
        else:
            depth += 1
    raise RuntimeError("unterminated div block")


def class_div_blocks(source: str, class_name: str) -> list[tuple[int, int, str]]:
    start_re = re.compile(
        rf'<div\b[^>]*class="[^"]*(?:^|\s){re.escape(class_name)}(?:\s|$)[^"]*"[^>]*>',
        re.I,
    )
    blocks: list[tuple[int, int, str]] = []
    for match in start_re.finditer(source):
        start, end = balanced_div_span(source, match.start())
        blocks.append((start, end, source[start:end]))
    return blocks


def remove_entry_row(source: str, entry_id: str) -> str:
    matches = []
    for start, end, block in class_div_blocks(source, "entry-row"):
        text = normalized(block)
        if re.search(rf"(?<![A-Z0-9]){re.escape(entry_id)}(?![A-Z0-9])", text):
            matches.append((start, end, block))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one pending row for {entry_id}, found {len(matches)}")
    start, end, _ = matches[0]
    return source[:start] + source[end:]


def remove_brief(source: str, brief_id: str) -> str:
    start_re = re.compile(rf'<div\b[^>]*class="brief"[^>]*id="{re.escape(brief_id)}"[^>]*>', re.I)
    matches = list(start_re.finditer(source))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one brief {brief_id}, found {len(matches)}")
    start, end = balanced_div_span(source, matches[0].start())
    return source[:start] + source[end:]


def remove_batch_row(source: str) -> str:
    marker = '<td class="batch-entries">S-01, S-02, S-03</td>'
    rows = [
        match
        for match in re.finditer(r"<tr\b[^>]*>.*?</tr>", source, re.I | re.S)
        if marker in match.group(0)
    ]
    if len(rows) != 1:
        raise RuntimeError(f"expected exactly one Batch 4 table row, found {len(rows)}")
    match = rows[0]
    return source[: match.start()] + source[match.end() :]


def rewrite_stat(source: str, label_fragment: str, old: int, new: int) -> str:
    candidates = []
    for start, end, block in class_div_blocks(source, "stat"):
        text = normalized(block).lower()
        if label_fragment.lower() in text:
            candidates.append((start, end, block))
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected one stat containing {label_fragment!r}, found {len(candidates)}"
        )
    start, end, block = candidates[0]
    number_re = re.compile(rf'(<div\b[^>]*class="stat-num"[^>]*>\s*){old}(\s*</div>)', re.I)
    replaced, count = number_re.subn(rf"\g<1>{new}\g<2>", block, count=1)
    if count != 1:
        raise RuntimeError(f"could not rewrite {label_fragment} stat {old} -> {new}")
    return source[:start] + replaced + source[end:]


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"expected one occurrence of {old!r}, found {count}")
    return source.replace(old, new, 1)


def page_card(source: str, number: int) -> str:
    match = re.search(
        rf'<article class="manual-page-card" id="manual-page-{number:03d}"[^>]*>.*?</article>',
        source,
        re.S,
    )
    if not match:
        raise RuntimeError(f"missing manual page {number:03d}")
    return match.group(0)


def assert_frozen_pass_properties(source: str) -> None:
    s01 = normalized(" ".join(page_card(source, n) for n in range(107, 112)))
    s02 = normalized(" ".join(page_card(source, n) for n in range(112, 117)))
    s03 = normalized(" ".join(page_card(source, n) for n in range(117, 122)))

    for token in ("WHO CAN INJECT", "specific actor type", "OBSERVABILITY STATUS"):
        if token.lower() not in s01.lower():
            raise RuntimeError(f"S-01 frozen PASS property missing: {token}")
    for token in ("HIDDEN STATE DEPENDENCIES", "safe modification", "actual behavior"):
        if token.lower() not in s02.lower():
            raise RuntimeError(f"S-02 frozen PASS property missing: {token}")
    for token in ("DETECTABILITY", "failure mode", "mandatory"):
        if token.lower() not in s03.lower():
            raise RuntimeError(f"S-03 frozen PASS property missing: {token}")


def main() -> int:
    source = INDEX.read_text(encoding="utf-8")
    before = reconcile(INDEX)
    failures = validate_expectations(
        before,
        expected_pending=14,
        expected_drafted=77,
        expected_total=91,
        expected_pages=315,
    )
    if failures:
        raise RuntimeError(f"unexpected pre-state: {failures}")

    assert_frozen_pass_properties(source)
    frozen_pages = {n: page_card(source, n) for n in range(107, 122)}

    for entry_id in TARGETS:
        source = remove_entry_row(source, entry_id)
    for brief_id in TARGET_BRIEFS:
        source = remove_brief(source, brief_id)
    source = remove_batch_row(source)

    source = rewrite_stat(source, "pending", 14, 11)
    source = rewrite_stat(source, "drafted", 77, 80)
    source = rewrite_stat(source, "batch", 7, 6)

    source = replace_once(
        source,
        "14 pending entries · 7 remaining batches · drafting authority",
        "11 pending entries · 6 remaining batches · drafting authority",
    )
    source = replace_once(
        source,
        "Production state: 77 drafted · 0 restore · 14 pending",
        "Production state: 80 drafted · 0 restore · 11 pending",
    )

    remaining_briefs = re.findall(r'<div class="brief" id="(b-[^"]+)">', source)
    if len(remaining_briefs) != 11:
        raise RuntimeError(f"expected 11 remaining briefs, found {len(remaining_briefs)}")
    next_two = remaining_briefs[:2]
    source = replace_once(
        source,
        "document.getElementById('b-s01').classList.add('open');",
        f"document.getElementById('{next_two[0]}').classList.add('open');",
    )
    source = replace_once(
        source,
        "document.getElementById('b-s02').classList.add('open');",
        f"document.getElementById('{next_two[1]}').classList.add('open');",
    )

    for number, original in frozen_pages.items():
        if page_card(source, number) != original:
            raise RuntimeError(f"Batch 4 PASS migration altered canonical body page {number}")

    INDEX.write_text(source, encoding="utf-8")
    after = reconcile(INDEX)
    failures = validate_expectations(
        after,
        expected_pending=11,
        expected_drafted=80,
        expected_total=91,
        expected_pages=315,
    )
    if failures:
        raise RuntimeError(f"unexpected post-state: {failures}")

    pending = {entry.entry_id for entry in after.pending_entries}
    briefs = {entry.entry_id for entry in after.briefs}
    for entry_id in TARGETS:
        if entry_id in pending or entry_id in briefs:
            raise RuntimeError(f"{entry_id} was not fully promoted out of pending state")

    digest = hashlib.sha256(INDEX.read_bytes()).hexdigest()
    DOC.write_text(
        "# Batch 4 disposition — 2026-09-17\n\n"
        "Batch 4 adjudicated the existing canonical S-01, S-02, and S-03 bodies against the frozen pending briefs. No replacement prompt bodies were drafted and no canonical body page changed.\n\n"
        "## Frozen classifications\n\n"
        "- **S-01 System Map with Trust Boundaries — PASS.** The canonical body already requires a `WHO CAN INJECT` field naming a specific actor type at trust-boundary crossings and retains explicit observability status.\n"
        "- **S-02 Code Archaeology — PASS.** The canonical body already names `HIDDEN STATE DEPENDENCIES` and separates actual behavior, safe modification zones, and uncertainty.\n"
        "- **S-03 Failure Mode Inventory — PASS.** The canonical body already makes `DETECTABILITY` an explicit required failure-mode property.\n\n"
        "## Production-state transition\n\n"
        "- Before: 14 pending / 77 drafted / 91 semantic entries / 315 pages / 7 remaining batches.\n"
        "- After: 11 pending / 80 drafted / 91 semantic entries / 315 pages / 6 remaining batches.\n"
        f"- Next default briefs: `{next_two[0]}` and `{next_two[1]}`.\n\n"
        "## Integrity boundary\n\n"
        "The migration removes only the three pending inventory rows, their three drafting briefs, the Batch 4 remaining-batch row, and current production-state/startup metadata. Pages 107–121 are byte-for-byte identical before and after the disposition mutation.\n\n"
        f"Final `index.html` SHA-256: `{digest}`\n",
        encoding="utf-8",
    )
    print(f"Batch 4 disposition applied; next briefs: {next_two}; index SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
