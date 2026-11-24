# Batch 7 adjudication — SEC-06 Tool-Agent Offense Probe

**Verdict: PASS at manuscript-contract level on the corrected source.** The report specifies an authorized defensive evaluation. The evidence in this PR verifies the manuscript contract, reader integrity, and lineage. Operational agent behavior and the effectiveness of a sandbox, monitor, or gate remain unverified. The illustrated control pair is planned only. This is a correction PR, with disposition reserved for a separate change.

## Source and identity

PR #41 merged at `c93608da305eb70e231613403edb8a275d7e1bbe`. Its tree matches approved head `7db2dfa760769f11b79e8b22d60eb6449e8d284b`. The complete frozen brief is `div#b-sec06` in that tree's [index.html](https://github.com/GnomeMan4201/gnome-prompt-field-manual/blob/c93608da305eb70e231613403edb8a275d7e1bbe/index.html). The live fragment is byte-identical to the frozen fragment.

The heading **SEC-06 Tool-Agent Offense Probe** starts on page 187 after SEC-05's residual-risk and AP-13 follow-up text. The entry continues through the last paragraph of Safety Notes on page 197. The next heading, **SEC-07 Human Confirmation Gate Designer**, starts on page 198. Criteria 2, 7, and 9 and the agent tool-permission subject agree with the brief. The shared SEC-05 prefix on page 187 remains byte-identical in the canonical text and standalone fallback.

The correction changes the 11 physical pages **187–197**. Page 187 introduces the bounded evaluation and page 188 defines the prompt's written authorization gate. Pages 189–192 align the inventory, controls, categories, and verdict logic. Pages 193–194 align the artifact count, planned example, and failure modes. Pages 195–196 clarify the cited entry roles and review handoff. Page 197 consolidates the containment and safety requirements. The other 304 cards and all manuscript content outside those cards remain byte-identical.

### Cross-reference verification

| Reference | Canonical heading page | SEC-06 use |
| --- | --- | --- |
| S-01 System Map with Trust Boundaries | 107 | Map the crossing, principal and runtime control before evaluation |
| S-03 Failure Mode Inventory | 117 | Prioritize and hand back evidence, severity, detectability and open gaps |
| S-06 Observability Gap Finder | 127 | Investigate stale, missing or untrustworthy telemetry |
| SEC-01 Prompt Injection Recognizer | 145 | Classify the input surface before evaluation |
| SEC-02 Prompt Firewall Designer | 154 | Route evidenced input or output boundary gaps to system-level control design |
| SEC-05 Command/Data Separator (Refactor) | 179 | Route structural boundary issues, with runtime and model claims evaluated separately |
| SEC-07 Human Confirmation Gate Designer | 198 | Require an enforced gate covering the affected action path for every HIGH finding |
| SEC-09 Indirect Injection Tracer | 203 | Review the data path where evidence points to a tool-output crossing |
| CH-09 Agent Build-Break-Harden Chain | 270, with SEC-06 cited in Step 5 on 271 | Apply the written-scope and payload-free limits to that step |

## Requirements and evidence

