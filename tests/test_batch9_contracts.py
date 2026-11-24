"""Editorial contract and preservation tests. These do not evaluate model output."""
import base64
import json
import re
import subprocess
import unittest

from batch8_baseline import BATCH8_DISPOSITION_SOURCE_SHA, PR45_MERGE, ROOT, batch8_disposition_bytes
from batch9_baseline import BATCH9_SOURCE_SHA, batch9_correction_bytes
from test_batch6_correction import (
    ADAPTER_PATH, CANONICAL, DATASET, EXPECTED_PDF_SHA256, HISTORICAL_ROOTS, INDEX_PATH, STATIC,
    canonical_surface, cards, changed_pages, dataset_rows, digest, parity_errors, visible,
)
from test_batch6_partial_disposition import extract_brief

READER = "GNOME-Field-Manual.html"
PAGES = set(range(222, 233))
REQUIREMENTS = {
    "unchanged sample": (225, ("return the supplied work verbatim", "supplied unchanged attachment",
                              "name what is needed for completion")),
    "inspectable sources": (223, ("artifact version or snapshot", "give a supplied locator",
                                  "do not invent a locator")),
    "attribution": (223, ("original individual work", "collaborative work", "third-party work or dependencies",
                         "source for attribution", "attribution unverified")),
    "point annotations": (224, ("for each annotation, name the exact work point first",
                                "constraint annotations", "decision annotations", "alternative paths not taken",
                                "recorded reason it was rejected")),
    "review limits": (224, ("measured result, comparison basis, and scope", "mark unverified impact",
                            "known limitations, unresolved weaknesses")),
    "reuse": (225, ("reusability notes", "anchor each note", "prerequisites", "what does not transfer")),
    "disclosure": (225, ("if permission is unclear", "hold the public package", "do not silently alter the original")),
    "release provenance": (229, ("release not verified", "closed issue alone does not show that a change shipped",
                                  "mark incomplete history")),
    "classification": (229, ("shipped, planned, reverted and unverified", "keep planned and unverified work out",
                             "mark unsupported claims", "group duplicate records", "net-zero work")),
    "migration": (229, ("name the affected users", "concrete action to migrate", "mark the gap and hold publication")),
    "significance": (230, ("observable user impact", "high / medium / low", "one-sentence rationale for every high",
                           "evidence-based reasoning note for non-obvious changes")),
    "release gate": (230, ("separate, lower-prominence section", "mark the draft provisional",
                            "none verified")),
}
CHANGELOG_SECTIONS = ("USER-FACING CHANGES", "REMOVED/DEPRECATED", "INTERNAL CHANGES")


def contract_errors(pages):
    body = {n: canonical_surface(text) for n, text in pages.items()}
    errors = {
        key for key, (n, terms) in REQUIREMENTS.items()
        if any(term not in body[n] for term in terms)
    }
    headings = re.findall(r"(?m)^(USER-FACING CHANGES|REMOVED/DEPRECATED|INTERNAL CHANGES) —", pages[230])
    if tuple(headings) != CHANGELOG_SECTIONS:
        errors.add("changelog sections")
    if re.search(r"\binternal (?:changes|notes) (?:are )?optional\b", body[230] + " " + body[231]):
        errors.add("release gate")
    return errors


def rfc_suffix(raw):
    return raw.split(b"  P-07 RFC Draft Generator", 1)[1]


