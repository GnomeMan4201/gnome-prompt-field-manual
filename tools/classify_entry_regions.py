#!/usr/bin/env python3
"""Phase V: lossless per-line region classification within PARTIAL raw entry spans.

Classification is a source-structure aid, never editorial verification.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
from discover_entry_boundaries import parse_cards
from reconstruct_body_candidates import produce,sha,reconstruct

RUNNING_HEADER="GNOME Prompt Field Manual"
PAGE_NUMBER=re.compile(r"^[ \t]*[0-9]{1,3}[ \t]*$")
SECTION_TITLE=re.compile(r"^[ \t]*(?:Part[ \t]+[IVX]+[ \t]*[—–:-]|Appendix[ \t]+[A-Z]\b)",re.I)
CRITERIA=re.compile(r"^[ \t]*Criteria[ \t]*:",re.I)
ENTRY_LABELS={"WHAT IT DOES","WHEN TO USE","THE PROMPT","INPUTS NEEDED","EXPECTED OUTPUT",
"KNOBS","FAILURE MODE","FOLLOW-UP","SAFETY NOTES","WHAT IT DETECTS","WHEN TO RUN",
"THE ANTI-PROMPT","PURPOSE","CHAIN","LINK LOGIC","BREAK CONDITION","SAFETY",
"OUTPUT CONTRACT","VERIFICATION","CHECKLIST","OUTPUT","WHEN","WHY IT MATTERS"}
def source_lines(raw):
 pos=0
 for line in raw.splitlines(keepends=True):
  yield pos,pos+len(line),line
  pos+=len(line)
def source_fragments(pages,start,end):
 sp,so=start;ep,eo=end
 if not start<end:raise ValueError("Empty/negative entry span")
 for p in range(sp,ep+1):
  a=so if p==sp else 0;b=eo if p==ep else len(pages[p])
  if a>b:raise ValueError("Out of order offset")
  for x,y,line in source_lines(pages[p]):
   lo=max(a,x);hi=min(b,y)
   if lo<hi:yield p,lo,hi,pages[p][lo:hi],x,y
def classify(page,offset,full_line_start,full_line_end,raw,full_page,heading):
 text=raw.strip()
 if not text:return "WHITESPACE","blank",False
 # A running header must be a *whole original source line* in the top of its page.
 if (text==RUNNING_HEADER and offset==full_line_start
     and offset+len(raw)==full_line_end
     and not full_page[:offset].strip()):
  return "PAGE_HEADER","exact top-of-page running header",True
 # Only whole bottom-of-page numeric lines matching physical page number.
 if (PAGE_NUMBER.fullmatch(raw.rstrip("\r\n")) and text==str(page)
     and offset==full_line_start and offset+len(raw)==full_line_end
     and not full_page[full_line_end:].strip()):
  return "PAGE_FOOTER","exact trailing physical page number",True
 if raw.strip()==heading.strip():
  return "ENTRY_DECLARATION_CANDIDATE","matched source declaration",False
 if CRITERIA.match(raw):
  return "ENTRY_CRITERIA_CANDIDATE","adjacent criteria evidence",False
 if SECTION_TITLE.match(raw):
  return "SECTION_TRANSITION_REVIEW","possible part/appendix transition",False
 if text.upper() in ENTRY_LABELS:
  return "ENTRY_SECTION_LABEL_CANDIDATE","known section label",False
 return "ENTRY_TEXT_CANDIDATE","text within bounded candidate span, ownership unverified",False
def report(source,ids,declarations):
 result=produce(source,ids,declarations)
 cards=parse_cards(source.read_text(encoding="utf-8"))
 pages={c["page"]:c["text"] for c in cards}
 dd=json.loads(declarations.read_text())
 heading_by_id={e["id"]:e["headingRaw"] for e in dd["candidates"]}
 output=[]
 counts={}
 for entry in result["entryCandidates"]:
  start=(entry["startPage"],entry["startOffsetCodepoints"])
  end=(entry["endPage"],entry["endOffsetCodepoints"])
  fragments=list(source_fragments(pages,start,end))
  if "".join(s for _,_,_,s,_,_ in fragments)!=entry["rawSpan"]:
   raise ValueError("Region concatenation mismatch: "+entry["entryId"])
  regions=[]
  for page,lo,hi,segment,original_lo,original_hi in fragments:
   classification,reason,auto_excludable=classify(page,lo,original_lo,original_hi,segment,pages[page],heading_by_id[entry["entryId"]])
   regions.append({"page":page,"startOffsetCodepoints":lo,"endOffsetCodepoints":hi,
    "regionType":classification,"reason":reason,"eligibleForProposedExclusion":auto_excludable,
    "textSha256":sha(segment.encode("utf-8"))})
   counts[classification]=counts.get(classification,0)+1
  if not regions or not any(r["regionType"]=="ENTRY_DECLARATION_CANDIDATE" for r in regions):
   raise ValueError("Entry declaration not found in own region set: "+entry["entryId"])
  proposed="".join(pages[r["page"]][r["startOffsetCodepoints"]:r["endOffsetCodepoints"]]
     for r in regions if not r["eligibleForProposedExclusion"])
  output.append({"entryId":entry["entryId"],"status":"PARTIAL","sourceStart":{"page":start[0],"offset":start[1]},
   "sourceEnd":{"page":end[0],"offset":end[1]},"rawSpanSha256":entry["rawSpanSha256"],
   "regionRoundTrip":True,"proposedCleanTextSha256":sha(proposed.encode("utf-8")),
   "proposedCleanTextLength":len(proposed),"reviewRequired":True,
   "regions":regions})
 return {"schemaVersion":"gnome.manual.region-classification.v1","sourceHtmlSha256":result["sourceHtmlSha256"],
 "status":"CLASSIFIED_CANDIDATES_REVIEW_REQUIRED","counts":{"entries":len(output),"VERIFIED":0,"PARTIAL":len(output),
 "regionClasses":counts,"autoExclusionsProposed":sum(r["eligibleForProposedExclusion"] for e in output for r in e["regions"])},
 "scope":"Lossless line-level candidates; source region roles and exclusions are heuristic proposals, not adjudicated editorial ownership",
 "entries":output}
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--input",type=Path,default=Path("index.html"))
 p.add_argument("--identity-index",type=Path,default=Path("workbench/data/entry_identity_index.json"))
 p.add_argument("--declarations",type=Path,default=Path("workbench/data/entry_declaration_candidates.json"))
 p.add_argument("--output",type=Path,default=Path("workbench/data/region_classification_review.json"))
 p.add_argument("--require-verified",action="store_true")
 a=p.parse_args();r=report(a.input,a.identity_index,a.declarations)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(r["status"],r["counts"])
 if a.require_verified:return 2
 return 0
if __name__=="__main__":sys.exit(main())
