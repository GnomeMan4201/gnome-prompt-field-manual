"""Offline external case integrity tests; no Ollama inference or external network."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from reactor_external_case import (CaseError, MODEL, sha, strict_json,
    verify_bundle, verify_mirror, verify_raw_condition, verify_index)


class ExternalCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)/'evidence'
        self.dir.mkdir()

    def manifest(self):
        lines = [sha(p.read_bytes())+'  '+p.name for p in sorted(self.dir.iterdir())
                 if p.is_file() and p.name != 'SHA256SUMS.txt']
        (self.dir/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')

    def sample(self):
        request = {'model':MODEL,'format':'json','stream':False,'prompt':'test prompt'}
        response = {'model':MODEL,'done':True,'response':'{"answer":"18ms"}'}
        (self.dir/'control-request.raw.json').write_text(json.dumps(request))
        (self.dir/'control-response.raw.json').write_text(json.dumps(response))

    def test_manifest_validates_intact_files(self):
        (self.dir/'test.txt').write_text('payload')
        self.manifest()
        got = verify_bundle(self.dir)
        self.assertEqual(got['verifiedFiles'],1)

    def test_manifest_rejects_changed_data(self):
        (self.dir/'test.txt').write_text('payload')
        self.manifest()
        (self.dir/'test.txt').write_text('tampered')
        with self.assertRaisesRegex(CaseError,'EVIDENCE_HASH_MISMATCH'):
            verify_bundle(self.dir)

    def test_manifest_rejects_unlisted_extra_file(self):
        (self.dir/'test.txt').write_text('payload')
        self.manifest()
        (self.dir/'unlisted.txt').write_text('extra')
        with self.assertRaisesRegex(CaseError,'EVIDENCE_FILESET_MISMATCH'):
            verify_bundle(self.dir)

    def test_manifest_rejects_traversal(self):
        (self.dir/'SHA256SUMS.txt').write_text('a'*64+'  ../outside\n')
        with self.assertRaisesRegex(CaseError,'INVALID_MANIFEST_ENTRY'):
            verify_bundle(self.dir)

    def test_manifest_rejects_symlink(self):
        (self.dir/'test.txt').write_text('payload')
        self.manifest()
        (self.dir/'test.txt').unlink()
        (self.dir/'test.txt').symlink_to('/etc/hosts')
        with self.assertRaisesRegex(CaseError,'MISSING_OR_UNSAFE_FILE'):
            verify_bundle(self.dir)

    def test_raw_answer_accepts_matching_request(self):
        self.sample()
        self.assertEqual(verify_raw_condition(self.dir,'control','18ms'),'18ms')
        with self.assertRaisesRegex(CaseError,'ANSWER_DISAGREEMENT'):
            verify_raw_condition(self.dir,'control','999ms')

    def test_raw_rejects_duplicate_keys_and_incomplete_model(self):
        self.sample()
        p = self.dir/'control-response.raw.json'
        p.write_text('{"model":"'+MODEL+'","done":true,"done":true,"response":"{}"}')
        with self.assertRaisesRegex(CaseError,'DUPLICATE_JSON_KEY'):
            verify_raw_condition(self.dir,'control','18ms')
        response = {'model':MODEL, 'done':False, 'response':'{"answer":"18ms"}'}
        p.write_text(json.dumps(response))
        with self.assertRaisesRegex(CaseError,'RESPONSE_INCOMPLETE'):
            verify_raw_condition(self.dir,'control','18ms')

    def test_index_rejects_modified_summary(self):
        good = {'schemaVersion':'gnome.phase8c.external-case.v1','caseId':'phase8c-qwen-0p5b-instruction-attribution',
                'observedAnswers':{'pilot':['18ms','999ms']}}
        self.assertTrue(verify_index(good, good.copy()))
        fake = json.loads(json.dumps(good))
        fake['observedAnswers']['pilot']=['999ms','999ms']
        with self.assertRaisesRegex(CaseError,'CASE_INDEX_REPLAY_MISMATCH'):
            verify_index(fake, good)

    def test_mirror_rejects_unequal_hashes(self):
        (self.dir/'test.txt').write_text('payload')
        self.manifest()
        mirror = Path(self.tmp.name)/'usb'/self.dir.name
        mirror.mkdir(parents=True)
        (mirror/'test.txt').write_text('tampered')
        (mirror/'SHA256SUMS.txt').write_bytes((self.dir/'SHA256SUMS.txt').read_bytes())
        with self.assertRaisesRegex(CaseError,'EVIDENCE_HASH_MISMATCH'):
            verify_mirror(self.dir, mirror.parent)


if __name__ == '__main__':
    unittest.main()
