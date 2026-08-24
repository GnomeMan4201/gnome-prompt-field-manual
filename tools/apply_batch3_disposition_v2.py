from __future__ import annotations
import hashlib, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; INDEX=ROOT/'index.html'
PRE='e0d88f80a6f14e90732a7f0765794ffe348bf526aaa3225fe3b87c8acb073bac'; BASE='5893ce77993e7362b276e4b486733a6ec220286a'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def one(s,a,b,label):
 c=s.count(a)
 if c!=1: raise SystemExit(f'{label}: expected 1, found {c}')
 return s.replace(a,b,1)
def rx(s,p,r,label):
 out,c=re.subn(p,r,s,count=1,flags=re.S)
 if c!=1: raise SystemExit(f'{label}: expected 1, found {c}')
 return out
def page_edit(s,n,fn):
 p=rf'<article class="manual-page-card" id="manual-page-{n:03d}"[^>]*>.*?</article>'; m=re.search(p,s,re.S)
 if not m: raise SystemExit(f'missing page {n}')
 old=m.group(0); new=fn(old)
 if old==new: raise SystemExit(f'page {n}: no change')
 return s[:m.start()]+new+s[m.end():]
def meta_edit(card,fn):
 m=re.search(r'data-manual-text="([^"]*)"',card,re.S); old=m.group(1); new=fn(old)
 if old==new: raise SystemExit('metadata no change')
 return card[:m.start(1)]+new+card[m.end(1):]
def pre_edit(card,fn):
 m=re.search(r'<pre>(.*?)</pre>',card,re.S); old=m.group(1); new=fn(old)
 if old==new: raise SystemExit('pre no change')
 return card[:m.start(1)]+new+card[m.end(1):]

if sha(INDEX)!=PRE: raise SystemExit(f'index hash mismatch: {sha(INDEX)}')
s=INDEX.read_text(encoding='utf-8')
for a,b,label in [
('16 pending entries · 8 remaining batches · drafting authority','14 pending entries · 7 remaining batches · drafting authority','header'),
('Production state: 75 drafted · 0 restore · 16 pending','Production state: 77 drafted · 0 restore · 14 pending','production'),
('<div class="stat"><div class="stat-num sn-pending">16</div><div class="stat-label">Pending Entries</div></div>','<div class="stat"><div class="stat-num sn-pending">14</div><div class="stat-label">Pending Entries</div></div>','pending stat'),
('<div class="stat"><div class="stat-num sn-drafted">75</div><div class="stat-label">Drafted</div></div>','<div class="stat"><div class="stat-num sn-drafted">77</div><div class="stat-label">Drafted</div></div>','drafted stat'),
('<div class="stat"><div class="stat-num sn-batch">8</div><div class="stat-label">Remaining Batches</div></div>','<div class="stat"><div class="stat-num sn-batch">7</div><div class="stat-label">Remaining Batches</div></div>','batch stat'),
('<span class="section-count">16 entries · 4 parts</span>','<span class="section-count">14 entries · 3 parts</span>','inventory count'),
('<span class="section-count">16 entries</span>','<span class="section-count">14 entries</span>','brief count')]: s=one(s,a,b,label)
s=rx(s,r'\n  <div class="part-block">\n    <div class="part-label">Part III — Raw Work to Evidence · 2 pending</div>.*?(?=\n  <div class="part-block">\n    <div class="part-label">Part IV)','', 'inventory')
s=rx(s,r'\n  <!-- R-01 -->.*?(?=\n  <!-- S-01 -->)','', 'briefs')
s=rx(s,r'\n\s*<tr><td class="batch-num">3</td><td class="batch-entries">R-01, R-03</td>.*?</tr>','', 'batch row')
s=one(s,'Batches 1 and 2 are complete. Remaining drafting proceeds part-by-part beginning with Batch 3 / Part III, using the adjudicated Part I and Part II bodies as the entry-level quality bar.','Batches 1 through 3 are complete. Remaining drafting proceeds part-by-part beginning with Batch 4 / Part IV, using the adjudicated Parts I through III as the entry-level quality bar.','order')
s=one(s,'<strong>Batches 1 and 2 completed 2026-08-24:</strong> T-01/T-02 and W-01/W-02/W-03 passed bounded disposition and were promoted from pending to drafted state. The table below contains the eight remaining production batches; the original Batch 1 drafting prompt remains preserved in Section 6 as historical provenance.','<strong>Batches 1 through 3 completed 2026-08-24:</strong> T-01/T-02, W-01/W-02/W-03, and R-01/R-03 passed bounded disposition and were promoted from pending to drafted state. The table below contains the seven remaining production batches; the original Batch 1 drafting prompt remains preserved in Section 6 as historical provenance.','callout')

