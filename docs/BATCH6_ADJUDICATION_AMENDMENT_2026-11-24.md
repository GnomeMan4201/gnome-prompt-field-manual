# Batch 6 final adjudication amendment

This amendment applies to the active SEC-02 and SEC-05 briefs in the manuscript at PR #39 merge commit `0615d10bcc446796d8f97603f72594c18d9fd26f` (verified PR head `30b2e7598a617d2f29ac0484e1a5ffabbbe48391`). Both briefs remain byte-identical to that merge. The [archived PR #39 evidence](BATCH6_PR39_EVIDENCE_2026-11-24.md) records the prior correction and both original HOLD verdicts.

For SEC-02, the brief's statement “if they do, an injection has occurred” is superseded by this interpretation for the corrected manuscript. A canary match is an observation. Determine the match class, evidence quality, provenance, authorizations, competing explanations, and policy response. Treat a verified crossing of the authorized boundary as potential disclosure. Attribute injection only when independent, trustworthy evidence connects untrusted input to a policy-violating change. Escalation or quarantine can be appropriate before attribution is established. This amendment retains the canary format, placement, rotation, measurement, and fallback requirements.

## SEC-02 — PASS on manuscript review

| Requirement | Evidence | Result |
| --- | --- | --- |
| Remove unsupported causation across the entry | Pages 154 and 156 describe review signals, and page 158 separates canary investigation from corroborated injection evidence. Pages 154–162 were reviewed. | Met |
| Distinguish match classes | Page 156 specifies complete issued value, a defined fragment, and format resemblance without a value match. | Met |
| Distinguish potential disclosure from corroborated injection | Page 156 requires authorization, audience, and provenance checks for disclosure and independent evidence of the input-to-behavior link for injection attribution. | Met |
| Require uncertainty and alternatives per observation | Page 156 requires evidence class, confidence limitations, alternative explanations and policy response with an owner. It names legitimate reproduction, accidental collisions, contaminated logs and authorized testing. | Met |
| Test triage without inferring causation | Page 158 requires synthetic output tests for all three match classes, including an authorized exact match, and checks the class and policy response. Manuscript tests reject reinstated causal wording and missing corroboration. | Met |
| Preserve prior briefing and correction requirements | Both briefs remain frozen, with this explicit interpretation. The PR #39 contracts for alert thresholds, fallback, eight output sections and cross-references still pass on current source. | Met |

PASS applies to the corrected editorial contract. It confers no independently verified canonical-body status and does not establish operational firewall effectiveness.

## SEC-05 — INSUFFICIENT EVIDENCE for disposition

The frozen mandatory artifact calls for “Test suite: at minimum, normal-input passing test, delimiter-escape attempt that should fail, injection attempt that should be blocked. The test suite must be copy-paste executable.” The phrase “injection attempt that should be blocked” is the unresolved criterion. EDT-06 remains a category-only description, with no payload or executable fixture. The reference fixture below demonstrates an authorization decision for a synthetic operation. It supplies no evidence that an injection attempt through a refactored separator was recognized or blocked. The frozen requirement remains in force.

| Requirement | Evidence | Result |
| --- | --- | --- |
| Retain the benign and delimiter structural test contract | Pages 182 and 184 and EDT-00 through EDT-05 remain byte-identical to PR #39. The existing tests verify the manuscript contract. | Met at manuscript level |
| Preserve the EDT-06 payload-free boundary | Pages 182–184 remain byte-identical, including the cross-page description. The reference fixture contains only ordinary synthetic caller and operation values. | Met |
| Exercise a real reference authorization boundary | `CounterBoundary.execute` checks authorization before it can increment an in-memory counter. The harness supplies caller identity separately from the requested operation. | Met for the reference fixture |
| Demonstrate denial with no side effect and a successful benign control | The observer's request was denied, with the counter staying at 0. The operator's request was allowed, with the counter advancing from 0 to 1. | Met for the reference fixture |
| Reject disabled enforcement, reject-all and missing controls | Executed negative tests reject all three mutations of the observed controls. | Met for the reference fixture |
| Demonstrate the mandatory injection-attempt blocking outcome in the refactored mechanism | No deployment separator, model, injected input, or deployment integration runs in this fixture. An ordinary unauthorized call cannot satisfy the frozen injection-attempt criterion. | Insufficient evidence |
| Bound interpretation | No network calls, external targets, sensitive data, LLMs, or real injection payloads are involved. The reference fixture establishes its own authorization boundary behavior only. | Met |

Run the offline reference with `python examples/batch6_runtime_policy.py`. It emits the observed outcomes as JSON and fails if either decision or state transition differs from the expected pair.

## Source binding and preservation

Only physical pages **154, 156, and 158** changed relative to PR #39. All four manuscript representations agree. The other 312 canonical cards, standalone rows, standalone fallback cards, and canonical bytes outside page cards are byte-identical. The latter includes both active briefs and the historical PDF. Prior historical documents, adjudication data and research artifacts match the pinned Git tree.

| Artifact | SHA-256 |
| --- | --- |
| PR #39 canonical HTML | `1562471af6710a1a4c46e7409131abf7e55d2953262e88f652a2fb0167b73061` |
| PR #39 standalone HTML | `4031039aed49199b8e2ead651bd3a0ae589a9a88530f31ef293791b8bcea21ae` |
| Archived PR #39 evidence | `f16126becf6c44c1ac30dff2da70227295b62b99558742c9db3414a0e01e3c0c` |
| Corrected canonical HTML | `25fff84e54dd4db8d4131f65fdebcc5941b1c90738f4ebef82d4612a705b3c44` |
| Corrected standalone HTML | `bb904821afdf41f003ba8bbd3b94d4d62cac28ce69531909198902946584d67e` |
| Corrected current identity index | `691d95da7e2793946ae7a1d566d9424e9af6fe2e795ea25768de4972bbf1db36` |
| Historical embedded v9 PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |
| 312 unchanged canonical cards, ascending and NUL-separated | `757e69f87ce9536535c581680da695f77134a950746202870a49f025bc7584c9` |

The correction preserves 10 pending, 81 non-pending, 91 total, 315 pages, five remaining batches, and 0/91 independently verified canonical bodies. There is no disposition change.
