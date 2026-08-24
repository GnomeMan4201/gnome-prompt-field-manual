# Batch 1 Disposition Record — 2026-08-24

## Scope

Bounded editorial disposition of the existing canonical bodies for `T-01 Idea Stress-Test` and `T-02 Claim Dissection` under issue #10. No replacement entry was drafted, no historical PDF was modified, and dated provenance baselines remain unchanged.

## Artifact binding

- Base commit: `0ee5a50bc1fddf86e45c9b51818b78e7c40fccfc`
- Pre-mutation `index.html` SHA-256: `4ac0157df83a7deed06583da6d9f000d4ec2220490fa07e03de4bd6759d65243`
- Post-mutation `index.html` SHA-256: `35da23093a45b13e1e9aca6748314c5a8faba2be0a7df349e470c5ae0afb8949`
- Pre-state: 21 pending / 70 drafted / 91 semantic entries / 315 pages / 10 batches
- Post-state: 19 pending / 72 drafted / 91 semantic entries / 315 pages / 9 remaining batches

## Frozen disposition matrix

| Entry | Frozen classification | Demonstrated gap | Disposition |
|---|---|---|---|
| T-01 | PARTIAL | Lens 6 was dependent weakest-link synthesis | Replaced only Lens 6 with an independent Constraint Lens; weakest-link synthesis remains after the six-lens pass |
| T-01 | PARTIAL | FOLLOW-UP omitted T-02 | Added a conditional T-02 Claim Dissection handoff for isolated claims |
| T-01 | PARTIAL | Weakest-link choice did not explicitly select highest severity | Post-pass WEAKEST LINK now selects the highest-severity finding from the six lenses |
| T-01 | PARTIAL | STRESS VERDICT lacked required one-sentence justification | Added explicit VERDICT JUSTIFICATION field and expected-output requirement |
| T-02 | PARTIAL | Verdict token used `COLLAPSES` | Canonical T-02 body now uses frozen singular token `COLLAPSE` consistently |
| T-02 | PARTIAL | CHERRY-PICK RISK lacked explicit one-sentence rationale | Added mandatory RATIONALE field and propagated it into expected output |
| T-02 | PARTIAL | EXPECTED OUTPUT called an eight-item artifact “seven-section” | Corrected to “eight-item claim dissection” |

## Production-state disposition

- T-01 and T-02 were removed from the active pending inventory and per-entry drafting briefs.
- The original Batch 1 drafting prompt remains byte-for-byte intact inside its prompt block and is explicitly labelled completed historical provenance.
- Batch 1 was removed from the active drafting-order table; original batch numbering 2–10 is preserved for lineage rather than renumbered.
- Current-state README, identity/scope, changelog, lineage CI expectations, and reconciliation tests were updated to 19/72/91.

## Fail-closed regression gate

`tests/test_batch1_disposition.py` proves that:

- T-01/T-02 are absent from active pending inventory and drafting briefs;
- each entry retains exactly one canonical full body;
- both bodies retain all nine manuscript fields;
- the frozen mandatory T-01/T-02 clauses are present in visible text and mirrored `data-manual-text`;
- stale `COLLAPSES` and dependent “Lens 6 — Weakest Link Lens” semantics cannot silently return;
- the Batch 1 prompt is historical provenance rather than an active instruction.

## Verification policy

The one-shot migration workflow commits this record only if the complete Python unit suite, strict structural validator, 19/72/91 lineage reconciliation, frozen editorial-lineage classifier check, and editorial-lineage audit all pass. Pull-request CI then supplies the repository browser matrix before merge.
