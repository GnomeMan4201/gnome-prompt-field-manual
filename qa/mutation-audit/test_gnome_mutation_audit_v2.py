"""Harness tests using synthetic repositories; NOT GNOME validator tests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'gnome_mutation_audit_v2.py'
spec = importlib.util.spec_from_file_location('audit', SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class HarnessTests(unittest.TestCase):
    def test_classification(self):
        def x(state): return {'check': {'state': state}}
        for a,b,c,want in [('PASS','PASS',False,'SURVIVED_TESTED_CHECKS'),('PASS','REJECTED_UNREVIEWED',False,'REJECTED_REVIEW_REQUIRED'),('PASS','ERROR',False,'INCONCLUSIVE_CHECK_ERROR'),('ERROR','PASS',False,'INCONCLUSIVE_BASELINE'),('PASS','PASS',True,'CONTROL_ACCEPTED'),('PASS','REJECTED_UNREVIEWED',True,'CONTROL_REJECTED_REVIEW_REQUIRED')]:
            self.assertEqual(audit.verdict(x(a),x(b),c),want)

    def test_process_failures(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            self.assertEqual(audit.run([sys.executable,'-c','raise ValueError("bad")'],p,2)['state'],'ERROR')
            self.assertEqual(audit.run([sys.executable,'-c','import time; time.sleep(5)'],p,0.05)['state'],'ERROR')
            self.assertEqual(audit.run(['nonexistent-gnome-test-executable'],p,2)['state'],'ERROR')
            self.assertEqual(audit.run([sys.executable,'-c','raise SystemExit(1)'],p,2)['state'],'REJECTED_UNREVIEWED')

    def test_two_reader_precondition(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'index.html').write_text('target'); (p/'GNOME-Field-Manual.html').write_text('absent')
            with self.assertRaises(ValueError): audit.sub(None,'target','changed',both_readers=True)(p)

    def fixture(self, root, broken=False):
        def put(path,text):
            p=root/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text)
        put('index.html','executed. It has failed badly.\nor P-05 (RFC):')
        put('GNOME-Field-Manual.html','executed. It has failed badly.\nor P-05 (RFC):')
        put('tests/test_fixture.py','import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n')
        put('tools/validate_manual.py', 'from pathlib import Path\nraise SystemExit(1 if "succeeded" in Path("index.html").read_text() else 0)\n' if not broken else 'raise SystemExit(1)\n')
        for f in ['reconcile_entry_lineage','audit_editorial_lineage','build_current_body_review']: put('tools/'+f+'.py','pass\n')
        kit='research/phase8d-independent-replication/kit/'
        put(kit+'payload','test\n'); import hashlib
        put(kit+'LOCK.sha256',hashlib.sha256(b'test\n').hexdigest()+'  payload\n')
        def git(*a): return subprocess.check_output(['git','-C',str(root),*a],stderr=subprocess.STDOUT).decode().strip()
        git('init','-q'); git('add','.'); git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture')
        return git('rev-parse','HEAD')

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); root=p/'repo'; root.mkdir(); sha=self.fixture(root)
            out=p/'out.json'; r=subprocess.run([sys.executable,str(SCRIPT),str(root),str(out),'--commit',sha,'--only','M01,M02,M16'],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            data=json.loads(out.read_text()); self.assertTrue(data['source_checkout_unchanged'])
            self.assertEqual([m['verdict'] for m in data['mutations']],['REJECTED_REVIEW_REQUIRED','REJECTED_REVIEW_REQUIRED','CONTROL_ACCEPTED'])
            self.assertEqual(len(data['mutations'][1]['changes']),2)
            self.assertIn('subject_reference_gate',data['missing_optional_checks'])
            self.assertIn('failed badly',(root/'index.html').read_text())

    def test_bad_baseline_stops(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); root=p/'repo'; root.mkdir(); sha=self.fixture(root,True)
            out=p/'out.json'; r=subprocess.run([sys.executable,str(SCRIPT),str(root),str(out),'--commit',sha,'--only','M01'],capture_output=True,text=True)
            self.assertEqual(r.returncode,2); self.assertEqual(json.loads(out.read_text())['mutations'],[])

    def test_history_survives_snapshot(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); root=p/'repo'; root.mkdir(); first=self.fixture(root)
            (root/'extra.txt').write_text('second commit')
            subprocess.check_call(['git','-C',str(root),'add','extra.txt'])
            subprocess.check_call(['git','-C',str(root),'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','second'])
            sha=audit.git(root,'rev-parse','HEAD').decode().strip()
            dest=p/'snapshot'; dest.mkdir()
            audit.extract_snapshot(root,sha,dest)
            self.assertEqual(audit.git(dest,'show',first+':index.html'),audit.git(root,'show',first+':index.html'))
            self.assertEqual(audit.git(dest,'remote').strip(),b'')
            self.assertFalse((dest/'.git/objects/info/alternates').exists())
            self.assertFalse(any(k.startswith('.git/') for k in audit.hashes(dest)))
            (dest/'index.html').write_text('mutated')
            self.assertIn(b'failed badly',audit.git(dest,'show','HEAD:index.html'))
            self.assertFalse(audit.git(root,'status','--porcelain').strip())

    def test_unittest_failure_and_skip_classification(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); t=p/'test_example.py'
            cmd=[sys.executable,'-m','unittest','discover']
            for body,want in [
                ('self.assertTrue(False)','REJECTED_UNREVIEWED'),
                ('raise RuntimeError("oops")','ERROR'),
                ('self.skipTest("missing dependency")','ERROR'),
                ('self.assertTrue(True)','PASS'),
            ]:
                t.write_text('import unittest\nclass T(unittest.TestCase):\n def test_case(self): '+body+'\n')
                import shutil
                shutil.rmtree(p/'__pycache__',ignore_errors=True)
                self.assertEqual(audit.run(cmd,p,5)['state'],want)
            t.unlink()
            self.assertEqual(audit.run(cmd,p,5)['state'],'ERROR')

    def test_wrong_commit_and_dirty_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); root=p/'repo'; root.mkdir(); sha=self.fixture(root); dest=p/'snapshot'; dest.mkdir()
            with self.assertRaises(ValueError): audit.extract_snapshot(root,'0'*40,dest)
            (root/'untracked').write_text('dirty')
            with self.assertRaises(ValueError): audit.extract_snapshot(root,sha,dest)

if __name__=='__main__': unittest.main()
