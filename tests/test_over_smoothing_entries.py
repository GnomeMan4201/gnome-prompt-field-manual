"""W-04 and AP-01: distinct titles and an explicit no-source contract.

Manuscript checks only. They do not run a model or measure detection quality.
"""
import base64
import hashlib
import json
import re
import subprocess
import unittest

from test_batch6_correction import (
    CANONICAL, DATASET, STATIC, ROOT, cards, changed_pages, dataset_rows,
    parity_errors, static_text, visible,
)
from tools.audit_editorial_lineage import EXPECTED_PDF_SHA256, canonical_surface

BASE = "8f58c4cb55a99b72778387179e577b00418b2ea5"
CHANGED = {49, 50, 275, 276}
DETECTOR = "Over-Smoothing Detector"
GATE = "Over-Smoothing Publication Gate"


def previous(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def flat(text):
    return " ".join(canonical_surface(text).split())


class OverSmoothingEntries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "index.html").read_bytes()
        cls.pages = cards(cls.raw)
        cls.reader = (ROOT / "GNOME-Field-Manual.html").read_bytes()
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.serialized = dataset_rows(cls.reader)
        cls.text = {n: visible(card) for n, card in cls.pages.items()}
        cls.packet = json.loads((ROOT / "workbench/data/current_body_review.json").read_text())

    def surfaces(self, pages=None):
        for n in sorted(pages or self.pages):
            yield f"canonical page {n}", self.text[n]
            yield f"search metadata page {n}", re.search(rb'data-manual-text="([^"]*)"', self.pages[n])[1].decode()
            if b"typeset-body" in self.static[n]:
                yield f"static page {n}", static_text(self.static[n])
            yield f"serialized page {n}", self.rows[n]["text"]

    def test_edit_scope_and_parity(self):
        old_source, old_reader = previous("index.html"), previous("GNOME-Field-Manual.html")
        for old, new in [(cards(old_source), self.pages), (cards(old_reader, STATIC), self.static),
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

    def test_each_entry_has_its_own_heading(self):
        self.assertRegex(self.text[48], rf"(?m)^\s*W-04 {DETECTOR}\s*$")
        self.assertRegex(self.text[275], rf"(?m)^\s*AP-01 {GATE}\s*$")
        headings = {e["entryId"]: e["canonicalHeadingCandidate"] for e in self.packet["entries"]}
        self.assertEqual((headings["W-04"], headings["AP-01"]), (DETECTOR, GATE))
        owners = [i for i, t in headings.items() if t == DETECTOR]
        self.assertEqual(owners, ["W-04"])
        self.assertIn("use it to decide whether a draft can be published. for a five-part audit of what a "
                      "rewrite changed, use w-04 (over-smoothing detector).", flat(self.text[275]))

    def test_every_detector_reference_names_w04(self):
        for name, text in self.surfaces():
            surface = flat(text)
            for m in re.finditer(r"over-smoothing detector", surface):
                before, after = surface[max(0, m.start() - 8):m.start()], surface[m.end():m.end() + 8]
                with self.subTest(surface=name, at=m.start()):
                    self.assertTrue(before.endswith("w-04 (") or before.endswith("w-04 ") or after.startswith(" (w-04)"),
                                    f"'{surface[max(0, m.start() - 30):m.end() + 12]}' does not name W-04")
            for ref, label in re.findall(r"\b(ap-01|w-04)\s*\(([^()]{3,60})\)", surface):
                with self.subTest(surface=name, reference=ref, label=label):
                    title = {"ap-01": GATE, "w-04": DETECTOR}[ref].lower()
                    self.assertTrue(title.startswith(label.strip()), f"{ref.upper()} cited as '{label}'")

    def test_ap01_no_source_findings_cannot_trigger_the_gate(self):
        for name, text in self.surfaces({276}):
            surface = flat(text)
            with self.subTest(surface=name):
                original = "for each instance: quote the original and the smoothed version."
                no_source = ("if no source is available, quote the output passage instead, state what the stated "
                             "purpose requires that it lacks, and mark the claimed loss unverified — no source.")
                self.assertIn(original, surface)
                self.assertIn(no_source, surface, "AP-01 lacks the no-source instruction")
                self.assertLess(surface.index(original), surface.index(no_source))
                self.assertIn("without a source, rate not rated — no source.", surface)
                signal = surface[surface.index("signal of failure"):] if "signal of failure" in surface else surface
                self.assertIn("these signals require findings checked against the source. an unverified — no source "
                              "finding is not a hit: obtain the source before deciding whether to publish.", signal)
        self.assertIn("do not publish the smoothed version", flat(self.text[277]))

    def test_w04_does_not_infer_an_original(self):
        for name, text in self.surfaces({49, 50}):
            surface = flat(text)
            with self.subTest(surface=name):
                if "the prompt" in surface:
                    for phrase in ("if only the output is provided, do not infer what an original contained",
                                   "mark the claimed loss unverified — no original",
                                   "answer check 5 against the stated purpose",
                                   "if no original was provided, report not rated — no original"):
                        self.assertIn(phrase, surface)
                else:
                    self.assertIn("it cannot confirm what was lost. mark each claimed loss unverified — no original.", surface)


if __name__ == "__main__":
    unittest.main()
