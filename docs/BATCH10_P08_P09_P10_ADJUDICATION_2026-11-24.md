# Batch 10 correction — P-08, P-09 and P-10

## Source and identity

PR #47 was merged as `15a389fb66c3cdc7459806b9cc104d56267161be`; the Git tree `95c927d9b726b2a48859f3fbc7811558e4cdde7b` matches approved head `c17ed5e0b74da1cabebfffe6bdf9132a3b4c13f2`. The [pinned original](https://github.com/GnomeMan4201/gnome-prompt-field-manual/blob/15a389fb66c3cdc7459806b9cc104d56267161be/index.html) contains the complete frozen `b-p08`, `b-p09` and `b-p10` briefs; all three remain byte-identical. SEC-05 remains independently pending.

| Frozen plan | Canonical heading / physical boundaries | Identity finding |
| --- | --- | --- |
| P-08 Peer Review Responder (criteria 4, 10) | P-08 Peer Review Responder, page 238 after P-07 Safety Notes through page 242 before P-09; canonical criteria 3, 6, 10 | Same identifier and subject. Criterion 4 is addressed by evidence-backed criticism handling; no heading renumbering. |
| P-09 Correction / Retraction Writer (criteria 6, 10) | P-09 Correction/Retraction Writer, page 242 through page 247 before P-10; canonical criteria 3, 6, 10 | Same subject; spacing variant only. |
| P-10 Open Source Contribution Guide Generator (criteria 6, 9) | P-10 Open Source Contribution Guide Generator, page 247 through Safety Notes on page 253; canonical criteria 6, 9, 10 | Same identifier and subject. Page 254 is a spacer. |

The subject crosswalk is one-to-one. Shared page 238 and page 243 remain unchanged. The P-09 heading/criteria suffix on page 242 and P-10 heading/criteria suffix on page 247 are unchanged in visible, dynamic and static text. P-07 RFC Draft Generator remains distinct. These observed headings support editorial mapping, not independent canonical-body verification.

## P-08 requirement matrix

| Frozen requirement / additional quality gate | Original source | Corrected contract and evidence |
| --- | --- | --- |
| Four required classifications, one per comment | PARTIAL: pages 239–240 used validity and type, not the four frozen classes | SATISFIED: p239 ACCEPTED / CONTESTED / CLARIFICATION NEEDED / DEFERRED; split partial acceptance into classified subpoints with parent IDs |
| One-to-three sentence response; plain classification | PARTIAL: exact response text without bounded length | SATISFIED: p240 explicitly states length, classification and action, no evasive courtesy |
| Accepted exact change; contested specific evidence | PARTIAL: required action and revision location, without separate completed/unverified gate | SATISFIED: p240 exact change, verification criterion, counter-evidence, before/after artifact, VERIFIED CHANGE / PLANNED / NOT MADE / UNVERIFIED |
| Clarification and deferral | PARTIAL: original type and validity fields | SATISFIED: p240 identify misunderstanding or missing evidence and ask a precise question; scope explanation and reopening condition |
| Summary table covering all comments | ABSENT as mandatory: p241 optional knob | SATISFIED: p240 mandatory summary with every original ID, classification, revision status, source and unresolved issue; p241 three-part output |
| Stable IDs, accurate criticism, partial acceptance and unresolved disagreement | PARTIAL: original IDs and faithful paraphrase but no parent/subpoint or explicit unresolved evidence gate | SATISFIED: pp239–242 preserve reviewer order, parent IDs, evidence and uncertainty; no invented reviewers or findings; incomplete draft when required revisions unverified |
| T-06 prior, W-05, W-09 | PARTIAL: W-05 and W-09 present, T-06 absent | SATISFIED: p239 T-06 first; p242 W-05 and W-09 retained; actual headings at pp23, 50, 60 |
| Avoid defensiveness and maintain reviewer-facing clarity | PARTIAL | SATISFIED: pp241–242 reject unsupported concession and contest, fabricated completed work, and concealed disagreement; author review remains necessary |

## P-09 requirement matrix

