#!/usr/bin/env python3
"""Generate a source-bound review packet, never a verified-body index.

Offsets are half-open Unicode codepoint ranges inside decoded <pre> text.
Keep historic manifests and live semantic identity status untouched.
"""
from __future__ import annotations
import argparse, collections, json, tempfile
from pathlib import Path
from discover_entry_boundaries import discover, parse_cards
from reconstruct_body_candidates import produce, reconstruct, sha
from classify_entry_regions import report, source_fragments
from adjudicate_entry_regions import build_queue, validate

SCHEMA = 'gnome.manual.current-body-review.v1'
SOURCE = 'index.html'
IDENTITY = 'workbench/data/current_entry_identity_index.json'
OUTPUT = 'workbench/data/current_body_review.json'
HISTORICAL = ('workbench/data/entry_identity_index.json', 'workbench/data/entry_declaration_candidates.json',
    'workbench/data/body_boundary_review.json', 'workbench/data/region_review_summary.json', 'workbench/data/adjudication_queue.json',
    'workbench/data/batch5_identity_crosswalk.json', 'workbench/data/batch9_identity_crosswalk.json')
STANDARD = ('WHAT IT DOES','WHEN TO USE','THE PROMPT','INPUTS NEEDED','EXPECTED OUTPUT','KNOBS','FAILURE MODE','FOLLOW-UP','SAFETY NOTES')
CHAIN = ('PURPOSE','WHEN','CHAIN','LINK LOGIC','OUTPUT','SAFETY')
ANTI = ('WHAT IT DETECTS','WHEN TO RUN','THE ANTI-PROMPT','SIGNAL OF FAILURE','WHAT TO DO ON HIT','NOTES')

def digest(path): return sha(path.read_bytes())
def location(pair): return {'page':pair[0],'offset':pair[1]}
def pair(loc): return loc['page'],loc['offset']
def dump(obj): return json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
def required(entry_id): return CHAIN if entry_id.startswith('CH-') else ANTI if entry_id.startswith('AP-') else STANDARD

def check_crosswalks(root, declarations):
    by_id={d['id']:d for d in declarations}
    a,b=(json.loads((root/p).read_text()) for p in HISTORICAL[-2:])
    subjects=[a['canonicalSubject'],a['canonicalCollision']]
    for row in b['entries']: subjects.extend([row['canonicalSubject'],row['canonicalCollision']])
    for row in b['crossReferenceResolutions']: subjects.extend([row['canonicalSubject'],row['canonicalCollision']])
    for item in subjects:
        d=by_id[item['entryId']]
        first=item.get('firstPage',item.get('pages',[None])[0])
        if (d['titleCandidate'],d['page'])!=(item['title'],first): raise ValueError('Crosswalk conflict: '+item['entryId'])
    return sorted({x['entryId'] for x in subjects})

def section_markers(pages,start,end,labels):
    result=[]
    for p,lo,hi,line,orig_lo,orig_hi in source_fragments(pages,start,end):
        # Never join pages before detecting headings: a footer without a newline
        # otherwise makes the next heading look like e.g. 14INPUTS NEEDED.
        if lo!=orig_lo or hi!=orig_hi: continue
        t=line.strip()
        for label in labels:
            if t==label or (label=='FOLLOW-UP' and t in ('FOLLOW-UP — BEFORE EVALUATION','FOLLOW-UP — AFTER EVALUATION')):
                result.append([label,p,lo,hi]);break
    return result

def gap(pages,start,end,kind):
    raw=reconstruct(pages,start,end)
    return {'start':location(start),'end':location(end),'kind':kind,'rawSha256':sha(raw.encode()),'codepoints':len(raw),'decision':'NEEDS_REVIEW'}

