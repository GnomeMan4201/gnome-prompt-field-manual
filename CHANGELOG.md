# Changelog

All material changes to the GNOME Prompt Field Manual production workspace are recorded here. Dates use UTC. A release entry describes the committed artifact; it does not imply that every prompt pattern behaves identically across model families or versions.

## [Unreleased]

### Corrected

- 2026-11-25, from base `8f58c4c`. W-04 and AP-01 were both titled "Over-Smoothing Detector." AP-01 is now **Over-Smoothing Publication Gate**. It decides whether a draft can be published, while W-04 performs the five-part audit of what a rewrite changed. W-04 keeps its title because every titled cross-reference in the manuscript already names it, on pages 38, 69, 212, 227, 257 and 269. AP-01 now points to W-04 at the point of selection.
- Both entries allowed a review against the stated purpose when no source or original was supplied, but still asked the reviewer to quote or rate the original. In that case, AP-01 (page 276) now asks for the output passage and what the purpose requires, marks the claimed loss UNVERIFIED — NO SOURCE and rates NOT RATED — NO SOURCE. Such findings do not trigger its do-not-publish signal; the reviewer obtains the source first. W-04 (pages 49–50) says not to infer an original, marks claimed losses UNVERIFIED — NO ORIGINAL and reports NOT RATED — NO ORIGINAL. Page 50 also fixes an existing static/canonical mismatch ("Cross-reference"). IDs, anchors, the 31 title-mismatch review items and the 669 review records are unchanged.
- 2026-11-25, from base `a7e415e`. 31 of 91 Evidence Reactor entry labels showed cross-reference fragments such as "(Scope", "(Competing Hypothe-" and "(In-". The cause was that the Reactor displayed the identity index's advisory `titleCandidate`. The reconciler takes that value from the first page that mentions an ID, which is often a cross-reference rather than the entry heading. Labels now use the candidate packet's `canonicalHeadingCandidate`: the ID-and-title line followed by a Criteria line. The packet must match the Reactor's pinned source and the advisory titles and statuses of the identity index it loads. If it is missing or stale, the Reactor shows a banner and marks each label as an advisory candidate. Exported source references keep `titleCandidate` with its advisory value. IDs, the identity index, the manuscript, body verification (0/91), SEC-05 pending and the release designation are unchanged.
- 2026-11-25, from base `71bcdb7`. Page 6 said every prompt "was tested against ten inclusion criteria." The repository records criteria and verdicts only for the 22 prompts audited in Appendix A, from an earlier draft. Page 6 now numbers the ten criteria, says each entry's Criteria line cites them, and separates editorial selection from model behavior. The list is unchanged.
- SEC-01 (page 153) said Classification 6 "is reliable for" standard Base64, ROT13, hexadecimal and obvious character substitution. No evidence measured this. The page now treats a model's decode as an unverified interpretation. A decode reproduced by a deterministic tool is labelled TOOL-CHECKED. Otherwise it is labelled MODEL INTERPRETATION — UNVERIFIED and stays at POSSIBLE. Harmless examples are included. The pre-scan now applies to all content, matching page 149; Base64 and hexadecimal are ASCII. The pre-scan steps on pages 149–150 are unchanged.
- Renamed AP-06 from "Generated Junk Classifier" to **Passage Evidence Review**, and SEC-08 from "Generated Junk Detector" to **Collection Evidence Audit**. Both titles had described authorship detection after the entries became evidence reviews. "Collection" follows SEC-08's own wording and avoids overlap with AP-06, which already mentions corpora. Each entry now names the other at the point of selection. The field card lists both. Cross-references on pages 227, 232 and 252 use the new title, with a reason based on evidence rather than generic style. IDs, anchors, findings, exclusion rules and unknown-authorship rules are unchanged. The historical PDF, Batch 3 fixture, historical identity data and the AP-06 pilot keep the old names; the pilot evaluated revision `f592c6a`.
- Revised SEC-08 (pages 200–202) to audit source support and coverage. The previous edition inferred authorship from specificity and hedge density. SEC-08 and AP-06 now require inspectable supplied evidence for claims, record unknown authorship without provenance, and refer exclusions to human review.
- Identified SEC-05 as pending at its entry, in its referring workflows, in the field index and alongside the historical KEEP decision. Page 7 records the release candidate and independent body count. The post-incident field card now distinguishes reporting (S-09) from the rollback decision (S-08).

