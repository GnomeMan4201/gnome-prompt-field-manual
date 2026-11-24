# Batch 5 — manuscript correction candidate (2026-11-23)

**Disposition: REVISE.** No pending identifier was promoted. The release remains 1.0.0-rc.1.

## Identity crosswalk

- Frozen planned brief b-s10 = **S-10 Migration Risk Classifier**.
- Existing canonical **S-07 Migration Risk Classifier** begins on physical page 129.
- Existing canonical **S-10 Architecture Decision Record Generator** begins on page 140, and is byte-preserved.
- Planned S-10 and canonical S-07 match by subject but **not** identifier. A future disposition must explicitly accept or reject the crosswalk. Do not silently promote planned S-10 based on a matching title.
- The brief's MEDIUM label maps to the canonical manuscript's MODERATE risk level, without rewriting the four-level scale.

## Exact candidate edit

The corrected canonical page 133 explicitly requires **ROLLBACK TRIGGER CONDITIONS** with:
- observable failure signal;
- numeric threshold or unambiguous measurable condition, or [REQUIRES OPERATIONAL CONFIRMATION];
- evaluation window (time or samples);
- evidence source or monitoring mechanism;
- authorized decision owner;
- immediate halt or rollback action with safety preconditions;
- escalation procedure.

This is **planning criteria**, not real-time migration monitoring or rollback execution. The standalone reader GNOME-Field-Manual.html now includes the same corrected page 133 in both its static fallback and BOOK_PAGES dataset, with matching per-page SHA-256. The canonical page 140, historical embedded v9 PDF, and 314 other page cards remain untouched.

## Hash-bound preservation evidence

- Baseline main commit: 55c603d976563a29817ecfffc8e5b00f0d207a89.
- Before source index.html SHA-256: 8c7a56dc0687809e691ee09030f2a028c290c3ab81a64e63f4b58b6d809df3bd.
- Candidate standalone reader GNOME-Field-Manual.html SHA-256: 37fa881e887eb6ac9f18aadaa92759e55baab505fc7ce3d2bea993053a3ffb56.
- Candidate source index.html SHA-256: ee9537a51a407a5fcb2931468a54d0a3a31e37afea54549d4c0397336f1975ab.
- Candidate NUL-separated ascending 315 page-card SHA-256: 4b5e506301981930a1efce5211fd4ad15225ea07b62f562ced0db1d2bb9127fe.
- Unchanged 314-card SHA-256 (excluding page 133): 75e3cc4fee094ea766390b8d0cc19cfc8c86cef3d9098cd4dc56baca8b995190.
- Unchanged page 140 card SHA-256: 66a08d8d367d91ae61221fa48865e5f217247e2af8aab7003a43be6bd4b32276.
- Frozen Batch 4 page cards 107–121 SHA-256: 145b5fe00fedfa43d2a098f3bca1e59e6a9d7ffef8e4a378bc0852626a2d9a1a.
- Batch 4's original disposition document continues to bind its original source digest rather than this candidate.
- Historic 14 pending / 77 drafted review data is bound to source 1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19; those artifacts have not been rewritten.

## Release and disposition boundary

The candidate does not confer canonical body verification. The fresh index remains **11 pending / 80 drafted / 91 total / 315 pages, 0/91 verified bodies**. Require independent editorial review and evidence of correct layout at page 133 before a Batch 5 PASS or pending-entry promotion. Confirm the planned-to-canonical identity crosswalk explicitly and re-run all source, provenance, accessibility and browser gates.
