# Batch 5 source-bound disposition — 2026-11-23

**Verdict: SUBSUMED / RESOLVED AS AN EXISTING CANONICAL SUBJECT.**
This is a bounded editorial plan disposition, not an independently verified
canonical body attribution, not an additional entry, and not a release approval.

## Frozen brief and canonical evidence

- **Planned S-10 Migration Risk Classifier:** frozen prior pending brief in
  [archived planned brief](../tests/fixtures/batch5-frozen-planned-s10.html)
  (SHA-256 7861e414160693367726f8277d430274f259a7fe779ee5672a9b39003b2440a4), originally bound to
  source SHA-256 dca538299e7a0a6ee74d627baa231089c051a1627a29a0364c8ff136e1b4e448. The brief was not silently rewritten.
- **Canonical S-07 Migration Risk Classifier:** physical page 129 identifies
  the subject. The prompt on page 130 and continued dimensions on pages
  131–132 specify eight evidence-backed migration-specific risk dimensions.
  Page 130 now requires a **four-category summary**, separately rating
  DATA COMPATIBILITY, BEHAVIORAL, INTEGRATION and ROLLBACK COMPLEXITY with
  evidence and an explicit mapping back to those dimensions; the
  MEDIUM / MODERATE mapping is bounded to that summary.
- **Expected output and control:** page 133 mandates the four-category
  summary, a go/no-go migration verdict, required test/dry run, and
  ROLLBACK TRIGGER CONDITIONS (signal, threshold, window, evidence
  source, owner, halt/rollback action and escalation). Absent evidence
  yields UNASSESSED / DO NOT MIGRATE YET. The prompt does **not**
  claim to monitor production or execute a rollback.
- **Canonical S-10 Architecture Decision Record Generator:** page 140
  is an unrelated existing canonical body. It was **not** reidentified as
  Migration Risk Classifier. Planned S-10 was a redundant planned name,
  not authority to replace the canonical S-10 identifier.
- **Frozen cross-references:** planned S-07 Rollback Decision Gate and
  planned S-08 Incident Report Scaffold correspond by subject to
  canonical S-08 and S-09 respectively, as explicitly named on page 135.
  No global renumbering is inferred.

## Editorial disposition and arithmetic

The frozen brief's mandatory artifacts are covered by canonical S-07
after the reviewed page 130 and 133 corrections. **Close the planned S-10
pending brief as SUBSUMED** rather than invent a new manuscript body,
renumber S-07, or rename the canonical S-10 ADR.

The reconciled count transition is **11 pending / 80 non-pending IDs /
91 total / 315 page cards / 6 remaining batches** to
**10 pending / 81 non-pending IDs / 91 total / 315 page cards /
5 remaining batches**. This is a *classification* change to one existing
semantic identifier in the deterministic ID partition. It is **not**
proof that 81 independent manuscript bodies have been verified; the
separate identity index still records **0/91 verified canonical bodies**.

## Integrity / preservation

- Previous main SHA-256 index.html: dca538299e7a0a6ee74d627baa231089c051a1627a29a0364c8ff136e1b4e448.
- Resulting index.html SHA-256: d5c0f82c33ab228166225972d7de0945b819c7d9a424451916fb5c2efca97e7d.
- All **315 canonical page cards are byte-identical** before and after
  this disposition. The corrected page 130/133 text remains unchanged;
  standalone reader and historical v9 PDF remain unchanged.
- Frozen planned brief HTML archive SHA-256: 7861e414160693367726f8277d430274f259a7fe779ee5672a9b39003b2440a4.
- Existing historical Batch 1–4 and Phase VIII hash-bound records stay
  tied to their recorded sources. The prior Batch 5 correction and
  four-category candidate reviews remain historical records.
- Current identity index and Reactor source-adapter are regenerated
  against the resulting SHA. The plan-to-canonical subject crosswalk is
  a distinct machine-readable artifact; it does not change verified-body
  coverage.

## Independent evidence not established

This disposition was derived from documented text and automated source
regressions. It is **not an external model replication**, a factual
guarantee about every prompt invocation, or independent verification of
91 body boundaries. Source authority for the uncommitted editable v3
manuscript remains limited to the frozen PTSP evidence.

Next work begins with Batch 6 **SEC-02 / SEC-05**. Keep stable release
blocked pending the other 10 briefs, replication, accessibility and
publication gates described in issue #1.