- 2026-11-24, PR #53. Page 7 previously claimed these prompts work where generic prompts fail. The revised introduction describes inspectable outputs and identifies comparative effectiveness as an open research question. It also describes Part IX as an entry lookup aid.
- AP-06 (pages 275, 283–284) previously allowed exclusion based on inferred authorship. The revised instruction requires passage-level evidence and a human decision against a stated quality criterion.
- Corrected the destinations for architecture decisions (page 260, S-10), incident reports (pages 262 and 265, S-09), and RFC drafts (page 273, P-07) in both reader versions.

- Batch 5 contract correction (REVISE/HOLD): canonical S-07 Migration Risk Classifier now requires the frozen planned S-10 brief's four separately rated categories, explicit category-to-dimension evidence mapping, and an UNASSESSED/DO NOT MIGRATE YET gate for absent evidence. The already-adopted rollback-trigger criteria remain mandatory.
- Added a machine-checkable planned S-10 / canonical S-07 / distinct canonical S-10 ADR crosswalk, with byte-preservation and standalone-reader regression tests. No entry promotion or independent body verification is claimed.

- Adjudicated R-01 Source Map with Contested Zones and R-03 Replication Risk Auditor against their frozen Batch 3 briefs without drafting replacement bodies.
- Added R-01's explicit cross-source `INSTITUTIONAL INTEREST MAP` while preserving the existing per-source institutional-interest disclosure and source-flattening controls.
- Restored R-03's `VERY HIGH RISK` level, retained `NOT REPLICATION-READY` as a separate insufficient-information status, and added the frozen R-05 Failure-to-Test Converter follow-up.

- Adjudicated W-01 Dense-to-Clear, W-02 Argument Skeleton Extractor, and W-03 Adversarial Reader against their frozen Batch 2 briefs without drafting replacement bodies.
- Added the frozen W-11 prerequisite to W-01 `INPUTS NEEDED` for source material that may not be safely summarizable.
- Preserved W-02 unchanged after it passed its frozen brief as written.
- Added W-03's explicit minimum-three requirement for persona-specific objections while preserving the existing adversarial report structure.

- Adjudicated T-01 Idea Stress-Test and T-02 Claim Dissection against their frozen Batch 1 briefs without drafting replacement bodies.
- Replaced T-01's dependent weakest-link Lens 6 with an independent Constraint Lens; weakest-link synthesis now occurs after all six lenses and explicitly selects the highest-severity finding.
- Added T-01's missing T-02 follow-up and one-sentence STRESS VERDICT justification requirement.
- Normalized T-02's verdict token to `COLLAPSE`, added the required one-sentence CHERRY-PICK RISK rationale, and corrected the expected artifact from seven sections to eight items.

- Completed the frozen semantic mapping: Competing Hypotheses Table is now `R-07`; Source-of-Truth Conflict Resolver is now `R-10`.
- Corrected Failure-to-Test Converter cross-references from `R-06` to the existing `R-05` entry.
- Removed the orphaned `R-05 (Field Journal Entry)` reference from `manual-page-213`; the evidence identifies its `W-04 Field Journal Scaffolder` predecessor as cut, not as a live entry eligible for reassignment.
- Removed completed `R-10` work from the pending inventory and drafting briefs without creating a duplicate body.
- Reconciled the post-state to 21 pending, 70 embedded non-pending, and 91 semantic entries across 315 reader pages.

### Changed

- Resolved the planned Batch 5 S-10 Migration Risk Classifier as **SUBSUMED** by the existing canonical S-07 after checking all frozen required artifacts. The different canonical S-10 ADR remains unchanged; no new body or identifier was minted. Current 10 pending / 81 non-pending IDs / 91 total / 315 pages / 5 batches. Frozen S-10 brief preserved separately.

- Promoted R-01 and R-03 from pending to drafted after bounded disposition; current state is 14 pending / 77 drafted / 91 semantic entries / 315 pages / 7 remaining batches.
- Removed R-01/R-03 from active pending inventory and drafting briefs, removed Batch 3 from the remaining-batch table without renumbering later batches, and retargeted startup defaults to S-01/S-02.
- Added a fail-closed Batch 3 disposition regression gate and SHA-bound audit record.

- Promoted W-01, W-02, and W-03 from pending to drafted after bounded disposition.
- Removed W-01/W-02/W-03 from active pending inventory and drafting briefs, removed Batch 2 from the remaining-batch table without renumbering later batches, and retargeted startup defaults to R-01/R-03.
- Added a fail-closed Batch 2 disposition regression gate and SHA-bound audit record.

- Promoted T-01 and T-02 from pending to drafted after bounded disposition.
- Removed T-01/T-02 from active pending inventory and drafting briefs while preserving the original Batch 1 drafting prompt as explicitly completed historical provenance.
- Added a fail-closed Batch 1 disposition regression gate and SHA-bound audit record.

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
