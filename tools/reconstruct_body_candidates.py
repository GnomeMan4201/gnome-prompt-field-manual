#!/usr/bin/env python3
"""Conservative raw span reconstruction from previously validated declarations.

Extracted spans are diagnostic candidates, not verified editorial bodies.
Does not silently promote PARTIAL -> VERIFIED.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
from discover_entry_boundaries import parse_cards

PART=re.compile(r"^\s*Part\s+[IVX]+\s*[—–:-]\s*.+",re.I)
APPENDIX=re.compile(r"^\s*Appendix\s+[A-Z]\b",re.I)
def sha(b):return hashlib.sha256(b).hexdigest()
def flatten(cards):
 return {p['page']:p['text'] for p in cards}
def reconstruct(pages,start,end):
 sp,so=start;ep,eo=end
 if start>end:raise ValueError('Negative span')
 if sp==ep:return pages[sp][so:eo]
 return pages[sp][so:]+''.join(pages[p] for p in range(sp+1,ep))+pages[ep][:eo]
def structural_stops(cards):
 found=[]
 for c in cards:
  off=0
  for ln in c['text'].splitlines(keepends=True):
   if PART.match(ln) or APPENDIX.match(ln):
    found.append((c['page'],off,ln.strip()[:100]))
   off+=len(ln)
 return found
def produce(source, identity_path, declaration_path):
 data=source.read_bytes();digest=sha(data)
 identity=json.loads(identity_path.read_text(encoding='utf-8'))
 decl=json.loads(declaration_path.read_text(encoding='utf-8'))
 if identity['sourceIndexSha256']!=digest or decl['sourceHtmlSha256']!=digest:
  raise ValueError('Source hash mismatch')
 if decl['status']!='DECLARATIONS_COMPLETE_CANDIDATE_ONLY':
  raise ValueError('Declaration index incomplete')
 ids={i['id'] for i in identity['entries']}
 cand=decl['candidates']
 if len(ids)!=91 or len(cand)!=91 or {d['id'] for d in cand}!=ids:
  raise ValueError('Identity and declaration universes differ')
 cards=parse_cards(data.decode('utf-8'))
 if len(cards)!=315:raise ValueError('Expected 315 page cards')
 pages=flatten(cards);stops=structural_stops(cards)
 starts=[]
 for d in cand:
  pt=(d['page'],d['startOffsetCodepoints'])
  raw=pages[pt[0]]
  if not raw.startswith(d['headingRaw'],pt[1]):
   raise ValueError('Offset does not point to declared heading: '+d['id'])
  starts.append(pt)
 if starts!=sorted(starts) or len(set(starts))!=len(starts):
  raise ValueError('Declarations not strictly ordered')
 rows=[]
 for i,d in enumerate(cand):
  start=starts[i]
  next_boundary=starts[i+1] if i+1<len(starts) else (307,0)
  reasons=['NEXT_DECLARATION' if i+1<len(starts) else 'PART_IX_BEGINNING']
  between=[(p,o,desc) for p,o,desc in stops if start<(p,o)<next_boundary]
  if between:
   p,o,desc=min(between)
   end=(p,o);reasons=['SECTION_TRANSITION: '+desc]
  else:end=next_boundary
  raw=reconstruct(pages,start,end)
  if not raw.startswith(d['headingRaw']) or not raw.strip():
   raise ValueError('Invalid reconstructed candidate '+d['id'])
  if i+1<len(cand) and end==next_boundary and cand[i+1]['headingRaw'] in raw[-len(cand[i+1]['headingRaw']):]:
   raise ValueError('Next declaration absorbed')
  rows.append({'entryId':d['id'],'titleCandidate':d['titleCandidate'],
   'editorialStatus':next((x['status'] for x in identity['entries'] if x['id']==d['id']),'UNKNOWN'),
   'bodyStatus':'PARTIAL','reviewRequired':True,
   'startPage':start[0],'startOffsetCodepoints':start[1],
   'endPage':end[0],'endOffsetCodepoints':end[1],
   'rawSpan':raw,'rawSpanSha256':sha(raw.encode('utf-8')),
   'spanRoundTrip':reconstruct(pages,start,end)==raw,
   'boundaryReason':reasons,'warnings':['Includes potentially unrelated running headers/page footers; editorial ownership unverified','End-boundary classification not independently adjudicated']})
 if any((r['endPage'],r['endOffsetCodepoints'])>(rows[i+1]['startPage'],rows[i+1]['startOffsetCodepoints']) for i,r in enumerate(rows[:-1])):
  raise ValueError('Overlapping candidates')
 return {'schemaVersion':'gnome.manual.raw-body-candidates.v1','sourceHtmlSha256':digest,
  'scope':'Diagnostic contiguous raw source spans, not authoritative full entry bodies',
  'status':'PARTIAL_REVIEW_REQUIRED','counts':{'total':len(rows),'VERIFIED':0,'PARTIAL':len(rows),'UNRESOLVED':0,'CONFLICT':0},
  'entryCandidates':rows,
  'limitations':['Span round-trip checks copying, not editorial ownership','Part and appendix transitions are structural heuristics requiring human adjudication','No source-region ownership or clean normalized text is verified']}
def main():
 a=argparse.ArgumentParser()
 a.add_argument('--input',type=Path,default=Path('index.html'))
 a.add_argument('--identity-index',type=Path,default=Path('workbench/data/entry_identity_index.json'))
 a.add_argument('--declarations',type=Path,default=Path('workbench/data/entry_declaration_candidates.json'))
 a.add_argument('--output',type=Path,default=Path('workbench/data/raw_body_candidates.json'))
 a.add_argument('--require-verified',action='store_true')
 z=a.parse_args()
 d=produce(z.input,z.identity_index,z.declarations)
 z.output.parent.mkdir(parents=True,exist_ok=True);z.output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(d['status'],d['counts'])
 if z.require_verified and d['counts']['VERIFIED']!=d['counts']['total']:
  print('Fail closed: complete verified editorial ownership not established',file=sys.stderr);return 2
 return 0
if __name__=='__main__':sys.exit(main())
