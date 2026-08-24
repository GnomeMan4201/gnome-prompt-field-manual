# Batch 3 Disposition Record — 2026-08-24

Bounded editorial disposition of the existing canonical bodies for `R-01 Source Map with Contested Zones` and `R-03 Replication Risk Auditor`.

## Artifact binding
- Base commit: `5893ce77993e7362b276e4b486733a6ec220286a`
- Pre-mutation `index.html` SHA-256: `e0d88f80a6f14e90732a7f0765794ffe348bf526aaa3225fe3b87c8acb073bac`
- Final corrected `index.html` SHA-256: `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`
- Pre-state: 16 pending / 75 drafted / 91 semantic entries / 315 pages / 8 remaining batches
- Post-state: 14 pending / 77 drafted / 91 semantic entries / 315 pages / 7 remaining batches
- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`

## Frozen audit matrix
| Entry | Classification | Demonstrated gap | Disposition |
|---|---|---|---|
| R-01 | PARTIAL | Cross-source INSTITUTIONAL INTEREST MAP absent. | Added aggregate map and named it in EXPECTED OUTPUT; preserved per-source disclosure. |
| R-03 | PARTIAL | VERY HIGH risk level and R-05 follow-up absent. | Restored VERY HIGH, retained NOT REPLICATION-READY as separate insufficiency status, and added R-05 follow-up. |

## Human diff correction
The final `index.html` review caught a metadata-only migration defect on page 073: the new R-01 institutional-interest map had been inserted inside the normalized `If no contested zones...` sentence even though the visible reader was correct. The malformed search metadata was repaired by moving the map ahead of `CONTESTED ZONES`, restoring the original conditional sentence, and adding a permanent regression that enforces map → contested zones → conditional → known gaps ordering. No additional manuscript prose was authorized or changed.

## Verification contract
Accept only after complete Python, strict validator, 14/77/91 lineage, frozen classifier, editorial-lineage audit, `git diff --check`, Chromium/Firefox/WebKit smoke, and human final diff review all pass on the exact cleaned head.
