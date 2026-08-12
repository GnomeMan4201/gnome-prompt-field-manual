#!/usr/bin/env python3
"""Audit the completed editorial renumbering and reader boundary.

The audit is deterministic and network-free. It verifies the corrected HTML
surface, the unchanged historical PDF, page metadata/visible-text parity, and
the immutable 2026-08-06 provenance records. Any failed invariant produces a
non-zero exit status.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from tools.reconcile_entry_lineage import (
        TreeParser,
        extract_briefs,
        extract_pending,
        normalize_text,
    )
except ModuleNotFoundError:  # Direct execution from tools/.
    from reconcile_entry_lineage import (  # type: ignore[no-redef]
        TreeParser,
        extract_briefs,
        extract_pending,
        normalize_text,
    )


EXPECTED_PDF_SHA256 = "97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9"
BASELINE_SHA256 = "b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1"
HISTORICAL_RECORDS = {
    "docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md": "341d645c44583f31b3b195dc68e7dcafc3f26a0ba0c23effbe6fb3fd4db31075",
    "docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md": "c10a2f24b18b25c0a1bed83bbfdbb10ad0cb01476d7f0435b9fb1a375023ad8f",
    "docs/BASELINE_AUDIT_2026-08-06.md": "efa69cb5f5ff893da4e8c1d3d6caf1134a34009bd669255cc138dc190a5e1c3c",
}
CLASSIFIER_PATH = "docs/EDITORIAL_OCCURRENCE_CLASSIFIER_2026-08-12.csv"

PAGE_RULES = {
    "manual-page-076": {
        "required": ("r-07 (competing hypotheses table)",),
        "forbidden": (),
    },
    "manual-page-091": {
        "required": ("r-05 afterward", "r-07 competing hypotheses table"),
        "forbidden": ("r-06",),
    },
    "manual-page-093": {
        "required": ("r-10 source-of-truth conflict resolver",),
        "forbidden": ("r-07 source-of-truth conflict resolver",),
    },
    "manual-page-101": {
        "required": ("r-05 (failure-to-test converter)",),
        "forbidden": ("r-06",),
    },
    "manual-page-105": {
        "required": ("r-05 (failure-to-test converter)",),
        "forbidden": ("r-06",),
    },
    "manual-page-267": {
        "required": ("r-07 (competing hypotheses table)",),
        "forbidden": ("r-06 (competing hypotheses table)",),
    },
    "manual-page-307": {
        "required": ("r-11 · r-05",),
        "forbidden": ("r-11 · r-06",),
    },
}


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class PageEvidence:
    page_id: str
    metadata_sha256: str
    visible_sha256: str
    parity: bool
    required_phrases: list[str]
    forbidden_phrases: list[str]


@dataclass(frozen=True)
class HistoricalRecord:
    path: str
    expected_sha256: str
    actual_sha256: str
    preserved: bool


@dataclass(frozen=True)
class AuditResult:
    source: str
    source_sha256: str
    baseline_source_sha256: str
    pdf_sha256: str
    text_surface_sha256: str
    passed: bool
    checks: list[Check]
    affected_pages: list[PageEvidence]
    historical_records: list[HistoricalRecord]
    limitations: list[str]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_surface(value: str) -> str:
    lowered = value.casefold().replace("\u00ad", "")
    dehyphenated = re.sub(r"-\s+", "", lowered)
    return normalize_text(dehyphenated)


def contains_token(value: str, token: str) -> bool:
    return re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", value) is not None


def add_check(checks: list[Check], name: str, passed: bool, detail: str) -> None:
    checks.append(Check(name=name, passed=passed, detail=detail))


def classifier_check(repository_root: Path) -> tuple[bool, str]:
    path = repository_root / CLASSIFIER_PATH
    if not path.is_file():
        return False, f"missing {CLASSIFIER_PATH}"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "baseline_commit",
        "container",
        "stable_locator",
        "surface",
        "token",
        "classification",
        "disposition",
        "new_value",
        "context_sha256",
    }
    fields = set(rows[0]) if rows else set()
    unclassified = [row for row in rows if not row.get("classification") or not row.get("disposition")]
    baselines = {row.get("baseline_commit") for row in rows}
    valid = required <= fields and not unclassified and len(rows) == 151 and baselines == {
        "410e8b46e8f50b9dbfc8d2c37358818722c9b9c2"
    }
    return valid, (
        f"rows={len(rows)}, unclassified={len(unclassified)}, "
        f"schema_complete={required <= fields}, baselines={sorted(str(v) for v in baselines)}"
    )


def audit(path: Path, repository_root: Path | None = None) -> AuditResult:
    repository_root = repository_root or path.resolve().parent
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    parser = TreeParser()
    parser.feed(text)
    parser.close()
    root = parser.root
    checks: list[Check] = []

    cards = {
        node.element_id: node
        for node in root.walk()
        if "manual-page-card" in node.classes and node.element_id
    }
    page_evidence: list[PageEvidence] = []
    for page_id, rule in PAGE_RULES.items():
        card = cards.get(page_id)
        if card is None:
            add_check(checks, f"{page_id}:exists", False, "page card missing")
            continue
        pre = card.first_tag("pre")
        metadata = canonical_surface(card.attrs.get("data-manual-text", ""))
        visible = canonical_surface(pre.raw_text() if pre is not None else "")
        parity = metadata == visible
        required = list(rule["required"])
        forbidden = list(rule["forbidden"])
        requirements_ok = all(
            phrase in metadata and phrase in visible for phrase in required
        )
        forbidden_ok = all(
            not contains_token(metadata, phrase)
            and not contains_token(visible, phrase)
            for phrase in forbidden
        )
        add_check(
            checks,
            f"{page_id}:surface-parity",
            parity,
            f"metadata={sha256_bytes(metadata.encode())}, visible={sha256_bytes(visible.encode())}",
        )
        add_check(
            checks,
            f"{page_id}:semantic-rules",
            requirements_ok and forbidden_ok,
            f"required={required}, forbidden={forbidden}",
        )
        page_evidence.append(
            PageEvidence(
                page_id=page_id,
                metadata_sha256=sha256_bytes(metadata.encode()),
                visible_sha256=sha256_bytes(visible.encode()),
                parity=parity,
                required_phrases=required,
                forbidden_phrases=forbidden,
            )
        )

    visible_pages = "\n".join(
        node.first_tag("pre").raw_text()
        for node in cards.values()
        if node.first_tag("pre") is not None
    )
    competing_bodies = re.findall(
        r"(?im)^\s*R-07\s+Competing Hypotheses Table\s*$", visible_pages
    )
    source_bodies = re.findall(
        r"(?im)^\s*R-10\s+Source-of-Truth Conflict Resolver\s*$", visible_pages
    )
    add_check(
        checks,
        "exactly-one-competing-hypotheses-body",
        len(competing_bodies) == 1,
        f"count={len(competing_bodies)}",
    )
    add_check(
        checks,
        "exactly-one-source-of-truth-body",
        len(source_bodies) == 1,
        f"count={len(source_bodies)}",
    )

    pending_ids = {item.entry_id for item in extract_pending(root)}
    brief_ids = {item.entry_id for item in extract_briefs(root)}
    add_check(
        checks,
        "r10-not-pending",
        "R-10" not in pending_ids and "R-10" not in brief_ids,
        f"pending={sorted(pending_ids)}, briefs={sorted(brief_ids)}",
    )

    normalized_raw = canonical_surface(text)
    stale_patterns = {
        "R-06 Competing Hypotheses": r"r-06\s+(?:\()?competing hypotheses table",
        "R-07 Source-of-Truth": r"r-07\s+(?:—\s*)?source-of-truth conflict resolver",
        "R-06 Failure-to-Test": r"r-06\s*\(failure-to-test converter\)",
        "R-11 · R-06": r"r-11\s*·\s*r-06",
    }
    stale_hits = [name for name, pattern in stale_patterns.items() if re.search(pattern, normalized_raw)]
    add_check(
        checks,
        "no-stale-current-state-pairing",
        not stale_hits,
        f"hits={stale_hits}",
    )

    objects = [node for node in root.walk() if "manual-pdf-object" in node.classes]
    pdf_sha256 = ""
    if len(objects) == 1:
        data = objects[0].attrs.get("data", "")
        prefix = "data:application/pdf;base64,"
        try:
            pdf_sha256 = sha256_bytes(base64.b64decode(data.removeprefix(prefix), validate=True))
        except ValueError:
            pdf_sha256 = "invalid-base64"
    add_check(
        checks,
        "historical-pdf-byte-preservation",
        len(objects) == 1 and pdf_sha256 == EXPECTED_PDF_SHA256,
        f"objects={len(objects)}, sha256={pdf_sha256}",
    )

    tabs = [node for node in root.walk() if "manual-tab" in node.classes]
    views = {
        node.element_id: node
        for node in root.walk()
        if node.element_id in {"manualPdfView", "manualTextView"}
    }
    text_tabs = [node for node in tabs if node.attrs.get("data-view") == "text"]
    pdf_tabs = [node for node in tabs if node.attrs.get("data-view") == "pdf"]
    boundary_ok = (
        len(text_tabs) == 1
        and "active" in text_tabs[0].classes
        and "canonical" in text_tabs[0].text().casefold()
        and len(pdf_tabs) == 1
        and "active" not in pdf_tabs[0].classes
        and "historical" in pdf_tabs[0].text().casefold()
        and "active" in views.get("manualTextView", root).classes
        and "active" not in views.get("manualPdfView", root).classes
        and EXPECTED_PDF_SHA256 in text
    )
    add_check(
        checks,
        "canonical-text-historical-pdf-boundary",
        boundary_ok,
        "searchable text must be canonical/default; PDF must be historical/non-default and hash-labelled",
    )

    ordered_metadata = [
        node.attrs.get("data-manual-text", "")
        for node in root.walk()
        if "manual-page-card" in node.classes
    ]
    text_surface_sha256 = sha256_bytes(("\n".join(ordered_metadata) + "\n").encode())
    add_check(
        checks,
        "reader-page-count",
        len(ordered_metadata) == 315,
        f"page_cards={len(ordered_metadata)}",
    )

    historical_records: list[HistoricalRecord] = []
    for relative_path, expected in HISTORICAL_RECORDS.items():
        record_path = repository_root / relative_path
        actual = sha256_bytes(record_path.read_bytes()) if record_path.is_file() else "missing"
        preserved = actual == expected
        historical_records.append(
            HistoricalRecord(relative_path, expected, actual, preserved)
        )
        add_check(checks, f"preserve:{relative_path}", preserved, f"sha256={actual}")

    classifier_ok, classifier_detail = classifier_check(repository_root)
    add_check(checks, "occurrence-classifier-complete", classifier_ok, classifier_detail)

    passed = all(check.passed for check in checks)
    return AuditResult(
        source=str(path),
        source_sha256=sha256_bytes(raw),
        baseline_source_sha256=BASELINE_SHA256,
        pdf_sha256=pdf_sha256,
        text_surface_sha256=text_surface_sha256,
        passed=passed,
        checks=checks,
        affected_pages=page_evidence,
        historical_records=historical_records,
        limitations=[
            "The authoritative editable v3 manuscript and editable v9 source remain unavailable.",
            "The embedded PDF is intentionally preserved as an uncorrected historical v9 snapshot.",
            "R-05 (Field Journal Entry) at manual-page-213 remains a separately tracked semantic collision and is not guessed here.",
        ],
    )


def markdown(result: AuditResult) -> str:
    check_rows = "\n".join(
        f"| {item.name} | {'PASS' if item.passed else 'FAIL'} | {item.detail.replace('|', '&#124;')} |"
        for item in result.checks
    )
    page_rows = "\n".join(
        f"| `{item.page_id}` | {'yes' if item.parity else 'no'} | `{item.metadata_sha256}` | `{item.visible_sha256}` |"
        for item in result.affected_pages
    )
    historical_rows = "\n".join(
        f"| `{item.path}` | {'yes' if item.preserved else 'no'} | `{item.actual_sha256}` |"
        for item in result.historical_records
    )
    limits = "\n".join(f"- {value}" for value in result.limitations)
    return f"""# Editorial Renumbering Completion Audit

