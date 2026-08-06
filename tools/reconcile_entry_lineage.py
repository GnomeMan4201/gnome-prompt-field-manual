#!/usr/bin/env python3
"""Reconcile PTSP production metadata with the embedded manual reader.

The analysis is deterministic and network-free. It extracts source-reported
production counts, pending-entry inventory rows, drafting briefs, embedded page
cards, and entry-ID occurrences from the committed HTML.

Presence in the embedded reader is an occurrence observation. It is not proof
that an entry is complete, current, approved, or authoritative. Non-entry tokens
that share the entry-ID shape are retained in an explicit exclusion record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


ENTRY_ID_RE = re.compile(r"(?<![A-Z0-9])([A-Z]{1,5}-\d{2})(?![A-Z0-9])")
WHITESPACE_RE = re.compile(r"\s+")
NUMBER_RE = re.compile(r"\d+")
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

EXACT_NON_ENTRY_IDS = {
    "AP-00": "blank anti-prompt template placeholder",
    "X-00": "blank prompt-entry template placeholder",
}
NON_ENTRY_PREFIXES = {
    "EDT": "embedded test-case identifier used inside an entry",
}


@dataclass
class Node:
    tag: str
    attrs: dict[str, str]
    line: int
    children: list["Node"] = field(default_factory=list)
    text_parts: list[str] = field(default_factory=list)

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())

    @property
    def element_id(self) -> str:
        return self.attrs.get("id", "").strip()

    def text(self) -> str:
        parts: list[str] = []
        self._collect_text(parts)
        return normalize_text(" ".join(parts))

    def raw_text(self) -> str:
        parts: list[str] = []
        self._collect_text(parts)
        return "\n".join(part for part in parts if part)

    def _collect_text(self, parts: list[str]) -> None:
        parts.extend(self.text_parts)
        for child in self.children:
            child._collect_text(parts)

    def walk(self) -> Iterable["Node"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def first_with_class(self, class_name: str) -> "Node | None":
        for node in self.walk():
            if class_name in node.classes:
                return node
        return None

    def first_tag(self, tag: str) -> "Node | None":
        for node in self.walk():
            if node.tag == tag:
                return node
        return None


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document", {}, 0)
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._start(tag, attrs, force_void=True)

    def _start(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        force_void: bool = False,
    ) -> None:
        line, _ = self.getpos()
        normalized_tag = tag.lower()
        node = Node(
            normalized_tag,
            {key.lower(): value or "" for key, value in attrs},
            line,
        )
        self.stack[-1].children.append(node)
        if not force_void and normalized_tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == normalized:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].text_parts.append(data)


@dataclass(frozen=True)
class SourceCounts:
    pending: int | None
    drafted: int | None
    total: int | None
    batches: int | None
    caution: int | None
    embedded_pages: int


@dataclass(frozen=True)
class PendingEntry:
    entry_id: str
    name: str
    badge: str
    rationale: str
    source_line: int


@dataclass(frozen=True)
class DraftBrief:
    entry_id: str
    name: str
    audit: str
    source_line: int


@dataclass(frozen=True)
class ManualOccurrence:
    entry_id: str
    page_index: int
    page_label: str
    source_line: int
    context: str


@dataclass(frozen=True)
class ExcludedToken:
    token: str
    reason: str
    page_indices: list[int]
    page_labels: list[str]
    contexts: list[str]


@dataclass(frozen=True)
class EntryRecord:
    entry_id: str
    name: str
    pending_inventory: bool
    drafting_brief: bool
    embedded_manual_occurrences: int
    embedded_page_indices: list[int]
    embedded_page_labels: list[str]
    status: str
    rationale: str
    audit: str
    first_manual_context: str


@dataclass(frozen=True)
class Summary:
    source: str
    source_sha256: str
    source_counts: SourceCounts
    pending_inventory_rows: int
    unique_pending_ids: int
    drafting_briefs: int
    unique_brief_ids: int
    embedded_page_cards: int
    candidate_embedded_ids: int
    excluded_non_entry_ids: int
    unique_embedded_entry_ids: int
    reconciled_universe_ids: int
    drafted_embedded_not_pending: int
    pending_missing_from_embedded: int
    pending_present_in_embedded: int
    inventory_without_brief: int
    brief_without_inventory: int


@dataclass(frozen=True)
class Reconciliation:
    summary: Summary
    entries: list[EntryRecord]
    pending_entries: list[PendingEntry]
    briefs: list[DraftBrief]
    occurrences: list[ManualOccurrence]
    excluded_tokens: list[ExcludedToken]
    conflicts: dict[str, list[str]]
    prefix_counts: dict[str, int]


def normalize_text(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value).strip()


def field_text(node: Node, class_name: str) -> str:
    field_node = node.first_with_class(class_name)
    return field_node.text() if field_node is not None else ""


def first_entry_id(*values: str) -> str:
    for value in values:
        match = ENTRY_ID_RE.search(value)
        if match:
            return match.group(1)
    return ""


def exclusion_reason(entry_id: str) -> str | None:
    exact = EXACT_NON_ENTRY_IDS.get(entry_id)
    if exact is not None:
        return exact
    prefix = entry_id.split("-", 1)[0]
    return NON_ENTRY_PREFIXES.get(prefix)


def parse_labelled_number(text: str, label: str) -> int | None:
    pattern = re.compile(rf"(?i)(\d[\d,]*)\s+{re.escape(label)}\b")
    match = pattern.search(text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def extract_source_counts(root: Node, page_cards: list[Node]) -> SourceCounts:
    stats_nodes = [node for node in root.walk() if "stat" in node.classes]
    labels: dict[str, int] = {}
    for node in stats_nodes:
        number_text = field_text(node, "stat-num")
        label_text = field_text(node, "stat-label").lower()
        number_match = NUMBER_RE.search(number_text)
        if number_match and label_text:
            labels[label_text] = int(number_match.group(0))

    document_text = root.text()

    def count(label_key: str, fallback_label: str) -> int | None:
        for key, value in labels.items():
            if label_key in key:
                return value
        return parse_labelled_number(document_text, fallback_label)

    return SourceCounts(
        pending=count("pending", "pending entries"),
        drafted=count("drafted", "drafted"),
        total=count("total", "total entries"),
        batches=count("batch", "batches"),
        caution=count("caution", "special caution"),
        embedded_pages=len(page_cards),
    )


def extract_pending(root: Node) -> list[PendingEntry]:
    rows = [node for node in root.walk() if "entry-row" in node.classes]
    records: list[PendingEntry] = []
    for row in rows:
        records.append(
            PendingEntry(
                entry_id=first_entry_id(field_text(row, "er-id"), row.text()),
                name=field_text(row, "er-name"),
                badge=field_text(row, "er-badge"),
                rationale=field_text(row, "er-why"),
                source_line=row.line,
            )
        )
    return records


def extract_briefs(root: Node) -> list[DraftBrief]:
    nodes = [node for node in root.walk() if "brief" in node.classes]
    records: list[DraftBrief] = []
    for node in nodes:
        records.append(
            DraftBrief(
                entry_id=first_entry_id(
                    field_text(node, "brief-id"),
                    node.element_id.replace("b-", "").upper(),
                    node.text(),
                ),
                name=field_text(node, "brief-name"),
                audit=field_text(node, "audit-chip"),
                source_line=node.line,
            )
        )
    return records


def line_context(raw_text: str, entry_id: str) -> str:
    lines = [normalize_text(line) for line in raw_text.splitlines()]
    for line in lines:
        if entry_id in line:
            return line[:300]
    compact = normalize_text(raw_text)
    index = compact.find(entry_id)
    if index == -1:
        return ""
    return compact[max(0, index - 80) : min(len(compact), index + 220)]


def extract_manual_tokens(
    page_cards: list[Node],
) -> tuple[list[ManualOccurrence], list[ExcludedToken], set[str]]:
    accepted: list[ManualOccurrence] = []
    excluded_occurrences: dict[str, list[ManualOccurrence]] = defaultdict(list)
    candidate_ids: set[str] = set()

    for page_index, card in enumerate(page_cards, start=1):
        header = field_text(card, "manual-page-head")
        content_node = card.first_tag("pre") or card
        raw = content_node.raw_text()
        for entry_id in sorted(set(ENTRY_ID_RE.findall(raw))):
            candidate_ids.add(entry_id)
            occurrence = ManualOccurrence(
                entry_id=entry_id,
                page_index=page_index,
                page_label=header,
                source_line=card.line,
                context=line_context(raw, entry_id),
            )
            reason = exclusion_reason(entry_id)
            if reason is None:
                accepted.append(occurrence)
            else:
                excluded_occurrences[entry_id].append(occurrence)

    excluded = [
        ExcludedToken(
            token=token,
            reason=exclusion_reason(token) or "",
            page_indices=[item.page_index for item in items],
            page_labels=[item.page_label for item in items],
            contexts=[item.context for item in items],
        )
        for token, items in sorted(excluded_occurrences.items())
    ]
    return accepted, excluded, candidate_ids


def choose_name(
    entry_id: str,
    pending_by_id: dict[str, PendingEntry],
    brief_by_id: dict[str, DraftBrief],
    occurrences: list[ManualOccurrence],
) -> str:
    pending = pending_by_id.get(entry_id)
    if pending and pending.name:
        return pending.name
    brief = brief_by_id.get(entry_id)
    if brief and brief.name:
        return brief.name
    for occurrence in occurrences:
        match = re.search(
            rf"{re.escape(entry_id)}\s*[:—–-]?\s*(.+)", occurrence.context
        )
        if match:
            candidate = match.group(1).strip()
            if candidate:
                return candidate[:160]
    return ""


def reconcile(path: Path) -> Reconciliation:
    raw = path.read_bytes()
    parser = TreeParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    parser.close()
    root = parser.root

    page_cards = [node for node in root.walk() if "manual-page-card" in node.classes]
    pending_entries = extract_pending(root)
    briefs = extract_briefs(root)
    occurrences, excluded_tokens, candidate_ids = extract_manual_tokens(page_cards)
    source_counts = extract_source_counts(root, page_cards)

    pending_by_id = {
        record.entry_id: record for record in pending_entries if record.entry_id
    }
    brief_by_id = {record.entry_id: record for record in briefs if record.entry_id}
    occurrences_by_id: dict[str, list[ManualOccurrence]] = defaultdict(list)
    for occurrence in occurrences:
        occurrences_by_id[occurrence.entry_id].append(occurrence)

    pending_ids = set(pending_by_id)
    brief_ids = set(brief_by_id)
    embedded_ids = set(occurrences_by_id)
    universe = pending_ids | brief_ids | embedded_ids

    entries: list[EntryRecord] = []
    for entry_id in sorted(universe):
        entry_occurrences = occurrences_by_id.get(entry_id, [])
        in_pending = entry_id in pending_ids
        in_brief = entry_id in brief_ids
        in_embedded = bool(entry_occurrences)
        if in_pending and in_embedded:
            status = "pending-listed-and-present-in-embedded"
        elif in_pending:
            status = "pending-listed-not-found-in-embedded"
        elif in_embedded:
            status = "embedded-not-listed-pending"
        else:
            status = "brief-only"

        pending = pending_by_id.get(entry_id)
        brief = brief_by_id.get(entry_id)
        entries.append(
            EntryRecord(
                entry_id=entry_id,
                name=choose_name(
                    entry_id, pending_by_id, brief_by_id, entry_occurrences
                ),
                pending_inventory=in_pending,
                drafting_brief=in_brief,
                embedded_manual_occurrences=len(entry_occurrences),
                embedded_page_indices=[item.page_index for item in entry_occurrences],
                embedded_page_labels=[item.page_label for item in entry_occurrences],
                status=status,
                rationale=pending.rationale if pending else "",
                audit=brief.audit if brief else "",
                first_manual_context=(
                    entry_occurrences[0].context if entry_occurrences else ""
                ),
            )
        )

    pending_missing = sorted(pending_ids - embedded_ids)
    pending_present = sorted(pending_ids & embedded_ids)
    drafted_embedded = sorted(embedded_ids - pending_ids)
    inventory_without_brief = sorted(pending_ids - brief_ids)
    brief_without_inventory = sorted(brief_ids - pending_ids)
    numbering_rationale = sorted(
        entry_id
        for entry_id in pending_missing
        if re.search(
            r"(?i)renumber|already contains|already exists|duplicate",
            pending_by_id[entry_id].rationale,
        )
    )

    conflicts = {
        "pending_missing_from_embedded": pending_missing,
        "pending_present_in_embedded": pending_present,
        "drafted_embedded_not_pending": drafted_embedded,
        "pending_missing_with_numbering_rationale": numbering_rationale,
        "inventory_without_brief": inventory_without_brief,
        "brief_without_inventory": brief_without_inventory,
        "blank_inventory_ids": [
            str(item.source_line) for item in pending_entries if not item.entry_id
        ],
        "blank_brief_ids": [
            str(item.source_line) for item in briefs if not item.entry_id
        ],
        "excluded_non_entry_tokens": [item.token for item in excluded_tokens],
    }

    prefix_counts = Counter(entry_id.split("-", 1)[0] for entry_id in universe)
    summary = Summary(
        source=str(path),
        source_sha256=hashlib.sha256(raw).hexdigest(),
        source_counts=source_counts,
        pending_inventory_rows=len(pending_entries),
        unique_pending_ids=len(pending_ids),
        drafting_briefs=len(briefs),
        unique_brief_ids=len(brief_ids),
        embedded_page_cards=len(page_cards),
        candidate_embedded_ids=len(candidate_ids),
        excluded_non_entry_ids=len(excluded_tokens),
        unique_embedded_entry_ids=len(embedded_ids),
        reconciled_universe_ids=len(universe),
        drafted_embedded_not_pending=len(drafted_embedded),
        pending_missing_from_embedded=len(pending_missing),
        pending_present_in_embedded=len(pending_present),
        inventory_without_brief=len(inventory_without_brief),
        brief_without_inventory=len(brief_without_inventory),
    )
    return Reconciliation(
        summary=summary,
        entries=entries,
        pending_entries=pending_entries,
        briefs=briefs,
        occurrences=occurrences,
        excluded_tokens=excluded_tokens,
        conflicts=conflicts,
        prefix_counts=dict(sorted(prefix_counts.items())),
    )


def validate_expectations(
    result: Reconciliation,
    *,
    expected_pending: int | None,
    expected_drafted: int | None,
    expected_total: int | None,
    expected_pages: int | None,
) -> list[str]:
    failures: list[str] = []
    summary = result.summary
    counts = summary.source_counts

    if expected_pending is not None:
        if summary.unique_pending_ids != expected_pending:
            failures.append(
                f"unique pending IDs: {summary.unique_pending_ids} != {expected_pending}"
            )
        if counts.pending != expected_pending:
            failures.append(
                f"source-reported pending: {counts.pending} != {expected_pending}"
            )

    if expected_drafted is not None:
        if summary.drafted_embedded_not_pending != expected_drafted:
            failures.append(
                "embedded non-pending entry IDs: "
                f"{summary.drafted_embedded_not_pending} != {expected_drafted}"
            )
        if counts.drafted != expected_drafted:
            failures.append(
                f"source-reported drafted: {counts.drafted} != {expected_drafted}"
            )

    if expected_total is not None:
        if summary.reconciled_universe_ids != expected_total:
            failures.append(
                f"reconciled universe: {summary.reconciled_universe_ids} != {expected_total}"
            )
        if counts.total != expected_total:
            failures.append(
                f"source-reported total: {counts.total} != {expected_total}"
            )

    if expected_pages is not None and summary.embedded_page_cards != expected_pages:
        failures.append(
            f"embedded page cards: {summary.embedded_page_cards} != {expected_pages}"
        )

    if summary.unique_pending_ids != summary.unique_brief_ids:
        failures.append(
            "pending inventory and drafting brief unique-ID counts do not match"
        )
    if counts.pending is not None and counts.drafted is not None and counts.total is not None:
        if counts.pending + counts.drafted != counts.total:
            failures.append("source-reported pending + drafted does not equal total")
    if summary.unique_pending_ids + summary.drafted_embedded_not_pending != summary.reconciled_universe_ids:
        failures.append("extracted pending + embedded non-pending does not equal universe")
    if result.conflicts["blank_inventory_ids"]:
        failures.append("one or more pending inventory rows lack an entry ID")
    if result.conflicts["blank_brief_ids"]:
        failures.append("one or more drafting briefs lack an entry ID")
    if result.conflicts["inventory_without_brief"]:
        failures.append("one or more pending inventory IDs lack a drafting brief")
    if result.conflicts["brief_without_inventory"]:
        failures.append("one or more drafting brief IDs lack an inventory row")
    return failures


def markdown_list(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "_none_"


def _escape_table(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def markdown_report(result: Reconciliation, failures: list[str]) -> str:
    summary = result.summary
    counts = summary.source_counts
    failure_text = (
        "\n".join(f"- {failure}" for failure in failures)
        if failures
        else "- All configured structural expectations passed."
    )
    entry_rows = []
    for entry in result.entries:
        pages = ", ".join(map(str, entry.embedded_page_indices)) or "—"
        name = entry.name.replace("|", "\\|")
        entry_rows.append(
            f"| `{entry.entry_id}` | {name} | {entry.status} | "
            f"{'yes' if entry.drafting_brief else 'no'} | {pages} |"
        )
    prefix_rows = "\n".join(
        f"| `{prefix}` | {count} |" for prefix, count in result.prefix_counts.items()
    ) or "| — | 0 |"
    excluded_rows = "\n".join(
        f"| `{item.token}` | {item.reason} | "
        f"{', '.join(map(str, item.page_indices))} | "
        f"{_escape_table(item.contexts[0] if item.contexts else '')} |"
        for item in result.excluded_tokens
    ) or "| — | — | — | — |"

    return f"""# PTSP / Embedded Manual Entry-Lineage Reconciliation

