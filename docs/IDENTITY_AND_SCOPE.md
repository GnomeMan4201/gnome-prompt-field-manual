# Identity and Scope

## Repository identity

The public `index.html` identifies itself as **PTSP — Pending Entry Draft Plan** and combines:

1. a production workspace for completing and reviewing manual entries;
2. an embedded GNOME Prompt Field Manual reader.

The supported identity is:

> **GNOME Prompt Field Manual production workspace and embedded reader**

It is not yet a final stable manual release.

## Verified production state

The deterministic entry-lineage baseline confirms:

- 11 pending inventory IDs;
- 11 matching drafting briefs;
- 80 embedded non-pending entry IDs;
- 91 reconciled semantic manual entries;
- 6 remaining production batches;
- 5 special-caution entries;
- 315 embedded reader page cards.

Eight additional ID-shaped tokens are templates or embedded test-case identifiers: `AP-00`, `X-00`, and `EDT-01` through `EDT-06`.

## Resolved version roles

The apparent v3/v9 conflict is a role distinction:

- **v3 master:** the editable manuscript and production-planning authority named throughout PTSP. It defines planned numbering and pending/drafted disposition. The named DOCX is not committed.
- **canonical searchable text:** the corrected current reader embedded in `index.html`.
- **historical v9 PDF:** the unchanged rendered snapshot embedded in `index.html`. It is retained as provenance, explicitly non-canonical, and still contains the pre-correction labels.
- **1.0.0-rc.1:** the repository/package validation baseline, not the manuscript or publication version.

The repository does not prove the complete editorial transformation history between v3 and v9 because the underlying editable documents are absent. See [Editorial Lineage and Identifier Decision — 2026-08-06](EDITORIAL_LINEAGE_DECISION_2026-08-06.md).

## Resolved numbering authority

The PTSP instructions defined the planned numbering and identified the rendered-body mismatch:

- Competing Hypotheses Table appeared as `R-06`; it is now `R-07` in the canonical text.
- Source-of-Truth Conflict Resolver appeared as `R-07`; it is now `R-10` in the canonical text.
- `R-10` is not a missing substantive entry and must not receive a duplicate body.

The frozen correction is therefore:

- `R-06` → `R-07` for Competing Hypotheses Table;
- `R-07` → `R-10` for Source-of-Truth Conflict Resolver.

The decision and physical mutation are complete. A classified occurrence inventory covers every baseline `R-06`, `R-07`, and `R-10` token, the affected searchable metadata and visible text agree, and no duplicate Source-of-Truth body was created.

## Canonical boundaries

For the current `1.0.0-rc.1` release candidate:

- `index.html` is the canonical committed workspace artifact.
- PTSP production state is distinct from publication-version state.
- Entry presence is distinct from editorial completion.
- The v3 master is the strongest committed authority for planned numbering and pending state.
- Corrected searchable text is the canonical/default reader.
- The unchanged v9 PDF is a separately labelled and hashed historical snapshot.
- Structural and lineage validation do not establish factual correctness, prompt portability, accessibility conformance, external-link health, or evidence quality.

## Stable public-product decision

The repository uses a **combined product** boundary: PTSP remains visible as production state, corrected searchable text is the canonical/default manual reader, and the historical v9 PDF remains available as a separately labelled provenance artifact with an independent hash.

## Batch 5 identity hold — planned S-10 versus canonical S-07 / S-10

**REVISE, not PASS.** PTSP's frozen `b-s10` means **planned S-10 Migration Risk Classifier**, while the canonical searchable manual calls that entry **S-07 Migration Risk Classifier** (starting page 129), and uses **S-10** for the *different* **Architecture Decision Record Generator** (starting page 140). The unresolved title/ID mapping must be documented before changing the pending state. The current identity index records ID occurrences, not canonical-body attribution; its `S-10` occurrence on page 140 cannot establish a body match for the planned migration-risk brief.

The current migration-risk prompt lacks the brief's required output artifact **ROLLBACK TRIGGER CONDITIONS**. Do not promote S-10 until a separately authorized manuscript revision, deliberate crosswalk decision, and regression tests establish compliance. This hold leaves the live state at **11 pending / 80 drafted**. See [Batch 5 REVISE hold](BATCH5_REVISE_HOLD_2026-11-23.md).

## Remaining release blockers

Issue #1 is the umbrella stable-release closeout. Batches 1 through 3 promoted T-01/T-02, W-01/W-02/W-03, and R-01/R-03 on 2026-08-24; 11 pending entries remain after the 2026-11-23 Batch 4 disposition.

Remaining blockers:

- editorial disposition of the 11 remaining pending entries;
- regression browser/accessibility validation after the final content mutation;
- stable-release versioning, independent or documented-equivalent editorial review, and publication evidence.

Issue #6 resolved the former `R-05 (Field Journal Entry)` collision at
`manual-page-213`. The committed audit appendix identifies the predecessor as
`W-04 Field Journal Scaffolder` and records that it was cut; live `W-04` and
`R-05` are already assigned to Over-Smoothing Detector and Failure-to-Test
Converter. The unsupported current-state cross-reference was therefore removed
without inventing a replacement identifier. See
[Field Journal Identifier Decision — 2026-08-12](FIELD_JOURNAL_IDENTIFIER_DECISION_2026-08-12.md).
