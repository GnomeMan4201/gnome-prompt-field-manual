# Final scheduled editorial closeout

**Disposition state:** 1 pending identifier, 90 non-pending identifiers, 91 semantic identifiers, 315 canonical page cards, one nonempty batch, and 0/91 independently verified canonical bodies. Batch 6 remains open for SEC-05. The package remains at `1.0.0-rc.1`.

This record consolidates the scheduled editorial decisions. Evidence for the last three decisions is bound to PR #48 head `4b90f644044f4b17de884b99ca8b3f47cce49b6c` and merge `bd03aeeade2b0a74cbcbc39e99f55fbbd0e26755`. The corrected `index.html` SHA-256 is `28fd210da6ec549d64d31b2aa79433843df3c04e6aeab3aa31b53ee5007c6dbd`. The requirement matrices have SHA-256 `52caf4799507c732a5a3aa5c260cec94f1fec15b8c21e5bc8f2da6131493151b`. Independent manuscript-contract review and all seven PR #48 checks passed. The disposition record holds the separate post-disposition source and archive hashes. [Requirement matrices](BATCH10_P08_P09_P10_ADJUDICATION_2026-11-24.md) · [Disposition and source bindings](BATCH10_DISPOSITION_2026-11-24.md)

## Outcome by batch

Counts are the editorial inventory at each decision. The total stayed at 91 semantic identifiers across 315 canonical page cards.

| Batch | Recorded outcome | Pending / non-pending after decision | Record |
| --- | --- | --- | --- |
| 1 | T-01 Idea Stress-Test and T-02 Claim Dissection closed after bounded corrections. | 19 / 72 | [Batch 1 disposition](BATCH1_DISPOSITION_2026-08-24.md) |
| 2 | W-01 Dense-to-Clear and W-03 Adversarial Reader closed after bounded corrections. W-02 Argument Skeleton Extractor passed against the existing contract. | 16 / 75 | [Batch 2 disposition](BATCH2_DISPOSITION_2026-08-24.md) |
| 3 | R-01 Source Map with Contested Zones and R-03 Replication Risk Auditor closed after bounded corrections. The corrected Batch 3 source remains the frozen research baseline. | 14 / 77 | [Batch 3 disposition](BATCH3_DISPOSITION_2026-08-24.md) |
| 4 | S-01 System Map with Trust Boundaries, S-02 Code Archaeology, and S-03 Failure Mode Inventory passed. | 11 / 80 | [Batch 4 disposition](BATCH4_DISPOSITION_2026-11-23.md) |
| 5 | The planned S-10 Migration Risk Classifier brief was closed as **SUBSUMED** by canonical S-07. Canonical S-10 Architecture Decision Record Generator retains its own identifier and body. | 10 / 81 | [Batch 5 disposition](BATCH5_DISPOSITION_2026-11-23.md) |
| 6 | SEC-02 Prompt Firewall Designer passed at manuscript-contract level. SEC-05 Command/Data Separator (Refactor) remains **INSUFFICIENT EVIDENCE**. | 9 / 82 | [SEC-02 disposition](BATCH6_SEC02_DISPOSITION_2026-11-24.md) · [SEC-05 evidence requirement](BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md) |
| 7 | SEC-06 Tool-Agent Offense Probe passed at manuscript-contract level. Pages 187–197 define the current defensive evaluation contract. | 8 / 83 | [Batch 7 disposition](BATCH7_SEC06_DISPOSITION_2026-11-24.md) |
| 8 | P-01 Build-in-Public Post (Structured) and P-02 Learning Log Extractor passed at manuscript-contract level. | 6 / 85 | [Batch 8 disposition](BATCH8_P01_P02_DISPOSITION_2026-11-24.md) |
| 9 | Planned P-06 Work Sample Annotator and P-07 Changelog Curation Engine closed as **SUBSUMED** by canonical P-05 and P-06, respectively. Canonical P-07 remains RFC Draft Generator. | 4 / 87 | [Batch 9 disposition](BATCH9_P06_P07_DISPOSITION_2026-11-24.md) |
| 10 | P-08 Peer Review Responder, P-09 Correction/Retraction Writer, and P-10 Open Source Contribution Guide Generator passed independent review at manuscript-contract level. | 1 / 90 | [Batch 10 disposition](BATCH10_DISPOSITION_2026-11-24.md) |

## Open SEC-05 evidence requirement

