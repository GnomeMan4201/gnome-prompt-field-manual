"""Manuscript contract checks for the P-01 scaffold and P-02 learning inventory."""
import json
import re
import subprocess
import unittest

from batch7_baseline import BATCH7_DISPOSITION_SOURCE_SHA
from batch8_baseline import BATCH8_SOURCE_SHA, PR43_MERGE, ROOT, batch8_base_bytes, corrected_batch8_bytes
from test_batch6_correction import (
    ADAPTER_PATH, CANONICAL, DATASET, HISTORICAL_ROOTS, INDEX_PATH, STATIC,
    canonical_surface, cards, changed_pages, dataset_rows, digest, parity_errors, visible,
)
from test_batch6_partial_disposition import extract_brief

PAGES = set(range(209, 217))
P01_SLOTS = (
    "what was built/done", "one thing that worked", "one thing that didn’t work",
    "what was learned", "next step",
)
P02_SECTIONS = (
    "NEW UNDERSTANDINGS", "DISPROVEN ASSUMPTIONS", "REVERSAL CONDITIONS",
    "OPEN QUESTIONS GENERATED", "NON-LEARNING FILTER",
)
REQUIREMENTS = {
    "p01-scaffold": (210, ("fill-in-the-blank content skeleton", "do not assemble a post")),
    "p01-failure": (211, ("[missing: observed failure]", "keep the scaffold blocked", "keep all five labels visible")),
    "p01-evidence": (211, (
        "link each factual claim to supplied evidence", "flag unverified assumptions",
        "what i am not claiming yet", "no flags with the checks performed",
    )),
    "p02-prior": (213, (
        "[prior assumption unconfirmed]", "pending evidence or confirmation",
        "do not reconstruct a prior belief from its outcome",
    )),
    "p02-update": (214, (
        "evidence for update", "confidence level", "cite a supplied source locator", "relevant confounds",
    )),
    "p02-disproof": (214, (
        "this section is mandatory", "distinguish disproven from weakened",
        "experimental or uncertain work is covered", "at least one evidenced disproof",
        "[disproof not established]", "inventory incomplete",
    )),
    "p02-reversal": (214, (
        "for every accepted learning", "observable finding", "name the decision that would change",
        "[reversal condition missing]",
    )),
    "p02-filter": (214, (
        "activity logged, no learning extracted", "missing prior beliefs", "reasonable alternative explanations",
    )),
}


def contract_errors(text):
    clean = {number: canonical_surface(body) for number, body in text.items()}
    failures = {key for key, (page, required) in REQUIREMENTS.items()
                if any(phrase not in clean[page] for phrase in required)}
    if any("final post draft" in clean[n] for n in range(209, 213)):
        failures.add("p01-scaffold")
    if "reconstruct it from what the observation contradicts" in clean[214]:
        failures.add("p02-prior")
    slots = re.findall(r"(?:^| )(\d+)\. ([a-z/ ’]+) —", clean[210])
    if tuple(slots) != tuple((str(i), slot) for i, slot in enumerate(P01_SLOTS, 1)):
        failures.add("p01-slots")
    section_headers = tuple(line.strip() for line in text[214].splitlines()
                            if line.strip() in P02_SECTIONS)
    if section_headers != P02_SECTIONS:
        failures.add("p02-sections")
    return failures


