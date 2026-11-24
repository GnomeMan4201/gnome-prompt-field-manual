"""Source-bound editorial tests; no model output or prompt efficacy is measured."""
import base64
import json
import re
import subprocess
import unittest
from pathlib import Path
from batch10_baseline import BATCH10_SOURCE_SHA, PR47_MERGE, ROOT, batch10_base_bytes
from batch9_baseline import BATCH9_DISPOSITION_SOURCE_SHA
from test_batch6_correction import (ADAPTER_PATH, CANONICAL, DATASET, EXPECTED_PDF_SHA256,
    HISTORICAL_ROOTS, INDEX_PATH, STATIC, cards, changed_pages, dataset_rows, digest, parity_errors, visible, canonical_surface)
from test_batch6_partial_disposition import extract_brief

PAGES = {239, 240, 241, 242, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253}
READER = 'GNOME-Field-Manual.html'
REQUIRED = {
    'review classification': (239, ('comment id', 'accepted / contested / clarification needed / deferred', 'partial acceptance', 'faithful paraphrase')),
    'review action': (240, ('specific counter-evidence', 'exact change', 'verification criterion', 'one to three sentences', 'out of scope')),
    'review evidence': (240, ('verified change / planned / not made / unverified', 'before/after artifact or diff', 'never invent a revision', 'summary table')),
    'review completion': (241, ('mandatory summary table', 'do not treat unresolved disagreements as resolved', 'verify it against the supplied versions')),
    'review prior': (239, ('t-06 (belief update scaffold) first',)),
    'review safety': (242, ('never hide a material disagreement', 'missing evidence')),
    'correction source': (244, ('original claim / artifact', 'error description', 'discovery record', 'impact assessment', 'corrected claim', 'known downstream uses', 'unassessed claims as unassessed')),
    'correction threshold': (245, ('minor correction', 'material correction', 'withdrawal', 'retraction', 'scope of retraction', 'uncertain', 'not reputation')),
    'correction archive': (245, ('link original and corrected records', 'do not silently rewrite', 'standalone notice', 'draft pending human review')),
    'correction artifact': (246, ('original claim, error description, corrected claim, impact assessment, and scope of retraction', 'reader unfamiliar with the original')),
    'correction safety': (247, ('institutional communication norms', 'must not obscure the original error', 'r-11 (negative result documenter)')),
    'guide prerequisites': (248, ('exact revision', 'readme to pass', 'mark the guide provisional', 'do not invent commands')),
    'guide scope': (249, ('contribution scope', 'conventions', 'rationale and source', 'inspected commands from executed commands', 'ownership')),
    'guide acceptance': (250, ('acceptance criteria', 'what done looks like', 'do not invent a channel', 'licensing, attribution', 'observed results')),
    'guide artifact': (251, ('decision context', 's-10 (architecture decision record generator)', 'first contribution guide', 'real, approved and available issue', 'do not invent an issue')),
    'guide safety': (253, ('confirmed, monitored private reporting route', 'do not fabricate', 'not proof that vulnerabilities cannot exist')),
}

def contract_errors(page_text):
    norm = {p: canonical_surface(t) for p, t in page_text.items()}
    return {key for key, (page, terms) in REQUIRED.items() if any(t not in norm[page] for t in terms)}

