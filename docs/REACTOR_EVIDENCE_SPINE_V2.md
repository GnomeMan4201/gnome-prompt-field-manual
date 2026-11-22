# GNOME Evidence Spine — Phase VIII-B reference-bound evaluator

**Status: implementation candidate.** This is a meaningful additional evaluation path, not a claim of verified scientific ground truth or independently reproduced model results.

## What the new path actually does

The existing Phase VIII-A control/variant engine and Phase VIII-B Chamber preview remain available. The new **Evidence Spine** implements two explicit trust boundaries:

1. **Untrusted raw observations** cannot dictate evaluation outcomes. It refuses any imported `passed`, `evaluation`, or `disposition` field. Every score is recalculated from the actual `outputText` and the pinned rubric and reference.
2. **Reviewer-provided exact references** supply an explicit scoring anchor but are **not independently authenticated**. For example, a reference claiming the answer is `42` remains an analyst assertion until independently substantiated. Source SHA-256 anchors a declared source identifier but does not prove body text was correctly extracted, and a capsule checksum is not an external signature.

The evaluator supports deliberately narrow **flat, primitive-valued JSON-object** response contracts. Duplicate output keys, nested output values, unsafe integers and malformed JSON fail closed in both Python and JavaScript. It avoids unrestricted regex, semantic substring matching masquerading as ground truth, or treating a language-model judge as authority. Its deterministic check requires the declared keys and detects forbidden strings; the reference-grounded check compares **typed values** to a complete expected JSON object. **Both checks must agree** on `PASS/SUPPORTED` or `FAIL/CONTRADICTED` before the existing strict Phase VIII-A classifier is invoked. Disagreement, incomplete observations, altered hashes, unknown model settings, and unsupported output formats fail closed.

**This is not causal inference.** `VARIANT_INDUCED_FAILURE` means one observed paired output passed these specific checks and the other failed under matching declared conditions; experimental conclusions still require controls, actual model provenance and substantive evaluation review.

## Files and routes

- `workbench/reactor/evidence-lab.html` — accessible offline browser lab, explicit synthetic first-run example, JSON plan and observation import, recalculate, capsule export, capsule reimport and verification.
- `workbench/reactor/evidence-v2.js` — browser evaluator, checksums, deterministic replay.
- `workbench/reactor/evidence-lab.js` — interface logic; no network backend or remote model connections.
- `tools/reactor_evidence_v2.py` — Python evaluator, v2 capsule verifier and CLI.
- `tools/reactor_pair_runner.py` — **opt-in** paired test runner with the existing numeric-loopback-only Ollama client; no automatic network calls, no model-generated code execution, no judge, no fabricated results.
- `schemas/reactor-evaluation-plan-v2.schema.json` and `schemas/reactor-evidence-v2.schema.json` — v2 contracts; no v1 schema overwritten.
- `tests/test_reactor_evidence_v2.py`, `tests/test_reactor_evidence_v2_schema.py`, `tests/test_reactor_pair_runner.py` — cross-runtime, model mock, adversarial and formal-schema tests.
- `qa/run_evidence_browser.py` — optional desktop/mobile Playwright acceptance script, requires Chromium and network permission to serve localhost. Not imported by default unit-test discovery.

## Local reproducibility

```bash
# From the project repository root, with Python 3.12+, Node 22, jsonschema:
python3 -m unittest discover -s tests -v
for f in workbench/reactor/*.js; do node --check "$f"; done

# Start a local static web server for browser use (no evaluation backend):
python3 -m http.server 8000
# Open http://127.0.0.1:8000/workbench/reactor/evidence-lab.html

# Analyze reviewer-provided input (does NOT call any model):
python3 tools/reactor_evidence_v2.py analyze --plan my-plan.json --observations my-observations.json
python3 tools/reactor_evidence_v2.py build --plan my-plan.json --observations my-observations.json --out my-v2-capsule.json
python3 tools/reactor_evidence_v2.py verify my-v2-capsule.json

# OPTIONAL local execution against an Ollama endpoint you operate:
python3 tools/reactor_pair_runner.py --plan my-plan.json \
  --endpoint http://127.0.0.1:11434 --trial-id trial-001 --out local-run.json
# Import the local-run.json *observations* array into the Evidence Spine.
# This is raw data; NOT automatically scored as correct.
```

### Plan data contract

`gnome.reactor.evaluation-plan.v1` includes a plan ID, experiment/dataset ID, model/provider/evaluator configuration, temperature, nullable seed, empty tools list, source reference with `entryId`/`sourceSha256`/`bodyStatus`, distinct control/variant prompts, `requiredFields`, `forbiddenTokens`, and per-input text with exact `reference.expectedJson` and `reference.evidenceRefs`.

`gnome.reactor.evidence.v2` contains source-bound plan, raw observations, recomputed analysis, a synthetic-demo flag, and SHA-256 checksums of the plan, observations, analysis and manifest. Python and JavaScript verify the checksums and independently recompute the analysis before accepting the capsule. A forged analysis cannot be accepted just by updating its checksum.

### Limitations that remain open

- References and `evidenceRefs` are **not** independently verified or signed. A malicious author can rewrite the reference, all observations and every checksum to produce a self-consistent but dishonest capsule. External independent evidence, authentication and signatures are required for stronger claims.
- The local Ollama adapter reports requested options but cannot guarantee the model implementation actually used them. It intentionally marks actual parameter application and model digest **not independently verified**. The browser cannot and does not invoke a model endpoint.
- The v2 evaluator is deliberately limited to exact structured JSON outcomes and a small deterministic rubric. It cannot ground arbitrary natural-language claims or establish genuine scorer independence.
- Browser-native file selection, screen readers, full WCAG audit and all cross-browser behavior require additional end-to-end testing. The optional Playwright runner covers a bounded subset.
- JSON canonicalization is implemented for the restricted schema types, not general RFC 8785, and must not be represented as globally interoperable for arbitrary floating-point values.
- This phase does not resolve any of GNOME's **629 editorial decisions** or certify any of the **91 canonical bodies**.

## Security/false-success acceptance examples

- Already-failing baseline and failing variant → `SHARED_FAILURE`, **not attack-induced**.
- Different input hashes or seed values → rejected before scoring.
- Missing second trial → `UNATTRIBUTABLE`, proportion `null`.
- Model text instructing an evaluator to give itself a pass → text remains data; unexpected JSON keys are not scored as verified success.
- Control pass and variant fail on an explicitly referenced field under matched conditions → `VARIANT_INDUCED_FAILURE` **within the narrow declared rubric only**.
- Tampering with output without changing checksums → rejected. Rehashing a forged analysis without recomputing it → rejected by replay mismatch.

All included example responses are synthetic, do not constitute model measurements, and cannot claim empirical validation.
