## Scope

Source-bound correction for pages **133, 157, 158, 159, 161, 182, and 184**. Preflight found open PRs #16 and #17, on separate branches. Base verified against remote `main` at `5061755c9fbaf88c5ea9a07e406de7366798940f`. Inventory remains **10 pending, 81 non-pending, 91 total, 315 pages, 5 remaining batches, and 0/91 independently verified canonical bodies**.

## Before and after

| Page | Before | After |
| --- | --- | --- |
| 133 | “SCHEMA/CONTRACT DEPENDENCY” | “SCHEMA/CONTRACT, DEPENDENCY” in the eight-dimension enumeration |
| 157 | “List observable output signals” | “For each alert, specify all eight fields”, followed by measurement, decision, and baseline requirements |
| 158 | “Specify what the system returns when the firewall blocks or quarantines a response” | “Continue only explicitly approved low-risk functions that do not depend on the unavailable control” and explicit block, hold, escalation, timeout, and recovery rules |
| 159 | “seven structured sections” | “eight structured sections”, with “7. FALLBACK BEHAVIOR” |
| 161 | SEC-09 and SEC-10 absent from FOLLOW-UP | “SEC-10 (Trust Boundary Mapper (Security), page 205)” before finalizing the architecture and “SEC-09 (Indirect Injection Tracer, page 203)” after design |
| 182 | Cases started at EDT-01 and called for test descriptions | “Provide executable structural tests for EDT-00 through EDT-05 against the actual refactored separation mechanism.” EDT-00 must accept benign input and preserve its expected result. EDT-06 remains category-only. |
| 184 | “six typed test cases with pass/fail conditions” | “seven cases, EDT-00 through EDT-06”, with executable structural tests for EDT-00 through EDT-05 |

## Requirement coverage

| Requirement | Evidence |
| --- | --- |
| Eight distinct risks | Page 133 exact ordered enumeration, with missing-comma and duplicate-dimension negative cases |
| Measurable behavioral alerts and baseline failure modes | Page 157 covers metric/event, method, threshold/trigger, window, sample size, evidence, response and owner. Each field has a negative case. The page also addresses deterministic policy events, statistical anomalies, unknown thresholds, contamination, drift, telemetry failure, and false positives and negatives. |
| Safe response and complete output | Pages 158–159 cover degradation, quarantine, block, escalation, unavailable telemetry, recovery and tests. A missing FALLBACK BEHAVIOR section fails the contract check. |
| Canonical references | Page 161 uses headings checked on pages 203 and 205. Removing either reference fails the check. |
| Executable test contract and evidence limits | Pages 182 and 184 require EDT-00–05 against the actual mechanism, real imports/setup/assertions/commands/results, and blocked status for missing prerequisites. EDT-00 detects reject-all. EDT-06 stays payload-free. Structural separation, parser correctness, runtime enforcement, model interpretation and empirical behavior are separate claims. |
| Reader synchronization | The seven visible pages, search metadata, standalone search data and static fallback agree. Negative cases mutate each representation independently. Browser smoke exercises discovery, anchors, fit and dynamic/static presentation at desktop, mobile and 200%-equivalent reflow widths. |
| Historical and editorial integrity | Exact physical-page scope, frozen file comparison, PDF digest, independent current digest, reproducible current identity, drift/promotion negative tests, and historical queue binding. |

## Exact changed files

- `.github/workflows/entry-lineage.yml`
- `.github/workflows/reactor-integrity.yml`
- `GNOME-Field-Manual.html`
- `index.html`
- `tests/batch6_baseline.py`
- `tests/browser_smoke.mjs`
- `tests/test_batch4_disposition.py`
- `tests/test_batch5_candidate.py`
- `tests/test_batch5_contract_crosswalk.py`
- `tests/test_batch5_disposition.py`
- `tests/test_batch6_correction.py`
- `workbench/data/current_entry_identity_index.json`
- `workbench/reactor/source-adapter.js`

## SHA-256 and preservation

