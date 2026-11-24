"""Editorial contract and provenance checks. No agent or tool is exercised."""
from collections import Counter
import json
import re
import subprocess
import unittest

from batch6_baseline import PARTIAL_SOURCE_SHA
from batch7_baseline import BATCH7_SOURCE_SHA, PR41_MERGE, ROOT, corrected_sec06_bytes, merged_disposition_bytes
from test_batch6_correction import (
    ADAPTER_PATH, CANONICAL, DATASET, HISTORICAL_ROOTS, INDEX_PATH, STATIC,
    canonical_surface, cards, changed_pages, dataset_rows, digest, parity_errors, visible,
)
from test_batch6_partial_disposition import extract_brief

PAGES = set(range(187, 198))
TITLE = "SEC-06 Tool-Agent Offense Probe"
FIELDS = (
    "defensive purpose", "attack vector description and attack type", "chaining potential",
    "exploitation conditions", "test setup and controls", "expected safe response",
    "observed outcome", "detection signal", "defensive control", "mitigation and retest",
    "evidence provenance", "probe verdict",
)
CATEGORIES = (
    "tool scope escalation", "tool chaining risk", "authority confusion", "loop induction",
    "indirect injection through tool output", "unauthorized action attempt",
    "data exfiltration via side channel", "human confirmation bypass attempt",
    "logging / detection coverage", "safe response expectation",
)
REQUIRED = {
    "scope": (188, (
        "authorization scope", "written scope reference", "isolated environment", "excluded targets and data",
        "if authorization, containment, or the stop owner is missing",
    )),
    "enforcement": (189, (
        "attack surface inventory", "authenticated principal", "policy enforcement point",
        "treat tool output and other untrusted data as data",
    )),
    "controls": (189, ("benign positive control", "negative control", "declare both outcomes in advance")),
    "observation": (190, ("measured before/after state", "never fill observations from expectations",
                          "a detector alert and an enforced denial are separate observations")),
    "provenance": (190, ("run id, timestamp, system and policy version, fixture version",)),
    "verdicts": (192, (
        "not run — the runtime check was not executed", "inconclusive", "preserve a supported fail",
        "scoped run produced the declared safe decision and state", "benign and negative controls behaved as expected",
        "static review, planned test, simulation, or observed runtime result",
    )),
    "output": (193, ("deliver four parts", "ten per-probe records", "the twelve fields", "probe plan summary")),
    "review": (196, ("for every high-severity finding", "enforced human confirmation gate",
                     "send every finding to the named human security reviewer before deploying remediation")),
    "safety": (197, (
        "authorized self-assessment", "unauthorized use", "stop on scope uncertainty",
        "disable external dispatch and side effects beyond the mock environment",
        "attack vector descriptions are for detection and mitigation only",
        "false positives and false negatives", "every attack vector finding must trigger human security review",
    )),
}


def contract_errors(text):
    failures = {key for key, (number, phrases) in REQUIRED.items()
                if any(phrase not in text[number] for phrase in phrases)}
    fields = re.findall(r"(?:^| )\d+\. ([a-z /]+) —", text[189] + " " + text[190])
    if tuple(fields) != FIELDS:
        failures.add("fields")
    categories = re.findall(r"category \d+ — ([a-z /]+)\.", text[190] + " " + text[191])
    if tuple(categories) != CATEGORIES:
        failures.add("categories")
    return failures


