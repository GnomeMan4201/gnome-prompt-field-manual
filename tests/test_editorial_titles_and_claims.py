"""Title and claim corrections for page 6, SEC-01 page 153, AP-06 and SEC-08.

These are manuscript checks. They do not run a model or measure decoding accuracy.
"""
import base64
import codecs
import hashlib
import json
import re
import subprocess
import sys
import unittest

from test_batch6_correction import (
    CANONICAL, DATASET, STATIC, ROOT, cards, changed_pages, dataset_rows,
    parity_errors, static_text, visible,
)
from tools.audit_editorial_lineage import EXPECTED_PDF_SHA256, canonical_surface

BASE = "71bcdb7926f33c3288ba7cdc5ad8ef6e823baca6"
CHANGED = {6, 153, 200, 227, 232, 252, 283, 307}
TITLES = {"AP-06": "Passage Evidence Review", "SEC-08": "Collection Evidence Audit"}
OBSOLETE = {"AP-06": "Generated Junk Classifier", "SEC-08": "Generated Junk Detector"}
CRITERIA = [
    "Reveal a hidden assumption", "Convert failure into a test", "Separate signal from noise",
    "Harden an idea against attack", "Protect a system from bad inputs",
    "Turn messy work into a reusable artifact", "Expose a trust boundary",
    "Improve decision quality under uncertainty", "Help a builder ship safer or cleaner",
    "Produce output that can be reused, tested, cited, published, or committed",
]
# Claims with no supporting evidence in this repository. Matched after normalization,
# so line wrapping and print hyphenation cannot hide them.
UNSUPPORTED_CLAIMS = [
    r"\bwas tested against (?:the )?ten inclusion criteria\b",
    r"\bclassification 6 is reliable for\b",
    r"\bis reliable for: standard base64\b",
]
PILOT = "research/ap06-paired-pilot"


def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def surface(text):
    return canonical_surface(text)


