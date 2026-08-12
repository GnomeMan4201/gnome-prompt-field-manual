# Changelog

All material changes to the GNOME Prompt Field Manual production workspace are recorded here. Dates use UTC. A release entry describes the committed artifact; it does not imply that every prompt pattern behaves identically across model families or versions.

## [Unreleased]

### Corrected

- Completed the frozen semantic mapping: Competing Hypotheses Table is now `R-07`; Source-of-Truth Conflict Resolver is now `R-10`.
- Corrected Failure-to-Test Converter cross-references from `R-06` to the existing `R-05` entry.
- Removed the orphaned `R-05 (Field Journal Entry)` reference from `manual-page-213`; the evidence identifies its `W-04 Field Journal Scaffolder` predecessor as cut, not as a live entry eligible for reassignment.
- Removed completed `R-10` work from the pending inventory and drafting briefs without creating a duplicate body.
- Reconciled the post-state to 21 pending, 70 embedded non-pending, and 91 semantic entries across 315 reader pages.

### Changed

- Made corrected searchable text the canonical/default reader.
- Preserved and labelled the unchanged v9 PDF as a historical snapshot with an independent SHA-256.
- Replaced the decision-freeze audit with fail-closed post-state, parity, duplicate-body, stale-reference, PDF-boundary, and provenance gates.
- Added a machine-readable classifier for all 151 baseline `R-06`, `R-07`, and `R-10` token occurrences.
- Added fail-closed page-213 and unique `R-05` body checks so an internally consistent but semantically false Field Journal pairing cannot pass.

### Known limitations

- The authoritative editable v3 manuscript and editable v9 source remain unavailable.
- The cut `W-04 Field Journal Scaffolder` has no live identifier and remains visible only in historical provenance.

## [1.0.0-rc.1] - 2026-08-06

### Added

- Deterministic structural validation for `index.html`.
- SHA-bound JSON and Markdown validation evidence.
- Deterministic PTSP entry-lineage reconciliation.
- Enforced read-only 22 pending / 70 drafted / 92 total / 315 page-card baseline.
- Deterministic editorial-lineage audit for v3/v9 roles and R-06/R-07/R-10 evidence.
- Structural, inventory, and editorial-lineage unit tests.
- Read-only GitHub Actions quality gates with non-persistent checkout credentials.
- Release-quality, correction, evidence, and model/version-sensitivity requirements.
- Canonical identity, scope, lineage, and release-candidate records.

### Changed

- Added document semantics and metadata without rewriting section content.
- Replaced the placeholder README with an evidence-backed production-workspace guide.
- Separated repository package version from manuscript and publication versions.
- Replaced source-reported entry arithmetic with a reproducible 92-entry reconciliation.
- Resolved v3 and v9 as different artifact roles rather than interchangeable version labels.

### Verified entry findings

- 22 unique pending IDs have 22 matching drafting briefs.
- 70 embedded non-pending IDs plus 22 pending IDs reconcile to 92 manual entries.
- `AP-00`, `X-00`, and `EDT-01` through `EDT-06` are explicitly excluded non-entry tokens.
- Twenty-one pending IDs already occur in the reader; occurrence does not override pending state.

### Resolved editorial lineage

- The named v3 master is the editable manuscript and production-planning authority represented by PTSP instructions; the DOCX is not committed.
- The embedded v9 reader is a rendered publication snapshot generated from a v9 PDF.
- `1.0.0-rc.1` is the repository/package validation version.
- Complete v3-to-v9 transformation history remains unprovable without the missing editable sources.

### Frozen numbering decision

- Competing Hypotheses Table: `R-06` → `R-07`.
- Source-of-Truth Conflict Resolver: `R-07` → `R-10`.
- R-10 is not a new entry and must not receive a duplicate body.
- Physical renumbering and every affected cross-reference remain a dedicated release-blocking mutation pass.

### Validation baseline

- `index.html` SHA-256: `b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`
- 2,208,371 bytes
- 2,399 parsed elements
- 348 unique IDs
- 8 headings
- 23 internal anchors
- 315 embedded reader page cards
- 92 reconciled manual entry IDs
- 0 structural errors
- 0 structural warnings

### Status

This remains an auditable release candidate. Stable publication is blocked by the complete renumbering pass, remaining pending-entry disposition, final public-product boundary, accessibility/browser validation, and final release evidence.

## [0.1.0] - 2026-05-24

### Added

- Initial public single-page workspace and repository README.

[1.0.0-rc.1]: https://github.com/GnomeMan4201/gnome-prompt-field-manual/compare/402c888eca4b02c434129c28ae6e685c3805ae6c...HEAD
[0.1.0]: https://github.com/GnomeMan4201/gnome-prompt-field-manual/commit/402c888eca4b02c434129c28ae6e685c3805ae6c
