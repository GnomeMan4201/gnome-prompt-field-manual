# PTSP Entry-Lineage Post-State Baseline — 2026-08-12

## Scope

This successor baseline records the production and embedded-reader state after execution of the frozen R-06/R-07/R-10 renumbering decision. It supplements rather than replaces the SHA-bound 2026-08-06 baseline.

## Artifact binding

- Implementation commit: `7c04707b677a5263bdbe0dd9a898d09007750fab`
- `index.html` SHA-256: `2edebb296c45148784259942d51e34e56426557376c525cbf2a90c7938ccfdf6`
- Canonical searchable-text surface SHA-256: `4f2e08ee26e1a71b6d1b78ef54a6b4cc5edb52fab9307645a83eaf40e3007d7e`
- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`

## Reconciled production state

The deterministic reconciler reports:

- 21 pending inventory rows and 21 unique pending IDs;
- 21 drafting briefs and 21 unique brief IDs;
- 70 embedded IDs not listed as pending;
- 91 reconciled semantic entry IDs;
- 21 pending IDs also present in the embedded reader;
- 0 pending IDs absent from the embedded reader;
- 0 inventory IDs without briefs;
- 0 briefs without inventory rows;
- 315 embedded reader page cards;
- 8 explicitly excluded non-entry tokens.

The source-reported arithmetic and extracted semantic universe agree:

```text
21 pending + 70 embedded non-pending = 91 semantic entries
```

## Identifier result

- `R-07` identifies Competing Hypotheses Table.
- `R-10` identifies Source-of-Truth Conflict Resolver.
- Each title has exactly one full-entry body.
- No pending or drafting-brief representation of `R-10` remains.
- Failure-to-Test Converter references corrected in this pass use `R-05`.

## Representation result

The corrected searchable text is the canonical/default reader. The unchanged PDF is explicitly labelled as a historical v9 snapshot and independently hash-bound. The two surfaces are not represented as one corrected publication.

## Structural measurements

- Bytes: 2,206,830
- Parsed elements: 2,381
- Unique IDs: 347
- Headings: 8
- Internal anchors: 23
- Embedded reader page cards: 315
- Structural errors: 0
- Structural warnings: 0

## Interpretation boundary

This baseline proves committed structure, occurrence reconciliation, corrected identifier semantics, affected-page parity, and the declared PDF/text boundary. It does not prove factual correctness, completion of the remaining pending entries, model portability, browser/accessibility conformance, or the intended identifier for the separate `R-05 (Field Journal Entry)` collision.