class Batch10ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / 'index.html').read_bytes()
        cls.reader = (ROOT / READER).read_bytes()
        cls.base = batch10_base_bytes('index.html')
        cls.base_reader = batch10_base_bytes(READER)
        cls.pages = cards(cls.raw)
        cls.static = cards(cls.reader, STATIC)
        cls.rows, cls.encoded = dataset_rows(cls.reader)
        cls.text = {n: visible(cls.pages[n]) for n in PAGES}

    def test_contracts_and_baseline_deficiencies(self):
        self.assertEqual(contract_errors(self.text), set())
        old = cards(self.base)
        self.assertTrue({'review classification', 'review evidence', 'correction threshold', 'guide artifact'} <= contract_errors({n: visible(old[n]) for n in PAGES}))

    def test_required_field_mutations(self):
        for key, (page, terms) in REQUIRED.items():
            norm = canonical_surface(self.text[page])
            for term in terms:
                with self.subTest(requirement=key, removed=term):
                    self.assertIn(term, norm)
                    self.assertIn(key, contract_errors({**self.text, page: norm.replace(term, 'omitted')}))

    def test_scope_four_surfaces_and_neighbor_suffixes(self):
        old = cards(self.base)
        old_static = cards(self.base_reader, STATIC)
        old_rows, old_encoded = dataset_rows(self.base_reader)
        for before, after in ((old,self.pages),(old_static,self.static),(old_encoded,self.encoded)):
            self.assertEqual(list(after), list(range(1,316)))
            self.assertEqual(changed_pages(before,after), PAGES)
        self.assertEqual(CANONICAL.sub(b'', self.raw), CANONICAL.sub(b'', self.base))
        self.assertEqual(DATASET.sub(b'', STATIC.sub(b'', self.reader)), DATASET.sub(b'', STATIC.sub(b'', self.base_reader)))
        for n, heading in ((242,'  P-09 Correction/Retraction Writer'),(247,'  P-10 Open Source Contribution Guide Generator')):
            for a,b in ((visible(old[n]),visible(self.pages[n])),(old_rows[n]['text'],self.rows[n]['text']), (old_static[n].decode(),self.static[n].decode())):
                self.assertIn(heading,a); self.assertIn(heading,b)
                self.assertEqual(a.split(heading,1)[1],b.split(heading,1)[1])
        for n in PAGES:
            self.assertEqual(parity_errors(n,self.pages[n],self.rows[n],self.static[n]),set())

    def test_parity_negative_controls(self):
        n=240
        card,row,static=self.pages[n],self.rows[n],self.static[n]
        self.assertIn('metadata',parity_errors(n,card.replace(b'summary table',b'missing section'),row,static))
        self.assertIn('dynamic',parity_errors(n,card,dict(row,text='different'),static))
        self.assertIn('static',parity_errors(n,card,row,static.replace(b'SUMMARY TABLE',b'MISSING SECTION')))

    def test_identity_and_cross_references(self):
        for page,heading in ((238,'P-08 Peer Review Responder'),(242,'P-09 Correction/Retraction Writer'),(247,'P-10 Open Source Contribution Guide Generator'),(232,'P-07 RFC Draft Generator'),(23,'T-06 Belief Update Scaffold'),(50,'W-05 Hedge Auditor'),(60,'W-09 Claim-Evidence Separator'),(219,'P-04 Technical Post-Mortem Publisher'),(101,'R-11 Negative Result Documenter'),(217,'P-03 README Quality Auditor'),(140,'S-10 Architecture Decision Record Generator'),(138,'S-09 Incident Report Scaffold')):
            self.assertRegex(visible(self.pages[page]),rf'(?m)^\s*{re.escape(heading)}\s*$')
        self.assertIn(b'S-09 (Architecture Decision Record Generator',extract_brief(self.raw,b'p10'))
        self.assertIn('s-10 (architecture decision record generator)',canonical_surface(self.text[251]))
        self.assertEqual(digest(self.base),BATCH9_DISPOSITION_SOURCE_SHA)
        for id in (b'sec05',b'p08',b'p09',b'p10'):
            self.assertEqual(extract_brief(self.raw,id),extract_brief(self.base,id))

    def test_historical_artifacts_pdf_and_current_identity(self):
        paths=subprocess.check_output(['git','ls-tree','-r','--name-only',PR47_MERGE,'--',*HISTORICAL_ROOTS],cwd=ROOT,text=True).splitlines()
        paths.remove(INDEX_PATH)
        for path in paths:
            with self.subTest(path=path): self.assertEqual((ROOT/path).read_bytes(),batch10_base_bytes(path))
        pdf=re.search(rb'data="data:application/pdf;base64,([^"]+)"',self.raw)[1]
        self.assertEqual(digest(base64.b64decode(pdf,validate=True)),EXPECTED_PDF_SHA256)
        cur=json.loads((ROOT/INDEX_PATH).read_bytes());old=json.loads(batch10_base_bytes(INDEX_PATH))
        self.assertEqual(cur['counts'],{'pending':4,'drafted':87,'total':91,'pages':315})
        self.assertEqual(cur['bodyCoverage'],0)
        self.assertEqual(digest(self.raw),BATCH10_SOURCE_SHA)
        self.assertEqual(cur['sourceIndexSha256'],BATCH10_SOURCE_SHA)
        self.assertIn(f"const EXPECTED_SOURCE='{BATCH10_SOURCE_SHA}';",(ROOT/ADAPTER_PATH).read_text())
        for a,b in zip(old['entries'],cur['entries'],strict=True):
            self.assertEqual({k:v for k,v in a.items() if k not in {'occurrencePages','titleCandidate'}},{k:v for k,v in b.items() if k not in {'occurrencePages','titleCandidate'}})
            self.assertFalse((set(a['occurrencePages'])^set(b['occurrencePages']))-PAGES)
            if a['id']!='AP-03': self.assertEqual(a['titleCandidate'],b['titleCandidate'])
        self.assertEqual({r['id'] for r in cur['entries'] if r['pendingInventory']},{'SEC-05','P-08','P-09','P-10'})
