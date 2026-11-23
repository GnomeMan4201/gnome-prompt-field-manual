#!/usr/bin/env python3
"""Opt-in loopback-only Ollama /api/generate adapter.

No redirects, proxies, hostname resolution, API credentials, or arbitrary routes.
Models' outputs are untrusted observations, not commands or scoring instructions.
"""
from __future__ import annotations
import http.client
import ipaddress
import json
import socket
import time
import urllib.parse
from typing import Any

MAX_REQUEST_BYTES = 128 * 1024
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


def is_localhost_url(url: str) -> bool:
    try:
        p=urllib.parse.urlsplit(url)
        if p.scheme!='http' or p.username or p.password or p.query or p.fragment or p.path not in ('','/'):
            return False
        addr=ipaddress.ip_address(p.hostname or '')
        return addr.is_loopback and str(addr) in ('127.0.0.1','::1') and p.port is not None and p.port>0
    except (ValueError,TypeError):
        return False


def run_local_ollama_trial(endpoint:str, model:str, prompt:str,temperature:float|None=None,
                           seed:int|None=None,timeout_seconds:float=10.0,trial_id:str='TRIAL-1',
                           cancel_check=None,format_json:bool=False) -> dict[str,Any]:
    result={'trialId':trial_id,'ok':False,'rawResponse':None}
    if not is_localhost_url(endpoint):return {**result,'errorClass':'NON_LOOPBACK_ENDPOINT_BLOCKED'}
    if not isinstance(model,str) or not model.strip() or not isinstance(prompt,str):return {**result,'errorClass':'INVALID_REQUEST'}
    if type(timeout_seconds) not in (int,float) or not 0<timeout_seconds<=300:return {**result,'errorClass':'INVALID_TIMEOUT'}
    if cancel_check is not None and cancel_check():return {**result,'errorClass':'CANCELLED'}
    options={}
    if temperature is not None:options['temperature']=temperature
    if seed is not None:options['seed']=seed
    if type(format_json) is not bool:return {**result,'errorClass':'INVALID_FORMAT_MODE'}
    payload={'model':model,'prompt':prompt,'stream':False}
    if format_json:payload['format']='json'
    if options:payload['options']=options
    raw_payload=json.dumps(payload,ensure_ascii=False).encode('utf-8')
    if len(raw_payload)>MAX_REQUEST_BYTES:return {**result,'errorClass':'REQUEST_TOO_LARGE'}
    p=urllib.parse.urlsplit(endpoint)
    started=time.monotonic()
    # http.client uses a literal loopback address, never follows redirects or honors HTTP proxies.
    conn=http.client.HTTPConnection(p.hostname,p.port,timeout=timeout_seconds)
    try:
        conn.request('POST','/api/generate',body=raw_payload,headers={'Content-Type':'application/json','Accept':'application/json'})
        resp=conn.getresponse()
        if 300<=resp.status<400:return {**result,'errorClass':'REDIRECT_BLOCKED','httpStatus':resp.status}
        if resp.status!=200:return {**result,'errorClass':'HTTP_ERROR','httpStatus':resp.status}
        if resp.length is not None and resp.length>MAX_RESPONSE_BYTES:return {**result,'errorClass':'RESPONSE_TOO_LARGE'}
        raw=resp.read(MAX_RESPONSE_BYTES+1)
        if len(raw)>MAX_RESPONSE_BYTES:return {**result,'errorClass':'RESPONSE_TOO_LARGE'}
        if cancel_check is not None and cancel_check():return {**result,'errorClass':'CANCELLED'}
        decoded=raw.decode('utf-8')
        data=json.loads(decoded)
        if not isinstance(data,dict) or not isinstance(data.get('response'),str):return {**result,'errorClass':'INVALID_RESPONSE'}
        return {**result,'ok':True,'provider':'ollama-local','model':data.get('model',model),
                'requestedModel':model,'requestedOptions':options,'outputText':data['response'],
                'rawResponse':decoded,'rawRequest':raw_payload.decode('utf-8'),'elapsedSeconds':round(time.monotonic()-started,3),'errorClass':None}
    except (socket.timeout,TimeoutError):return {**result,'errorClass':'TIMEOUT'}
    except (OSError,http.client.HTTPException):return {**result,'errorClass':'CONNECTION_OR_NETWORK_ERROR'}
    except (UnicodeError,ValueError):return {**result,'errorClass':'INVALID_RESPONSE'}
    finally:conn.close()


def main(argv=None)->int:
    """Explicit opt-in command line interface for a single local trial."""
    import argparse
    import sys
    parser=argparse.ArgumentParser(description='Run one bounded Ollama trial on an explicit numeric loopback endpoint.')
    parser.add_argument('--endpoint',required=True,help='e.g. http://127.0.0.1:11434')
    parser.add_argument('--model',required=True)
    parser.add_argument('--prompt-file',required=True,help='Local UTF-8 file; nothing is executed')
    parser.add_argument('--trial-id',default='TRIAL-1')
    parser.add_argument('--temperature',type=float)
    parser.add_argument('--seed',type=int)
    parser.add_argument('--timeout',type=float,default=10)
    args=parser.parse_args(argv)
    if not is_localhost_url(args.endpoint):
        print(json.dumps({'ok':False,'errorClass':'NON_LOOPBACK_ENDPOINT_BLOCKED'}));return 2
    try:
        data=open(args.prompt_file,'rb').read(MAX_REQUEST_BYTES+1)
        if len(data)>MAX_REQUEST_BYTES: raise ValueError('PROMPT_TOO_LARGE')
        prompt=data.decode('utf-8')
    except (OSError,UnicodeError,ValueError) as exc:
        print(json.dumps({'ok':False,'errorClass':'PROMPT_FILE_ERROR','detail':str(exc)}));return 2
    result=run_local_ollama_trial(args.endpoint,args.model,prompt,temperature=args.temperature,seed=args.seed,timeout_seconds=args.timeout,trial_id=args.trial_id)
    # Explicitly print raw model output as data to stdout, never evaluate it.
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result['ok'] else 2

if __name__=='__main__':raise SystemExit(main())
