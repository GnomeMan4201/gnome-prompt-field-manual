"""Manuscript/provenance checks and offline authorization reference controls."""
import json
import re
import subprocess
import unittest

from batch6_baseline import FINAL_SOURCE_SHA, PR39_MERGE, ROOT, adjudication_bytes, correction_bytes
from examples.batch6_runtime_policy import CounterBoundary, Outcome, run_controls, verify_controls
from test_batch6_correction import (
    ADAPTER_PATH, CANONICAL, DATASET, HISTORICAL_ROOTS, INDEX_PATH, STATIC, canonical_surface,
    cards, changed_pages, contract_errors, dataset_rows, digest, parity_errors, visible,
)

PAGES = {154, 156, 158}
PR39_EVIDENCE = "docs/BATCH6_PR39_EVIDENCE_2026-11-24.md"
PR39_EVIDENCE_SHA = "f16126becf6c44c1ac30dff2da70227295b62b99558742c9db3414a0e01e3c0c"
UNSUPPORTED = re.compile(
    r"injection has caused|deploys canary tokens to detect policy escape|"
    r"canary trigger — should fire escalation|canary fires, critical injection signals|"
    r"(?:match|trigger) (?:alone )?(?:proves|confirms|establishes|demonstrates) (?:an? )?injection"
)


def canary_errors(pages):
    messages = set()
    body = {n: canonical_surface(visible(pages[n])) for n in range(154, 163)}
    if any(UNSUPPORTED.search(text) for text in body.values()):
        messages.add("unsupported attribution")
    for n, required in {
        154: ("canary observations to flag possible policy escape for review",),
        156: (
            "exact match —", "fragment match —", "pattern-only match —",
            "potential unauthorized disclosure —", "corroborated injection evidence —",
            "evidence classification, confidence limitations, alternative explanations, and appropriate response",
            "legitimate reproduction", "accidental collision", "contaminated logs", "authorized testing",
            "may trigger quarantine or investigation", "a match alone does not establish injection",
            "require independent, trustworthy evidence connecting untrusted input",
        ),
        158: (
            "canary investigation from corroborated injection evidence",
            "verify the evidence class and policy response", "exact match from an authorized test",
        ),
    }.items():
        if any(phrase not in body[n] for phrase in required):
            messages.add(f"missing evidence requirement on page {n}")
    return messages


def history_changes(paths, read_current):
    return {path for path in paths if read_current(path) != correction_bytes(path)}


