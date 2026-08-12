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

- **Read/use the manual:** [published workspace and embedded reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/)
- **Inspect identity and scope:** [`docs/IDENTITY_AND_SCOPE.md`](docs/IDENTITY_AND_SCOPE.md)
- **Inspect the measured release baseline:** [`docs/BASELINE_AUDIT_2026-08-06.md`](docs/BASELINE_AUDIT_2026-08-06.md)
- **Inspect stable-release criteria:** [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md)

## Current release state

Current repository version: **1.0.0-rc.1**.

This is an auditable release candidate, not a final stable manual release. The committed structure reconciles to 21 pending IDs, 70 embedded non-pending IDs, and 91 semantic manual entries across 315 embedded page cards.

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
- issue #3

</details>

## Repository structure

- `index.html` — canonical combined PTSP workspace and embedded reader.
- `VERSION` — repository-package version.
- `CHANGELOG.md` — material repository and publication changes.
- `tools/validate_manual.py` — deterministic structural validator.
- `tools/reconcile_entry_lineage.py` — deterministic 21/70/91 entry-lineage reconciler.
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
- `docs/BASELINE_AUDIT_2026-08-06.md` — measured release-candidate baseline.
- `docs/IDENTITY_AND_SCOPE.md` — canonical identity and remaining release boundaries.
- `docs/QUALITY_GATE.md` — stable release criteria.

## Validate locally

Requires Python 3.11 or newer and no third-party packages.

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
  --json editorial-lineage.json \
  --markdown editorial-lineage.md
```

The reports record the exact SHA-256 of `index.html`. They establish structure, 21/70/91 inventory arithmetic, completed identifier semantics, searchable/visible parity, the historical PDF boundary, and preservation of the frozen provenance records. They do not establish factual correctness, editorial completion of the remaining pending entries, prompt portability, external-link health, or accessibility conformance.

## Release policy

Stable release remains blocked by the remaining pending-entry disposition, accessibility/browser review, and final release evidence. The former R-05 Field Journal collision is resolved without assigning a replacement ID; the predecessor was explicitly cut from the live entry set.

## Project

GnomeMan4201 / badBANANA Research Collective
