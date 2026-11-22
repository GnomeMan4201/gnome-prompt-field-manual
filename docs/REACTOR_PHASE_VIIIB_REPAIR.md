# Phase VIII-B additive repair — review candidate

## Scope and compatibility

This changes **none** of the Phase VIII-A files: `index.html`, `app.js`, `experiment-core.js`, `comparison-engine.js`, `source-adapter.js`, `replay-engine.js`, `evidence-capsule.js` and `tools/reactor_engine.py` remain exactly as merged. It adds a **separate** `workbench/reactor/chamber.html` route, alongside the existing Reactor. Canonical GNOME manual and all editorial-review records remain untouched.

The Gemini-supplied Phase VIII-B archive was **not** installed wholesale because it restored a noncryptographic hash fallback, five hardcoded source identities, trial-overwriting replay, and an attribution function that trusted `comparable: true` by default.

## Meaningful implemented capability

- Offline Chamber analysis: Paste a JSON array of control/variant pairs into `/workbench/reactor/chamber.html`; inspect full classification counts and per-trial rejection reasons. A synthetic invalid-pair example is explicitly labeled **not empirical evidence**. No model responses are generated in the browser.
- Cross-runtime strict attribution: Python (`tools/reactor_chamber.py`) and JavaScript (`workbench/reactor/attribution-engine.js`) use Phase VIII-A's strict matching requirements. The caller's `comparable` flag and `controlDisposition` or `variantDisposition` strings are ignored.
- **Scoring contract (limited):** A result must carry two agreeing *supplied evaluator assertions*: deterministic `PASS` plus grounded `SUPPORTED` for a pass, or deterministic `FAIL` plus grounded `CONTRADICTED` for a failure. Missing or disputed results remain `UNATTRIBUTABLE`. This checks consistency **only**, not scorer independence or whether the reference evidence is truthful. An optional judge status never substitutes for the required assertions.
- Threat-model validation rejects absent records and missing/empty required fields; deterministic scoring returns `UNKNOWN` with no active rules.
- Opt-in local Ollama runner: a separate CLI that accepts only literal `http://127.0.0.1:PORT` or `http://[::1]:PORT` endpoints; it uses no proxies, does not follow redirects, caps request/response bytes, and does not execute model-generated text. Its CLI requires an explicit prompt file and model. Cancellation can be requested before/after IO via an embedded callback but **cannot interrupt** a blocked socket read.
- Existing Phase VIII-A manifest checksums, trial IDs, capsule format and 91-entry source adapter are preserved by not touching those files.

## Quick test and example

```sh
python3 -m unittest discover -s tests -q
for file in workbench/reactor/*.js; do node --check "$file"; done
python3 tools/reactor_local_runner.py --endpoint http://127.0.0.1:11434 --model llama3.1 --prompt-file ./my-prompt.txt --trial-id TRIAL-001
```

The local runner only attempts a connection when the user invokes the command. Do not run it against endpoints you do not control. The runner returns raw model response text and metadata; it does not automatically build a complete experiment, judge answers, or certify outcomes.

## Mandatory future gates before calling VIII-B finished

1. Authenticate and validate evaluator execution records against pinned rubrics and externally anchored trusted references; currently the scoring assertions in imported pairs are **not independently verified**.
2. Integrate Chamber experiment records into a new **versioned** capsule schema and verify full export/import across Python and JS; Phase VIII-A's capsule format has intentionally not been modified here.
3. Provide a complete threat-model/variant lifecycle and audited mutational diffs, rather than the present narrowly scoped modules.
4. Complete an opt-in UI-to-local-runner interaction through a separately secured local companion; the static browser currently only supports offline Chamber analysis.
5. Run complete repository CI with Node and JSON Schema installed, with zero skips, and run browser/keyboard/mobile tests against the full repository.
6. Test real evaluator-injection isolation with an **actual evaluator** under a bounded, approved, local model environment. The tests here only show that a judge's asserted score cannot promote a Chamber classification.

This is a **security regression repair candidate and additive first slice of VIII-B**, not a full independent evaluation engine or a claim of causality.
