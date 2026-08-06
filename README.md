# GNOME Prompt Field Manual Production Workspace

Operational prompt engineering for auditable AI-assisted work.

[Open the published workspace and embedded reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/)

## Status

Current repository version: **1.0.0-rc.1**

This repository currently publishes **PTSP — Pending Entry Draft Plan**, a combined production workspace and embedded GNOME Prompt Field Manual reader. It is an auditable release candidate, not a final stable manual release.

The committed structure now independently reconciles to 22 pending IDs, 70 embedded non-pending IDs, and 92 total manual entry IDs across 315 embedded page cards. Eight additional ID-shaped tokens are explicitly classified as templates or embedded test cases rather than entries. Twenty-one pending IDs already occur in the reader; `R-10` is documented as a numbering collision with an existing `R-07`.

The entry arithmetic is verified, but the interface still names a v3 DOCX source while the embedded reader identifies itself as v9. Authoritative editorial lineage, pending-entry disposition, and the final public-product boundary remain release blockers.

See:

- [`docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md`](docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md)
- [`docs/IDENTITY_AND_SCOPE.md`](docs/IDENTITY_AND_SCOPE.md)
- [`docs/BASELINE_AUDIT_2026-08-06.md`](docs/BASELINE_AUDIT_2026-08-06.md)
- issue #3

## Repository structure

- `index.html` — canonical combined PTSP workspace and embedded reader.
- `VERSION` — repository-package version, not the unresolved embedded-manual editorial version.
- `CHANGELOG.md` — material repository and publication changes.
- `tools/validate_manual.py` — deterministic structural validator.
- `tools/reconcile_entry_lineage.py` — deterministic 22/70/92 entry-lineage reconciler.
- `tools/inspect_manual.py` — bounded structural inventory for the large HTML artifact.
- `tests/test_validate_manual.py` — structural validator tests.
- `tests/test_reconcile_entry_lineage.py` — lineage extraction and classification tests.
- `docs/ENTRY_LINEAGE_BASELINE_2026-08-06.md` — verified 92-entry arithmetic and interpretation boundary.
- `docs/BASELINE_AUDIT_2026-08-06.md` — measured release-candidate baseline and remaining gates.
- `docs/IDENTITY_AND_SCOPE.md` — canonical identity, boundaries, and unresolved version lineage.
- `docs/QUALITY_GATE.md` — stable release criteria.
- `docs/MODEL_VERSION_SENSITIVITY.md` — rules for model- and runtime-dependent claims.
- `docs/CORRECTIONS_AND_EVIDENCE.md` — correction, evidence, citation, and redaction policy.

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
```

The generated reports record the exact SHA-256 of `index.html`. They establish committed structure and inventory arithmetic; they do not establish external-link health, factual correctness, editorial completeness, prompt portability, or accessibility conformance.

## Release policy

A stable release requires all applicable gates in [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md), plus the version-lineage and public-product resolution tracked in issue #3. Prompt behavior is treated as an observation of a complete model/runtime environment, not as a permanent guarantee of prompt text alone.

## Project

GnomeMan4201 / badBANANA Research Collective
