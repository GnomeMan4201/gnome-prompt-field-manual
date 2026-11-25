# GNOME Prompt Field Manual

**Operational prompt engineering for structured, inspectable, auditable AI-assisted work.**

<p align="center">
  <img src="DC177E5E-70E7-4DED-A59D-469F51E607C0.png" alt="GNOME Prompt Field Manual graffiti banner" width="720" />
</p>

[Open the published workspace and embedded reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/)

## What this is

The GNOME Prompt Field Manual is a practical reference for people using AI inside analytical, research, investigative, and production workflows where the reasoning process needs to remain inspectable.

It is not a collection of magic prompt phrases. The manual focuses on repeatable working structures: defining evidence boundaries, separating observation from inference, preserving provenance, testing competing explanations, controlling revisions, recording uncertainty, and making AI-assisted work easier to audit after the fact.

The repository is also the production workspace for the manual. That means the public artifact preserves its editorial state, entry lineage, validation tooling, and unresolved release work instead of presenting a polished reader with its construction history hidden.

## Start here

- **Read on mobile:** [GNOME Field Manual — 315-page reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/GNOME-Field-Manual.html#page-1)
- **Read/use the manual:** [published workspace and embedded reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/)
- **Inspect the identity and scope baseline:** [`docs/IDENTITY_AND_SCOPE.md`](docs/IDENTITY_AND_SCOPE.md)
- **Inspect the measured release baseline:** [`docs/BASELINE_AUDIT_2026-08-06.md`](docs/BASELINE_AUDIT_2026-08-06.md)
- **Inspect stable-release criteria:** [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md)

## Current release state

Current repository version: **1.0.0-rc.1**.

This is an auditable release candidate, not a final stable manual release. The committed structure reconciles to 1 pending ID, 90 embedded non-pending IDs, and 91 semantic manual entries across 315 embedded page cards.

<details>
<summary><strong>Editorial lineage and numbering state</strong></summary>

The repository publishes **PTSP — Pending Entry Draft Plan**, a combined production workspace and embedded GNOME Prompt Field Manual reader.

The v3/v9 roles and public reader boundary are resolved:

- **v3 master** — editable manuscript and production-planning authority named by the PTSP instructions, but not physically committed;
- **canonical searchable text** — corrected current reader with the completed R-07/R-10 mapping;
- **historical v9 PDF** — unchanged rendered snapshot embedded in `index.html`, explicitly non-canonical and preserved for provenance;
- **1.0.0-rc.1** — repository/package validation version, not a manuscript or publication version.

The numbering correction is complete: Competing Hypotheses Table is **R-07**, and Source-of-Truth Conflict Resolver is **R-10**. R-10 is the existing Source-of-Truth body under its corrected identifier, not a new entry. The old mapping remains only in SHA-bound historical evidence and the explicitly historical PDF.

Authoritative records:

- [`docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md`](docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md)
- [`docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md`](docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md)
- [`docs/EDITORIAL_RENUMBERING_COMPLETION_2026-08-12.md`](docs/EDITORIAL_RENUMBERING_COMPLETION_2026-08-12.md)
- [`docs/ENTRY_LINEAGE_BASELINE_2026-08-12.md`](docs/ENTRY_LINEAGE_BASELINE_2026-08-12.md)
- [`docs/FIELD_JOURNAL_IDENTIFIER_DECISION_2026-08-12.md`](docs/FIELD_JOURNAL_IDENTIFIER_DECISION_2026-08-12.md)
- [`docs/IDENTITY_AND_SCOPE.md`](docs/IDENTITY_AND_SCOPE.md)
- [`docs/BASELINE_AUDIT_2026-08-06.md`](docs/BASELINE_AUDIT_2026-08-06.md)
- issue #1 — umbrella stable-release closeout
- [`docs/BATCH1_DISPOSITION_2026-08-24.md`](docs/BATCH1_DISPOSITION_2026-08-24.md) — SHA-bound Batch 1 disposition record
- [`docs/BATCH2_DISPOSITION_2026-08-24.md`](docs/BATCH2_DISPOSITION_2026-08-24.md) — SHA-bound Batch 2 disposition record
- [`docs/BATCH3_DISPOSITION_2026-08-24.md`](docs/BATCH3_DISPOSITION_2026-08-24.md) — SHA-bound Batch 3 disposition record
- [`docs/BATCH4_DISPOSITION_2026-11-23.md`](docs/BATCH4_DISPOSITION_2026-11-23.md) — source-bound S-01/S-02/S-03 disposition; frozen page bytes preserved.
- [`docs/BATCH5_FOUR_CATEGORY_CONTRACT_2026-11-23.md`](docs/BATCH5_FOUR_CATEGORY_CONTRACT_2026-11-23.md) — four-category risk-summary correction and source-bound identity crosswalk; historical REVISE/HOLD candidate.

</details>

- [Batch 5 disposition record](docs/BATCH5_DISPOSITION_2026-11-23.md) — planned S-10 is resolved as SUBSUMED by canonical S-07 without creating a new body; canonical S-10 ADR remains distinct.

- [Partial Batch 6 disposition](docs/BATCH6_SEC02_DISPOSITION_2026-11-24.md) — historical closure of SEC-02 at manuscript-contract level.

- [Batch 7 disposition](docs/BATCH7_SEC06_DISPOSITION_2026-11-24.md) closes SEC-06 at manuscript-contract level. For all SEC-06 references, use the current defensive evaluation contract on pages 187–197. It requires written authorization, isolated synthetic checks, and evidence-backed runtime verdicts. The archived brief and older probe wording serve as provenance.
- [Batch 8 disposition](docs/BATCH8_P01_P02_DISPOSITION_2026-11-24.md) closes P-01 and P-02 at manuscript-contract level. Pages 209–212 define the P-01 scaffold. Pages 213–217 define the P-02 learning inventory. The original briefs are preserved as archival evidence.
- [Batch 9 disposition](docs/BATCH9_P06_P07_DISPOSITION_2026-11-24.md) closes planned P-06 Work Sample Annotator as subsumed by canonical P-05, and planned P-07 Changelog Curation Engine as subsumed by canonical P-06. Canonical P-07 remains RFC Draft Generator. The [identity crosswalk](workbench/data/batch9_identity_crosswalk.json) resolves the archived S-09 ADR reference to canonical S-10 by subject. Use the same canonical heading when other frozen briefs cite S-09 for the ADR subject.
- [Batch 10 disposition](docs/BATCH10_DISPOSITION_2026-11-24.md) closes P-08 Peer Review Responder, P-09 Correction/Retraction Writer, and P-10 Open Source Contribution Guide Generator at manuscript-contract level. Their original briefs remain archived.
- The [final editorial closeout](docs/FINAL_EDITORIAL_CLOSEOUT_2026-11-24.md) records the outcomes of all ten scheduled reviews and the remaining release blockers. Batch 6 is the sole open batch. [SEC-05 awaits independent evidence](docs/BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md).

## Repository structure

- `index.html` — canonical combined PTSP workspace and embedded reader.
- `VERSION` — repository-package version.
- `CHANGELOG.md` — material repository and publication changes.
- `tools/validate_manual.py` — deterministic structural validator.
- `tools/reconcile_entry_lineage.py` — deterministic 1/90/91 entry-lineage reconciler.
- `tools/audit_editorial_lineage.py` — fail-closed renumbering, parity, PDF-boundary, and provenance audit.
- `tools/classify_editorial_occurrences.py` — deterministic generator for the frozen token classifier.
- `tools/inspect_manual.py` — bounded structural inventory for the large HTML artifact.
- `tests/` — structural, inventory, and editorial-lineage tests.
- `docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md` — frozen artifact roles and numbering decision.
- `docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md` — verified 92-entry arithmetic.
- `docs/EDITORIAL_OCCURRENCE_CLASSIFIER_2026-08-12.csv` — classified baseline occurrence inventory.
- `docs/EDITORIAL_RENUMBERING_COMPLETION_2026-08-12.md` — renumbering completion and artifact-boundary evidence.
- `docs/ENTRY_LINEAGE_BASELINE_2026-08-12.md` — verified 91-entry semantic post-state.
- `docs/FIELD_JOURNAL_IDENTIFIER_DECISION_2026-08-12.md` — evidence-backed disposition of the cut Field Journal predecessor and page-213 correction.
- `docs/BATCH1_DISPOSITION_2026-08-24.md` — adjudication record for T-01/T-02 promotion from pending to drafted.
- `docs/BATCH2_DISPOSITION_2026-08-24.md` — adjudication record for W-01/W-02/W-03 promotion from pending to drafted.
- `docs/BATCH3_DISPOSITION_2026-08-24.md` — adjudication record for R-01/R-03 promotion from pending to drafted.
- `docs/BASELINE_AUDIT_2026-08-06.md` — measured release-candidate baseline.
- `docs/IDENTITY_AND_SCOPE.md` — canonical identity and remaining release boundaries.
- `docs/QUALITY_GATE.md` — stable release criteria.

## Prompt reliability evidence

A paired pilot compared AP-06 with a plain-language review instruction on six synthetic cases using Qwen2.5-0.5B-Instruct. A blinded AI reviewer found both claims correctly assessed in one of six cases for each prompt. The original operator scored AP-06 at one of six and the control at zero of six. Both readings used the same twelve captured responses. Human scoring and separate-operator replication remain open. [Protocol, raw outputs, scoring sheets and reproduction commands](research/ap06-paired-pilot/README.md)

## Source-bound research history

The live editorial inventory now records **1 pending / 90 non-pending IDs**, with **0/91 independently verified canonical bodies**. The Reactor identity adapter uses `workbench/data/current_entry_identity_index.json`, deterministically derived from the current `index.html`.

Previously issued Phase V–VIII source-bound evidence (including the 629-decision adjudication queue) is **not relabeled** as current: it remains pinned to the original Batch 3 `index.html` digest `1f06445e…`. A byte-identical standalone HTML snapshot is preserved at `tests/fixtures/batch3-canonical-1f06445e.html` for offline verification and historical test replay. The adjudication workbench requires the matching original HTML, not the latest `index.html`, for source-hash verification. Recreating or rebinding its research manifest requires a separate, independently tested migration.

**Current-source review (Phase 12B):** the [current adjudication workbench](workbench/adjudication/current/index.html) is a separate mode using the current 91-candidate packet, with 669 pending review records (629 core decisions, 31 title discrepancies, nine unassigned regions). Run it through GitHub Pages or a localhost HTTP server. Local review records are not independently verified bodies; validate exports with `tools/validate_current_review_session.py`. See [the workflow and evidence limits](docs/PHASE12B_CURRENT_REVIEW_WORKBENCH_2026-11-24.md).

## Validate locally

The standalone validators require Python 3.11 or newer. The full regression suite also uses Node.js and Python `jsonschema`, as configured in Reactor Integrity CI.

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
  --expect-pending 1 \
  --expect-drafted 90 \
  --expect-total 91 \
  --expect-pages 315 \
  --enforce

python tools/audit_editorial_lineage.py \
  --input index.html \
  --json editorial-lineage.json \
  --markdown editorial-lineage.md
```

The reports record the exact SHA-256 of `index.html`. They check structure, 1/90/91 inventory arithmetic, identifier reconciliation, reader parity within the audited scope, the historical PDF boundary, and preservation of frozen provenance. Factual correctness, SEC-05 closure, prompt portability, external-link health, and accessibility conformance require separate evidence.

## Release policy

Stable release remains blocked by SEC-05 evidence, outstanding canonical-body verification and cross-reference review, final browser and accessibility review, independent editorial review or a documented equivalent, and publication evidence. The former R-05 Field Journal collision is resolved without assigning a replacement ID; the predecessor was explicitly cut from the live entry set.

## Project

GnomeMan4201 / badBANANA Research Collective
