# Batch 4 disposition — 2026-11-23

Batch 4 adjudicated the existing canonical S-01, S-02, and S-03 bodies against the frozen pending briefs. No replacement prompt bodies were drafted and no canonical body page changed.

## Frozen classifications

- **S-01 System Map with Trust Boundaries — PASS.** The canonical body already requires a `WHO CAN INJECT` field naming a specific actor type at trust-boundary crossings and retains explicit observability status.
- **S-02 Code Archaeology — PASS.** The canonical body already names `HIDDEN STATE DEPENDENCIES` and separates actual behavior, safe modification zones, and uncertainty.
- **S-03 Failure Mode Inventory — PASS.** The canonical body already makes `DETECTABILITY` an explicit required failure-mode property.

## Production-state transition

- Before: 14 pending / 77 drafted / 91 semantic entries / 315 pages / 7 remaining batches.
- After: 11 pending / 80 drafted / 91 semantic entries / 315 pages / 6 remaining batches.
- Next default briefs: `b-s10` and `b-sec02`.

## Integrity boundary

The migration removes only the three pending inventory rows, their three drafting briefs, the Batch 4 remaining-batch row, and current production-state/startup metadata. Pages 107–121 are byte-for-byte identical before and after the disposition mutation.

Final `index.html` SHA-256: `8c7a56dc0687809e691ee09030f2a028c290c3ab81a64e63f4b58b6d809df3bd`

## Independent source checks (read-only)

Reviewed against canonical text in `main` at `6dcd3d1196034257b377a21819350784acf10432` and frozen pre-disposition briefs for S-01/S-02/S-03.

- **S-01** (pages 107–111): the prompt uses `WHO CAN INJECT` and requires naming specific actor types; it also requires `OBSERVABILITY STATUS`.
- **S-02** (pages 112–116): the prompt explicitly contains `HIDDEN STATE DEPENDENCIES`, dangerous and safe modification zones, and stated-vs-actual behavior.
- **S-03** (pages 117–121): `DETECTABILITY` is mandatory for each failure mode and includes HIGH/MEDIUM/LOW/UNKNOWN definitions.
- These checks establish the **specific Batch 4 brief requirements** only, not overall body verification, external reproducibility, or editorial completion of unrelated entries.
- Every one of the 315 `article.manual-page-card` elements is byte-identical to the input commit, including the v9 historical PDF and corrected searchable text.
- SHA-256 of the NUL-separated raw HTML page cards 107–121 (ascending physical page): `145b5fe00fedfa43d2a098f3bca1e59e6a9d7ffef8e4a378bc0852626a2d9a1a`.
- SHA-256 of the NUL-separated raw HTML for all 315 page cards: `a05c4eaa08489f8125dcd242e2b4d0059de6627920eb7a3f04b6f48150b94e0d`.
- Full source after disposition: `8c7a56dc0687809e691ee09030f2a028c290c3ab81a64e63f4b58b6d809df3bd`.

## Historical research evidence boundary

Phase VII / VIII workbench evidence remains bound to the earlier 14/77 source digest `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19` and has not been rewritten or claimed to originate from this editorial post-state. The new `workbench/data/current_entry_identity_index.json` is derived afresh from the updated canonical `index.html`; this does not promote any of the 91 canonical bodies to independently verified status. The 629-decision adjudication queue remains a historic SHA-pinned review dataset. It requires its originally pinned source to complete hash-verified reviews, not the current `index.html`.

Historical source snapshot: `tests/fixtures/batch3-canonical-1f06445e.html` (byte-identical to the original `index.html` digest `1f06445e…`). Existing raw Phase V–VIII artifacts and their recorded source identities are intentionally unchanged.
