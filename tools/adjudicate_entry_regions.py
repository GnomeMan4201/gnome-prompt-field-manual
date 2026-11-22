#!/usr/bin/env python3
"""Phase VI: fail-closed human adjudication record validator.

No automated decisions, no promotion of canonical body status.
Review decisions bind to the exact source span and source SHA-256.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA = "gnome.manual.adjudication.v1"
CHOICES = {"ACCEPT_EXCLUSION", "REJECT_EXCLUSION", "NEEDS_REVIEW"}
END_CHOICES = {"ACCEPT_BOUNDARY", "REJECT_BOUNDARY", "NEEDS_REVIEW"}
OWN_CHOICES = {"ACCEPT_OWNERSHIP", "REJECT_OWNERSHIP", "NEEDS_REVIEW"}
SHA256 = re.compile(r"^[a-f0-9]{64}$")

def canonical_bytes(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

def fingerprint(item):
    return hashlib.sha256(canonical_bytes(item)).hexdigest()

def build_queue(manifest):
    if manifest.get("schemaVersion") != "gnome.manual.region-review-summary.v1":
        raise ValueError("Wrong manifest schema")
    entries = manifest["entries"]
    if len(entries) != 91 or len({x["entryId"] for x in entries}) != 91:
        raise ValueError("91 unique entries required")
    if manifest["counts"]["VERIFIED"] != 0 or manifest["counts"]["PARTIAL"] != 91:
        raise ValueError("Unexpected baseline status")
    if not SHA256.fullmatch(manifest["sourceHtmlSha256"]):
        raise ValueError("Invalid source SHA-256")
    queue = {"schemaVersion": SCHEMA, "sourceHtmlSha256": manifest["sourceHtmlSha256"],
             "manifestSha256": fingerprint(manifest), "status": "PENDING_HUMAN_ADJUDICATION",
             "scope": "Human review queue, not verification or canonical text export",
             "entries": []}
    for e in entries:
        ident = e["entryId"]
        if not e.get("reviewRequired") or not SHA256.fullmatch(e["rawSpanSha256"]):
            raise ValueError("Unreviewable span: " + ident)
        proposals=[]
        for i, span in enumerate(e["proposedExclusions"]):
            if len(span) != 4 or span[3] not in ("PAGE_HEADER", "PAGE_FOOTER"):
                raise ValueError("Unexpected proposed exclusion: " + ident)
            proposal = {"entryId": ident, "span": span, "rawSpanSha256": e["rawSpanSha256"]}
            proposals.append({"proposalId": fingerprint(proposal), "span": span,
                "decision": "NEEDS_REVIEW", "reviewer": None, "rationale": None,
                "evidence": [], "reviewedAt": None})
        queue["entries"].append({"entryId": ident, "rawSpanSha256": e["rawSpanSha256"],
            "exclusions": proposals,
            "endBoundary": {"location": e["sourceEnd"], "decision": "NEEDS_REVIEW",
                "reviewer": None, "rationale": None, "evidence": [], "reviewedAt": None},
            "bodyOwnership": {"start": e["sourceStart"], "end": e["sourceEnd"],
                "decision": "NEEDS_REVIEW", "reviewer": None, "rationale": None,
                "evidence": [], "reviewedAt": None}})
    return queue

def check_record(record, expected, *, decisions, label, issues):
    if not isinstance(record, dict):
        issues.append(label + ": missing record");return False
    if record.get("decision") not in decisions:
        issues.append(label + ": invalid decision");return False
    if expected is not None:
        for key in expected:
            if record.get(key) != expected[key]:
                issues.append(label + ": immutable provenance field changed " + key)
                return False
    if record["decision"] == "NEEDS_REVIEW":
        if any(record.get(x) not in (None, [], "") for x in ("reviewer","rationale","reviewedAt")):
            issues.append(label + ": pending record contains apparent review metadata")
        return False
    fields=("reviewer","rationale","reviewedAt")
    if not all(isinstance(record.get(f),str) and record[f].strip() for f in fields):
        issues.append(label + ": completed decision missing reviewer/rationale/timestamp")
        return False
    if not isinstance(record.get("evidence"),list) or not record["evidence"] or any(
        not isinstance(x,str) or not x.strip() for x in record["evidence"]):
        issues.append(label + ": completed decision missing evidence reference")
        return False
    return True

def validate(manifest, reviewed):
    expected=build_queue(manifest)
    issues=[]
    if reviewed.get("schemaVersion")!=SCHEMA: issues.append("Wrong schema")
    for key in ("sourceHtmlSha256","manifestSha256"):
        if reviewed.get(key)!=expected[key]:issues.append("Source/manifest mismatch: "+key)
    exp_entries=expected["entries"]
    given=reviewed.get("entries")
    if not isinstance(given,list) or len(given)!=len(exp_entries):
        return {"valid":False,"reviewComplete":False,"approvedBodies":0,
                "pendingDecisions":None,"issues":issues+["Missing or unexpected entries"]}
    seen=set();pending=0;completed=0
    for exp,g in zip(exp_entries,given):
        ident=exp["entryId"];lab=ident
        if g.get("entryId")!=ident or g.get("rawSpanSha256")!=exp["rawSpanSha256"] or ident in seen:
            issues.append(lab+": entry identity/order/hash mismatch")
        seen.add(ident)
        exclusions=g.get("exclusions",[])
        if len(exclusions)!=len(exp["exclusions"]):
            issues.append(lab+": exclusions count mismatch");continue
        for ix,(want,actual) in enumerate(zip(exp["exclusions"],exclusions)):
            ok=check_record(actual,{"proposalId":want["proposalId"],"span":want["span"]},
                decisions=CHOICES,label=f"{lab}:exclusion:{ix}",issues=issues)
            if ok:completed+=1
            else:pending+=1
        for kind,choice in (("endBoundary",END_CHOICES),("bodyOwnership",OWN_CHOICES)):
            immutable={"location":exp[kind]["location"]} if kind=="endBoundary" else {
                "start":exp[kind]["start"],"end":exp[kind]["end"]}
            ok=check_record(g.get(kind),immutable,decisions=choice,label=lab+":"+kind,issues=issues)
            if ok:completed+=1
            else:pending+=1
    # This gate validates review records; it never certifies canonical body text.
    return {"valid":len(issues)==0,"reviewComplete":pending==0 and not issues,
        "approvedBodies":0,"completedDecisions":completed,"pendingDecisions":pending,
        "issues":issues}

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--manifest",type=Path,default=Path("workbench/data/region_review_summary.json"))
    ap.add_argument("--queue",type=Path,default=Path("workbench/data/adjudication_queue.json"))
    ap.add_argument("--review",type=Path)
    args=ap.parse_args(argv)
    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.review:
        result=validate(manifest,json.loads(args.review.read_text(encoding="utf-8")))
        print(json.dumps(result,indent=2))
        return 0 if result["reviewComplete"] else 2
    data=build_queue(manifest)
    args.queue.parent.mkdir(parents=True,exist_ok=True)
    args.queue.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"entries":len(data["entries"]),
                      "proposedExclusions":sum(len(e["exclusions"]) for e in data["entries"]),
                      "endBoundaryDecisions":len(data["entries"]),
                      "ownershipDecisions":len(data["entries"]),
                      "reviewStatus":"PENDING_HUMAN_ADJUDICATION"},indent=2))
    return 0
if __name__=="__main__":sys.exit(main())
