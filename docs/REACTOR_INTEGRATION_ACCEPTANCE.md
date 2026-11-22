# Phase VIII-A — Integration and browser smoke-test record

**Date:** November 22, 2026. **Scope:** feature branch `feature/reactor-viiia-integrity-hardening`, draft PR #25.

## GitHub integration evidence

All 27 source files from `gnome-reactor-integrity-hardening.zip` were applied as **new repository files** (not root publication replacements). A fresh clone of the branch was compared byte-for-byte to the package for all 27 files: **0 mismatches**.

The full GNOME unit suite executed in the fresh checkout:

```text
Ran 110 tests in 3.203s
OK (skipped=9)
```

Five cross-runtime tests were skipped because Node was unavailable in the Linux integration sandbox. Four formal JSON Schema tests were skipped because `jsonschema` was unavailable there. The standalone package was separately tested in an environment with Node and `jsonschema`: 26 tests OK, one skipped because the real source identity index wasn't present inside the standalone archive; JavaScript files passed `node --check`.

The existing strict manuscript validator, 14/77/91/315 lineage reconciliation, and editorial lineage audit passed. Root `index.html` SHA-256 remained `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`.

## Temporary HTTPS browser smoke test

A browser opened the actual feature-branch copy at `/workbench/reactor/index.html` hosted by an isolated HTTPS test sandbox.

Observed:

- Interface rendered with six navigable modes and without visible error banners.
- Source-bound method selector displayed **91** identities from the actual index rather than five hardcoded entries.
- Every identity was marked `UNVERIFIED_SOURCE_CANDIDATE`; the source panel indicated **0/91 verified**.
- Experiment Designer mode opened and exposed the hypothesis, model identifier, and `Freeze Prompt Hashes` controls, without claiming model results.
- Synthetic onboarding demonstration was visibly labeled as a demonstration.
- The browser inspection showed some titles inherited from the existing candidate-only identity index with truncation or unusual title fragments. These should not be confused with independently verified headings.

**Not tested:** actual model execution, end-to-end observation import or capsule export/import in this hosted session, browser developer console logs, mobile viewport resizing, keyboard-only navigation, and cross-browser accessibility. The browser agent did not establish that all modes are functionally complete.

## Merge recommendation

Keep PR #25 in **draft** until the full repository's Node and `jsonschema` cross-runtime checks and a genuine browser capsule export/import/replay round trip pass. This is an experimental integrity-hardening candidate, **not** certification of experimental claims or editorial bodies.

Editorial status stays 0/91 verified canonical bodies; 629 human review decisions remain pending.
