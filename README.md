# GNOME Prompt Field Manual

Operational prompt engineering for auditable AI-assisted work.

[Read the published manual](https://gnomeman4201.github.io/gnome-prompt-field-manual/)

## Status

Current repository version: **1.0.0-rc.1**

This is an auditable release candidate, not the final stable release. The existing single-page manual remains the canonical publication artifact while structural validation, source-grounded examples and counterexamples, technical-claim review, accessibility review, and browser-matrix checks are completed.

## Repository structure

- `index.html` — canonical self-contained manual.
- `VERSION` — current repository version.
- `CHANGELOG.md` — material release history.
- `tools/validate_manual.py` — deterministic, network-free structural validator.
- `tests/test_validate_manual.py` — validator success and failure-path tests.
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
  --markdown manual-validation.md
```

The generated report records the exact SHA-256 of the validated `index.html`. It checks structural integrity and local references; it does not prove that external links are live or that technical prose is factually correct.

## Release policy

A stable release requires all applicable gates in [`docs/QUALITY_GATE.md`](docs/QUALITY_GATE.md). Prompt behavior is treated as an observation of a complete model/runtime environment, not as a permanent guarantee of prompt text alone.

## Project

GnomeMan4201 / badBANANA Research Collective