def p73(card):
 card=meta_edit(card,lambda x: one(x,' contested zones ',' institutional interest map aggregate the source-level disclosures above by conclusion or outcome. for each identified interest: conclusion / outcome: [the conclusion or outcome an institution has a stake in] sources with an identified stake: [named sources] nature of interest: [funding / regulatory / commercial / organizational / other] evidentiary implication: [what must be disclosed or independently verified; interest alone is not evidence the source is wrong] if none are identified, state: none identified. contested zones ','r01 meta map'))
 return pre_edit(card,lambda x: rx(x,r'(explicitly, or state: NONE IDENTIFIED\]\s*)(━+CONTESTED ZONES)',r'\1━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━INSTITUTIONAL INTEREST MAP\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nAggregate the source-level disclosures above by conclusion or outcome.\n\nFor each identified interest: CONCLUSION / OUTCOME: [The conclusion or outcome an institution has a stake in]\n\nSOURCES WITH AN IDENTIFIED STAKE: [Named sources]\n\nNATURE OF INTEREST: [Funding / regulatory / commercial / organizational / other]\n\nEVIDENTIARY IMPLICATION: [What must be disclosed or independently verified; interest alone is not evidence the source is wrong]\n\nIf none are identified, state: NONE IDENTIFIED.\n\n\2','r01 visible map'))
s=page_edit(s,73,p73)

def p74(card):
 def m(x):
  x=one(x,'five components:','six components:','r01 meta count'); return one(x,'institutional position;','institutional position; institutional interest map aggregating sources by the conclusions or outcomes they have an identified stake in;','r01 meta expected')
 def p(x):
  x=one(x,'Five components:','Six components:','r01 visible count'); return one(x,'institutional position;','institutional position; INSTITUTIONAL INTEREST MAP aggregating sources by the conclusions or outcomes they have an identified stake in;','r01 visible expected')
 return pre_edit(meta_edit(card,m),p)
s=page_edit(s,74,p74)

def p83(card):
 card=meta_edit(card,lambda x: one(x,'independent replication should be attempted before acting on this result. not replication-ready:','independent replication should be attempted before acting on this result. very high risk: severe or compounding threats across core design and reporting dimensions. the result should not be load-bearing before independent replication. not replication-ready:','r03 meta very high'))
 return pre_edit(card,lambda x: rx(x,r'(Independent replication should be attempted before\s+acting on this result\.\s+)(NOT REPLICATION-READY:)',r'\1VERY HIGH RISK: Severe or compounding threats across core design and reporting dimensions. The result should not be load-bearing before independent replication. \2','r03 visible very high'))
s=page_edit(s,83,p83)

def p84(card):
 def m(x):
  x=one(x,'one of four levels:','one of four risk levels:','r03 meta label'); return one(x,'low risk, moderate risk, high risk, or not replication-ready.','low risk, moderate risk, high risk, or very high risk. if critical information is missing, report not replication-ready as a separate assessment-status outcome rather than forcing a risk level.','r03 meta taxonomy')
 def p(x):
  x=one(x,'one of four levels:','one of four risk levels:','r03 visible label'); return rx(x,r'LOW\s+RISK, MODERATE RISK, HIGH RISK, or NOT REPLICATION-READY\.','LOW\nRISK, MODERATE RISK, HIGH RISK, or VERY HIGH RISK. If critical information is missing, report NOT REPLICATION-READY as a separate assessment-status outcome rather than forcing a risk level.','r03 visible taxonomy')
 return pre_edit(meta_edit(card,m),p)