class Batch8ContractsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = corrected_batch8_bytes("index.html")
        cls.reader = corrected_batch8_bytes("GNOME-Field-Manual.html")
        cls.base = batch8_base_bytes("index.html")
        cls.base_reader = batch8_base_bytes("GNOME-Field-Manual.html")
        cls.pages = cards(cls.raw)
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.encoded = dataset_rows(cls.reader)

    def test_contracts_and_baseline_deficiencies(self):
        actual = {n: visible(self.pages[n]) for n in PAGES}
        self.assertEqual(contract_errors(actual), set())
        old = cards(self.base)
        previous = {n: visible(old[n]) for n in PAGES}
        self.assertTrue({"p01-scaffold", "p01-slots", "p02-prior", "p02-sections", "p02-disproof"}
                        <= contract_errors(previous))

    def test_mutations_remove_material_requirements(self):
        actual = {n: visible(self.pages[n]) for n in PAGES}
        for n, phrase, violation in (
            (210, "ONE THING THAT DIDN’T WORK", "p01-slots"),
            (210, "Do not assemble a post.", "p01-scaffold"),
            (211, "[MISSING: OBSERVED FAILURE]", "p01-failure"),
            (211, "Link each factual claim to supplied evidence", "p01-evidence"),
            (213, "Do not reconstruct a prior belief from its outcome.", "p02-prior"),
            (214, "at least one evidenced disproof", "p02-disproof"),
            (214, "For every accepted learning", "p02-reversal"),
            (214, "OPEN QUESTIONS GENERATED", "p02-sections"),
        ):
            with self.subTest(page=n, removed=phrase):
                altered = re.sub(r"\s+".join(map(re.escape, phrase.split())), "omitted", actual[n], count=1)
                self.assertNotEqual(altered, actual[n])
                self.assertIn(violation, contract_errors({**actual, n: altered}))
        self.assertIn("p01-scaffold", contract_errors({**actual, 211: actual[211] + "\nFINAL POST DRAFT"}))
        self.assertIn("p02-prior", contract_errors({
            **actual, 214: actual[214] + "\nReconstruct it from what the observation contradicts."
        }))

    def test_frozen_brief_followups_and_boundaries(self):
        for reference, source, destination in (
            ("P-04 Technical Post-Mortem Publisher", 210, 219),
            ("W-04 Over-Smoothing Detector", 212, 48),
            ("W-11 The Anti-Summary", 212, 64),
            ("P-01 Build-in-Public Post (Structured)", 216, 209),
            ("R-04 Research Artifact Generator (Schema-Locked)", 216, 86),
            ("R-08 Artifact Extraction Protocol", 216, 96),
        ):
            with self.subTest(reference=reference):
                entry_id, title = reference.split(" ", 1)
                self.assertIn(reference, visible(self.pages[destination]))
                source_text = canonical_surface(visible(self.pages[source]))
                self.assertIn(entry_id.lower(), source_text)
                self.assertIn(title.lower(), source_text)
        self.assertIn("P-02 Learning Log Extractor", visible(self.pages[213]))
        self.assertIn("P-03 README Quality Auditor", visible(self.pages[217]))

    def test_exact_page_scope_shared_prefix_and_reader_parity(self):
        originals = cards(self.base)
        for old, new in (
            (originals, self.pages),
            (cards(self.base_reader, STATIC), self.static),
            (dataset_rows(self.base_reader)[1], self.encoded),
        ):
            self.assertEqual(list(new), list(range(1, 316)))
            self.assertEqual(changed_pages(old, new), PAGES)
        self.assertEqual(CANONICAL.sub(b"", self.raw), CANONICAL.sub(b"", self.base))
        self.assertEqual(DATASET.sub(b"", STATIC.sub(b"", self.reader)),
                         DATASET.sub(b"", STATIC.sub(b"", self.base_reader)))
        for n in (209, 213):
            self.assertEqual(visible(self.pages[n]).split("WHAT IT DOES", 1)[0],
                             visible(originals[n]).split("WHAT IT DOES", 1)[0])
        for n in PAGES:
            with self.subTest(page=n):
                self.assertEqual(parity_errors(n, self.pages[n], self.rows[n], self.static[n]), set())

    def test_drift_is_detected(self):
        for n, term in ((210, "what was built/done"), (214, "disproven assumptions")):
            for surface, card, row, static in (
                ("metadata", self.pages[n].replace(term.encode(), b"missing term"), self.rows[n], self.static[n]),
                ("dynamic", self.pages[n], dict(self.rows[n], text="different"), self.static[n]),
                ("static", self.pages[n], self.rows[n], self.static[n].replace(term.upper().encode(), b"MISSING")),
            ):
                with self.subTest(page=n, surface=surface):
                    self.assertIn(surface, parity_errors(n, card, row, static))

    def test_historical_artifacts_and_frozen_briefs_are_unchanged(self):
        self.assertEqual(digest(self.base), BATCH7_DISPOSITION_SOURCE_SHA)
        for entry in (b"p01", b"p02", b"sec05"):
            self.assertEqual(extract_brief(self.raw, entry), extract_brief(self.base, entry))
        historical = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR43_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        historical.remove(INDEX_PATH)
        for path in historical:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), batch8_base_bytes(path))

    def test_current_identity_binding_and_status(self):
        current = json.loads(corrected_batch8_bytes(INDEX_PATH))
        prior = json.loads(batch8_base_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), BATCH8_SOURCE_SHA)
        self.assertEqual(current["sourceIndexSha256"], BATCH8_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH8_SOURCE_SHA}';", corrected_batch8_bytes(ADAPTER_PATH).decode())
        self.assertEqual(current["counts"], {"pending": 8, "drafted": 83, "total": 91, "pages": 315})
        self.assertEqual(current["bodyCoverage"], 0)
        for old, new in zip(prior["entries"], current["entries"], strict=True):
            self.assertEqual({k: v for k, v in old.items() if k not in {"titleCandidate", "occurrencePages"}},
                             {k: v for k, v in new.items() if k not in {"titleCandidate", "occurrencePages"}})
            self.assertFalse((set(old["occurrencePages"]) ^ set(new["occurrencePages"])) - PAGES)
            if old["id"] != "AP-02":
                self.assertEqual(old["titleCandidate"], new["titleCandidate"])
        pending = {e["id"] for e in current["entries"] if e["pendingInventory"]}
        self.assertTrue({"SEC-05", "P-01", "P-02"} <= pending)