class CanaryAndSourceTests(unittest.TestCase):
    """Verify PR #40 on its pinned adjudication tree."""
    @classmethod
    def setUpClass(cls):
        cls.raw = adjudication_bytes("index.html")
        cls.reader = adjudication_bytes("GNOME-Field-Manual.html")
        cls.pages = cards(cls.raw)
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.serialized = dataset_rows(cls.reader)

    def test_canary_attribution_and_prior_contracts(self):
        self.assertEqual(canary_errors(self.pages), set())
        self.assertEqual(contract_errors(self.pages), set())

    def test_restoring_old_causal_claims_is_rejected(self):
        old = cards(correction_bytes("index.html"))
        for n in PAGES:
            with self.subTest(page=n):
                self.assertIn("unsupported attribution", canary_errors({**self.pages, n: old[n]}))
        page = dict(self.pages)
        page[156] = re.sub(
            rb"A match alone does not establish\s+injection\.", b"A match alone proves injection.", page[156]
        )
        self.assertIn("unsupported attribution", canary_errors(page))

    def test_requires_independent_evidence_and_alternative_explanations(self):
        for clause in (rb"independent, trustworthy\s+evidence", b"accidental collision, contaminated logs"):
            with self.subTest(clause=clause):
                page = dict(self.pages)
                page[156] = re.sub(clause, b"unavailable", page[156])
                self.assertIn("missing evidence requirement on page 156", canary_errors(page))

    def test_reader_parity_and_exact_scope_from_pr39(self):
        historical_index = correction_bytes("index.html")
        historical_reader = correction_bytes("GNOME-Field-Manual.html")
        for old, new in (
            (cards(historical_index), self.pages),
            (cards(historical_reader, STATIC), self.static),
            (dataset_rows(historical_reader)[1], self.serialized),
        ):
            self.assertEqual(list(new), list(range(1, 316)))
            self.assertEqual(changed_pages(old, new), PAGES)
        self.assertEqual(CANONICAL.sub(b"", self.raw), CANONICAL.sub(b"", historical_index))
        self.assertEqual(DATASET.sub(b"", STATIC.sub(b"", self.reader)),
                         DATASET.sub(b"", STATIC.sub(b"", historical_reader)))
        for n in PAGES:
            with self.subTest(page=n):
                self.assertEqual(parity_errors(n, self.pages[n], self.rows[n], self.static[n]), set())

    def test_reader_divergence_on_each_surface_is_detected(self):
        n = 156
        canonical, row, static = self.pages[n], self.rows[n], self.static[n]
        for expected, c, d, s in (
            ("metadata", canonical.replace(b"pattern-only match", b"incorrect"), row, static),
            ("metadata", canonical.replace(b"PATTERN-ONLY MATCH", b"INCORRECT"), row, static),
            ("dynamic", canonical, dict(row, text="incorrect", textSha256=digest(b"incorrect")), static),
            ("static", canonical, row, static.replace(b"PATTERN-ONLY MATCH", b"INCORRECT")),
        ):
            with self.subTest(surface=expected):
                self.assertIn(expected, parity_errors(n, c, d, s))

    def test_merged_evidence_and_prior_historical_files_remain_frozen(self):
        paths = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR39_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        paths.remove(INDEX_PATH)
        self.assertEqual(history_changes(paths, lambda path: (ROOT / path).read_bytes()), set())
        self.assertEqual(digest((ROOT / PR39_EVIDENCE).read_bytes()), PR39_EVIDENCE_SHA)

    def test_altered_historical_artifact_is_detected(self):
        path = "workbench/data/adjudication_queue.json"
        self.assertEqual(history_changes([path], lambda p: correction_bytes(p) + b" "), {path})

    def test_current_identity_is_bound_to_actual_bytes_without_promotion(self):
        identity = json.loads(adjudication_bytes(INDEX_PATH))
        historical = json.loads(correction_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), FINAL_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{FINAL_SOURCE_SHA}';", adjudication_bytes(ADAPTER_PATH).decode())
        self.assertNotEqual(identity["sourceIndexSha256"], historical["sourceIndexSha256"])
        self.assertEqual(identity, dict(historical, sourceIndexSha256=FINAL_SOURCE_SHA))


class RuntimePolicyFixtureTests(unittest.TestCase):
    def test_reference_policy_captures_both_actual_outcomes(self):
        outcomes = run_controls(CounterBoundary())
        verify_controls(outcomes)
        self.assertEqual(outcomes, (
            Outcome("unauthorized", "denied", 0, 0),
            Outcome("authorized", "allowed", 0, 1),
        ))

    def test_disabled_enforcement_cannot_pass(self):
        class Disabled(CounterBoundary):
            def authorize(self, caller, operation):
                return True

        outcomes = run_controls(Disabled())
        self.assertEqual(outcomes[0], Outcome("unauthorized", "allowed", 0, 1))
        with self.assertRaisesRegex(ValueError, "Runtime controls failed"):
            verify_controls(outcomes)

    def test_reject_all_cannot_pass(self):
        class RejectAll(CounterBoundary):
            def authorize(self, caller, operation):
                return False

        outcomes = run_controls(RejectAll())
        self.assertEqual(outcomes[1], Outcome("authorized", "denied", 0, 0))
        with self.assertRaisesRegex(ValueError, "Runtime controls failed"):
            verify_controls(outcomes)

    def test_missing_positive_control_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "Runtime controls failed"):
            verify_controls(run_controls(CounterBoundary())[:1])
