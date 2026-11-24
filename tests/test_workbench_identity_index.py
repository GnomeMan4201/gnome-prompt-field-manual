"""Regression gates for conservative manual identity export."""
from pathlib import Path
import sys
import unittest
import tempfile
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from export_entry_identity_index import build_inventory

class IdentityIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT / "index.html"
        cls.result = build_inventory(cls.source)

    def test_counts_and_preserved_w04(self):
        out = self.result
        self.assertEqual(out["counts"], {"pending": 8, "drafted": 83, "total": 91, "pages": 315})
        idx = {e["id"]: e for e in out["entries"]}
        self.assertIn("W-04", idx)
        self.assertIn("R-07", idx)
        self.assertIn("R-10", idx)
        self.assertEqual(len(idx), 91)
        self.assertEqual(sum(e["status"] == "PENDING" for e in idx.values()), 8)

    def test_no_phantom_from_cross_reference(self):
        out = self.result
        ids = {e["id"] for e in out["entries"]}
        self.assertNotIn("S-99", ids)
        self.assertEqual(out["bodyCoverage"], 0)
        for e in out["entries"]:
            self.assertIsNone(e["canonicalBody"])
            self.assertEqual(e["bodyStatus"], "UNRESOLVED_BOUNDARIES")
            self.assertEqual(e["crossRefStatus"], "NOT_VALIDATED")

    def test_source_mutation_fails_closed(self):
        raw = self.source.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "index.html"
            # An additional unattested page must not silently pass count checks.
            p.write_text(raw.replace("</body>", '<article class="manual-page-card" id="invented-page"></article></body>'), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_inventory(p)

if __name__ == "__main__":
    unittest.main()