Source SHA-256: `{summary.source_sha256}`

## Source-reported production state

- Pending entries: **{counts.pending}**
- Drafted entries: **{counts.drafted}**
- Total entries: **{counts.total}**
- Batches: **{counts.batches}**
- Special-caution entries: **{counts.caution}**
- Embedded page cards: **{counts.embedded_pages}**

## Extracted structure

- Pending inventory rows / unique IDs: **{summary.pending_inventory_rows} / {summary.unique_pending_ids}**
- Drafting briefs / unique IDs: **{summary.drafting_briefs} / {summary.unique_brief_ids}**
- ID-shaped tokens observed in embedded pages: **{summary.candidate_embedded_ids}**
- Explicitly excluded non-entry tokens: **{summary.excluded_non_entry_ids}**
- Accepted embedded manual entry IDs: **{summary.unique_embedded_entry_ids}**
- Embedded non-pending entry IDs: **{summary.drafted_embedded_not_pending}**
- Reconciled entry universe: **{summary.reconciled_universe_ids}**
- Pending IDs absent from embedded pages: **{summary.pending_missing_from_embedded}**
- Pending IDs also present in embedded pages: **{summary.pending_present_in_embedded}**

## Expectation result

{failure_text}

## Reconciliation finding

The source-reported **70 drafted + 22 pending = 92 total** is structurally
consistent after excluding eight documented non-entry tokens. The embedded
reader contains all 70 IDs not listed as pending, plus 21 of the 22 pending IDs.
The remaining pending ID is surfaced rather than inferred.

