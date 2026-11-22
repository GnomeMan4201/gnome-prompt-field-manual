# Canonical identity index — bounded verification (2026-11-22)

This change deliberately **does not promote Gemini's v2 workbench extractor** into the canonical manual. The v2 implementation used every ID-shaped token in a page as an entry owner, which admits phantom entries from cross-references and incorrectly excludes the active `W-04`.

## What has been verified

The new `tools/export_entry_identity_index.py` reuses the repository's established `tools/reconcile_entry_lineage.py` inventory algorithm rather than an independent ID regex universe.

Against committed main source `index.html` at SHA-256 `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`:

- **91 identities** reconciled; **14** pending inventory entries; **77** non-pending entries; **315** page cards.
- The *active* `W-04` is retained; the retired `W-04 Field Journal Scaffolder` predecessor is not reintroduced as a new entry.
- `R-07` and `R-10` are retained under their corrected current identity mapping.
- All page references in the index are labeled **ID occurrences, not verified entry body ownership**.
- No canonical body text or validated cross-reference association is emitted. `canonicalBody=null`, `bodyStatus=UNRESOLVED_BOUNDARIES` and `crossRefStatus=NOT_VALIDATED` are deliberate.

The reconciler's candidate title field is included as `titleCandidate` and marked **unverified**. Some original source occurrences have truncated titles; these should not be shown as authoritative titles.

The generated `workbench/data/entry_identity_index.json` is an **identity inventory**, not the complete workbench reader dataset. It must not be silently substituted for `manual_entries.json`.

## Tests performed in isolated clean checkout

- `python3 -m unittest discover -s tests -q`: **47 passed**, including three new identity-index regression cases.
- `python3 tools/validate_manual.py --input index.html --strict-warnings`: **0 errors, 0 warnings**.
- `python3 tools/export_entry_identity_index.py`: completed and exported 91 identities.
- Tests include invariants for active W-04, current R-07/R-10, no invented S-99, and source page-count fail-closed behavior.

## Remaining blocker

The HTML embeds a PDF-derived continuous text stream across 315 pages. A page can contain the end of one entry, another entry's header, and citations to other entry IDs. Future work must establish **verified, segment-level start/end offsets** and compare mapped titles/body spans with editorial evidence; it must explicitly adjudicate any ambiguity. The existing ID occurrence inventory and source checksums provide the baseline, not the answer.

Only after segment-level verification passes can a full canonical reader dataset be generated and the v2 UI integrated. The canonical root `index.html`, `VERSION`, historical PDF, `docs/`, and existing release policy remain unchanged.