s=page_edit(s,84,p84)

def p85(card):
 card=meta_edit(card,lambda x: one(x,'→if a replication attempt proceeds','→run r-05 (failure-to-test converter) on the highest-severity replication risks or blockers to convert them into concrete test specifications before attempting replication. →if a replication attempt proceeds','r03 meta r05'))
 return pre_edit(card,lambda x: rx(x,r'(→Run R-09 \(Citation\s+Integrity Check\).*?artifact rather than the effect\.\s+)(→If a replication attempt proceeds)',r'\1→Run R-05 (Failure-to-Test Converter) on the highest-severity replication risks or blockers to convert them into concrete test specifications before attempting replication. \2','r03 visible r05'))
s=page_edit(s,85,p85)
s=one(s,"document.getElementById('b-r01').classList.add('open');","document.getElementById('b-s01').classList.add('open');",'startup1')
s=one(s,"document.getElementById('b-r03').classList.add('open');","document.getElementById('b-s02').classList.add('open');",'startup2')
for f in ('id="b-r01"','id="b-r03"','<td class="batch-entries">R-01, R-03</td>'):
 if f in s: raise SystemExit('pending residue '+f)
if s.count('R-01 Source Map with Contested Zones')!=1 or s.count('R-03 Replication Risk Auditor')!=1: raise SystemExit('canonical title count changed')
INDEX.write_text(s,encoding='utf-8',newline=''); POST=sha(INDEX)

for rel in ('tests/test_batch1_disposition.py','tests/test_batch2_disposition.py','tests/test_reconcile_entry_lineage.py'):
 p=ROOT/rel; t=p.read_text(encoding='utf-8')
 t=t.replace('expected_pending=16','expected_pending=14').replace('expected_drafted=75','expected_drafted=77').replace('16 pending entries · 8 remaining batches · drafting authority','14 pending entries · 7 remaining batches · drafting authority').replace('Production state: 75 drafted · 0 restore · 16 pending','Production state: 77 drafted · 0 restore · 14 pending').replace("document.getElementById('b-r01').classList.add('open');","document.getElementById('b-s01').classList.add('open');").replace("document.getElementById('b-r03').classList.add('open');","document.getElementById('b-s02').classList.add('open');").replace('test_repository_post_state_reconciles_to_16_75_91','test_repository_post_state_reconciles_to_14_77_91')
 p.write_text(t,encoding='utf-8')

