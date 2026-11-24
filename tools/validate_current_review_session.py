#!/usr/bin/env python3
"""Validate a current-source review session, not independent body ownership."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from build_current_body_review import build, dump, OUTPUT
from adjudicate_entry_regions import validate as validate_queue

SCHEMA = 'gnome.manual.current-review-session.v1'
PACKET_SHA = '603a81d5867e6b62b44d2fde199a7ab452ccf266eab7a77cd4084c8de9fb6401'
CHOICES = {'NEEDS_REVIEW', 'ACCEPT', 'REJECT'}
RECORD_FIELDS = {'key', 'decision', 'reviewer', 'rationale', 'evidence', 'reviewedAt'}
SESSION_FIELDS = {'schemaVersion', 'sourceHtmlSha256', 'packetSha256', 'reviewQueueManifestSha256', 'records'}

def keys(packet):
    result=[]
    for entry in packet['entries']:
        eid=entry['entryId']
        result.extend(f'{eid}:exclusion:{i}' for i,_ in enumerate(entry['proposedExclusions']))
        result.extend((f'{eid}:end', f'{eid}:owner'))
        if entry['titleMismatch']:
            result.append(f'{eid}:title')
    result.extend(f'region:{i}' for i,_ in enumerate(packet['unassignedRegions']))
    return result

def blank_session(packet):
    return {'schemaVersion':SCHEMA, 'sourceHtmlSha256':packet['sourceHtmlSha256'],
        'packetSha256':PACKET_SHA, 'reviewQueueManifestSha256':packet['reviewQueueManifestSha256'],
        'records':[{'key':k,'decision':'NEEDS_REVIEW','reviewer':None,'rationale':None,
                    'evidence':[],'reviewedAt':None} for k in keys(packet)]}

def nonempty(value):
    return isinstance(value,str) and bool(value.strip())

def timestamp(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',value):
        return False
    try:
        dt.datetime.strptime(value,'%Y-%m-%dT%H:%M:%S.%fZ')
        return True
    except ValueError:
        return False

def load_basis(root):
    root=Path(root)
    raw=(root/OUTPUT).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PACKET_SHA:
        raise ValueError('CURRENT_PACKET_HASH_MISMATCH')
    packet=json.loads(raw)
    expected,manifest,queue=build(root)
    if packet!=expected:
        raise ValueError('Current packet differs from reproducible source')
    return packet,manifest,queue

def validate_session(session,packet):
    expected=blank_session(packet)
    if not isinstance(session,dict) or set(session)!=SESSION_FIELDS:
        raise ValueError('Session schema fields differ')
    for key in SESSION_FIELDS-{'records'}:
        if session[key]!=expected[key]:
            raise ValueError('Source binding mismatch: '+key)
    records=session['records']
    if not isinstance(records,list) or len(records)!=len(expected['records']):
        raise ValueError('Record count mismatch')
    for row,want in zip(records,expected['records']):
        if not isinstance(row,dict) or set(row)!=RECORD_FIELDS or row['key']!=want['key']:
            raise ValueError('Record identity or fields differ')
        decision=row['decision']
        if not isinstance(decision,str) or decision not in CHOICES:
            raise ValueError('Invalid decision: '+row['key'])
        if decision=='NEEDS_REVIEW':
            if row!=want:
                raise ValueError('Pending record contains review metadata: '+row['key'])
        elif not (nonempty(row['reviewer']) and nonempty(row['rationale']) and isinstance(row['evidence'],list)
                  and row['evidence'] and all(map(nonempty,row['evidence'])) and timestamp(row['reviewedAt'])):
            raise ValueError('Missing or invalid reviewer evidence: '+row['key'])
    accepted=sum(r['decision']=='ACCEPT' for r in records)
    rejected=sum(r['decision']=='REJECT' for r in records)
    return {'records':len(records),'accepted':accepted,'rejected':rejected,
        'pending':len(records)-accepted-rejected,'completedReviewRecords':accepted+rejected,
        'independentlyVerifiedBodies':0,'scope':'Record structure and source binding only; reviewer identity is self-declared'}

def compatible_queue(session,packet,manifest,queue):
    import copy
    validate_session(session,packet)
    result=copy.deepcopy(queue)
    rows={r['key']:r for r in session['records']}
    def apply(target,key,accept,reject):
        source=rows[key]
        target.update({k:source[k] for k in ('reviewer','rationale','evidence','reviewedAt')})
        target['decision']={'NEEDS_REVIEW':'NEEDS_REVIEW','ACCEPT':accept,'REJECT':reject}[source['decision']]
    for entry in result['entries']:
        eid=entry['entryId']
        for i,ex in enumerate(entry['exclusions']):
            apply(ex,f'{eid}:exclusion:{i}','ACCEPT_EXCLUSION','REJECT_EXCLUSION')
        apply(entry['endBoundary'],eid+':end','ACCEPT_BOUNDARY','REJECT_BOUNDARY')
        apply(entry['bodyOwnership'],eid+':owner','ACCEPT_OWNERSHIP','REJECT_OWNERSHIP')
    checked=validate_queue(manifest,result)
    if not checked['valid'] or checked['approvedBodies']!=0:
        raise ValueError('Compatible queue failed existing validator')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('session',type=Path);p.add_argument('--root',type=Path,default=Path('.'))
    p.add_argument('--queue-out',type=Path,help='Optional new file containing only 629 compatible records; keep full session separately')
    a=p.parse_args()
    if a.session.stat().st_size>8*1024*1024:
        p.error('Session exceeds 8 MiB')
    try:
        packet,manifest,queue=load_basis(a.root)
        session=json.loads(a.session.read_text(encoding='utf-8'))
        result=validate_session(session,packet)
        if a.queue_out:
            converted=compatible_queue(session,packet,manifest,queue)
            with a.queue_out.open('x',encoding='utf-8') as out:
                out.write(dump(converted))
        print(json.dumps(result,sort_keys=True))
    except (ValueError,TypeError,KeyError,OSError) as exc:
        p.exit(2,f'Review session rejected: {exc}\n')
if __name__=='__main__':
    main()