| Frozen requirement / additional quality gate | Original source | Corrected contract and evidence |
| --- | --- | --- |
| Standalone notice: original claim, error description, corrected claim, impact assessment, scope of retraction | PARTIAL: most fields in internal package; p245 public notice did not require impact or explicit retraction scope | SATISFIED: pp244–246 require all five fields in standalone public draft, source locators and discovery record |
| No minimizing or reputation-protective framing | PARTIAL: already stated, without a complete public artifact gate | SATISFIED: pp244–247 evidence-backed severity, unknown reach, disputed versus confirmed errors and visible limitations |
| Correction severity and withdrawal / retraction distinction | PARTIAL: correction/update/retraction threshold | SATISFIED: p245 MINOR CORRECTION, MATERIAL CORRECTION, UPDATE, WITHDRAWAL, RETRACTION, UNCERTAIN; venue rules, evidence and explicit scope |
| Downstream effects, archive preservation and linking | PARTIAL: impact and archive action, no bidirectional links | SATISFIED: pp244–245 known uses, decisions and citations needing review, notification plan, preserve original and link records; no silent rewrite |
| Avoid validating unaffected claims automatically | PARTIAL: "what remains valid" without evidence qualification | SATISFIED: pp244, 246 mark unassessed claims and reject general validation from a single correction |
| P-04 process failure and R-11 negative result | PARTIAL: P-04 existed; R-11 missing | SATISFIED: p247 P-04 Technical Post-Mortem Publisher (219) and R-11 Negative Result Documenter (101) |
| Safety notes: institutional communication versus honest correction | PARTIAL: professional and legal review, no explicit tension | SATISFIED: p247 reassuring tone cannot obscure error, severity or downstream consequences; accountable review before publication |

## P-10 requirement matrix

| Frozen requirement / additional quality gate | Original source | Corrected contract and evidence |
| --- | --- | --- |
| CONTRIBUTION SCOPE including exclusions and rationale | PARTIAL: accepted/not accepted categories, weak source gate | SATISFIED: p249 scope, actual examples, reasons, constraints and maintainer confirmation for undecided policy |
| CONVENTIONS naming, structure, testing with rationale | PARTIAL: branch and workflow fields but no rationale requirement | SATISFIED: p249 named conventions, rationale, source, enforcement versus preference, unknown rationale |
| DECISION CONTEXT and ADRs | ABSENT as required output; frozen brief has legacy S-09 label | SATISFIED: pp251–252 actual architecture/ADR paths, component boundaries and owners; canonical S-10 (140) by subject, canonical S-09 Incident Report Scaffold (138) preserved |
| ACCEPTANCE CRITERIA and definition of done | PARTIAL: generic review process | SATISFIED: p250 exact maintainer checks, CI, scope, compatibility, review resolution and evidence; actual policy versus proposals |
| FIRST CONTRIBUTION GUIDE | ABSENT as required artifact | SATISFIED: p251 real approved available task, source, component, prerequisites, commands, artifact, review and acceptance; missing task remains provisional |
| Actual project inputs, setup/test commands and source verification | PARTIAL: p251 permitted a generic description and language as minimum viable input | SATISFIED: pp248–251 exact revision, repository files, lockfiles, CI and policy; inspected versus executed commands and observed outcomes; missing inputs keep guide provisional |
| P-03 prior | PARTIAL: p252 alongside rather than prior | SATISFIED: pp248, 252 P-03 first and passing relevant checks before readiness; canonical heading page 217 |
| Security, licensing, attribution, ownership, disclosure | PARTIAL: existing reporting and expectations fields but insufficient missing-policy controls; p253 equated unmonitored channel with public disclosure | SATISFIED: pp249–250, 253 confirmed monitored route or explicit provisional gap; no invented channels, support commitments, licensing rules, or attribution |
| Generic boilerplate and acceptance readiness | PARTIAL | SATISFIED: pp251–252 reject generic tutorials and invented policies, distinguish provisional guide from READY FOR MAINTAINER REVIEW |

## Before/after examples

- P-08 p241: optional "include a summary table" becomes mandatory summary table and evidence-linked draft. P240 distinguishes verified and planned changes.
- P-09 p245: notice fields omitted downstream impact and scope; now explicit standalone impact and scope of retraction, plus threshold decisions and archive links.
- P-10 p251: minimum viable description is replaced by repository revision and accessible sources. Named decision-context and first-contribution sections must identify actual records and approved work.

