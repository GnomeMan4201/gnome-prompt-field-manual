from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.validate_manual import markdown_report, validate


VALID_DOCUMENT = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Test manual">
  <title>Test Manual</title>
</head>
<body>
  <main>
    <h1 id="top">Test Manual</h1>
    <h2 id="method">Method</h2>
    <a href="#method">Read method</a>
    <a href="https://example.test" target="_blank" rel="noopener noreferrer">External</a>
    <img src="diagram.svg" alt="Test diagram">
  </main>
</body>
</html>
"""


class ManualValidatorTests(unittest.TestCase):
    def workspace(self, html: str, *, asset: bool = False) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        path = root / "index.html"
        path.write_text(html, encoding="utf-8")
        if asset:
            (root / "diagram.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
        return path

    def codes(self, html: str, *, asset: bool = False) -> list[str]:
        result = validate(self.workspace(html, asset=asset))
        return [finding.code for finding in result.findings]

    def test_valid_document_has_no_findings(self) -> None:
        result = validate(self.workspace(VALID_DOCUMENT, asset=True))
        self.assertEqual(result.metrics.error_count, 0)
        self.assertEqual(result.metrics.warning_count, 0)
        self.assertEqual(result.metrics.heading_count, 2)
        self.assertEqual(result.metrics.external_link_count, 1)

    def test_missing_document_metadata_fails(self) -> None:
        codes = self.codes("<html><head><title></title></head><body></body></html>")
        self.assertIn("missing-html-lang", codes)
        self.assertIn("missing-title", codes)
        self.assertIn("missing-viewport", codes)
        self.assertIn("missing-description", codes)
        self.assertIn("main-count", codes)
        self.assertIn("h1-count", codes)

    def test_duplicate_ids_and_broken_anchor_fail(self) -> None:
        html = VALID_DOCUMENT.replace(
            '<h2 id="method">Method</h2>',
            '<h2 id="method">Method</h2><p id="method">Duplicate</p><a href="#missing">Missing</a>',
        )
        codes = self.codes(html, asset=True)
        self.assertIn("duplicate-id", codes)
        self.assertIn("broken-anchor", codes)

    def test_missing_and_escaping_assets_fail(self) -> None:
        html = VALID_DOCUMENT.replace(
            '<img src="diagram.svg" alt="Test diagram">',
            '<img src="missing.svg" alt="Missing"><script src="../escape.js"></script>',
        )
        codes = self.codes(html)
        self.assertIn("missing-local-asset", codes)
        self.assertIn("unsafe-local-reference", codes)

    def test_target_blank_and_image_alt_fail_closed(self) -> None:
        html = VALID_DOCUMENT.replace(
            '<a href="https://example.test" target="_blank" rel="noopener noreferrer">External</a>',
            '<a href="https://example.test" target="_blank">External</a>',
        ).replace(' alt="Test diagram"', "")
        codes = self.codes(html, asset=True)
        self.assertIn("unsafe-blank-target", codes)
        self.assertIn("missing-image-alt", codes)

    def test_heading_jump_and_placeholder_are_warnings(self) -> None:
        html = VALID_DOCUMENT.replace(
            '<h2 id="method">Method</h2>',
            '<h3 id="method">TODO Method</h3>',
        )
        result = validate(self.workspace(html, asset=True))
        self.assertEqual(result.metrics.error_count, 0)
        self.assertIn("heading-jump", [item.code for item in result.findings])
        self.assertIn("editorial-marker", [item.code for item in result.findings])

    def test_report_is_deterministic_and_hash_bound(self) -> None:
        result = validate(self.workspace(VALID_DOCUMENT, asset=True))
        first = markdown_report(result)
        second = markdown_report(result)
        self.assertEqual(first, second)
        self.assertIn(result.metrics.source_sha256, first)
        self.assertNotIn("Generated:", first)


if __name__ == "__main__":
    unittest.main()
