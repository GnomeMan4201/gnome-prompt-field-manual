# Changelog

All material changes to the GNOME Prompt Field Manual production workspace are recorded here. Dates use UTC. A release entry describes the committed artifact; it does not imply that every prompt pattern behaves identically across model families or versions.

## [1.0.0-rc.1] - 2026-08-06

### Added

- Deterministic, network-free structural validation for `index.html`.
- Source-SHA-256-bound JSON and Markdown validation evidence.
- Eight unit tests covering validator success and failure paths.
- Read-only GitHub Actions quality gate with non-persistent checkout credentials.
- Explicit release-quality, correction, evidence, and model/version-sensitivity requirements.
- Bounded structural inventory tooling for the large embedded artifact.
- Canonical identity and scope record.
- Release-candidate version record.

### Changed

- Added a document description, one main landmark, one primary heading, and seven section headings without changing the underlying section text.
- Replaced the placeholder README with an accurate production-workspace guide.
- Clarified that the repository package version is distinct from the unresolved embedded-manual editorial version.

### Discovered

- The public artifact is **PTSP — Pending Entry Draft Plan**, not a neutral final-manual landing page.
- It combines a production workspace with an embedded GNOME Prompt Field Manual v9 reader.
- The artifact reports 22 pending, 70 drafted, and 92 total entries across 10 batches, while also citing a v3 DOCX source.
- The v3/v9 lineage, pending-entry inventory, and final public-product boundary require reconciliation before stable release.

### Validation baseline

- `index.html` SHA-256: `b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`
- 2,208,371 bytes
- 2,399 parsed elements
- 348 unique IDs
- 8 headings
- 23 internal anchors
- 0 structural errors
- 0 structural warnings

### Status

This is an auditable release baseline, not the final stable release. Identity/version reconciliation, source-grounded examples and counterexamples, technical-claim review, accessibility review, and browser-matrix validation remain open.

## [0.1.0] - 2026-05-24

### Added

- Initial public single-page workspace and repository README.

[1.0.0-rc.1]: https://github.com/GnomeMan4201/gnome-prompt-field-manual/compare/402c888eca4b02c434129c28ae6e685c3805ae6c...HEAD
[0.1.0]: https://github.com/GnomeMan4201/gnome-prompt-field-manual/commit/402c888eca4b02c434129c28ae6e685c3805ae6c