## Preservation and evidence

| Binding | SHA-256 |
| --- | --- |
| Original canonical HTML | `208211b102aa75bf9f35fefbd2c33cf7f89365a8468058abd8567b8b442937d6` |
| Corrected canonical HTML | `28fd210da6ec549d64d31b2aa79433843df3c04e6aeab3aa31b53ee5007c6dbd` |
| Original standalone HTML | `778ae1a6a8412882eeb30a0433b30b089fd302394559fb1b3e0be65a57c766ec` |
| Corrected standalone HTML | `cfa5a6bff04cc1d4ada3c1ce410ee6bc8893db2bc903599927de15115ca95393` |
| Corrected identity JSON | `849aa57c3a1125fb8367720fc46df13fb756b4b2db1fbb0fd2e9bd9f26306a46` |
| P-08 brief | `a04df5e0db9720b3f11ba978ce7c8d8558996f8502c1acd0256315870511fe07` |
| P-09 brief | `123233eff9d78f5a5875fcdd3f64b33f56f03cabf0d12de0db530be9424f12e1` |
| P-10 brief | `6f27cfc91051e49a5ffd83056d210f2a29e0d4fad860f333fe928fbe15dcd098` |
| SEC-05 brief | `a56431111256a6f952f0aebdaaa6f50ef882838877377d497bfa01e0e4189123` |
| 301 unaffected canonical cards in order, NUL-separated | `affe728f153f51e45059e00a3917c6861f08a99647c6013adc89f706e1ef164c` |
| Historical PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |

Only pages 239–242 and 244–253 change across all four surfaces (14 pages). Exact-scope tests compare each card and serialized row, both shared-page suffixes, bytes outside the cards, all four active briefs, PDF bytes and 80 protected historical files. The regenerated advisory AP-03 title candidate changes because its reference context on page 247 changes; authority remains unverified. Occurrence differences are confined to changed pages. Earlier Batch 9 tests now replay against their pinned disposition tree rather than live manuscript bytes; current-source assertions retain independent pins. All editorial flags and counts remain unchanged.

## Executed validation and limits

- Initial Python baseline: missing jsonschema and Node; after installing jsonschema, 305 tests passed with 14 Node-dependent skips. After installing Node 22, the post-edit baseline suite passed 305/305 without skips. The first correction run detected newly introduced S-10 occurrences; the historical occurrence list remains pinned and the current expected list was updated. The focused suite initially detected a line-wrap-sensitive ADR assertion; canonical normalization fixed it. Final full Python suite: 311/311, zero skips; Reactor 131/131.
- Strict manual validation: 0 errors and 0 warnings. Editorial lineage: 34/34. Entry lineage: 4/87/91/315, two nonempty batches. Identity exporter reproduced the current source. Node syntax checks passed. Replication kit lock verified; 8 fixture-based tests passed, no new empirical study performed.
- Browser smoke probes were checked against continuous dataset text; one line-wrapped phrase was replaced. Local browser installation failed with ENOSPC on the 241 MiB temporary filesystem. The three-engine browser matrix is delegated to the PR CI; do not claim successful browser execution until observed.

## Candidate adjudication

P-08 **PASS**, P-09 **PASS**, P-10 **PASS** at manuscript-contract level, subject to independent review and successful CI. These are author-side adjudications, not an independent review or a measurement of model adherence. Maintain **4 pending / 87 non-pending / 91 semantic IDs / 315 pages / 2 nonempty batches / 0 independently verified canonical bodies**. Do not promote or merge this correction automatically. SEC-05 remains pending; empirical reliability, comparative utility, independent canonical-body verification, accessibility and final publication readiness remain unestablished.

### Final local validation

The complete Python suite was rerun module-by-module in separate processes to avoid retained historical blobs in the resource-limited sandbox: 45 modules, 311 tests, zero skips, zero failures. Node v24.19.0 was available. The monolithic run remains recorded as terminated; the module-isolated run does not establish monolithic resource behavior. All three browser engines remain CI gates, not locally verified results.
