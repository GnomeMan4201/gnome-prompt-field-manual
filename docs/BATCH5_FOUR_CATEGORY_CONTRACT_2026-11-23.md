# Batch 5 — four-category contract and explicit identity crosswalk (2026-11-23)

**State: REVISE / HOLD, not PASS.** This correction repairs the frozen brief's
four-category output shape but does not establish that planned and canonical identifiers are interchangeable.

## Source-bound comparison

- Frozen PTSP `b-s10`: **planned S-10 Migration Risk Classifier** with four
  independently rated categories (**DATA COMPATIBILITY RISK**, **BEHAVIORAL
  RISK**, **INTEGRATION RISK**, **ROLLBACK COMPLEXITY RISK**), GO/NO-GO and
  ROLLBACK TRIGGER CONDITIONS.
- Canonical searchable **S-07 Migration Risk Classifier**: pages 129–135;
  eight evidence-backed primary dimensions (pages 130–132); go/no-go,
  rollback trigger criteria and four-category summary now made mandatory
  in the standard prompt / expected output (pages 130 and 133).
- Canonical **S-10 Architecture Decision Record Generator**, page 140, is
  a *different manuscript entry*. No global renumbering or repurposing.
- Risk scale: canonical eight-dimensional **MODERATE** is rendered
  **MEDIUM** only for the frozen brief's four-category summary. Preserve
  the source dimension ratings; do not average away a HIGH/CRITICAL risk.
  Missing evidence is **UNASSESSED / DO NOT MIGRATE YET**, not a guessed
  numeric risk.
- The four-category mapping is a documented *assessment mapping*, not
  proof that two separately named IDs are one canonical body. See
  [structured crosswalk](../workbench/data/batch5_identity_crosswalk.json).

## Change boundary and exact hashes

- Baseline main: `8c13d621edb675b8560d554a552828f9837abc40`.
- Changed canonical page cards: **130 and 133 only**. **313 other cards are
  byte-identical**, including page 140 and frozen Batch 4 pages 107–121.
- Corrected `index.html` SHA-256: `dca538299e7a0a6ee74d627baa231089c051a1627a29a0364c8ff136e1b4e448`.
- Corrected standalone `GNOME-Field-Manual.html` SHA-256:
  `558fec69b1dc5f2ceb3821d7918a1601d017e93b289c97c4f8e6afcb35895fb3`. Dynamic BOOK_PAGES and no-JS static
  fallback carry the same explicit four-category requirement.
- Unchanged 313-card SHA-256: `31f9f2d953c9bc5c8392f4010cc80eb26524cff54e92ff2fc633f2f67cf918e0`.
- Unchanged page 140 SHA-256: `66a08d8d367d91ae61221fa48865e5f217247e2af8aab7003a43be6bd4b32276`.
- Unchanged Batch 4 pages 107–121 SHA-256: `145b5fe00fedfa43d2a098f3bca1e59e6a9d7ffef8e4a378bc0852626a2d9a1a`.
- Historical v9 PDF and Phase VIII frozen research evidence remain unchanged.
- Current identity index and Reactor source bind to this new canonical digest.

## Pending adjudication

A reader must explicitly decide the editorial **identifier collision**:
planned S-10 / canonical S-07 share subject; canonical S-10 ADR is distinct.
Do not silently delete, merge, renumber, or change 91-entry arithmetic based
on title similarity. An approved disposition must document what constitutes
the expected independent entry before altering status.

This candidate **does not** promote `b-s10`, authorize a stable release,
or verify any of the 91 canonical bodies. Inventory remains **11 pending /
80 drafted / 91 semantic IDs / 315 pages, 0/91 verified body boundaries**.
