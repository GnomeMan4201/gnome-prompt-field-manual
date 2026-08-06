#!/usr/bin/env python3
"""Validate the GNOME Prompt Field Manual as an auditable static artifact.

The validator performs deterministic, network-free checks. It verifies the
committed document and local assets only; it does not claim that external links
are live or that technical prose is factually correct.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


PLACEHOLDER_PATTERNS = (
    ("template-expression", re.compile(r"\{\{[^{}]+\}\}|\{%[^%]+%\}")),
    ("editorial-marker", re.compile(r"(?im)^\s*(TODO|FIXME|TBD|XXX)\b")),
    ("placeholder-copy", re.compile(r"(?i)\blorem ipsum\b|\bexample\.com\b")),
)

SKIPPED_SCHEMES = {"data", "mailto", "tel", "javascript", "blob"}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    line: int
    message: str


@dataclass(frozen=True)
class Metrics:
    source: str
    source_sha256: str
    bytes: int
    element_count: int
    unique_ids: int
    heading_count: int
    internal_anchor_count: int
    local_asset_reference_count: int
    external_link_count: int
    image_count: int
    script_count: int
    style_count: int
    error_count: int
    warning_count: int


class ManualParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str], int]] = []
        self.ids: dict[str, list[int]] = defaultdict(list)
        self.anchor_refs: list[tuple[str, int]] = []
        self.local_refs: list[tuple[str, str, int]] = []
        self.external_links: list[tuple[str, int]] = []
        self.headings: list[tuple[int, str, int]] = []
        self.images: list[tuple[dict[str, str], int]] = []
        self.blank_targets: list[tuple[dict[str, str], int]] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.html_attrs: dict[str, str] = {}
        self.meta_tags: list[dict[str, str]] = []
        self.main_lines: list[int] = []
        self.script_count = 0
        self.style_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        line, _ = self.getpos()
        normalized = {key.lower(): value or "" for key, value in attrs}
        tag = tag.lower()
        self.elements.append((tag, normalized, line))

        element_id = normalized.get("id", "").strip()
        if element_id:
            self.ids[element_id].append(line)

        if tag == "html" and not self.html_attrs:
            self.html_attrs = normalized
        elif tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta_tags.append(normalized)
        elif tag == "main":
            self.main_lines.append(line)
        elif tag == "script":
            self.script_count += 1
        elif tag == "style":
            self.style_count += 1
        elif tag == "img":
            self.images.append((normalized, line))

        if len(tag) == 2 and tag[0] == "h" and tag[1].isdigit():
            level = int(tag[1])
            if 1 <= level <= 6:
                self.headings.append((level, tag, line))

        if tag == "a":
            href = normalized.get("href", "").strip()
            self._record_reference("href", href, line)
            if normalized.get("target", "").lower() == "_blank":
                self.blank_targets.append((normalized, line))
        else:
            for attr in ("src", "href", "poster"):
                value = normalized.get(attr, "").strip()
                if value:
                    self._record_reference(attr, value, line)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    def _record_reference(self, attr: str, value: str, line: int) -> None:
        if not value:
            return
        if value.startswith("#"):
            self.anchor_refs.append((unquote(value[1:]), line))
            return

        parsed = urlsplit(value)
        if parsed.scheme.lower() in SKIPPED_SCHEMES:
            return
        if parsed.scheme or parsed.netloc or value.startswith("//"):
            if attr == "href" and parsed.scheme.lower() in {"http", "https"}:
                self.external_links.append((value, line))
            return

        path = unquote(parsed.path)
        if not path or path == ".":
            if parsed.fragment:
                self.anchor_refs.append((unquote(parsed.fragment), line))
            return
        self.local_refs.append((attr, path, line))


@dataclass(frozen=True)
class ValidationResult:
    metrics: Metrics
    findings: list[Finding]


def _safe_local_path(root: Path, reference: str) -> Path | None:
    pure = PurePosixPath(reference.replace("\\", "/"))
    if pure.is_absolute() or ".." in pure.parts:
        return None
    candidate = (root / Path(*pure.parts)).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _meta_present(meta_tags: list[dict[str, str]], *, name: str) -> bool:
    expected = name.lower()
    return any(tag.get("name", "").lower() == expected for tag in meta_tags)


def validate(path: Path) -> ValidationResult:
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    parser = ManualParser()
    findings: list[Finding] = []

    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:  # HTMLParser exceptions are unusual but actionable.
        findings.append(Finding("error", "html-parse", 0, str(exc)))

    lang = parser.html_attrs.get("lang", "").strip()
    if not lang:
        findings.append(
            Finding("error", "missing-html-lang", 0, "The html element needs a lang attribute")
        )

    title = " ".join(part.strip() for part in parser.title_parts if part.strip())
    if not title:
        findings.append(Finding("error", "missing-title", 0, "The document title is empty"))

    if not _meta_present(parser.meta_tags, name="viewport"):
        findings.append(
            Finding("error", "missing-viewport", 0, "A responsive viewport meta tag is required")
        )
    if not _meta_present(parser.meta_tags, name="description"):
        findings.append(
            Finding("warning", "missing-description", 0, "A meta description is recommended")
        )

    if len(parser.main_lines) != 1:
        findings.append(
            Finding(
                "error",
                "main-count",
                parser.main_lines[0] if parser.main_lines else 0,
                f"Expected exactly one main element; found {len(parser.main_lines)}",
            )
        )

    h1_lines = [line for level, _, line in parser.headings if level == 1]
    if len(h1_lines) != 1:
        findings.append(
            Finding(
                "error",
                "h1-count",
                h1_lines[0] if h1_lines else 0,
                f"Expected exactly one h1; found {len(h1_lines)}",
            )
        )

    previous_level: int | None = None
    for level, _, line in parser.headings:
        if previous_level is not None and level > previous_level + 1:
            findings.append(
                Finding(
                    "warning",
                    "heading-jump",
                    line,
                    f"Heading level jumps from h{previous_level} to h{level}",
                )
            )
        previous_level = level

    for element_id, lines in sorted(parser.ids.items()):
        if len(lines) > 1:
            findings.append(
                Finding(
                    "error",
                    "duplicate-id",
                    lines[0],
                    f"ID {element_id!r} appears on lines {', '.join(map(str, lines))}",
                )
            )

    known_anchors = set(parser.ids)
    for anchor, line in parser.anchor_refs:
        if anchor and anchor not in known_anchors:
            findings.append(
                Finding(
                    "error",
                    "broken-anchor",
                    line,
                    f"Local anchor #{anchor} does not match an element ID",
                )
            )

    root = path.parent
    for attr, reference, line in parser.local_refs:
        candidate = _safe_local_path(root, reference)
        if candidate is None:
            findings.append(
                Finding(
                    "error",
                    "unsafe-local-reference",
                    line,
                    f"{attr} reference escapes the document root: {reference}",
                )
            )
        elif not candidate.is_file():
            findings.append(
                Finding(
                    "error",
                    "missing-local-asset",
                    line,
                    f"{attr} references missing file: {reference}",
                )
            )

    for attrs, line in parser.blank_targets:
        rel_tokens = {token.lower() for token in attrs.get("rel", "").split()}
        if "noopener" not in rel_tokens:
            findings.append(
                Finding(
                    "error",
                    "unsafe-blank-target",
                    line,
                    'target="_blank" must include rel="noopener"',
                )
            )

    for attrs, line in parser.images:
        if "alt" not in attrs:
            findings.append(
                Finding("error", "missing-image-alt", line, "Image is missing an alt attribute")
            )

    for code, pattern in PLACEHOLDER_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                Finding(
                    "warning",
                    code,
                    line,
                    f"Potential unresolved placeholder: {match.group(0)[:80]!r}",
                )
            )

    findings.sort(key=lambda item: (item.severity != "error", item.line, item.code, item.message))
    counts = Counter(finding.severity for finding in findings)
    metrics = Metrics(
        source=str(path),
        source_sha256=hashlib.sha256(raw).hexdigest(),
        bytes=len(raw),
        element_count=len(parser.elements),
        unique_ids=len(parser.ids),
        heading_count=len(parser.headings),
        internal_anchor_count=len(parser.anchor_refs),
        local_asset_reference_count=len(parser.local_refs),
        external_link_count=len(parser.external_links),
        image_count=len(parser.images),
        script_count=parser.script_count,
        style_count=parser.style_count,
        error_count=counts["error"],
        warning_count=counts["warning"],
    )
    return ValidationResult(metrics, findings)


def markdown_report(result: ValidationResult) -> str:
    metrics = result.metrics
    findings = result.findings
    finding_rows = "\n".join(
        f"| {finding.severity} | `{finding.code}` | {finding.line or '—'} | {finding.message.replace('|', r'\|')} |"
        for finding in findings
    ) or "| — | — | — | No findings. |"
    return f"""# GNOME Prompt Field Manual Validation