def build(root):
    root=Path(root); source=root/SOURCE; ids=root/IDENTITY
    raw=source.read_bytes(); source_sha=sha(raw)
    identity=json.loads(ids.read_text()); declarations=discover(source,ids)
    if declarations['status']!='DECLARATIONS_COMPLETE_CANDIDATE_ONLY': raise ValueError('Incomplete declaration inventory')
    if identity['bodyCoverage']!=0 or any(x['canonicalBody'] is not None for x in identity['entries']): raise ValueError('Unexpected body promotion in live identity')
    hist={p:digest(root/p) for p in HISTORICAL}
    crosswalk=check_crosswalks(root,declarations['candidates'])
    cards=parse_cards(raw.decode()); pages={c['page']:c['text'] for c in cards}
    if [c['htmlId'] for c in cards]!=[f'manual-page-{i:03d}' for i in range(1,316)]: raise ValueError('Physical page identities invalid')
    with tempfile.TemporaryDirectory() as td:
        d=Path(td)/'declarations.json';d.write_text(dump(declarations))
        spans=produce(source,ids,d); regions=report(source,ids,d)
    by_id={x['id']:x for x in identity['entries']}; rows=[]; summary=[]; gaps=[]; cursor=(1,0)
    for n,(decl,span,reg) in enumerate(zip(declarations['candidates'],spans['entryCandidates'],regions['entries'],strict=True)):
        eid=span['entryId']; start=(span['startPage'],span['startOffsetCodepoints']); end=(span['endPage'],span['endOffsetCodepoints'])
        if not cursor<=start<end or not all(0<=o<=len(pages[p]) for p,o in (start,end)): raise ValueError('Invalid boundary '+eid)
        if start>cursor: gaps.append(gap(pages,cursor,start,'FRONT_MATTER' if n==0 else 'PART_TRANSITION'))
        cursor=end
        if not (eid==decl['id']==reg['entryId'] and span['rawSpanSha256']==reg['rawSpanSha256']): raise ValueError('Region identity mismatch '+eid)
        actual=reconstruct(pages,start,end)
        if sha(actual.encode())!=span['rawSpanSha256'] or actual!=span['rawSpan']: raise ValueError('Raw reconstruction mismatch '+eid)
        for other in declarations['candidates']:
            if other['id']!=eid and start <= (other['page'],other['startOffsetCodepoints']) < end:
                raise ValueError('Neighbor heading absorbed '+eid)
        exclusions=[[r['page'],r['startOffsetCodepoints'],r['endOffsetCodepoints'],r['regionType']] for r in reg['regions'] if r['eligibleForProposedExclusion']]
        markers=section_markers(pages,start,end,required(eid))
        counts=collections.Counter(x[0] for x in markers)
        missing=[x for x in required(eid) if not counts[x]]; repeated=[x for x in required(eid) if counts[x]>1]
        ident=by_id[eid]; mismatch=ident['titleCandidate']!=decl['titleCandidate']
        pieces=[]
        for p in range(start[0],end[0]+1):
            a=start[1] if p==start[0] else 0;b=end[1] if p==end[0] else len(pages[p])
            if a<b: pieces.append([p,a,b,sha(pages[p][a:b].encode())])
        row={'entryId':eid,'canonicalHeadingCandidate':decl['titleCandidate'],'headingRaw':decl['headingRaw'],
          'editorialStatus':ident['status'],'advisoryIdentityTitle':ident['titleCandidate'],'titleMismatch':mismatch,
          'bodyStatus':'PARTIAL','reviewRequired':True,'start':location(start),'endExclusive':location(end),
          'previousEntry':declarations['candidates'][n-1]['id'] if n else None,
          'nextEntry':declarations['candidates'][n+1]['id'] if n+1<len(declarations['candidates']) else None,
          'boundaryReason':span['boundaryReason'],'rawSpanSha256':span['rawSpanSha256'],
          'proposedCleanTextSha256':reg['proposedCleanTextSha256'],'proposedCleanTextLength':reg['proposedCleanTextLength'],
          'pageSlices':pieces,'sectionMarkers':markers,'expectedSectionLabels':list(required(eid)),
          'missingSectionLabels':missing,'repeatedSectionLabels':repeated,'proposedExclusions':exclusions,
          'ownershipDecision':'NEEDS_REVIEW','endBoundaryDecision':'NEEDS_REVIEW'}
        rows.append(row)
        summary.append({'entryId':eid,'status':'PARTIAL','sourceStart':row['start'],'sourceEnd':row['endExclusive'],
            'rawSpanSha256':row['rawSpanSha256'],'proposedExclusions':exclusions,'reviewRequired':True})
    last=(315,len(pages[315]));gaps.append(gap(pages,cursor,last,'PART_IX_AND_APPENDICES'))
    # Entire decoded source must partition exactly once into candidates and unassigned regions.
    segments=sorted([(pair(r['start']),pair(r['endExclusive'])) for r in rows]+[(pair(g['start']),pair(g['end'])) for g in gaps])
    if segments[0][0]!=(1,0) or segments[-1][1]!=last or any(a[1]!=b[0] for a,b in zip(segments,segments[1:])): raise ValueError('Source partition gap or overlap')
    if sum(len(reconstruct(pages,a,b)) for a,b in segments)!=sum(map(len,pages.values())): raise ValueError('Source partition length mismatch')
    manifest={'schemaVersion':'gnome.manual.region-review-summary.v1','sourceHtmlSha256':source_sha,'counts':{'VERIFIED':0,'PARTIAL':91},'entries':summary}
    queue=build_queue(manifest); outcome=validate(manifest,queue)
    if not outcome['valid'] or outcome['approvedBodies'] or outcome['reviewComplete']: raise ValueError('Unexpected review promotion')
    return {'schemaVersion':SCHEMA,'sourceHtmlSha256':source_sha,'identityIndexSha256':digest(ids),
      'historicalBindings':hist,'status':'PARTIAL_REVIEW_REQUIRED','counts':{'pages':315,'entries':91,'VERIFIED':0,'PARTIAL':91,'UNRESOLVED':0,'CONFLICT':0,
      'titleMismatches':sum(r['titleMismatch'] for r in rows),'entriesWithMissingSectionMarkers':sum(bool(r['missingSectionLabels']) for r in rows),'entriesWithRepeatedSectionMarkers':sum(bool(r['repeatedSectionLabels']) for r in rows),
      'proposedExclusions':sum(len(r['proposedExclusions']) for r in rows),'pendingLegacyQueueDecisions':outcome['pendingDecisions'],'unassignedRegions':len(gaps)},
      'crosswalkSubjectsChecked':crosswalk,'offsetConvention':'Half-open Unicode codepoint offsets in decoded page <pre> text; end may point to next page offset zero.',
      'reviewQueueManifestSha256':queue['manifestSha256'],'entries':rows,'unassignedRegions':gaps},manifest,queue

