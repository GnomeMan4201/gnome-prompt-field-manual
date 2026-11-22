# Phase VIII-B additive Chamber — browser smoke-test evidence

**Date:** November 22, 2026. **Branch:** `feature/phase8b-additive-integrity-repair` (draft PR #27).

A temporary HTTPS server hosted an exact fresh clone of this branch; the test-only browser automation clicked existing unmodified controls on `/workbench/reactor/chamber.html`.

## Executed

1. Chamber route loaded with heading `Adversarial Evaluation Chamber`.
2. Clicked `Load synthetic invalid-pair demonstration`. UI explicitly labeled the data `SYNTHETIC DEMONSTRATION — NOT EMPIRICAL EVIDENCE`.
3. Clicked `Inspect attribution`. UI displayed:

```json
{
  "counts": {
    "validPairedTrials": 0,
    "variantInducedFailures": 0,
    "unattributableCount": 1
  },
  "observedVariantInducedFailureProportion": null,
  "outcomes": [{
    "trialId": "QA-1",
    "attribution": "UNATTRIBUTABLE",
    "reason": "INSUFFICIENT_INDEPENDENT_SCORING"
  }]
}
```

The fixture deliberately set a caller-supplied `comparable: true` but did not include the required metadata and independent scoring assertions. The Chamber did not accept the supplied comparison claim as evidence. No visible errors were reported.

## Other observed evidence

- A fresh GitHub clone of PR branch contains **19 repair-package files byte-for-byte identical** to the locally tested package.
- Integrated GNOME Python suite: **127 tests run, 117 pass, 10 skip**, because Node and formal JSON Schema dependencies were absent from that isolated sandbox.
- Separate local hardening package: **43 tests run, 42 pass, 1 skip** because the canonical GitHub identity index was not included in the standalone package.
- Canonical `index.html` SHA-256 still `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`. Manuscript structural, reconciliation, and editorial lineage checks passed.

## Standalone full-dependency validation

With the actual 91-entry identity index copied from the original repository into the local repair-package test directory, Node 22 and `jsonschema` installed, the complete standalone repair suite reported **43 tests, OK, zero skipped**. This is separate from the **127-test integrated repository run**, which had 10 environment-dependent skips. GitHub Actions success remains unconfirmed.

## Not established

This smoke test does **not** establish the validity of real model-derived scores, true scorer independence, prompt-injection resistance of an actual connected evaluator, local Ollama integration in the browser, full adversarial attack generation, native file import, new VIII-B evidence capsules, mobile or keyboard accessibility, or full zero-skip GitHub Actions CI.

The existing Phase VIII-A Reactor implementation and editorial records are untouched. Keep the PR **draft** until the zero-skip CI and deeper evaluation claims are reviewed.
