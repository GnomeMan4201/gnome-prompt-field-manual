from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.audit_editorial_lineage import audit, markdown


FIXTURE = """<!doctype html><html><body>
<p>Source: GNOME_Prompt_Field_Manual_v3_final.docx</p>
<p>Embedded reader: GNOME Prompt Field Manual v9</p>
<div class="entry-row">R-10 Source-of-Truth Conflict Resolver Body already contains this entry as R-07. Requires renumbering fix, not new draft.</div>
<div class="brief">R-10 Source-of-Truth Conflict Resolver</div>
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

    def test_retains_r07_and_treats_r10_as_alias_request(self) -> None:
        result = audit(self.write())
        self.assertIn("Retain R-07", result.decision["r07_r10"])
        evidence = {(item.entry_id, item.location) for item in result.entry_evidence}
        self.assertIn(("R-07", "embedded-reader-page"), evidence)
        self.assertIn(("R-10", "pending-inventory"), evidence)
        self.assertNotIn(("R-10", "embedded-reader-page"), evidence)

    def test_refuses_automatic_decision_when_r10_is_embedded(self) -> None:
        text = FIXTURE.replace(
            "Use the stated authority order.",
            "Use the stated authority order. R-10 duplicate body.",
        )
        result = audit(self.write(text))
        self.assertIn("insufficient", result.decision["r07_r10"].lower())

    def test_report_is_deterministic_and_hash_bound(self) -> None:
        result = audit(self.write())
        first = markdown(result)
        second = markdown(result)
        self.assertEqual(first, second)
        self.assertIn(result.source_sha256, first)
        self.assertIn("R-07", first)
        self.assertIn("v3", first)


if __name__ == "__main__":
    unittest.main()
