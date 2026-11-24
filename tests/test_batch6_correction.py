"""Source and manuscript-contract checks. These do not execute a firewall or separator."""
from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import subprocess
import unittest

from batch6_baseline import BASELINE_COMMIT, CURRENT_SOURCE_SHA, ROOT, baseline_bytes, correction_bytes
from tools.audit_editorial_lineage import EXPECTED_PDF_SHA256, canonical_surface

PAGES = {133, 157, 158, 159, 161, 182, 184}
CANONICAL = re.compile(rb'<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>', re.S)
STATIC = re.compile(rb'<article class="book-page(?: print-spacer)?" id="page-(\d+)">.*?</article>', re.S)
DATASET = re.compile(rb"(?m)^      var BOOK_PAGES = (.+);$")
INDEX_PATH = "workbench/data/current_entry_identity_index.json"
ADAPTER_PATH = "workbench/reactor/source-adapter.js"
HISTORICAL_ROOTS = ["docs", "research", "examples", "tests/fixtures", "workbench/data", "workbench/adjudication"]

DIMENSIONS = [
    "compatibility", "schema/contract", "dependency", "ordering/sequencing",
    "rollback", "observability", "user/downstream impact", "detectability",
]
ALERT_FIELDS = [
    "observable metric or event", "measurement method", "threshold or trigger condition",
    "observation window", "minimum sample size", "evidence source",
    "associated response", "responsible decision owner",
]
FIREWALL_SECTIONS = [
    "threat model", "trust boundaries", "input classification table", "canary strategy",
    "behavioral baseline", "escalation/quarantine policy", "fallback behavior", "firewall test plan",
]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def cards(raw, pattern=CANONICAL):
    matches = list(pattern.finditer(raw))
    result = {int(match[1]): match[0] for match in matches}
    if len(result) != len(matches):
        raise ValueError("duplicate page")
    return result


def visible(card):
    return html.unescape(re.search(rb"<pre>(.*?)</pre>", card, re.S)[1].decode())


def search_metadata(text):
    return " ".join(text.lower().split())


def static_text(card):
    body = re.search(rb'<div class="book-prose typeset-body">(.*)</div><a href="#page-directory">', card, re.S)[1]
    return html.unescape(re.sub(rb"<[^>]+>", b" ", body).decode()).strip()


def changed_pages(before, after):
    return {n for n in before.keys() | after.keys() if before.get(n) != after.get(n)}


def dataset_rows(raw):
    dataset = DATASET.search(raw)[1].decode()
    decoder = json.JSONDecoder()
    cursor = 1
    rows, encoded = {}, {}
    while cursor < len(dataset) - 1:
        row, end = decoder.raw_decode(dataset, cursor)
        n = row["pageNumber"]
        if n in rows:
            raise ValueError("duplicate dataset page")
        rows[n] = row
        encoded[n] = dataset[cursor:end]
        cursor = end + 1
    return rows, encoded


def contract_errors(pages):
    errors = set()
    plain = {n: canonical_surface(visible(pages[n])) for n in PAGES}
    dims = re.search(r"eight risk dimension assessments \(([^)]+)\)", plain[133])
    if not dims or dims[1].split(", ") != DIMENSIONS:
        errors.add("dimensions")

    fields = re.findall(r"(?:^| )(\d+)\. ([a-z /]+) —", plain[157])
    if fields != [(str(i), name) for i, name in enumerate(ALERT_FIELDS, 1)]:
        errors.add("alert fields")
    for phrase in (
        "[requires operational confirmation]", "deterministic policy violation", "statistical anomalies",
        "contamination", "drift", "monitor health", "false positives", "false negatives",
    ):
        if phrase not in plain[157]:
            errors.add("baseline safeguards")
    sections = re.findall(r"(?:^| )(\d+)\. ([a-z /]+) \(", plain[159])
    if ("eight structured sections" not in plain[159]
            or sections != [(str(i), name) for i, name in enumerate(FIREWALL_SECTIONS, 1)]):
        errors.add("firewall output")
    for phrase in ("safe degradation", "monitoring", "quarantine", "block", "escalation", "never silently fail open"):
        if phrase not in plain[158]:
            errors.add("fallback behavior")

    for ref, target, title in (
        ("sec-09", 203, "indirect injection tracer"),
        ("sec-10", 205, "trust boundary mapper (security)"),
    ):
        if (f"{ref} ({title}, page {target})" not in plain[161]
                or f"{ref} {title}" not in canonical_surface(visible(pages[target]))):
            errors.add("cross-references")

    cases = re.findall(r"\bedt-(\d{2}):", plain[182])
    if cases != [f"{i:02d}" for i in range(7)] or any(phrase not in plain[182] for phrase in (
        "representative non-empty benign input", "the input is accepted", "leaves instructions unchanged",
        "expected legitimate result", "a reject-all implementation must fail",
    )):
        errors.add("test cases")
    if any(phrase not in plain[182] for phrase in (
        "provide executable structural tests for edt-00 through edt-05",
        "actual refactored separation mechanism", "imports, setup, assertions, execution commands, and expected results",
        "real interfaces", "mark affected tests blocked",
    )):
        errors.add("executable tests")
    if ("seven cases, edt-00 through edt-06" not in plain[184]
            or "executable structural tests for edt-00 through edt-05" not in plain[184]):
        errors.add("separator output")
    if ("edt-06: category-only description, with no payload or executable fixture" not in plain[182]
            or "describe category only, no payload" not in canonical_surface(visible(pages[183]))
            or any(phrase not in plain[182] for phrase in (
                "structural separation", "parser correctness", "runtime enforcement", "model interpretation",
                "empirical resistance to injection requires separate behavioral evidence",
            ))):
        errors.add("claims and payload boundary")
    return errors


