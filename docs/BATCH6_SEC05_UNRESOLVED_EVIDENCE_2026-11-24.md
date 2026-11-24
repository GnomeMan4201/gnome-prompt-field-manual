# SEC-05 unresolved evidence — Batch 6

**Disposition: INSUFFICIENT EVIDENCE.** SEC-05 remains pending in Batch 6. Its evidence review is separate from the Batch 7 manuscript reconciliation.

The active SEC-05 brief is byte-identical to `div#b-sec05` in the PR #40 merge `cc155b1190c968a8fe5c8f5448f49ea50742feff`. The source `index.html` SHA-256 is `25fff84e54dd4db8d4131f65fdebcc5941b1c90738f4ebef82d4612a705b3c44` and the brief fragment SHA-256 is `a56431111256a6f952f0aebdaaa6f50ef882838877377d497bfa01e0e4189123`. Current [active brief](../index.html#b-sec05) and [PR #40 adjudication amendment](BATCH6_ADJUDICATION_AMENDMENT_2026-11-24.md).

## Frozen mandatory artifact

> Two outputs: (1) Refactored code/prompt with annotations at each separation point explaining the change. (2) Test suite: at minimum, normal-input passing test, delimiter-escape attempt that should fail, injection attempt that should be blocked. The test suite must be copy-paste executable.

| Evidence layer | Established | Limit |
| --- | --- | --- |
| Manuscript and structural-test contract | Pages 182 and 184 require executable EDT-00–05 against the actual supplied mechanism, with a benign positive control, delimiter and boundary assertions, and explicit reporting of missing prerequisites. Regression tests verify the contract, four-surface parity and the payload-free EDT-06 description. | There is no deployment separator or executable outcome for a deployment supplied by these pages. |
| Runtime authorization | PR #40 recorded the offline [reference fixture](../examples/batch6_runtime_policy.py), SHA-256 `b191ad83af6915e31e2e791df9a4bafb5dabe07f8614365b3b5d5609adb611cc`. The unauthorized synthetic increment was denied with no state change. The authorized increment succeeded. Disabled enforcement, reject-all, and missing positive-control variants failed verification. | This evidence is accepted for the fixture’s authorization boundary. It establishes neither a separator’s behavior nor injection resistance. |
| Independent behavioral evidence | The mandatory injection-attempt blocking outcome remains unobserved for an actual refactored mechanism. | An ordinary unauthorized call and an EDT-06 category description cannot establish that outcome. |

## Closure criteria

Independent behavioral evaluation must identify the exact refactored artifact and execution environment, the authorization and scope of the evaluation, the declared outcome and acceptance criteria, and the actual observed results. The evidence must connect the blocked outcome to an in-scope injection attempt through that mechanism, show that the relevant control caused the denial, and include an observed authorized benign control. Preserve replayable, executable evidence in the authorized review environment, with reviewer disposition and enough provenance to assess uncertainty, runtime enforcement, and confounding explanations. Insufficient or inconclusive evidence leaves SEC-05 pending.

Keep EDT-06 category-only and payload-free. A public disposition may cite evidence provenance and bounded findings without publishing sensitive inputs or details. Any subsequent evaluation needs independent review and authorization for its scope. A passing result would apply to the evaluated artifact and conditions. It could not establish general LLM injection resistance.