class Batch9ContractsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = batch9_correction_bytes("index.html")
        cls.reader = batch9_correction_bytes(READER)
        cls.base = batch8_disposition_bytes("index.html")
        cls.base_reader = batch8_disposition_bytes(READER)
        cls.pages = cards(cls.raw)
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.encoded = dataset_rows(cls.reader)
        cls.visible = {n: visible(cls.pages[n]) for n in PAGES}

    def test_contracts_and_deficiencies_in_pinned_baseline(self):
        self.assertEqual(contract_errors(self.visible), set())
        old = cards(self.base)
        self.assertTrue({
            "unchanged sample", "point annotations", "reuse", "significance", "changelog sections"
        } <= contract_errors({n: visible(old[n]) for n in PAGES}))

    def test_mutations_remove_required_fields_or_reintroduce_optional_internal_section(self):
        for n, phrase, violation in (
            (223, "THIRD-PARTY WORK OR DEPENDENCIES", "attribution"),
            (223, "Do not invent a locator", "inspectable sources"),
            (224, "For each annotation, name the exact work point first", "point annotations"),
            (224, "Mark unverified impact", "review limits"),
            (225, "Return the supplied work verbatim", "unchanged sample"),
            (225, "what does not transfer", "reuse"),
            (225, "hold the public package", "disclosure"),
            (229, "Mark incomplete history", "release provenance"),
            (229, "Group duplicate records", "classification"),
            (229, "Mark unsupported claims", "classification"),
            (229, "concrete action to migrate", "migration"),
            (230, "one-sentence rationale for every HIGH", "significance"),
            (230, "REMOVED/DEPRECATED", "changelog sections"),
            (230, "mark the draft PROVISIONAL", "release gate"),
        ):
            with self.subTest(page=n, requirement=violation, removed=phrase):
                pattern = r"\s+".join(map(re.escape, phrase.split()))
                changed, replacements = re.subn(pattern, "omitted", self.visible[n], count=1)
                self.assertEqual(replacements, 1)
                self.assertIn(violation, contract_errors({**self.visible, n: changed}))
        self.assertIn("release gate", contract_errors({
            **self.visible, 231: self.visible[231] + "\nInternal changes are optional."
        }))

    def test_subject_boundaries_and_followups(self):
        for n, title in (
            (138, "S-09 Incident Report Scaffold"),
            (140, "S-10 Architecture Decision Record Generator"),
            (217, "P-03 README Quality Auditor"),
            (219, "P-04 Technical Post-Mortem Publisher"),
            (222, "P-05 Work Sample Annotator"),
            (228, "P-06 Changelog Curation Engine"),
            (232, "P-07 RFC Draft Generator"),
        ):
            with self.subTest(page=n):
                self.assertRegex(visible(self.pages[n]), rf"(?m)^\s*{re.escape(title)}\s*$")
        for n, reference in (
            (227, "p-03 (readme quality auditor)"),
            (227, "p-04 (technical post-mortem publisher)"),
            (232, "s-10 (architecture decision record generator)"),
            (232, "p-04 (technical post-mortem publisher)"),
        ):
            self.assertIn(reference, canonical_surface(self.visible[n]))
        self.assertNotIn("s-09", canonical_surface(self.visible[232]).split("rfc draft generator", 1)[0])

    def test_exact_scope_and_unchanged_neighbor_across_readers(self):
        originals = cards(self.base)
        static_base = cards(self.base_reader, STATIC)
        rows_base, encoded_base = dataset_rows(self.base_reader)
        for old, new in ((originals, self.pages), (static_base, self.static), (encoded_base, self.encoded)):
            self.assertEqual(list(new), list(range(1, 316)))
            self.assertEqual(changed_pages(old, new), PAGES)
        self.assertEqual(CANONICAL.sub(b"", self.raw), CANONICAL.sub(b"", self.base))
        self.assertEqual(DATASET.sub(b"", STATIC.sub(b"", self.reader)),
                         DATASET.sub(b"", STATIC.sub(b"", self.base_reader)))
        for n in (222, 228):
            self.assertEqual(self.visible[n].split("WHAT IT DOES", 1)[0],
                             visible(originals[n]).split("WHAT IT DOES", 1)[0])
        pre = re.compile(rb"<pre>(.*?)</pre>", re.S)
        for old, new in (
            (pre.search(originals[232])[1], pre.search(self.pages[232])[1]),
            (static_base[232], self.static[232]),
            (rows_base[232]["text"].encode(), self.rows[232]["text"].encode()),
        ):
            self.assertEqual(rfc_suffix(old), rfc_suffix(new))

    def test_reader_parity_and_drift_detection(self):
        for n in PAGES:
            with self.subTest(page=n):
                self.assertEqual(parity_errors(n, self.pages[n], self.rows[n], self.static[n]), set())
                self.assertEqual(self.rows[n]["idTokens"], sorted(set(re.findall(
                    r"\b(?:AP|P|R|S|T|W)-\d{2}\b", self.visible[n]
                ))))
        n = 230
        card, row, static = self.pages[n], self.rows[n], self.static[n]
        for surface, altered, altered_row, altered_static in (
            ("metadata", card.replace(b"removed/deprecated", b"absent"), row, static),
            ("dynamic", card, dict(row, text="different", textSha256=digest(b"different")), static),
            ("static", card, row, static.replace(b"REMOVED/DEPRECATED", b"ABSENT")),
        ):
            with self.subTest(surface=surface):
                self.assertIn(surface, parity_errors(n, altered, altered_row, altered_static))

    def test_frozen_briefs_pdf_and_historical_artifacts(self):
        self.assertEqual(digest(self.base), BATCH8_DISPOSITION_SOURCE_SHA)
        for entry in (b"p06", b"p07", b"sec05"):
            self.assertEqual(extract_brief(self.raw, entry), extract_brief(self.base, entry))
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf, validate=True)), EXPECTED_PDF_SHA256)
        historical = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", PR45_MERGE, "--", *HISTORICAL_ROOTS],
            cwd=ROOT, text=True,
        ).splitlines()
        historical.remove(INDEX_PATH)
        for path in historical:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), batch8_disposition_bytes(path))

    def test_correction_binding_and_unchanged_editorial_status(self):
        current = json.loads(batch9_correction_bytes(INDEX_PATH))
        prior = json.loads(batch8_disposition_bytes(INDEX_PATH))
        self.assertEqual(digest(self.raw), BATCH9_SOURCE_SHA)
        self.assertEqual(current["sourceIndexSha256"], BATCH9_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH9_SOURCE_SHA}';", batch9_correction_bytes(ADAPTER_PATH).decode())
        self.assertEqual(current["counts"], {"pending": 6, "drafted": 85, "total": 91, "pages": 315})
        self.assertEqual(current["bodyCoverage"], 0)
        for old, new in zip(prior["entries"], current["entries"], strict=True):
            with self.subTest(entry=old["id"]):
                self.assertEqual({k: v for k, v in old.items() if k not in {"titleCandidate", "occurrencePages"}},
                                 {k: v for k, v in new.items() if k not in {"titleCandidate", "occurrencePages"}})
                self.assertFalse((set(old["occurrencePages"]) ^ set(new["occurrencePages"])) - PAGES)
                if old["id"] != "AP-06":
                    self.assertEqual(old["titleCandidate"], new["titleCandidate"])
        pending = {e["id"] for e in current["entries"] if e["pendingInventory"]}
        self.assertEqual(pending, {"SEC-05", "P-06", "P-07", "P-08", "P-09", "P-10"})