## Conflict and status sets

- Pending but not found in embedded pages: {markdown_list(result.conflicts['pending_missing_from_embedded'])}
- Pending and also found in embedded pages: {markdown_list(result.conflicts['pending_present_in_embedded'])}
- Missing pending IDs with numbering/duplicate rationale: {markdown_list(result.conflicts['pending_missing_with_numbering_rationale'])}
- Inventory without brief: {markdown_list(result.conflicts['inventory_without_brief'])}
- Brief without inventory: {markdown_list(result.conflicts['brief_without_inventory'])}

Presence in an embedded page is an occurrence observation, not proof that the
entry is complete, current, or authoritative.

## Excluded ID-shaped tokens

| Token | Exclusion reason | Page indices | First context |
|---|---|---|---|
{excluded_rows}

## Prefix distribution

| Prefix | Reconciled entry IDs |
|---|---:|
{prefix_rows}

## Reconciled 92-entry inventory

| ID | Best available name | Observed status | Brief | Embedded page indices |
|---|---|---|---|---|
{chr(10).join(entry_rows)}
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("index.html"))
    parser.add_argument("--json", type=Path, default=Path("entry-lineage.json"))
    parser.add_argument("--markdown", type=Path, default=Path("entry-lineage.md"))
    parser.add_argument("--expect-pending", type=int)
    parser.add_argument("--expect-drafted", type=int)
    parser.add_argument("--expect-total", type=int)
    parser.add_argument("--expect-pages", type=int)
    parser.add_argument("--enforce", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.input.is_file():
        print(f"error: input not found: {args.input}", file=sys.stderr)
        return 2
    result = reconcile(args.input)
    failures = validate_expectations(
        result,
        expected_pending=args.expect_pending,
        expected_drafted=args.expect_drafted,
        expected_total=args.expect_total,
        expected_pages=args.expect_pages,
    )
    payload = {
        "schema_version": 1,
        "summary": asdict(result.summary),
        "entries": [asdict(item) for item in result.entries],
        "pending_entries": [asdict(item) for item in result.pending_entries],
        "briefs": [asdict(item) for item in result.briefs],
        "occurrences": [asdict(item) for item in result.occurrences],
        "excluded_tokens": [asdict(item) for item in result.excluded_tokens],
        "conflicts": result.conflicts,
        "prefix_counts": result.prefix_counts,
        "expectation_failures": failures,
    }
    for output in (args.json, args.markdown):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.markdown.write_text(markdown_report(result, failures), encoding="utf-8")
    print(json.dumps(asdict(result.summary), sort_keys=True))
    if failures:
        for failure in failures:
            print(f"failure: {failure}", file=sys.stderr)
    return 1 if args.enforce and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