The canonical bytes outside the page cards, all other 308 canonical cards, and the corresponding standalone rows and fallback cards are byte-identical. The combined SHA-256 of the 308 unchanged canonical cards in ascending page order separated by NUL is `1208be85d86005c5e65f00e588f416f0b95f889337c2db325c8b361fa24ceb40`. The pinned Git baseline supplies immutable comparison bytes. The Reactor workflow checks the current source digest independently and reproduces the identity index with the exporter.

| File or surface | Baseline SHA-256 | Corrected SHA-256 |
| --- | --- | --- |
| `index.html` | `d5c0f82c33ab228166225972d7de0945b819c7d9a424451916fb5c2efca97e7d` | `1562471af6710a1a4c46e7409131abf7e55d2953262e88f652a2fb0167b73061` |
| `GNOME-Field-Manual.html` | `558fec69b1dc5f2ceb3821d7918a1601d017e93b289c97c4f8e6afcb35895fb3` | `4031039aed49199b8e2ead651bd3a0ae589a9a88530f31ef293791b8bcea21ae` |
| Historical embedded v9 PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |
| Current identity index | `844089d49040d7b180761cf21c61691a2c418a9fa3b3eb44693a163dba9e9137` | `c59b36e243e1dc00323458da1475cb39349524c7b5a7762e885747309039bad2` |

| Changed canonical card | Baseline SHA-256 | Corrected SHA-256 |
| --- | --- | --- |
| 133 | `3c676e44e125718871147a2324f7e15a7cf3ba190c3324046206fbfc12c3b09c` | `a205f389b9b1bdc2c5d5a02729e9c115ffccd5f3aee4bbdc1c0383c0c5101884` |
| 157 | `a8f67e369864cb8efb8226b2d6d11d34c07a75800d4cdb77f57bd019b954141c` | `bf3bf9175d3229c39d6d88ddab8f63d7d86d8693b69dd5dc13f201f0d2d3041b` |
| 158 | `b970a67c75bcb4cae13d18e2e532319dd0940fa95f2644f6f4cea8540345f167` | `47485e7861cd1a2ed76713a89e1a0de5c345f81a28e80f1b84410f76a59a1c00` |
| 159 | `25222d47d80846111288156db6111c8835b62e0997c63977172731b4e1748719` | `057cb5997c3c438bbf66c1f9872a692fbb5ac7e120aabc4514ad4394c72b79d2` |
| 161 | `90f4bde9d4a161ba10aebef430a11c6c903c5e199e55cdc6156ac681bb175072` | `5cc73494c89fc4c0a3f4f5c198845e98853ab199bb8942f8d05e430ade7df02b` |
| 182 | `38f8a8e6472b7b0b507413074e19732febe35dc2024e0bdfabb7bf69c157751d` | `83d9cccb8b1742b96d9222bec7c56b163dead3e9ec07d03fd6c47883bd172003` |
| 184 | `5756d1146506d0605d26622c773361f787863f13a2eb8daa0459dfee7d77941d` | `88856f931e288232f453023ff152c7b4143d76f9f28e5095cc0c1fe11f7ccd4e` |

62 historical files matched the pre-edit SHA-256 capture. The historical Batch 5 crosswalk remains bound to the Batch 5 post-state. The frozen adjudication queue and historical identity index remain bound to the Batch 3 source.

<details><summary>Historical batch records, crosswalk, queue and frozen fixtures</summary>