| Requirement | Merged PR #41 source | Corrected source | Evidence |
| --- | --- | --- | --- |
| Stable SEC-06 identity, criteria 2/7/9, Batch 7 alone | SATISFIED | SATISFIED | Heading and criteria on 187, unchanged brief and singleton schedule row |
| Vulnerability report with explicit required artifact | PARTIAL | SATISFIED | Page 193 specifies four named parts. The original output claimed eight fields while listing seven. |
| Separate authorization scope, explicit in the prompt | PARTIAL | SATISFIED | Page 188 requires written owner, evaluator, environment, permissions, exclusions, limits, and stop owner. Missing prerequisites leave probes NOT RUN. |
| Attack surface inventory of all tool-agent crossings | PARTIAL | SATISFIED | Page 189 requires source, receiver, principal, tool/resource, permissions, side effects, confirmation and enforcement points, and evidence. |
| Vector description and type, exploitation conditions, chaining potential | PARTIAL | SATISFIED | Page 189 fields 2–4 capture observable failure, severity, affected downstream boundary, and defensive preconditions without operational attack procedures. |
| Detection signal and specific control for every vector | PARTIAL | SATISFIED | Pages 190 and 193 require a measurable observation, enforcement point, owner, and evidence provenance. |
| All ten coverage categories, including data exfiltration via side channel | SATISFIED | SATISFIED | Pages 190–191 preserve ten categories. Category 7 specifies defensive coverage of observer-visible surfaces using synthetic labels. |
| Separation of untrusted data and authorized instructions | PARTIAL | SATISFIED | Pages 187, 189–191 distinguish data, verified authority, and application enforcement. |
| Criterion 2, convert a failure into a test | PARTIAL | SATISFIED | Pages 189–192 pair benign and negative controls, declared expectations, actual outcomes, and before/after state. Page 194 gives a planned-only example and rejects reject-all. |
| Criterion 7, expose the trust boundary | PARTIAL | SATISFIED | Pages 189 and 195 tie every observation to a principal, crossing, runtime control and evidence source. |
| Criterion 9, ship safer | PARTIAL | SATISFIED | Pages 190, 192 and 196 require mitigation owners, reviewed gate coverage, a retest, and bounded readiness and coverage reporting. |
| Preserve SEC-01 prior, S-03 handoff, SEC-07 for every HIGH finding | PARTIAL | SATISFIED | Pages 195–196 state the ordering, evidence handoff and gate requirement. Missing gate coverage keeps the finding open. |
| Most extensive Safety Notes in Part V, including scope, unauthorized use, detection/mitigation only, human review before remediation | PARTIAL | SATISFIED | Page 197 covers all four demands and is longer by word count than each other Part V Safety Notes section. |
| Isolation, side-effect containment, escalation and stop conditions | PARTIAL | SATISFIED | Pages 188, 191 and 197 require inert resources, no external dispatch, fail-closed scope checks, an empowered stop owner, and evidence-based restart. |
| Expected versus observed outcomes, evidence provenance, false positives and negatives | PARTIAL | SATISFIED | Pages 189–192 separate fields and verdict handling. Page 197 requires both telemetry and state checks and discloses measurement limits. |
| Distinguish plan, simulation, detection, prevention, and observed runtime evidence | CONTRADICTORY | SATISFIED | Pages 190 and 192 separate evidence levels and remove the general hardened rating. A PASS requires an eligible scoped run and passing controls. |
| Independent runtime measurements and confirmed behavior of a specific deployment | UNVERIFIABLE | UNVERIFIABLE | No authorized target snapshot, scope approval, versioned runtime evidence, observed control outcomes, or independent behavioral review was supplied. Editorial tests and the planned example provide no runtime verdict. |

## Preservation evidence

| Binding | SHA-256 |
| --- | --- |
| Merged PR #41 `index.html` | `8735ebe991b4428fe9a210649d699365f449f2efc87450397df6fec039b0e97a` |
| Merged PR #41 standalone reader | `bb904821afdf41f003ba8bbd3b94d4d62cac28ce69531909198902946584d67e` |
| Frozen SEC-06 brief fragment | `1ca82b79a78a07235b4b6a39fe296513eb1d138a0915bca96f87675bc17d75e2` |
| Corrected `index.html` | `8ba47c93f4561c0daffa6bfce5d16401cded9f34a887bd8f300bcea38612e084` |
| Corrected standalone reader | `1b2a203eb8e252b6e8539fca78e82317e083a731ac08fdbc4d4e352ce66b259b` |
| Corrected current identity index | `6db3a2ed863ad302a32cfc931744bc3897b20da820e995d54977a1a44c202fe8` |
| Unchanged 304 page cards, physical order, NUL-separated | `f1c0e01dcf3f4384e9b4cb7121309084e9304b40f6f248272587c95b88a5b0dc` |
| Historical v9 PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |

The exporter reproduces the current index from the actual canonical bytes. All semantic IDs, pending statuses, occurrence pages and unresolved body statuses are preserved. The CH-09 and SEC-07 advisory title strings reflect the corrected cross-reference wrapping, with the original unverified authority classification. Historical hashes and old disposition assertions remain pinned to their original Git trees.

The correction inventory remains **9 pending, 82 non-pending, 91 semantic identifiers, 315 pages, five nonempty batches, and 0/91 independently verified canonical bodies**. SEC-05 remains independently pending under its unchanged evidence record.