def words(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


class EditorialTitlesAndClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "index.html").read_bytes()
        cls.pages = cards(cls.raw)
        cls.reader = (ROOT / "GNOME-Field-Manual.html").read_bytes()
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.serialized = dataset_rows(cls.reader)
        cls.text = {n: visible(card) for n, card in cls.pages.items()}
        cls.packet = json.loads((ROOT / "workbench/data/current_body_review.json").read_text())
        cls.identity = json.loads((ROOT / "workbench/data/current_entry_identity_index.json").read_text())

    def current_surfaces(self):
        """Every current reader surface, as (name, text)."""
        for n, card in self.pages.items():
            yield f"canonical page {n}", self.text[n]
            meta = re.search(rb'data-manual-text="([^"]*)"', card)[1].decode()
            yield f"search metadata page {n}", meta
        for n, card in self.static.items():
            if b"typeset-body" in card:
                yield f"static page {n}", static_text(card)
        for n, row in self.rows.items():
            yield f"serialized page {n}", row["text"]

    def test_edit_scope_and_parity(self):
        old_source = previous("index.html")
        old_reader = previous("GNOME-Field-Manual.html")
        for old, new in [(cards(old_source), self.pages),
                         (cards(old_reader, STATIC), self.static),
                         (dataset_rows(old_reader)[1], self.serialized)]:
            self.assertEqual(changed_pages(old, new), CHANGED)
        self.assertEqual(CANONICAL.sub(b"", self.raw), CANONICAL.sub(b"", old_source))
        outside = lambda raw: DATASET.sub(b"", STATIC.sub(b"", raw))
        self.assertEqual(outside(self.reader), outside(old_reader))
        for n in CHANGED:
            with self.subTest(page=n):
                self.assertEqual(parity_errors(n, self.pages[n], self.rows[n], self.static[n]), set())
        pdf = re.search(rb'data="data:application/pdf;base64,([^"]+)"', self.raw)[1]
        self.assertEqual(hashlib.sha256(base64.b64decode(pdf)).hexdigest(), EXPECTED_PDF_SHA256)

    def test_headings_name_the_level_of_review(self):
        self.assertRegex(self.text[283], r"(?m)^\s*AP-06 Passage Evidence Review\s*$")
        self.assertRegex(self.text[200], r"(?m)^\s*SEC-08 Collection Evidence Audit\s*$")
        headings = {e["entryId"]: e["canonicalHeadingCandidate"] for e in self.packet["entries"]}
        self.assertEqual({k: headings[k] for k in TITLES}, TITLES)
        passage = surface(self.text[283])
        collection = surface(self.text[200])
        self.assertIn("use it for one submission. for a collection, use sec-08 (collection evidence audit)", passage)
        self.assertIn("which items were examined or omitted", passage)
        self.assertIn("a finding for each claim in each item, plus an account of which items were examined or omitted", collection)
        self.assertIn("for a single submission, use ap-06 (passage evidence review)", collection)
        cards_page = surface(self.text[307])
        self.assertIn("ap-06 (passage evidence review) · sec-08 (collection evidence audit)", cards_page)

    def test_preserved_entry_contracts(self):
        anti_prompt = surface(self.text[283] + "\n" + self.text[284])
        for phrase in ("supported", "needs revision", "insufficient evidence", "authorship as unknown",
                       "unmet quality criterion", "human reviewer"):
            self.assertIn(phrase, anti_prompt)
        collection = surface(self.text[201] + "\n" + self.text[202])
        for phrase in ("supplied, inspectable source", "authorship as unknown", "items examined and omitted",
                       "before excluding an item", "record the denominator"):
            self.assertIn(phrase, collection)

    def test_references_use_current_titles(self):
        for name, text in self.current_surfaces():
            flat = surface(text)
            for entry, old in OBSOLETE.items():
                with self.subTest(surface=name, obsolete=old):
                    self.assertNotIn(words(old), words(flat))
            for entry, label in re.findall(r"\b(AP-06|SEC-08)\s*\(([^()]{3,85})\)", flat, re.I):
                with self.subTest(surface=name, reference=entry, label=label):
                    current = words(TITLES[entry.upper()])
                    self.assertTrue(current.startswith(words(label)),
                                    f"{entry} cited as '{label}', current title is '{TITLES[entry.upper()]}'")
        # Reader search matches continuous text, so a labelled reference must not wrap.
        for n, row in self.rows.items():
            for entry, label in re.findall(r"\b(AP-06|SEC-08)\s*\(([^()]{3,85})\)", row["text"]):
                with self.subTest(page=n, reference=entry):
                    self.assertNotIn("\n", label, "wrapped title is not found by reader search")
        for entry in self.packet["entries"]:
            for old in OBSOLETE.values():
                self.assertNotIn(words(old), words(entry["canonicalHeadingCandidate"] + " " + entry["advisoryIdentityTitle"]))
        for entry in self.identity["entries"]:
            for old in OBSOLETE.values():
                self.assertNotIn(words(old), words(entry["titleCandidate"] or ""))

    def test_no_unsupported_claims_remain(self):
        for name, text in self.current_surfaces():
            flat = surface(text)
            for claim in UNSUPPORTED_CLAIMS:
                with self.subTest(surface=name, claim=claim):
                    self.assertIsNone(re.search(claim, flat), f"unsupported claim on {name}")

    def test_admission_criteria_are_editorial(self):
        page = self.text[6]
        listed = re.findall(r"(?m)^\s*(\d{1,2})\. (.+(?:\n {3}\S.*)?)$", page)
        self.assertEqual([int(n) for n, _ in listed], list(range(1, 11)))
        self.assertEqual([" ".join(item.split()) for _, item in listed], CRITERIA)
        flat = surface(page)
        for phrase in ("criteria line under each entry heading", "these are editorial selection criteria",
                       "it does not show how a model responds", "no comparable record for its other entries",
                       "covers only the entry and revision it tested"):
            self.assertIn(phrase, flat)
        appendix_ids = set()
        for n in range(312, 316):
            appendix_ids |= set(re.findall(r"(?m)^([A-Z]{1,3}-\d\d)\s", self.text[n]))
        self.assertIn(f"for the {len(appendix_ids)} prompts in an earlier draft", flat)
        self.assertIn(f"the first draft of this manual contained {len(appendix_ids)} prompts", surface(self.text[311]))
        # Every entry's Criteria line must refer to the numbered list.
        for entry in self.packet["entries"]:
            start, end = entry["start"], entry["endExclusive"]
            first = re.search(r"Criteria:\s*([0-9, ]+)", self.text[start["page"]][start["offset"]:] + self.text.get(start["page"] + 1, ""))
            with self.subTest(entry=entry["entryId"]):
                self.assertIsNotNone(first)
                numbers = {int(x) for x in re.findall(r"\d+", first[1])}
                self.assertTrue(numbers and numbers <= set(range(1, 11)), numbers)

    def test_decoding_is_tool_checked_or_marked_unverified(self):
        flat = surface(self.text[153])
        for phrase in ("no test in this manual measures how accurately a model decodes",
                       "unverified interpretation until a tool reproduces it",
                       "label the result tool-checked",
                       "label it model interpretation — unverified",
                       "keep classification 6 at possible for that string",
                       "an unverified decode is not a confirmed encoded payload",
                       "on all content, not only non-ascii content"):
            self.assertIn(phrase, flat)
        b64 = re.search(r"Base64 string\s+([A-Za-z0-9+/]+={0,2})\s+decodes to\s+“([^”]+)”", self.text[153])
        rot = re.search(r"ROT13 text\s+“([a-z]+)”\s+decodes to\s+“([^”]+)”", self.text[153])
        self.assertEqual(base64.b64decode(b64[1]).decode(), b64[2])
        self.assertEqual(codecs.decode(rot[1], "rot13"), rot[2])
        # The example is detectable by the page-150 pre-scan it accompanies.
        prescan = re.search(r"regex: (\[A-Za-z0-9\+/\]\{20,\}=\{0,2\})", self.text[150])
        self.assertRegex(b64[1], prescan[1])
        for phrase in ("unicodedata.normalize", "u+200b", "manual sandboxed de-"):
            self.assertIn(phrase, self.text[150].lower())

    def test_pilot_evidence_is_preserved(self):
        listed = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", BASE, PILOT], cwd=ROOT, text=True).split()
        self.assertTrue(listed)
        for path in listed:
            with self.subTest(path=path):
                self.assertEqual((ROOT / path).read_bytes(), previous(path))
        expected = {
            "operator-provisional.csv": ("control fully correct 0 / 6", "gnome fully correct 1 / 6"),
            "blind-ai-second-read.csv": ("control fully correct 1 / 6", "gnome fully correct 1 / 6"),
        }
        for sheet, lines in expected.items():
            out = subprocess.check_output([sys.executable, "-I", "score.py", "run-02", sheet],
                                          cwd=ROOT / PILOT, text=True)
            for line in lines:
                self.assertIn(line, out)


if __name__ == "__main__":
    unittest.main()
