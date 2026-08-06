# GNOME Prompt Field Manual Production Workspace

Operational prompt engineering for auditable AI-assisted work.

[Open the published workspace and embedded reader](https://gnomeman4201.github.io/gnome-prompt-field-manual/)

## Status

Current repository version: **1.0.0-rc.1**

This repository currently publishes **PTSP — Pending Entry Draft Plan**, a combined production workspace and embedded GNOME Prompt Field Manual reader. It is an auditable release candidate, not a final stable manual release.

The committed interface reports 22 pending entries, 70 drafted entries, 92 total entries, 10 production batches, and an embedded v9 reader containing 315 pages. It also names a v3 DOCX source, so the editorial version and entry lineage remain under explicit reconciliation. These are source-reported production values, not independently verified completion claims.

See [`docs/IDENTITY_AND_SCOPE.md`](docs/IDENTITY_AND_SCOPE.md) and issue #3 before interpreting the repository version as the editorial version of the embedded manual.

## Repository structure

- `index.html` — canonical combined PTSP workspace and embedded reader.
- `VERSION` — repository-package version, not the unresolved embedded-manual editorial version.
- `CHANGELOG.md` — material repository and publication changes.
- `tools/validate_manual.py` — deterministic, network-free structural validator.
- `tools/inspect_manual.py` — bounded structural inventory for the large HTML artifact.
- `tests/test_validate_manual.py` — validator success and failure-path tests.
- `docs/IDENTITY_AND_SCOPE.md` — canonical identity, boundaries, and lineage conflict.
- `docs/QUALITY_GATE.md` — stable release criteria.
- `docs/MODEL_VERSION_SENSITIVITY.md` — rules for model- and runtime-dependent claims.
- `docs/CORRECTIONS_AND_EVIDENCE.md` — correction, evidence, citation, and redaction policy.

## Validate locally

Requires Python 3.11 or newer and no third-party packages.

```bash
python -m unittest discover -s tests -p 'test_validate_manual.py' -v
python tools/validate_manual.py \
  --input index.html \
  --json manual-validation.json \
  --markdown manual-validation.md \
  --strict-warnings
```

The report records the exact SHA-256 of the validated `index.html`. It checks committed structure and local references; it does not establish external-link health, factual correctness, editorial completeness, prompt portability, or accessibility conformance.

## Release policy

A stable release requires all applicable gates in [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md), plus the identity and version-lineage resolution tracked in issue #3. Prompt behavior is treated as an observation of a complete model/runtime environment, not as a permanent guarantee of prompt text alone.

## Project

GnomeMan4201 / badBANANA Research Collective
