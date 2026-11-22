# Reactor Phase VIII-A — Browser-to-Python evidence acceptance

**Date:** November 22, 2026. **Target:** PR #25, branch `feature/reactor-viiia-integrity-hardening`. This report records tests of the unmodified Reactor code together with **temporary QA-only controls and a capsule-capture endpoint in an isolated sandbox**. The temporary controls, synthetic QA observations, and capture endpoint were never committed.

## Independent runtime verification

The Reactor package ran in a local environment with Node 22 and `jsonschema` available:

```text
python3 -m unittest discover -s tests -v
Ran 26 tests
OK (skipped=1)
```

The one skipped test expects the real GitHub 91-identity index, which is absent from the standalone ZIP. No test skipped for lack of Node or `jsonschema` in this run. All Reactor JavaScript files passed `node --check`.

The earlier fresh repository integration ran 110 tests with 9 skips because Node and `jsonschema` were missing in that sandbox. This is **not** the same as a fully unskipped integrated suite; the dedicated `Reactor Integrity` GitHub Actions workflow is intended to establish that evidence on the actual repository.

## Live browser source and experiment workflow

The PR branch was cloned into an isolated server and hosted over HTTPS. Browser automation observed:

- The **actual source index loaded 91 candidate identities**, marked `UNVERIFIED_SOURCE_CANDIDATE` and 0/91 verified.
- Experiment mode froze hashes for the control and variant prompts successfully.
- Execution mode imported two QA observations through the **normal observation import handler**. The QA-only button merely filled the text area with the temporary fixture; the normal Import Observation Records button performed validation.
- Analysis classified the pair as `UNATTRIBUTABLE: 1`, and `VARIANT_INDUCED_FAILURE: 0`, with `COMPARABLE_WITH_DISCLOSED_LIMITATIONS`. The fixture has explicitly null temperature metadata, so attribution was appropriately withheld despite different imported pass/fail flags.
- Capsule mode exported the browser-generated JSON without visible error.

**The QA observations are synthetic test assertions, not real model execution or scientific findings.** The choice to classify them as UNATTRIBUTABLE arises from the metadata conditions; offline importing alone is not itself a criterion in the classifier.

## Exact exported capsule → Python verifier

A temporary QA-only capture route received the **same Blob** created by the browser's normal Export Evidence Capsule action. It did not create a replacement capsule.

- Byte length: **4,525**.
- SHA-256 of exact JSON export: `60880e5014db50caaa9de7ff0c7a1b8ddec8d10dc7efd34adf4349e547094ab8`.
- Python invocation: `python3 tools/verify_reactor_capsule.py qa/captured.json`.
- Result: `valid=true`, `errors=[]`, `COMPUTATIONAL_REPLAY_ONLY`, 1 input pair, `UNATTRIBUTABLE=1`, no induced failures; exit 0.

An observation in the captured JSON was modified without updating its checksum. The Python validator returned:

```text
valid: false
errors: ["CHECKSUM_MISMATCH:runs/observations.json"]
replay: null
exit status: 2
```

## Exact exported capsule → browser import and replay

A temporary QA-only button loaded the exact captured JSON bytes into a browser File and dispatched a change event on the **existing** capsule file-input control. The normal capsule import/replay handler then reported:

```text
valid=true
errors=[]
replay.classifications.UNATTRIBUTABLE=1
```

A second QA-only control imported the checksum-tampered file. The ordinary import/replay handler reported:

```text
Capsule rejected: CHECKSUM_MISMATCH:runs/observations.json
valid=false
replay=null
```

**Limit:** OS-native manual file-picker interaction was not tested. The test did exercise the actual browser File input event and normal import function.

## Remaining release gates

- CI run using the complete repository with Node and `jsonschema`, proving **zero skipped tests**. The new `.github/workflows/reactor-integrity.yml` fails on any test skip; its CI result must be observed before merge.
- Visual accessibility review at 390px; browser keyboard Tab/Enter/Space testing and WCAG checks.
- Formal source-title adjudication: candidate headings such as truncated titles are not canonical publication headings.
- Actual model-run evidence and trusted evaluator scoring remain outside this QA scope.
- Reviewer attribution/authenticity, trusted signing, independent replication and robust cross-language JSON canonicalization remain separately unresolved.

**Editorial baseline:** 629 pending human adjudications; 0/91 independently verified manual bodies. No editorial records or canonical manual content were changed by these tests.

**Recommendation:** Keep PR #25 draft until its new CI gate succeeds; don't represent its QA flags as empirical LLM behavior.