def verify(root, packet):
    expected,_,_=build(root)
    if packet!=expected: raise ValueError('Review packet differs from reproducible current-source candidates; stale, mutated, or unauthorized promotion')
    return expected['counts']

def entry_packet(root, packet, entry_id):
    """Inspect exact source slices, not a cleaned or verified prompt export."""
    verify(root,packet)
    row=next((r for r in packet['entries'] if r['entryId']==entry_id),None)
    if row is None: raise ValueError('Unknown entry '+entry_id)
    pages={c['page']:c['text'] for c in parse_cards((root/SOURCE).read_text())}
    slices=[{'page':p,'start':a,'endExclusive':b,'sha256':h,'text':pages[p][a:b]} for p,a,b,h in row['pageSlices']]
    exclusions=[{'page':p,'start':a,'endExclusive':b,'kind':k,'text':pages[p][a:b],'decision':'NEEDS_REVIEW'} for p,a,b,k in row['proposedExclusions']]
    return {'sourceHtmlSha256':packet['sourceHtmlSha256'],'entry':row,'rawPageSlices':slices,'exclusionEvidence':exclusions,
        'reviewQuestions':['Does this heading name the intended canonical subject?', 'Does the end exclude the next entry and part introduction?',
          'Are all substantive sections present and correctly owned?', 'Are proposed exclusions only running headers and physical footers?',
          'Could a cross-reference, example, or ambiguous line instead belong to another entry?', 'Are any relevant regions outside this span?'],
        'independence':'No reviewer decision is supplied by this generator.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));p.add_argument('--output',type=Path);p.add_argument('--verify',action='store_true');p.add_argument('--entry');p.add_argument('--queue',type=Path);p.add_argument('--manifest',type=Path);a=p.parse_args()
    out=a.output or a.root/OUTPUT
    if a.verify or a.entry:
        if a.queue or a.manifest or (a.verify and a.entry): p.error('Select one read-only mode')
        packet=json.loads(out.read_text())
        if a.entry: print(dump(entry_packet(a.root,packet,a.entry)),end='')
        else: print(json.dumps(verify(a.root,packet),sort_keys=True))
        return
    destinations=[x for x in (out,a.manifest,a.queue) if x is not None]
    if len(set(x.resolve() for x in destinations))!=len(destinations) or any(x.exists() for x in destinations):
        raise ValueError('Refusing to overwrite or alias existing evidence')
    result,manifest,queue=build(a.root)
    for path,data in ((out,result),(a.manifest,manifest),(a.queue,queue)):
        if path is not None:
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('x',encoding='utf-8') as handle: handle.write(dump(data))
    print(json.dumps(result['counts'],sort_keys=True))
if __name__=='__main__': main()
