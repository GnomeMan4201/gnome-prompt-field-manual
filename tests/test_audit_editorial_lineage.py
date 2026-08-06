from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.audit_editorial_lineage import audit, markdown


FIXTURE = """<!doctype html><html><body>
<p>Source: GNOME_Prompt_Field_Manual_v3_final.docx</p>
<p>Embedded reader: GNOME Prompt Field Manual v9</p>
<div class="entry-row">R-10 Source-of-Truth Conflict Resolver Body already contains this entry as R-07. Requires renumbering fix, not new draft.</div>
<div class="brief">R-10 Source-of-Truth Conflict Resolver. The v3 master's planned numbering has R-07 = Competing Hypotheses Table and R-10 = Source-of-Truth Conflict Resolver. The body uses R-06 = Competing Hypotheses and R-07 = Source-of-Truth. Update the body labels to match the planned TOC numbering.</div>
<div class="manual-page-card"><pre>R-06 — Competing Hypotheses Table\nCompare alternatives.</pre></div>
<div class="manual-page-card"><pre>R-07 — Source-of-Truth Conflict Resolver\nUse the stated authority order.</pre></div>
</body></html>"""


class EditorialLineageAuditTests(unittest.TestCase):
    def write(self, text: str = FIXTURE) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "index.html"
        path.write_text(text, encoding="utf-8")
        return path

    def test_finds_v3_and_v9_references(self) -> None:
        result = audit(self.write())
        classifications = {item.classification for item in result.version_references}
        self.assertIn("source-filename-or-v3-reference", classifications)
        self.assertIn("embedded-reader-v9-reference", classifications)

    def test_freezes_two_label_renumbering_without_new_entry(self) -> None:
        result = audit(self.write())
        decision = result.decision["identifier_decision"]
        self.assertIn("R-06 → R-07", decision)
        self.assertIn("R-07 → R-10", decision)
        self.assertIn("not a new entry", decision)
        evidence = {(item.entry_id, item.location) for item in result.entry_evidence}
        self.assertIn(("R-06", "embedded-reader-page"), evidence)
        self.assertIn(("R-07", "embedded-reader-page"), evidence)
        self.assertIn(("R-10", "pending-inventory"), evidence)
        self.assertNotIn(("R-10", "embedded-reader-page"), evidence)

    def test_refuses_decision_when_expected_body_pattern_is_incomplete(self) -> None:
        broken = FIXTURE.replace("R-06 — Competing Hypotheses Table", "R-05 — Competing Hypotheses Table")
        result = audit(self.write(broken))
        self.assertIn("insufficient", result.decision["identifier_decision"].lower())

    def test_report_is_deterministic_and_hash_bound(self) -> None:
        result = audit(self.write())
        first = markdown(result)
        second = markdown(result)
        self.assertEqual(first, second)
        self.assertIn(result.source_sha256, first)
        self.assertIn("R-06", first)
        self.assertIn("R-10", first)
        self.assertIn("v3", first)


if __name__ == "__main__":
    unittest.main()
