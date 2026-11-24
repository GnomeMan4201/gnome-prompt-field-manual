# Batch 5 adjudication hold — 2026-11-23

**Verdict: REVISE / DO NOT PROMOTE** `S-10` (PTSP planned `Migration Risk Classifier`). This is a source-grounded editorial blocker, not a failure of the repository's CI or a completed manuscript revision.

## Source-bound conflict

The current PTSP pending inventory and frozen brief `b-s10` name **S-10 Migration Risk Classifier**. The frozen brief requires these deliverables: evidence-backed risk ratings in four structural categories, go/no-go criteria, and **ROLLBACK TRIGGER CONDITIONS** stating observable conditions that immediately halt the migration.

The corrected searchable **canonical manual**, however, contains the **S-07 Migration Risk Classifier** heading on `manual-page-129` and its prompt/output on pages 130–133. It uses eight risk dimensions, states explicit pre-migration gate conditions, and refers readers to S-08 Rollback Decision Gate and S-09 Incident Report Scaffold. It **does not** make a distinct `ROLLBACK TRIGGER CONDITIONS` output mandatory in its prompt or expected output. Its safety notes on page 135 say the prompt assesses risk *before* migration and does not monitor execution. An in-progress **knob** on page 134 does not satisfy a mandatory standard output contract.

The manual also already has a **different** `S-10 Architecture Decision Record Generator` beginning on `manual-page-140`. It must not be deleted, renamed, reclassified as Migration Risk Classifier, or treated as the body satisfying the frozen S-10 brief.

The current identity index lists `S-10` with the **candidate** title `Migration Risk Classifier` and an ID **occurrence** on page 140. This occurrence reflects the *different* canonical `S-10` ADR heading, **not** proof that the pending S-10 brief has a matching canonical body. The index already states `canonicalBody: null`, `bodyStatus: UNRESOLVED_BOUNDARIES`, and `bodyCoverage: 0`; those caveats remain in force.

## Editorial decision required before any promotion

1. **Confirm the ID crosswalk** between PTSP planned/v3 `S-10 Migration Risk Classifier` and canonical reader `S-07 Migration Risk Classifier`; separately retain canonical `S-10 Architecture Decision Record Generator`. Do not globally renumber S-07 or S-10; their identifiers refer to different reader entries.
2. **Authorize a bounded manuscript change** to the canonical migration-risk prompt and expected output (pages 130–133) to require **observed, measurable rollback/halt trigger conditions** (signal, threshold, time/window, owner, immediate stop action and escalation), while preserving its declared pre-migration risk-classification scope. Do not claim the prompt itself actively monitors production. Decide whether to retain the canonical `MODERATE` rating label or align it with the brief's `MEDIUM`.
3. **Revise the PTSP brief / ID crosswalk** as an expressly reviewed editorial decision; update the canonical search metadata and visible text together if the manuscript is changed, without modifying the v9 historical PDF.
4. **Re-adjudicate against the frozen brief**, record evidence and acceptance criteria, and only then consider the prospective state transition to 10 pending / 81 drafted. Prevent automatic promotion based on the S-10 ID occurrence alone.

## Hold invariants

- Baseline: merged PR #34, `main` commit `55c603d976563a29817ecfffc8e5b00f0d207a89`.
- `index.html` SHA-256 remains `8c7a56dc0687809e691ee09030f2a028c290c3ab81a64e63f4b58b6d809df3bd`.
- Production counts remain **11 pending, 80 drafted, 91 reconciled IDs, 315 page cards, 6 remaining batches**.
- Canonical body verification remains **0/91**, not a numerical PASS inferred from mere ID presence.
- All 315 canonical page-card bytes, historical v9 PDF, old research evidence hashes and release version remain unchanged by this HOLD record.

**No canonical manuscript edit, disposition promotion, identity-index rewrite, merger or deployment is authorized by this document.**
