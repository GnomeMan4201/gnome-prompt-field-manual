# Editorial Renumbering Completion — 2026-08-12

## Completion status

The frozen two-label repair is complete in the canonical searchable reader:

- Competing Hypotheses Table: `R-06` → `R-07`;
- Source-of-Truth Conflict Resolver: `R-07` → `R-10`;
- no second Source-of-Truth Conflict Resolver body was created;
- Failure-to-Test Converter cross-references exposed by the classifier now use the existing `R-05` identifier;
- `R-10` is no longer represented as pending work or as a drafting brief.

## Commit and artifact binding

- Frozen decision commit: `410e8b46e8f50b9dbfc8d2c37358818722c9b9c2`
- Pre-mutation branch commit: `3a8fb2a609048a218082575af9b5719ed536c75a`
- Post-mutation implementation commit: `7c04707b677a5263bdbe0dd9a898d09007750fab`
- Pre-mutation `index.html` SHA-256: `b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`
- Post-mutation `index.html` SHA-256: `2edebb296c45148784259942d51e34e56426557376c525cbf2a90c7938ccfdf6`
- Canonical searchable-text surface SHA-256: `4f2e08ee26e1a71b6d1b78ef54a6b4cc5edb52fab9307645a83eaf40e3007d7e`
- Historical v9 PDF SHA-256: `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`

The implementation commit is recorded instead of attempting to embed the final evidence-only commit's own SHA inside itself.

## Arithmetic invariant

The evidence-backed post-state is:

- 21 pending inventory IDs;
- 21 matching drafting briefs;
- 70 embedded non-pending IDs;
- 91 reconciled semantic entries;
- 315 embedded reader page cards.

The old 92 total was a syntactic union that counted pending-only `R-10` separately from the existing Source-of-Truth body. Removing that duplicate semantic representation reduces the total to 91 without inventing a replacement `R-06` entry.

## Occurrence-classifier disposition

`EDITORIAL_OCCURRENCE_CLASSIFIER_2026-08-12.csv` contains all 151 case-insensitive exact `R-06`, `R-07`, and `R-10` token occurrences in tracked text at the frozen baseline commit.

- zero occurrences are unclassified;
- every row records its container, stable locator, surface, old token, classification, disposition, new value or preservation decision, and a context hash;
- SHA-bound 2026-08-06 records are preserved rather than rewritten;
- no global replacement was used.

## Reader product boundary

The repository implements a combined product:

1. PTSP remains visible as production state.
2. Corrected searchable text is canonical and opens by default.
3. The embedded v9 PDF remains byte-for-byte unchanged, visibly labelled historical, independently hashed, and non-canonical.

The missing editable v3 manuscript and editable v9 source prevent generation of a corrected PDF from an authoritative common source. Representing the old PDF as corrected would therefore be unsupported.

## Verification evidence

The implementation commit passed:

- 24 unit tests;
- structural validation with 0 errors and 0 warnings;
- 21/70/91/315 enforced reconciliation;
- 25 editorial completion checks;
- exact parity for `manual-page-076`, `091`, `093`, `101`, `105`, `267`, and `307`;
- exactly one Competing Hypotheses body and one Source-of-Truth body;
- deterministic regeneration of the 151-row classifier;
- historical PDF byte-hash preservation;
- SHA preservation for all three frozen 2026-08-06 evidence records.

Commands:

```bash
python -m unittest discover -s tests -v

python tools/validate_manual.py \
  --input index.html \
  --json manual-validation.json \
  --markdown manual-validation.md \
  --strict-warnings

python tools/reconcile_entry_lineage.py \
  --input index.html \
  --json entry-lineage.json \
  --markdown entry-lineage.md \
  --expect-pending 21 \
  --expect-drafted 70 \
  --expect-total 91 \
  --expect-pages 315 \
  --enforce

python tools/audit_editorial_lineage.py \
  --input index.html \
  --repository-root . \
  --json editorial-lineage.json \
  --markdown editorial-lineage.md
```

## Preserved historical records

These files remain byte-identical to the frozen baseline:

- `EDITORIAL_LINEAGE_DECISION_2026-08-06.md`: `341d645c44583f31b3b195dc68e7dcafc3f26a0ba0c23effbe6fb3fd4db31075`
- `ENTRY_LINEAGE_BASELINE_2026-08-06.md`: `c10a2f24b18b25c0a1bed83bbfdbb10ad0cb01476d7f0435b9fb1a375023ad8f`
- `BASELINE_AUDIT_2026-08-06.md`: `efa69cb5f5ff893da4e8c1d3d6caf1134a34009bd669255cc138dc190a5e1c3c`

## Known limitations and blockers

- The authoritative editable v3 manuscript and editable v9 source are not committed.
- The historical PDF retains the old labels by design and must never be represented as the corrected current reader.
- `R-05 (Field Journal Entry)` at `manual-page-213` remains an independent semantic collision. It must be corrected only from authoritative source evidence and is tracked separately.
- Accessibility/browser evidence and deployed GitHub Pages byte verification remain merge/deployment gates rather than claims established by the local lineage audit.
