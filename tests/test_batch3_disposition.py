from __future__ import annotations
import html,re,unittest
from pathlib import Path
from tools.reconcile_entry_lineage import reconcile,validate_expectations
ROOT=Path(__file__).resolve().parents[1]; INDEX=ROOT/"index.html"; FIELDS=("WHAT IT DOES","WHEN TO USE","THE PROMPT","INPUTS NEEDED","EXPECTED OUTPUT","KNOBS","FAILURE MODE","FOLLOW-UP","SAFETY NOTES")
def page(n):
 s=INDEX.read_text(encoding="utf-8"); m=re.search(rf'<article class="manual-page-card" id="manual-page-{n:03d}"[^>]*>.*?</article>',s,re.S); assert m; return m.group(0)
def vis(c):
 m=re.search(r'<pre>(.*?)</pre>',c,re.S); return html.unescape(re.sub(r'<[^>]+>','',m.group(1)))
def meta(c):
 m=re.search(r'data-manual-text="([^"]*)"',c,re.S); return html.unescape(m.group(1))
class Batch3DispositionTests(unittest.TestCase):
 def test_state(self):
  r=reconcile(INDEX); self.assertEqual(validate_expectations(r,expected_pending=14,expected_drafted=77,expected_total=91,expected_pages=315),[]); p={x.entry_id for x in r.pending_entries}; b={x.entry_id for x in r.briefs}; self.assertNotIn("R-01",p); self.assertNotIn("R-03",p); self.assertNotIn("R-01",b); self.assertNotIn("R-03",b)
 def test_bodies_fields(self):
  d={"R-01":"\n".join(vis(page(n)) for n in range(71,78)),"R-03":"\n".join(vis(page(n)) for n in range(79,87))}; self.assertEqual(d["R-01"].count("R-01 Source Map with Contested Zones"),1); self.assertEqual(d["R-03"].count("R-03 Replication Risk Auditor"),1); [self.assertIn(f,x) for x in d.values() for f in FIELDS]
 def test_r01(self):
  cs=[page(n) for n in range(71,77)]; b=" ".join(vis(c) for c in cs); m=" ".join(meta(c) for c in cs); self.assertIn("INSTITUTIONAL INTEREST MAP",b); self.assertIn("SOURCE FLATTENING WARNINGS",b); self.assertIn("CONTESTED ZONES",b); self.assertIn("KNOWN GAPS",b); self.assertIn("institutional interest map",m); self.assertIn("Six components:",b)
 def test_r03(self):
  cs=[page(n) for n in range(79,87)]; b=" ".join(vis(c) for c in cs); m=" ".join(meta(c) for c in cs); self.assertIn("VERY HIGH RISK",b); self.assertIn("NOT REPLICATION-READY",b); self.assertIn("R-05 (Failure-to-Test Converter)",b); self.assertIn("HARKING FLAGS",b); self.assertIn("very high risk",m); self.assertIn("separate assessment-status outcome",m); self.assertIn("r-05 (failure-to-test converter)",m)
 def test_startup(self):
  s=INDEX.read_text(encoding="utf-8"); self.assertIn("document.getElementById('b-s01').classList.add('open');",s); self.assertIn("document.getElementById('b-s02').classList.add('open');",s); self.assertNotIn('<td class="batch-entries">R-01, R-03</td>',s)
if __name__=="__main__": unittest.main()
