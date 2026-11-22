"""Tests exercise a loopback mock, never a live model or external service."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from reactor_pair_runner import run_pairs, EvidenceError
from reactor_evidence_v2 import analyze
from test_reactor_evidence_v2 import plan

class MockHandler(BaseHTTPRequestHandler):
    requests=[]
    def log_message(self,*args):pass
    def do_POST(self):
        if self.path!='/api/generate':self.send_error(404);return
        n=int(self.headers.get('Content-Length','0'));value=json.loads(self.rfile.read(n));self.requests.append(value)
        if 'REDIRECT' in value['prompt']:
            self.send_response(302);self.send_header('Location','http://example.com/');self.end_headers();return
        response=json.dumps({'model':value['model'],'response':'{"answer":"42"}'}).encode()
        self.send_response(200);self.send_header('Content-Length',str(len(response)));self.end_headers();self.wfile.write(response)

class LocalPairedRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),MockHandler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.endpoint='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join(timeout=3)
    def setUp(self):MockHandler.requests.clear()
    def test_local_pair_executes_as_data_without_scoring(self):
        p=plan();p['provider']='ollama-local';p['model']='fixture-model'
        r=run_pairs(p,self.endpoint,'mock-pair-1')
        self.assertTrue(r['executionComplete'])
        self.assertEqual(len(r['observations']),2)
        self.assertEqual(r['scoringStatus'],'NOT_EVALUATED')
        self.assertTrue(all('passed' not in o for o in r['observations']))
        self.assertEqual(analyze(p,r['observations'])['counts']['bothPass'],1)
        self.assertEqual(len(MockHandler.requests),2)
    def test_reject_external_and_no_connection(self):
        p=plan();p['provider']='ollama-local'
        with self.assertRaisesRegex(EvidenceError,'NON_LOOPBACK'):run_pairs(p,'http://example.com:11434','T1')
        self.assertEqual(MockHandler.requests,[])
    def test_no_redirect_followed(self):
        p=plan();p['provider']='ollama-local';p['prompts']['control']='REDIRECT from local test'
        r=run_pairs(p,self.endpoint,'T1')
        self.assertFalse(r['executionComplete'])
        self.assertEqual(r['errors'][0]['errorClass'],'REDIRECT_BLOCKED')
    def test_wrong_model_identity_is_not_silently_accepted(self):
        p=plan();p['provider']='ollama-local'
        def wrong_model(*args,**kwargs):return {'ok':True,'model':'unexpected-model','outputText':'{}'}
        r=run_pairs(p,self.endpoint,'T1',run_call=wrong_model)
        self.assertEqual(len(r['observations']),0)
        self.assertEqual(len(r['errors']),2)
        self.assertEqual(r['errors'][0]['errorClass'],'MODEL_IDENTITY_MISMATCH')

if __name__=='__main__':unittest.main()
