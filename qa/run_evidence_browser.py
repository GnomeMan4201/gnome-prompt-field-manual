#!/usr/bin/env python3
"""Optional browser acceptance; run explicitly, not as CI unit test dependency."""
from __future__ import annotations
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import shutil
import tempfile
import threading

from playwright.sync_api import expect, sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from reactor_evidence_v2 import verify_capsule, checksums_for

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
url=f'http://127.0.0.1:{server.server_port}/workbench/reactor/evidence-lab.html'
issues=[]
try:
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'),headless=True,
                                           args=['--no-sandbox','--disable-dev-shm-usage'])
        context=browser.new_context(viewport={'width':1440,'height':900},accept_downloads=True)
        page=context.new_page()
        page.on('pageerror',lambda e:issues.append('PAGE_JS:'+str(e)))
        response=page.goto(url,wait_until='networkidle')
        assert response.status==200
        assert page.get_by_role('heading',name='Evidence, not assertions.').count()==1
        page.get_by_role('button',name='Load clearly labeled synthetic demonstration').click()
        assert 'SYNTHETIC DEMONSTRATION' in page.locator('#status').inner_text()
        page.get_by_role('button',name='Evaluate raw observations').click()
        assert page.locator('#induced').inner_text()=='1',page.locator('#result').inner_text()
        assert page.locator('#pairs').inner_text()=='1'
        page.locator('#evaluate').focus()
        page.keyboard.press('Enter')
        assert 'Evaluation completed' in page.locator('#status').inner_text()
        with page.expect_download() as info:
            page.get_by_role('button',name='Export v2 evidence capsule').click()
        download=info.value
        assert download.suggested_filename.startswith('SYNTHETIC-NOT-EMPIRICAL')
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/download.suggested_filename;download.save_as(str(path))
            obj=json.loads(path.read_text())
            assert obj['manifest']['isSyntheticDemo'] is True
            verdict=verify_capsule(obj);assert verdict['valid'],verdict
            page.locator('#capsule-file').set_input_files(str(path))
            expect(page.locator('#status')).to_contain_text('Capsule validated')
            tampered=json.loads(path.read_text());tampered['payload']['observations'][1]['outputText']='"tampered"'
            altered=Path(d)/'tampered.json';altered.write_text(json.dumps(tampered))
            page.locator('#capsule-file').set_input_files(str(altered))
            expect(page.locator('#status')).to_contain_text('CHECKSUM_MISMATCH:observations.json')
            expect(page.locator('#pairs')).to_have_text('—')
            print('DESKTOP: source labels, synthetic demo, rescoring, Enter key, browser download, Python verify, file-input reimport, tamper rejection PASS')
        mobile=browser.new_context(viewport={'width':390,'height':844})
        mp=mobile.new_page()
        mp.on('pageerror',lambda e:issues.append('MOBILE_JS:'+str(e)))
        mp.goto(url,wait_until='networkidle')
        dims=mp.evaluate('({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})')
        assert dims['scroll']<=dims['client'],dims
        mp.get_by_role('button',name='Load clearly labeled synthetic demonstration').click()
        mp.get_by_role('button',name='Evaluate raw observations').click()
        assert mp.locator('#induced').inner_text()=='1'
        print('MOBILE 390x844: no horizontal overflow; demo and evaluation controls accessible PASS')
        browser.close()
        assert not issues,issues
        print('NO JAVASCRIPT PAGE ERRORS')
finally:
    server.shutdown();server.server_close();thread.join(timeout=3)