def parity_errors(number, canonical_card, row, static_card):
    text = visible(canonical_card)
    metadata = html.unescape(re.search(rb'data-manual-text="([^"]*)"', canonical_card)[1].decode())
    errors = set()
    if metadata != search_metadata(text):
        errors.add("metadata")
    if row["text"] != text or row["textSha256"] != digest(text.encode()):
        errors.add("dynamic")
    printed_text = re.sub(fr"\s+{number}$", "", text)
    if canonical_surface(static_text(static_card)) != canonical_surface(printed_text):
        errors.add("static")
    return errors


def changed_historical_files(paths, read_current):
    return {path for path in paths if digest(read_current(path)) != digest(baseline_bytes(path))}


def source_errors(raw, identity, adapter):
    actual = digest(raw)
    errors = set()
    if (actual != CURRENT_SOURCE_SHA or identity["sourceIndexSha256"] != actual
            or f"const EXPECTED_SOURCE='{actual}';" not in adapter):
        errors.add("stale source")
    return errors


def editorial_errors(raw, identity, old_raw, old_identity):
    # Editorial rows, briefs, batch counts and handlers are all outside the page cards.
    if CANONICAL.sub(b"", raw) != CANONICAL.sub(b"", old_raw):
        return {"editorial surfaces"}
    old_rows = {entry["id"]: entry for entry in old_identity["entries"]}
    rows = {entry["id"]: entry for entry in identity["entries"]}
    if (identity["counts"] != {"pending": 10, "drafted": 81, "total": 91, "pages": 315}
            or identity["bodyCoverage"] != 0 or rows.keys() != old_rows.keys()):
        return {"editorial identity"}
    for key, old in old_rows.items():
        expected = dict(old)
        if key in {"SEC-09", "SEC-10"}:
            expected["occurrencePages"] = sorted(set(old["occurrencePages"]) | {161})
        if rows[key] != expected:
            return {"editorial identity"}
    return set()


