#!/usr/bin/env python3
"""Audit v3/v9 editorial lineage and the R-07/R-10 identifier conflict.

The audit is deterministic and network-free. It reports only what the committed
HTML and repository history support; it does not invent missing source files or
silently renumber entries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path

VERSION_RE = re.compile(
    r"(?i)(?:GNOME[_ ]Prompt[_ ]Field[_ ]Manual[^\n<>]{0,120}|\bversion\s+\d+(?:\.\d+)*\b|\bv\d+(?:\.\d+)*\b)"
)
ENTRY_RE = re.compile(r"(?<![A-Z0-9])(R-0?7|R-10)(?![A-Z0-9])")
WS_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class VersionReference:
    line: int
    text: str
    classification: str


@dataclass(frozen=True)
class EntryEvidence:
    entry_id: str
    location: str
    line: int
    text: str


@dataclass(frozen=True)
class AuditResult:
    source: str
    source_sha256: str
    version_references: list[VersionReference]
    entry_evidence: list[EntryEvidence]
    decision: dict[str, str]
    limitations: list[str]


class CaptureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str], int, list[str]]] = []
        self.blocks: list[tuple[str, set[str], int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        line, _ = self.getpos()
        self.stack.append((tag.lower(), set(values.get("class", "").split()), line, []))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == normalized:
                closing = self.stack[index:]
                del self.stack[index:]
                for item in closing:
                    text = normalize(" ".join(item[3]))
                    self.blocks.append((item[0], item[1], item[2], text))
                return

    def handle_data(self, data: str) -> None:
        if not data.strip():
            return
        for index in range(len(self.stack)):
            self.stack[index][3].append(data)


def normalize(value: str) -> str:
    return WS_RE.sub(" ", value).strip()


def classify_version(text: str) -> str:
    lowered = text.lower()
    if "v3" in lowered or "version 3" in lowered:
        return "source-filename-or-v3-reference"
    if "v9" in lowered or "version 9" in lowered:
        return "embedded-reader-v9-reference"
    return "other-version-reference"


def nearby_lines(lines: list[str], line_number: int, radius: int = 0) -> str:
    start = max(0, line_number - radius - 1)
    end = min(len(lines), line_number + radius)
    return normalize(" ".join(lines[start:end]))[:500]


def audit(path: Path) -> AuditResult:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()

    version_refs: list[VersionReference] = []
    seen_versions: set[tuple[int, str]] = set()
    for line_number, line in enumerate(lines, start=1):
        for _ in VERSION_RE.finditer(line):
            context = nearby_lines(lines, line_number)
            key = (line_number, context)
            if key not in seen_versions:
                version_refs.append(
                    VersionReference(line_number, context, classify_version(context))
                )
                seen_versions.add(key)

    parser = CaptureParser()
    parser.feed(text)
    parser.close()

    evidence: list[EntryEvidence] = []
    seen_evidence: set[tuple[str, str, int]] = set()
    relevant_classes = {
        "entry-row": "pending-inventory",
        "brief": "drafting-brief",
        "manual-page-card": "embedded-reader-page",
    }
    for _, classes, line, block_text in parser.blocks:
        location = next(
            (label for class_name, label in relevant_classes.items() if class_name in classes),
            None,
        )
        if location is None:
            continue
        for entry_id in sorted(set(ENTRY_RE.findall(block_text))):
            key = (entry_id, location, line)
            if key in seen_evidence:
                continue
            evidence.append(EntryEvidence(entry_id, location, line, block_text[:4000]))
            seen_evidence.add(key)

    r07_embedded = [
        item
        for item in evidence
        if item.entry_id == "R-07" and item.location == "embedded-reader-page"
    ]
    r10_pending = [
        item
        for item in evidence
        if item.entry_id == "R-10"
        and item.location in {"pending-inventory", "drafting-brief"}
    ]
    r10_embedded = [
        item
        for item in evidence
        if item.entry_id == "R-10" and item.location == "embedded-reader-page"
    ]

    decision = {
        "repository_package_version": "1.0.0-rc.1 remains a repository/package baseline only",
        "editorial_lineage": (
            "The committed evidence supports v3 as a named source-file label and v9 as the embedded reader's publication label. "
            "Because no v3 DOCX or separate v9 source artifact is committed, ancestry and authoritative editorial succession are not provable from this repository alone."
        ),
        "r07_r10": (
            "Retain R-07 as the current embedded-reader identifier and treat R-10 as a pending alias/renumbering request, not a new entry. "
            "Do not create a second body. Resolve the public identifier only when the authoritative editorial source is recovered."
            if r07_embedded and r10_pending and not r10_embedded
            else "Evidence is insufficient for an automatic identifier decision."
        ),
    }
    limitations = [
        "The repository history contains one original uploaded HTML artifact, a rename, and later documentation/validation changes; it does not contain the named v3 DOCX.",
        "No independent v9 source document is committed outside the embedded HTML reader.",
        "Textual occurrence does not prove editorial approval or source chronology.",
    ]
    return AuditResult(
        source=str(path),
        source_sha256=hashlib.sha256(raw).hexdigest(),
        version_references=sorted(
            version_refs, key=lambda item: (item.line, item.text)
        ),
        entry_evidence=sorted(
            evidence, key=lambda item: (item.entry_id, item.location, item.line)
        ),
        decision=decision,
        limitations=limitations,
    )


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def markdown(result: AuditResult) -> str:
    version_rows = "\n".join(
        f"| {item.line} | {item.classification} | {_escape_table(item.text)} |"
        for item in result.version_references
    ) or "| — | — | No version references found. |"
    evidence_rows = "\n".join(
        f"| `{item.entry_id}` | {item.location} | {item.line} | {_escape_table(item.text)} |"
        for item in result.entry_evidence
    ) or "| — | — | — | No R-07/R-10 evidence found. |"
    decisions = "\n".join(
        f"- **{key}:** {value}" for key, value in result.decision.items()
    )
    limits = "\n".join(f"- {value}" for value in result.limitations)
    return f"""# Editorial Lineage Audit

Source SHA-256: `{result.source_sha256}`

## Version references

| Line | Classification | Context |
|---:|---|---|
{version_rows}

## R-07 / R-10 evidence

| ID | Location | Line | Extracted text |
|---|---|---:|---|
{evidence_rows}

## Evidence-backed decision

{decisions}

## Limitations

{limits}
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("index.html"))
    parser.add_argument("--json", type=Path, default=Path("editorial-lineage.json"))
    parser.add_argument("--markdown", type=Path, default=Path("editorial-lineage.md"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.input.is_file():
        print(f"error: missing input: {args.input}", file=sys.stderr)
        return 2
    result = audit(args.input)
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
                "source_sha256": result.source_sha256,
                "version_references": len(result.version_references),
                "entry_evidence": len(result.entry_evidence),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
