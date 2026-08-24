# Batch 2 Disposition Record — 2026-08-24

Bounded editorial disposition of the existing canonical bodies for `W-01 Dense-to-Clear (Rule-Based)`, `W-02 Argument Skeleton Extractor`, and `W-03 Adversarial Reader (Persona-Specific)`.

## Artifact binding

- Base commit: `8591c9f7ed4dbdeb5ed83de96e33c4dfbfedc324`
- Pre-mutation `index.html` SHA-256: `92d4e6c395c620bb9eb08a6df798ff1d1685b7c091a5ffd910e8fd996d9c9559`
- Post-mutation `index.html` SHA-256: `0203cde07cc1b3d42323d04334d5699e9177bb11a2a7bdd96fc46ceb9cf86e76`
- Pre-state: 19 pending / 72 drafted / 91 semantic entries / 315 pages / 9 remaining batches
- Post-state: 16 pending / 75 drafted / 91 semantic entries / 315 pages / 8 remaining batches
- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`

## Frozen audit matrix

| Entry | Frozen classification | Demonstrated gap | Disposition |
|---|---|---|---|
| W-01 | PARTIAL | `INPUTS NEEDED` omitted the frozen W-11 prerequisite for source material that may not be safely summarizable. | Added only that prerequisite in visible text and mirrored search metadata. Existing numbered rules, per-change rule log, W-04 follow-up, and other prose remain authoritative. |
| W-02 | PASS | None demonstrated. | No manuscript content rewrite. Promoted from pending based on existing body satisfying the frozen brief. |
| W-03 | PARTIAL | `SPECIFIC OBJECTIONS` did not explicitly require the frozen minimum of three. | Added only the minimum-three requirement in visible text and mirrored search metadata. Existing persona constraints, avoidance analysis, confidence-laundering checks, verdict, and routing remain authoritative. |

## Production-state actions

- Removed W-01/W-02/W-03 from the active pending inventory and per-entry drafting briefs.
- Removed Batch 2 from the remaining production-batch table without renumbering historical batches 3-10.
- Updated current state to 16 pending / 75 drafted / 91 total / 315 pages / 8 remaining batches.
- Retargeted default-open drafting briefs from removed W-01/W-02 to the first two remaining briefs, R-01/R-03, preventing startup abort on missing elements.
- Preserved the historical PDF and dated historical baseline records unchanged.

## Verification contract

The Batch 2 change is acceptable only if the repository's complete Python suite, strict structural validator, 16/75/91 lineage reconciliation, frozen editorial-classifier comparison, editorial-lineage audit, `git diff --check`, and Chromium/Firefox/WebKit reader smoke all pass on the exact cleaned PR head, followed by human review of the final `index.html` patch.