Overall result: **{'PASS' if result.passed else 'FAIL'}**

- Current `index.html` SHA-256: `{result.source_sha256}`
- Frozen baseline SHA-256: `{result.baseline_source_sha256}`
- Historical PDF SHA-256: `{result.pdf_sha256}`
- Canonical searchable-text surface SHA-256: `{result.text_surface_sha256}`

## Invariant checks

| Check | Result | Evidence |
|---|---|---|
{check_rows}

## Affected-page parity

| Page | Metadata/visible parity | Metadata SHA-256 | Visible SHA-256 |
|---|---|---|---|
{page_rows}

## Preserved historical records

| Record | Preserved | Actual SHA-256 |
|---|---|---|
{historical_rows}

## Known limitations

{limits}
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("index.html"))
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--json", type=Path, default=Path("editorial-lineage.json"))
    parser.add_argument("--markdown", type=Path, default=Path("editorial-lineage.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.input.is_file():
        print(f"error: missing input: {args.input}", file=sys.stderr)
        return 2
    result = audit(args.input, args.repository_root.resolve())
    payload = asdict(result)
    for output in (args.json, args.markdown):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.markdown.write_text(markdown(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "passed": result.passed,
                "source_sha256": result.source_sha256,
                "pdf_sha256": result.pdf_sha256,
                "text_surface_sha256": result.text_surface_sha256,
                "checks": len(result.checks),
            },
            sort_keys=True,
        )
    )
    if not result.passed:
        for check in result.checks:
            if not check.passed:
                print(f"failure: {check.name}: {check.detail}", file=sys.stderr)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
