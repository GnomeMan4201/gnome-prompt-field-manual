#!/usr/bin/env python3
"""Conservative candidate declaration discovery for the GNOME Prompt Field Manual.
Never conflates declaration candidates with verified entry bodies."""
import argparse, hashlib, json, re, sys
from pathlib import Path
from html.parser import HTMLParser
HEADING=re.compile(r"^[ \t]{0,8}([A-Z]{1,5}-\d{2})[ \t]+([A-Za-z][^\r\n]{2,160})[ \t]*$")
CRITERIA=re.compile(r"^Criteria\s*:",re.I)
class Cards(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.cards=[];self.stack=[];self.active=None;self.pre_depth=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);cls=set(a.get('class','').split());self.stack.append(tag)
  if tag=='article' and 'manual-page-card' in cls:
   if self.active is not None:raise ValueError('Nested card')
   self.active={'page':len(self.cards)+1,'htmlId':a.get('id'),'text':''}
  if self.active is not None and tag=='pre':
   if self.pre_depth is not None:raise ValueError('Nested pre')
   self.pre_depth=len(self.stack)
 def handle_endtag(self,tag):
  if tag not in self.stack:raise ValueError('Unexpected HTML closing tag: '+tag)
  while self.stack:
   closing=self.stack.pop()
   if closing=='pre' and self.pre_depth is not None and len(self.stack)<self.pre_depth:self.pre_depth=None
   if closing=='article' and self.active is not None:
    if self.pre_depth is not None:raise ValueError('Unclosed pre')
    self.cards.append(self.active);self.active=None
   if closing==tag:break
 def handle_data(self,data):
  if self.active is not None and self.pre_depth is not None:self.active['text']+=data
def parse_cards(raw):
 p=Cards();p.feed(raw);p.close()
 if p.active is not None:raise ValueError('Unclosed card')
 return p.cards
def find_declarations(cards,allowed,max_page=306):
 candidates=[];rejected=[]
 for card in cards:
  if card['page']>max_page:continue
  lines=card['text'].splitlines(keepends=True);off=0
  for i,line in enumerate(lines):
   m=HEADING.fullmatch(line.rstrip('\r\n'))
   if m:
    eid,title=m.group(1),m.group(2).strip()
    if eid in allowed:
     nxt=next((x.strip() for x in lines[i+1:] if x.strip()),'')
     if CRITERIA.match(nxt):
      candidates.append({'id':eid,'titleCandidate':title,'page':card['page'],'pageCard':card['htmlId'],'startOffsetCodepoints':off,'headingRaw':line.rstrip('\r\n'),'evidence':'ID+title followed by adjacent Criteria line','status':'DECLARATION_CANDIDATE','bodyStatus':'NOT_VERIFIED'})
     else:rejected.append({'id':eid,'page':card['page'],'offsetCodepoints':off,'reason':'no adjacent Criteria line'})
   off+=len(line)
 return candidates,rejected
def discover(source,identity_path,expected_pages=315,expected_entries=91):
 src=source.read_bytes();sha=hashlib.sha256(src).hexdigest()
 identity=json.loads(identity_path.read_text())
 if identity.get('sourceIndexSha256')!=sha:raise ValueError('SOURCE_SHA_MISMATCH')
 identities=identity.get('entries',[]);allowed={x['id'] for x in identities}
 if len(allowed)!=len(identities) or len(allowed)!=expected_entries:raise ValueError('IDENTITY_UNIVERSE_INVALID')
 cards=parse_cards(src.decode('utf-8'));candidates,rejected=find_declarations(cards,allowed)
 from collections import Counter
 seen=Counter(x['id'] for x in candidates);duplicates=sorted(k for k,v in seen.items() if v>1);missing=sorted(allowed-set(seen))
 complete=len(cards)==expected_pages and len(candidates)==expected_entries and not duplicates and not missing
 return {'schemaVersion':'gnome.manual.declaration-discovery.v1','sourceHtmlSha256':sha,'identityIndexSha256':hashlib.sha256(identity_path.read_bytes()).hexdigest(),'scope':'Declaration candidates only. No verified canonical bodies.','status':'DECLARATIONS_COMPLETE_CANDIDATE_ONLY' if complete else 'INCOMPLETE_FAIL_CLOSED','counts':{'pages':len(cards),'identities':len(allowed),'declarationCandidates':len(candidates),'uniqueCandidates':len(seen),'missingIds':len(missing),'duplicateIds':len(duplicates),'verifiedEntryBodies':0},'missingIds':missing,'duplicateIds':duplicates,'candidates':candidates,'rejectedHeadingLikeLines':rejected,'limitations':['Candidate headings need editorial review','End offsets and entry body ownership not verified','Section introductions and PDF headers are not attributed','Part IX and editorial appendix excluded']}
def main():
 a=argparse.ArgumentParser();a.add_argument('--input',type=Path,default=Path('index.html'));a.add_argument('--identity-index',type=Path,default=Path('workbench/data/entry_identity_index.json'));a.add_argument('--output',type=Path,default=Path('workbench/data/entry_declaration_candidates.json'));a.add_argument('--allow-incomplete',action='store_true');args=a.parse_args()
 r=discover(args.input,args.identity_index);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(r['status'],r['counts']);return 0 if r['status']=='DECLARATIONS_COMPLETE_CANDIDATE_ONLY' or args.allow_incomplete else 1
if __name__=='__main__':sys.exit(main())