| Historical file | SHA-256 before and after |
| --- | --- |
| `docs/BATCH1_DISPOSITION_2026-08-24.md` | `577fe769b68e71a861574d490ede3469f874bd4f2f0ddea14bc20c5e6117d8bf` |
| `docs/BATCH2_DISPOSITION_2026-08-24.md` | `2e37ef1c42db91e2fc70e9f9d23ac6d37b232b2355a15447a332b6f89f5eb27a` |
| `docs/BATCH3_DISPOSITION_2026-08-24.md` | `c0b908dfb5e48beab81aca4ec7da837b73733447968feb334e1842ef1c3a3cd0` |
| `docs/BATCH4_DISPOSITION_2026-11-23.md` | `cea5654ba6988e600103850671e4a191e49cdaeaabb03f9e17b5d5b9906b2b65` |
| `docs/BATCH5_CORRECTION_CANDIDATE_2026-11-23.md` | `2e508747b53634792492d31bb1cc5cbfbc48754f475cbff822f9a5b97a6fd488` |
| `docs/BATCH5_DISPOSITION_2026-11-23.md` | `0af994f157af666697a4ff989c3635e44d3e4d25b59d15c28a75f51ed959e367` |
| `docs/BATCH5_FOUR_CATEGORY_CONTRACT_2026-11-23.md` | `9f524dacc8ddf2c52cd1aa195681c0130d0f929ed63096eced833bb9d12becd0` |
| `tests/fixtures/batch3-canonical-1f06445e.html` | `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19` |
| `tests/fixtures/batch5-frozen-planned-s10.html` | `7861e414160693367726f8277d430274f259a7fe779ee5672a9b39003b2440a4` |
| `workbench/data/adjudication_queue.json` | `427d9b40447f376d8d8e90613e97df81b9150eb6b9592d3a2add236d8cb6fc68` |
| `workbench/data/batch5_identity_crosswalk.json` | `3bd7f0d2ea15d7447c138fae2f05fa6dffbf357592a0a2fcd6242bc8ea6c3d84` |
| `workbench/data/entry_identity_index.json` | `b9c760567f678fa7599ebb2e0de8527e2d875cd3ec72ca58c307905b9acf7a40` |

</details>

## Executed validation

| Check | Baseline | Correction |
| --- | --- | --- |
| Strict manual validation | 0 errors, 0 warnings | 0 errors, 0 warnings |
| Editorial lineage audit | 34/34 | 34/34. Classifier regeneration was byte-identical. |
| Enforced entry lineage reconciliation | Passed | Passed with 10 pending, 81 non-pending, 91 total and 315 pages |
| Full Python unittest | 237 passed | 249 passed, 0 skipped, 0 failures, 0 errors |
| Reactor | Covered by baseline unittest | 131 Reactor tests passed. The workflow’s independent identity and frozen research provenance snippet passed. |
| Optional Reactor evidence browser | Failed at the tamper-status check on the detached baseline | Passed desktop and mobile on retry. The first run read the asynchronous import status before it settled. |
| Historical replication kit | — | 8 fixture-based tests passed. Both files matched `LOCK.sha256`. |
| Syntax, DOM inventory, identity regeneration, and diff whitespace | — | Passed |
| Chromium | Passed locally at all three widths | Expanded smoke passed locally and in GitHub Actions |
| Firefox | Local launch timed out | Expanded smoke passed in GitHub Actions. Local launch timed out with a read-only `/proc/self/uid_map` and software compositor initialization failure. |
| WebKit | Passed locally at all three widths after installing missing shared libraries in a temporary directory | Expanded smoke passed locally and in GitHub Actions |

All seven [checks on this PR](https://github.com/GnomeMan4201/gnome-prompt-field-manual/pull/39/checks) passed on commit `30b2e7598a617d2f29ac0484e1a5ffabbbe48391`, including the [three-engine browser matrix](https://github.com/GnomeMan4201/gnome-prompt-field-manual/actions/runs/45370250587).

## Independent adjudication

- **SEC-02 — HOLD for promotion.** Pages 157–161 meet the corrections for thresholds, fallback and cross-references. The active drafting brief and page 156 still attribute a canary match to injection even though the page also defines fragment and pattern-only matches. A match can justify triage under the chosen policy. It cannot by itself identify the cause. The existing language is outside this correction's authorized scope.
- **SEC-05 — HOLD for promotion.** Pages 182 and 184 meet the structural-test contract and preserve the payload-free EDT-06. The active drafting brief also asks for a copy-paste executable test of an injection attempt that should be blocked. EDT-06 supplies a category description, and there is no approved runtime test artifact establishing the brief's blocking outcome. The structural checks support structural claims only.

## Limits

The regression tests verify manuscript contracts, provenance and readers. The manual supplies no deployment-specific firewall, refactored separator or corresponding runtime fixtures for executing a SEC-02/SEC-05 behavioral evaluation. The correction provides no empirical injection-resistance result. Both entries remain pending.
