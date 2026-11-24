"""Source-bound Batch 5 REVISE hold. Does not promote a pending entry."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

from tools.reconcile_entry_lineage import TreeParser, extract_briefs, extract_pending, reconcile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'index.html'
INDEX = ROOT / 'workbench/data/current_entry_identity_index.json'
NOTE = ROOT / 'docs/BATCH5_REVISE_HOLD_2026-11-23.md'
PINNED_SHA = '8c7a56dc0687809e691ee09030f2a028c290c3ab81a64e63f4b58b6d809df3bd'


class Batch5HoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.parser = TreeParser()
        cls.parser.feed(cls.raw.decode('utf-8'))
        cls.parser.close()
        cls.nodes = {n.element_id: n for n in cls.parser.root.walk() if n.element_id}

    def page_text(self, n: int) -> str:
        node = self.nodes[f'manual-page-{n:03}']
        pre = node.first_tag('pre')
        self.assertIsNotNone(pre)
        return pre.raw_text().replace('\u00ad', '')

    def test_exact_source_hash_and_page_count_unchanged(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), PINNED_SHA)
        self.assertEqual(sum('manual-page-card' in node.classes for node in self.nodes.values()), 315)

    def test_pending_brief_is_not_misidentified_as_canonical_adr(self):
        pending = [v for v in extract_pending(self.parser.root) if v.entry_id == 'S-10']
        briefs = [v for v in extract_briefs(self.parser.root) if v.entry_id == 'S-10']
        self.assertEqual([(v.entry_id, v.name) for v in pending], [('S-10', 'Migration Risk Classifier')])
        self.assertEqual([(v.entry_id, v.name) for v in briefs], [('S-10', 'Migration Risk Classifier')])
        self.assertIn('S-07 Migration Risk Classifier', self.page_text(129))
        self.assertIn('S-10 Architecture Decision Record Generator', self.page_text(140))

    def test_frozen_rollback_trigger_contract_not_present_in_standard_prompt(self):
        brief = self.nodes['b-s10'].text().upper()
        self.assertIn('ROLLBACK TRIGGER CONDITIONS', brief)
        manuscript = ' '.join(self.page_text(n) for n in range(130, 134)).upper()
        self.assertNotIn('ROLLBACK TRIGGER CONDITIONS', manuscript)
        self.assertIn('MIGRATION VERDICT', manuscript)
        self.assertIn('THE PROMPT', manuscript)
        self.assertIn('EXPECTED OUTPUT', manuscript)
        self.assertIn('DOES NOT MONITOR MIGRATION IN PROGRESS', re.sub(r'\s+', ' ', re.sub(r'-\s+', '', self.page_text(135).upper())))

    def test_pending_state_and_current_identity_candidate_remain_explicit(self):
        report = reconcile(SOURCE)
        self.assertEqual(report.summary.pending_inventory_rows, 11)
        self.assertEqual(report.summary.drafting_briefs, 11)
        index = json.loads(INDEX.read_text())
        self.assertEqual(index['sourceIndexSha256'], PINNED_SHA)
        self.assertEqual(index['counts'], {'pending': 11, 'drafted': 80, 'total': 91, 'pages': 315})
        self.assertEqual(index['bodyCoverage'], 0)
        entry = next(row for row in index['entries'] if row['id'] == 'S-10')
        self.assertEqual(entry['titleCandidate'], 'Migration Risk Classifier')
        self.assertEqual(entry['occurrencePages'], [140])
        self.assertEqual(entry['titleAuthority'], 'reconciler-candidate-not-verified-heading')
        self.assertIsNone(entry['canonicalBody'])
        self.assertEqual(entry['bodyStatus'], 'UNRESOLVED_BOUNDARIES')

    def test_adjudication_hold_is_recorded_not_approved(self):
        note = NOTE.read_text()
        self.assertIn('REVISE / DO NOT PROMOTE', note)
        self.assertIn('manual-page-129', note)
        self.assertIn('manual-page-140', note)
        self.assertIn('ROLLBACK TRIGGER CONDITIONS', note)
        self.assertIn(PINNED_SHA, note)
        self.assertIn('No canonical manuscript edit', note)


if __name__ == '__main__':
    unittest.main()
