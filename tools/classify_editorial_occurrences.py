#!/usr/bin/env python3
"""Generate the frozen R-06/R-07/R-10 occurrence-classifier evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
from pathlib import Path


BASELINE = "410e8b46e8f50b9dbfc8d2c37358818722c9b9c2"
TOKEN_RE = re.compile(r"(?<![A-Z0-9])(R-(?:06|07|10))(?![A-Z0-9])", re.IGNORECASE)
LOCKED_PROVENANCE = {
    "docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md",
    "docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md",
    "docs/BASELINE_AUDIT_2026-08-06.md",
}
FIELDS = (
    "baseline_commit",
    "container",
    "stable_locator",
    "surface",
    "token",
    "classification",
    "disposition",
    "new_value",
    "context_sha256",
)


def git(*args: str) -> bytes:
    return subprocess.check_output(("git", *args))


def nearest_page(lines: list[str], line_index: int) -> str:
    for candidate in range(line_index, -1, -1):
        match = re.search(r'id="(manual-page-\d{3})"', lines[candidate])
        if match:
            return match.group(1)
    return ""


def context_for(line: str, start: int, end: int, radius: int = 120) -> str:
    return re.sub(r"\s+", " ", line[max(0, start - radius) : end + radius]).strip()


def classify(
    path: str,
    context: str,
    *,
    page: str,
    line_number: int,
    occurrence: int,
) -> str:
    lowered = context.casefold()
    if path in LOCKED_PROVENANCE:
        return "historical-provenance"
    if path == "index.html":
        if page in {"manual-page-101", "manual-page-105", "manual-page-307"}:
            return "unrelated/other-entry"
        if page in {"manual-page-076", "manual-page-267"}:
            return "competing-hypotheses"
        if page == "manual-page-093":
            return "source-of-truth"
        if page == "manual-page-091":
            if line_number == 6219:
                return (
                    "unrelated/other-entry"
                    if occurrence <= 2
                    else "competing-hypotheses"
                )
            if line_number in {6238, 6239}:
                return "unrelated/other-entry"
            if line_number == 6252:
                return "competing-hypotheses"
    distances: list[tuple[int, str]] = []
    center = len(context) // 2
    for phrase, label in (
        ("competing hypotheses", "competing-hypotheses"),
        ("source-of-truth", "source-of-truth"),
        ("failure-to-test", "unrelated/other-entry"),
        ("field journal entry", "unrelated/other-entry"),
    ):
        position = lowered.find(phrase)
        if position >= 0:
            distances.append((abs(position - center), label))
    return min(distances)[1] if distances else "historical-provenance"


def disposition(
    path: str, line_number: int, token: str, classification: str
) -> tuple[str, str]:
    normalized = token.upper()
    if path in LOCKED_PROVENANCE:
        return "preserve-sha-bound-record", "preserve"
    if path == "index.html":
        if line_number == 366 or 654 <= line_number <= 665:
            return "remove-completed-pending-state", "remove"
        if line_number == 346:
            return "replace-discrepancy-with-completion-record", "preserve"
        if line_number == 422:
            return "rewrite-rationale-as-completed", "preserve"
        if classification == "competing-hypotheses" and normalized == "R-06":
            return "replace-semantic-reference", "R-07"
        if classification == "source-of-truth" and normalized == "R-07":
            return "replace-semantic-reference", "R-10"
        if classification == "unrelated/other-entry" and normalized == "R-06":
            return "repair-failure-to-test-reference", "R-05"
        return "preserve-correct-reference", "preserve"
    if path.startswith("tools/") or path.startswith("tests/") or path.startswith(".github/"):
        return "replace-pre-state-gate-with-post-state-gate", "post-state assertion"
    if path in {"README.md", "CHANGELOG.md", "docs/IDENTITY_AND_SCOPE.md", "docs/QUALITY_GATE.md"}:
        return "update-current-state-documentation", "post-state wording"
    return "preserve-reviewed-context", "preserve"


def generate(baseline: str) -> list[dict[str, str]]:
    paths = git("ls-tree", "-r", "--name-only", baseline).decode().splitlines()
    rows: list[dict[str, str]] = []
    for path in paths:
        raw = git("show", f"{baseline}:{path}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        lines = text.splitlines()
        for line_index, line in enumerate(lines):
            occurrence = 0
            for match in TOKEN_RE.finditer(line):
                occurrence += 1
                line_number = line_index + 1
                context = context_for(line, match.start(), match.end())
                page = nearest_page(lines, line_index) if path == "index.html" else ""
                classification = classify(
                    path,
                    context,
                    page=page,
                    line_number=line_number,
                    occurrence=occurrence,
                )
                action, new_value = disposition(
                    path, line_number, match.group(1), classification
                )
                if path == "index.html" and "data-manual-text=" in line:
                    surface = "search-metadata"
                elif page:
                    surface = "visible-text"
                elif path == "index.html":
                    surface = "production-workspace"
                else:
                    surface = "repository-text"
                stable = (
                    f"{page}:L{line_number}#token-{occurrence}"
                    if page
                    else f"{path}:L{line_number}#token-{occurrence}"
                )
                rows.append(
                    {
                        "baseline_commit": baseline,
                        "container": path,
                        "stable_locator": stable,
                        "surface": surface,
                        "token": match.group(1),
                        "classification": classification,
                        "disposition": action,
                        "new_value": new_value,
                        "context_sha256": hashlib.sha256(context.encode()).hexdigest(),
                    }
                )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/EDITORIAL_OCCURRENCE_CLASSIFIER_2026-08-12.csv"),
    )
    args = parser.parse_args()
    rows = generate(args.baseline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} classified occurrences to {args.output}")
    return 0 if rows and all(row["classification"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