class Batch6CorrectionTests(unittest.TestCase):
    """Verify the original correction on its pinned merged source tree."""
    @classmethod
    def setUpClass(cls):
        cls.raw = correction_bytes("index.html")
        cls.reader = correction_bytes("GNOME-Field-Manual.html")
        cls.old_raw = baseline_bytes("index.html")
        cls.old_reader = baseline_bytes("GNOME-Field-Manual.html")
        cls.canonical = cards(cls.raw)
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.encoded = dataset_rows(cls.reader)
        cls.identity = json.loads(correction_bytes(INDEX_PATH))
        cls.old_identity = json.loads(baseline_bytes(INDEX_PATH))
        cls.adapter = correction_bytes(ADAPTER_PATH).decode()

    def test_manuscript_contract(self):
        self.assertEqual(contract_errors(self.canonical), set())

    def test_manuscript_contract_detects_missing_requirements(self):
        mutations = [
            (133, "SCHEMA/CONTRACT,", "SCHEMA/CONTRACT", "dimensions"),
            (133, "DEPENDENCY,", "ROLLBACK,", "dimensions"),
            (159, "7. FALLBACK BEHAVIOR", "7. USER MESSAGING", "firewall output"),
            (161, "SEC-09 (Indirect Injection Tracer", "SEC-09 (Follow-up", "cross-references"),
            (161, "SEC-10 (Trust Boundary Mapper", "SEC-10 (Mapping", "cross-references"),
            (182, "EDT-00: Use", "Use", "test cases"),
            (182, "Provide executable structural tests", "Describe structural cases", "executable tests"),
            (184, "with pass/fail conditions and executable", "with pass/fail conditions and optional", "separator output"),
        ]
        mutations.extend((157, field.upper(), "UNSPECIFIED", "alert fields") for field in ALERT_FIELDS)
        for n, before, after, missing in mutations:
            with self.subTest(page=n, missing=before):
                def mutate(match):
                    return match[0].replace(before.encode(), after.encode(), 1)
                changed = dict(self.canonical)
                changed[n] = re.sub(rb"<pre>.*?</pre>", mutate, changed[n], flags=re.S)
                self.assertNotEqual(changed[n], self.canonical[n])
                self.assertIn(missing, contract_errors(changed))

    def test_four_reader_surfaces_agree(self):
        for n in sorted(PAGES):
            with self.subTest(page=n):
                self.assertEqual(parity_errors(n, self.canonical[n], self.rows[n], self.static[n]), set())
                self.assertEqual(self.rows[n]["idTokens"], sorted(set(re.findall(
                    r'\b(?:AP|EDT|P|R|S|SEC|T|W)-\d{2}\b', visible(self.canonical[n])
                ))))

    def test_reader_parity_detects_independent_divergence(self):
        n = 157
        card, row, static = self.canonical[n], self.rows[n], self.static[n]
        for name, changed_card, changed_row, changed_static in (
            ("metadata", card.replace(b"observable metric or event", b"unrelated field"), row, static),
            ("metadata", card.replace(b"OBSERVABLE METRIC OR EVENT", b"UNRELATED FIELD"), row, static),
            ("dynamic", card, dict(row, text="different data", textSha256=digest(b"different data")), static),
            ("static", card, row, static.replace(b"OBSERVABLE METRIC OR EVENT", b"UNRELATED FIELD")),
        ):
            with self.subTest(surface=name):
                self.assertIn(name, parity_errors(n, changed_card, changed_row, changed_static))

    def test_exact_page_and_reader_scope(self):
        for old, new in (
            (cards(self.old_raw), self.canonical),
            (cards(self.old_reader, STATIC), self.static),
            (dataset_rows(self.old_reader)[1], self.encoded),
        ):
            self.assertEqual(sorted(old), list(range(1, 316)))
            self.assertEqual(list(old), list(new))
            self.assertEqual(changed_pages(old, new), PAGES)
        self.assertEqual(
            DATASET.sub(b"", STATIC.sub(b"", self.reader)),
            DATASET.sub(b"", STATIC.sub(b"", self.old_reader)),
        )

    def test_scope_detects_unauthorized_page_edit(self):
        mutated = dict(self.canonical)
        mutated[140] += b" "
        self.assertEqual(changed_pages(cards(self.old_raw), mutated) - PAGES, {140})

    def test_historical_evidence_and_queue_bindings(self):
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", BASELINE_COMMIT, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        paths.remove(INDEX_PATH)
        self.assertEqual(changed_historical_files(paths, lambda path: (ROOT / path).read_bytes()), set())
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf, validate=True)), EXPECTED_PDF_SHA256)

    def test_detects_historical_record_or_evidence_modified(self):
        for path in ("docs/BATCH5_DISPOSITION_2026-11-23.md", "workbench/data/adjudication_queue.json",
                     "tests/fixtures/batch3-canonical-1f06445e.html"):
            with self.subTest(path=path):
                self.assertEqual(changed_historical_files([path], lambda _: baseline_bytes(path) + b" "), {path})

    def test_current_source_binding(self):
        self.assertEqual(source_errors(self.raw, self.identity, self.adapter), set())

    def test_rejects_stale_index_adapter_and_self_consistent_unapproved_source(self):
        old_sha = self.old_identity["sourceIndexSha256"]
        self.assertEqual(source_errors(self.raw, self.old_identity, self.adapter), {"stale source"})
        self.assertEqual(source_errors(self.raw, self.identity, self.adapter.replace(CURRENT_SOURCE_SHA, old_sha)),
                         {"stale source"})
        self.assertEqual(source_errors(self.old_raw, self.old_identity, self.adapter.replace(CURRENT_SOURCE_SHA, old_sha)),
                         {"stale source"})

    def test_no_editorial_promotion(self):
        self.assertEqual(editorial_errors(self.raw, self.identity, self.old_raw, self.old_identity), set())

    def test_rejects_editorial_promotion(self):
        promoted = self.raw.replace(b'id="b-sec02"', b'id="b-sec02-promoted"', 1)
        self.assertEqual(editorial_errors(promoted, self.identity, self.old_raw, self.old_identity),
                         {"editorial surfaces"})
        altered = dict(self.identity, entries=[
            dict(entry, status="NON_PENDING") if entry["id"] == "SEC-05" else entry
            for entry in self.identity["entries"]
        ])
        self.assertEqual(editorial_errors(self.raw, altered, self.old_raw, self.old_identity),
                         {"editorial identity"})
