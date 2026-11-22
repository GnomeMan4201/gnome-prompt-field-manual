import json,sys,threading,unittest
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from reactor_local_runner import run_local_ollama_trial,MAX_RESPONSE_BYTES

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.requests.append(self.path)
        if self.path!='/api/generate':self.send_error(404);return
        if self.server.mode=='redirect':
            self.send_response(302);self.send_header('Location','https://example.com/private');self.end_headers();return
        if self.server.mode=='large':
            self.send_response(200);self.send_header('Content-Length',str(MAX_RESPONSE_BYTES+1));self.end_headers();return
        body=json.dumps({'model':'local-test','response':'not an executable instruction'}).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass

class RunnerSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.server.mode='ok';cls.server.requests=[]
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.endpoint=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def test_success_is_raw_data(self):
        self.server.mode='ok';r=run_local_ollama_trial(self.endpoint,'local-test','hello',temperature=0,seed=1)
        self.assertTrue(r['ok']);self.assertEqual(r['outputText'],'not an executable instruction')
        self.assertEqual(self.server.requests[-1],'/api/generate')
    def test_redirect_fails_closed(self):
        self.server.mode='redirect';r=run_local_ollama_trial(self.endpoint,'local-test','hello')
        self.assertEqual(r['errorClass'],'REDIRECT_BLOCKED')
    def test_oversize_fails_closed(self):
        self.server.mode='large';r=run_local_ollama_trial(self.endpoint,'local-test','hello')
        self.assertEqual(r['errorClass'],'RESPONSE_TOO_LARGE')
    def test_request_budget(self):
        self.assertEqual(run_local_ollama_trial(self.endpoint,'m','x'*(128*1024))['errorClass'],'REQUEST_TOO_LARGE')
    def test_cancellation_before_io(self):
        r=run_local_ollama_trial(self.endpoint,'m','hello',cancel_check=lambda:True)
        self.assertEqual(r['errorClass'],'CANCELLED')

if __name__=='__main__':unittest.main()
