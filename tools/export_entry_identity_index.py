#!/usr/bin/env python3
"""Evidence-safe GNOME manual inventory export.

This is an INDEX of reconciled entry identities, not a transcription of
entry bodies. The legacy 315-page PDF-derived HTML does not encode reliable
entry-body boundaries. Never promote ID occurrences to authoritative text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from reconcile_entry_lineage import reconcile

EXPECTED = {"pending": 14, "drafted": 77, "total": 91, "pages": 315}
SCHEMA = "gnome.manual.identity-index.v1"

def build_inventory(source: Path, *, expected: dict | None = None) -> dict:
    expected = expected or EXPECTED
    result = reconcile(source)
    entries = result.entries
    cards = result.summary.source_counts.embedded_pages
    pending = [e for e in entries if e.pending_inventory]
    drafted = [e for e in entries if not e.pending_inventory]
    observed = {"pending": len(pending), "drafted": len(drafted),
                "total": len(entries), "pages": cards}
    if observed != expected:
        raise ValueError(f"FAIL-CLOSED: expected {expected}, observed {observed}")
    # The reconciler labels its normal partition lists under conflicts too;
    # compare the authoritative invariant counts instead of rejecting them.
    ids = [e.entry_id for e in entries]
    if len(set(ids)) != len(ids):
        raise ValueError("FAIL-CLOSED: duplicate semantic IDs")
    if "W-04" not in ids:
        raise ValueError("FAIL-CLOSED: active W-04 is missing")
    if "R-07" not in ids or "R-10" not in ids:
        raise ValueError("FAIL-CLOSED: corrected R-07/R-10 identities missing")
    out = []
    for e in entries:
        # A page containing an ID is evidence of an OCCURRENCE, not an entry declaration.
        occurrences = sorted(set(e.embedded_page_indices))
        out.append({
            "id": e.entry_id,
            "titleCandidate": e.name or None,
            "titleAuthority": "reconciler-candidate-not-verified-heading",
            "status": "PENDING" if e.pending_inventory else "NON_PENDING",
            "pendingInventory": e.pending_inventory,
            "draftingBrief": e.drafting_brief,
            "occurrencePages": occurrences,
            "canonicalBody": None,
            "bodyStatus": "UNRESOLVED_BOUNDARIES",
            "crossRefs": [],
            "crossRefStatus": "NOT_VALIDATED",
            "lineage": {
                "canonicalVersion": "1.0.0-rc.1",
                "source": "index.html",
                "notes": "ID occurrences cannot establish body ownership",
            },
        })
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    return {
        "schemaVersion": SCHEMA,
        "sourceIndexSha256": source_sha,
        "counts": observed,
        "bodyCoverage": 0,
        "scope": "identity and occurrence index only; no canonical text exported",
        "sourceQuality": "reconciled inventory; candidate titles require independent checking",
        "lineageBoundary": {
            "correctedCurrentIds": ["R-07", "R-10"],
            "activeW04": "Over-Smoothing Detector",
            "retiredW04Predecessor": "Field Journal Scaffolder (cut, not a current entry)",
            "historicalV9Pdf": "historical non-canonical",
        },
        "entries": out,
    }

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("index.html"))
    ap.add_argument("--output", type=Path, default=Path("workbench/data/entry_identity_index.json"))
    args = ap.parse_args(argv)
    data = build_inventory(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Reconciled {len(data['entries'])} entry identities; canonical body coverage 0/{len(data['entries'])}")
    print("Explicitly unresolved: semantic entry boundaries and body-to-ID mapping.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