class Batch7Sec06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = corrected_sec06_bytes("index.html")
        cls.reader = corrected_sec06_bytes("GNOME-Field-Manual.html")
        cls.base = merged_disposition_bytes("index.html")
        cls.base_reader = merged_disposition_bytes("GNOME-Field-Manual.html")
        cls.pages = cards(cls.raw)
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.encoded = dataset_rows(cls.reader)

    def test_contract_and_negative_regressions(self):
        actual = {n: canonical_surface(visible(self.pages[n])) for n in PAGES}
        self.assertEqual(contract_errors(actual), set())
        previous = cards(self.base)
        baseline = {n: canonical_surface(visible(previous[n])) for n in PAGES}
        self.assertTrue({"fields", "controls", "provenance", "verdicts", "review"} <= contract_errors(baseline))
        for page, phrase, expected in (
            (188, "written scope reference", "scope"),
            (189, "policy enforcement point", "enforcement"),
            (189, "benign positive control", "controls"),
            (190, "observed outcome —", "fields"),
            (190, "run id, timestamp", "provenance"),
            (191, "data exfiltration via side channel", "categories"),
            (192, "benign and negative controls behaved as expected", "verdicts"),
            (196, "for every high-severity finding", "review"),
            (197, "stop on scope uncertainty", "safety"),
        ):
            with self.subTest(requirement=expected):
                self.assertIn(phrase, actual[page])
                self.assertIn(expected, contract_errors({**actual, page: actual[page].replace(phrase, "omitted")}))

    def test_cross_references_match_canonical_headings(self):
        for reference, page, target, heading in (
            ("S-01", 195, 107, "S-01 System Map with Trust Boundaries"),
            ("S-03", 195, 117, "S-03 Failure Mode Inventory"),
            ("S-06", 196, 127, "S-06 Observability Gap Finder"),
            ("SEC-01", 195, 145, "SEC-01 Prompt Injection Recognizer"),
            ("SEC-02", 196, 154, "SEC-02 Prompt Firewall Designer"),
            ("SEC-05", 196, 179, "SEC-05 Command/Data Separator (Refactor)"),
            ("SEC-07", 196, 198, "SEC-07 Human Confirmation Gate Designer"),
            ("SEC-09", 196, 203, "SEC-09 Indirect Injection Tracer"),
            ("CH-09", 188, 270, "CH-09 Agent Build-Break-Harden Chain"),
        ):
            with self.subTest(reference=reference):
                self.assertIn(reference, visible(self.pages[page]))
                self.assertIn(heading, visible(self.pages[target]))
        self.assertIn("STEP 5 →SEC-06 (Tool-Agent Offense Probe)", visible(self.pages[271]))

    def test_sec06_safety_notes_are_the_most_extensive_in_part_v(self):
        corpus = "\n".join(re.sub(
            r"(?m)^\s*(?:GNOME Prompt Field Manual|\d{3})\s*$", "", visible(self.pages[n])
        ) for n in range(145, 209))
        entries = re.split(r"(?m)^\s*(SEC-\d{2}) [^\n]+$", corpus)
        counts = {}
        for name, body in zip(entries[1::2], entries[2::2]):
            notes = body.split("SAFETY NOTES", 1)[1]
            counts[name] = len(re.findall(r"\b\w+\b", re.sub(r"-\s*\n\s*", "", notes)))
        self.assertEqual(len(counts), 10)
        self.assertGreater(counts.pop("SEC-06"), max(counts.values()))

    def test_exact_page_scope_shared_neighbor_and_reader_parity(self):
        before = cards(self.base)
        for old, new in (
            (before, self.pages),
            (cards(self.base_reader, STATIC), self.static),
            (dataset_rows(self.base_reader)[1], self.encoded),
        ):
            self.assertEqual(list(new), list(range(1, 316)))
            self.assertEqual(changed_pages(old, new), PAGES)
        self.assertEqual(CANONICAL.sub(b"", self.raw), CANONICAL.sub(b"", self.base))
        self.assertEqual(DATASET.sub(b"", STATIC.sub(b"", self.reader)),
                         DATASET.sub(b"", STATIC.sub(b"", self.base_reader)))
        self.assertEqual(visible(self.pages[187]).split("  " + TITLE, 1)[0],
                         visible(before[187]).split("  " + TITLE, 1)[0])
        prefix = rb'<div class="source-block"> *SEC-06 Tool-Agent Offense Probe'
        self.assertEqual(re.split(prefix, self.static[187], maxsplit=1)[0],
                         re.split(prefix, cards(self.base_reader, STATIC)[187], maxsplit=1)[0])
        self.assertIn("SEC-07 Human Confirmation Gate Designer", visible(self.pages[198]))
        for n in PAGES:
            with self.subTest(page=n):
                # The untouched SEC-05 prefix in the printed reader has an existing PDF wrap.
                static = self.static[n].replace(b"desig-nated", b"designated", 1) if n == 187 else self.static[n]
                self.assertEqual(parity_errors(n, self.pages[n], self.rows[n], static), set())

    def test_surface_drift_is_rejected(self):
        n = 188
        for surface, card, row, static in (
            ("metadata", self.pages[n].replace(b"authorization scope", b"authorization optional"),
             self.rows[n], self.static[n]),
            ("dynamic", self.pages[n], dict(self.rows[n], text="different"), self.static[n]),
            ("static", self.pages[n], self.rows[n], self.static[n].replace(b"AUTHORIZATION SCOPE", b"OPTIONAL")),
        ):
            with self.subTest(surface=surface):
                self.assertIn(surface, parity_errors(n, card, row, static))

    def test_historical_evidence_and_original_brief_remain_frozen(self):
        self.assertEqual(digest(self.base), PARTIAL_SOURCE_SHA)
        self.assertEqual(extract_brief(self.raw, b"sec06"), extract_brief(self.base, b"sec06"))
        protected = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR41_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        protected.remove(INDEX_PATH)
        for path in protected:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), merged_disposition_bytes(path))

    def test_current_bindings_preserve_inventory_and_body_status(self):
        inventory = json.loads(corrected_sec06_bytes(INDEX_PATH))
        before = json.loads(merged_disposition_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), BATCH7_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH7_SOURCE_SHA}';", corrected_sec06_bytes(ADAPTER_PATH).decode())
        self.assertEqual(inventory["sourceIndexSha256"], BATCH7_SOURCE_SHA)
        self.assertEqual(inventory["counts"], {"pending": 9, "drafted": 82, "total": 91, "pages": 315})
        self.assertEqual(inventory["bodyCoverage"], 0)
        self.assertEqual(Counter(row["status"] for row in inventory["entries"]),
                         Counter({"PENDING": 9, "NON_PENDING": 82}))
        for old, new in zip(before["entries"], inventory["entries"], strict=True):
            self.assertEqual({k: v for k, v in old.items() if k != "titleCandidate"},
                             {k: v for k, v in new.items() if k != "titleCandidate"})
            if old["id"] not in {"CH-09", "SEC-07"}:
                self.assertEqual(old["titleCandidate"], new["titleCandidate"])
        pending = {row["id"] for row in inventory["entries"] if row["pendingInventory"]}
        self.assertTrue({"SEC-05", "SEC-06"} <= pending)