(ROOT/'tests/test_batch3_disposition.py').write_text('''from __future__ import annotations\nimport html,re,unittest\nfrom pathlib import Path\nfrom tools.reconcile_entry_lineage import reconcile,validate_expectations\nROOT=Path(__file__).resolve().parents[1]; INDEX=ROOT/"index.html"; FIELDS=("WHAT IT DOES","WHEN TO USE","THE PROMPT","INPUTS NEEDED","EXPECTED OUTPUT","KNOBS","FAILURE MODE","FOLLOW-UP","SAFETY NOTES")\ndef page(n):\n s=INDEX.read_text(encoding="utf-8"); m=re.search(rf'<article class="manual-page-card" id="manual-page-{n:03d}"[^>]*>.*?</article>',s,re.S); assert m; return m.group(0)\ndef vis(c):\n m=re.search(r'<pre>(.*?)</pre>',c,re.S); return html.unescape(re.sub(r'<[^>]+>','',m.group(1)))\ndef meta(c):\n m=re.search(r'data-manual-text="([^"]*)"',c,re.S); return html.unescape(m.group(1))\nclass Batch3DispositionTests(unittest.TestCase):\n def test_state(self):\n  r=reconcile(INDEX); self.assertEqual(validate_expectations(r,expected_pending=14,expected_drafted=77,expected_total=91,expected_pages=315),[]); p={x.entry_id for x in r.pending_entries}; b={x.entry_id for x in r.briefs}; self.assertNotIn("R-01",p); self.assertNotIn("R-03",p); self.assertNotIn("R-01",b); self.assertNotIn("R-03",b)\n def test_bodies_fields(self):\n  d={"R-01":"\\n".join(vis(page(n)) for n in range(71,78)),"R-03":"\\n".join(vis(page(n)) for n in range(79,87))}; self.assertEqual(d["R-01"].count("R-01 Source Map with Contested Zones"),1); self.assertEqual(d["R-03"].count("R-03 Replication Risk Auditor"),1); [self.assertIn(f,x) for x in d.values() for f in FIELDS]\n def test_r01(self):\n  cs=[page(n) for n in range(71,77)]; b=" ".join(vis(c) for c in cs); m=" ".join(meta(c) for c in cs); self.assertIn("INSTITUTIONAL INTEREST MAP",b); self.assertIn("SOURCE FLATTENING WARNINGS",b); self.assertIn("CONTESTED ZONES",b); self.assertIn("KNOWN GAPS",b); self.assertIn("institutional interest map",m); self.assertIn("Six components:",b)\n def test_r03(self):\n  cs=[page(n) for n in range(79,87)]; b=" ".join(vis(c) for c in cs); m=" ".join(meta(c) for c in cs); self.assertIn("VERY HIGH RISK",b); self.assertIn("NOT REPLICATION-READY",b); self.assertIn("R-05 (Failure-to-Test Converter)",b); self.assertIn("HARKING FLAGS",b); self.assertIn("very high risk",m); self.assertIn("separate assessment-status outcome",m); self.assertIn("r-05 (failure-to-test converter)",m)\n def test_startup(self):\n  s=INDEX.read_text(encoding="utf-8"); self.assertIn("document.getElementById('b-s01').classList.add('open');",s); self.assertIn("document.getElementById('b-s02').classList.add('open');",s); self.assertNotIn('<td class="batch-entries">R-01, R-03</td>',s)\nif __name__=="__main__": unittest.main()\n''',encoding='utf-8')
(ROOT/'docs/BATCH3_DISPOSITION_2026-08-24.md').write_text(f'''# Batch 3 Disposition Record — 2026-08-24\n\nBounded editorial disposition of the existing canonical bodies for `R-01 Source Map with Contested Zones` and `R-03 Replication Risk Auditor`.\n\n## Artifact binding\n- Base commit: `{BASE}`\n- Pre-mutation `index.html` SHA-256: `{PRE}`\n- Post-mutation `index.html` SHA-256: `{POST}`\n- Pre-state: 16 pending / 75 drafted / 91 semantic entries / 315 pages / 8 remaining batches\n- Post-state: 14 pending / 77 drafted / 91 semantic entries / 315 pages / 7 remaining batches\n- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`\n\n## Frozen audit matrix\n| Entry | Classification | Demonstrated gap | Disposition |\n|---|---|---|---|\n| R-01 | PARTIAL | Cross-source INSTITUTIONAL INTEREST MAP absent. | Added aggregate map and named it in EXPECTED OUTPUT; preserved per-source disclosure. |\n| R-03 | PARTIAL | VERY HIGH risk level and R-05 follow-up absent. | Restored VERY HIGH, retained NOT REPLICATION-READY as separate insufficiency status, and added R-05 follow-up. |\n\n## Verification contract\nAccept only after complete Python, strict validator, 14/77/91 lineage, frozen classifier, editorial-lineage audit, `git diff --check`, Chromium/Firefox/WebKit smoke, and human final diff review all pass on the exact cleaned head.\n''',encoding='utf-8')
print(f'Batch 3 staged: {PRE} -> {POST}')