Pages 182 and 184 specify executable structural checks EDT-00 through EDT-05, a benign positive control, and a payload-free description for EDT-06. The offline reference fixture verifies its own synthetic authorization boundary. Independent behavioral evidence remains outstanding for the blocking claim on an actual refactored mechanism. Closure requires an authorized and scoped evaluation with exact artifact and environment identifiers, observed denial attributable to the relevant control, an observed authorized benign control, and replayable evidence that a reviewer can assess. The public record can describe scope and bounded findings while keeping sensitive inputs private. [Frozen requirement and closure criteria](BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md)

## Identity and cross-reference backlog

The live identity index reconciles semantic IDs and occurrence pages. Its title candidates remain advisory. Independent verification of canonical body boundaries and ownership remains **0/91**. Older production-state numbers remain tied to their dated records. The underlying editable v3 manuscript remains outside the repository, so the full editable-to-rendered lineage remains unestablished. The 629-decision Phase V–VIII adjudication queue and associated evidence still bind to the historical Batch 3 `index.html` SHA-256 `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`. [Identity and scope baseline](IDENTITY_AND_SCOPE.md) · [Live identity index](../workbench/data/current_entry_identity_index.json) · [Frozen source](../tests/fixtures/batch3-canonical-1f06445e.html)

| Location | Recorded mismatch or superseded guidance | Current resolution |
| --- | --- | --- |
| Page 260 | Uses S-09 for the Architecture Decision Record subject. | S-10 Architecture Decision Record Generator begins on page 140. S-09 Incident Report Scaffold begins on page 138. The changelog on page 232 and contribution guide on page 252 use S-10. [Batch 9 crosswalk](../workbench/data/batch9_identity_crosswalk.json) · [Page 260](../index.html#manual-page-260) |
| Page 273 | Uses P-05 for the RFC subject. | P-07 RFC Draft Generator starts on page 232. P-05 Work Sample Annotator starts on page 222. [Batch 9 crosswalk](../workbench/data/batch9_identity_crosswalk.json) · [Page 273](../index.html#manual-page-273) |
| Pages 121, 261, and 271 | Carry older SEC-06 wording superseded by the reviewed defensive evaluation contract. | Follow pages 187–197 for current SEC-06 use. [Batch 7 disposition](BATCH7_SEC06_DISPOSITION_2026-11-24.md) |

The frozen Batch 5 brief labels Rollback Decision Gate as S-07 and Incident Report Scaffold as S-08. The canonical subjects use S-08 and S-09 respectively, as named on page 135. The frozen Batch 9 changelog and Batch 10 contribution-guide briefs retain the S-09 label for the ADR subject as provenance. The subject mappings have narrow scope, and the disposition preserves the original brief and page bytes. [Batch 5 crosswalk](../workbench/data/batch5_identity_crosswalk.json) · [Batch 9 crosswalk](../workbench/data/batch9_identity_crosswalk.json) · [Batch 10 requirement matrices](BATCH10_P08_P09_P10_ADJUDICATION_2026-11-24.md)

The established parity checks also identify pre-existing differences between the canonical visible text and the search metadata on page 101, and between the canonical visible text and the standalone static text on page 219. The affected bytes match the approved correction. These reader parity findings are separate from the identifier mismatches above.

## Publication gates and empirical limits

- Stable publication remains open under issue #1. Its work includes the SEC-05 evidence decision, broader editorial and factual review, cross-reference consistency, and accessibility review beyond browser smoke. Record stable versioning, clean-checkout release evidence and matching published artifacts through the release gate. Keep the historical v9 PDF separately identified and hashed. [Stable-release issue](https://github.com/GnomeMan4201/gnome-prompt-field-manual/issues/1) · [Stable Release Quality Gate](QUALITY_GATE.md)
- Editorial decisions and automated regressions cover the written contracts, structural invariants and reader behavior. Empirical prompt reliability, comparative usefulness, model portability, external source authenticity and independent reviewer identity remain unestablished by those checks. Synthetic Reactor records and replay can check implementation and stored-result integrity. Independent execution requires its own evidence. [Sensitivity and evidence levels](MODEL_VERSION_SENSITIVITY.md) · [Reactor integrity limits](REACTOR_PHASE_VIIIC_REPAIR.md)
- The Phase VIII-C companion record preserves exploratory results and counterexamples for one local Qwen2.5 0.5B configuration. The recorded preregistered internal repeat matched six of six blocks, with independent operator replication still unestablished. The record includes control and formatting-dependent outcomes, with raw bundles kept outside Git. Population bypass rates, unique causal attribution, cross-model transfer, and general safety guarantees remain unestablished. [Exploratory record](../research/phase8c-qwen-0p5b/README.md) · [Locked replication program and limits](../research/phase8d-independent-replication/README.md)