Source SHA-256: `{metrics.source_sha256}`

## Metrics

- Bytes: **{metrics.bytes}**
- Elements: **{metrics.element_count}**
- Unique IDs: **{metrics.unique_ids}**
- Headings: **{metrics.heading_count}**
- Internal anchors: **{metrics.internal_anchor_count}**
- Local asset references: **{metrics.local_asset_reference_count}**
- External links: **{metrics.external_link_count}**
- Images: **{metrics.image_count}**
- Scripts / styles: **{metrics.script_count} / {metrics.style_count}**
- Errors: **{metrics.error_count}**
- Warnings: **{metrics.warning_count}**

## Findings

| Severity | Code | Line | Detail |
|---|---|---:|---|
{finding_rows}
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("index.html"))
    parser.add_argument("--json", type=Path, default=Path("manual-validation.json"))
    parser.add_argument("--markdown", type=Path, default=Path("manual-validation.md"))
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Return non-zero when warnings are present in addition to errors",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.input.is_file():
        print(f"error: manual not found: {args.input}", file=sys.stderr)
        return 2

    result = validate(args.input)
    payload = {
        "schema_version": 1,
        "metrics": asdict(result.metrics),
        "findings": [asdict(finding) for finding in result.findings],
    }
    for output in (args.json, args.markdown):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown.write_text(markdown_report(result), encoding="utf-8")

    print(json.dumps(asdict(result.metrics), sort_keys=True))
    for finding in result.findings:
        print(
            f"{finding.severity}: {finding.code}: line {finding.line}: {finding.message}",
            file=sys.stderr,
        )

    if result.metrics.error_count:
        return 1
    if args.strict_warnings and result.metrics.warning_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
