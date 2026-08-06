# GNOME Prompt Field Manual Production Workspace

Operational prompt engineering for auditable AI-assisted work.

[Open the published workspace and embedded reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/)

## Status

Current repository version: **1.0.0-rc.1**

This repository publishes **PTSP — Pending Entry Draft Plan**, a combined production workspace and embedded GNOME Prompt Field Manual reader. It is an auditable release candidate, not a final stable manual release.

The committed structure reconciles to 22 pending IDs, 70 embedded non-pending IDs, and 92 total manual entry IDs across 315 embedded page cards.

The v3/v9 roles are now resolved:

- **v3 master** — editable manuscript and production-planning authority named by the PTSP instructions, but not physically committed;
- **v9 reader** — rendered publication snapshot embedded in `index.html` and generated from a v9 PDF;
- **1.0.0-rc.1** — repository/package validation version, not a manuscript or publication version.

The numbering decision is also frozen: Competing Hypotheses Table must move **R-06 → R-07**, and Source-of-Truth Conflict Resolver must move **R-07 → R-10**. R-10 is not a new entry. The physical renumbering and all cross-reference updates remain a dedicated release-blocking change set.

See:

- [`docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md`](docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md)
- [`docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md`](docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md)
- [`docs/IDENTITY_AND_SCOPE.md`](docs/IDENTITY_AND_SCOPE.md)
- [`docs/BASELINE_AUDIT_2026-08-06.md`](docs/BASELINE_AUDIT_2026-08-06.md)
- issue #3

## Repository structure

- `index.html` — canonical combined PTSP workspace and embedded reader.
- `VERSION` — repository-package version.
- `CHANGELOG.md` — material repository and publication changes.
- `tools/validate_manual.py` — deterministic structural validator.
- `tools/reconcile_entry_lineage.py` — deterministic 22/70/92 entry-lineage reconciler.
- `tools/audit_editorial_lineage.py` — deterministic v3/v9 and R-06/R-07/R-10 decision audit.
- `tools/inspect_manual.py` — bounded structural inventory for the large HTML artifact.
- `tests/` — structural, inventory, and editorial-lineage tests.
- `docs/EDITORIAL_LINEAGE_DECISION_2026-08-06.md` — frozen artifact roles and numbering decision.
- `docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md` — verified 92-entry arithmetic.
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
  --expect-pending 22 \
  --expect-drafted 70 \
  --expect-total 92 \
  --expect-pages 315 \
  --enforce

python tools/audit_editorial_lineage.py \
  --input index.html \
  --json editorial-lineage.json \
  --markdown editorial-lineage.md
```

The reports record the exact SHA-256 of `index.html`. They establish structure, inventory arithmetic, and the committed editorial decision; they do not establish factual correctness, editorial completion, prompt portability, external-link health, or accessibility conformance.

## Release policy

Stable release remains blocked by the complete R-06/R-07/R-10 renumbering pass, remaining pending-entry disposition, public-product finalization, accessibility/browser review, and final release evidence.

## Project

GnomeMan4201 / badBANANA Research Collective
