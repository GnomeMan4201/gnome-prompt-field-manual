# Batch 9 adjudication — planned P-06 and P-07

## Source and identity

The approved PR #45 head `1544092db57bd7bd6e7d9f6b33a2b01dc4f43901` matches the tree merged as `88f1a6399eff6655bf511f24fb848f51bdb1ce88`. The [merged source](https://github.com/GnomeMan4201/gnome-prompt-field-manual/blob/88f1a6399eff6655bf511f24fb848f51bdb1ce88/index.html) contains the complete frozen `div#b-p06` and `div#b-p07` briefs. Their requirements, identifiers and original cross-reference labels remain byte-identical.

| Frozen plan | Canonical subject and physical boundaries | Collision |
| --- | --- | --- |
| P-06 Work Sample Annotator, criteria 6 and 10 | **P-05 Work Sample Annotator**, criteria 6, 9 and 10. Begins at its heading on page 222 after P-04 ends on page 221. Continues through its Safety Notes on page 228, up to the next heading. | Canonical P-06 is the changelog subject. |
| P-07 Changelog Curation Engine, criteria 6 and 9 | **P-06 Changelog Curation Engine**, criteria 6, 9 and 10. Begins at its heading on page 228 and ends with its Safety Notes on page 232. | Canonical P-07 is **RFC Draft Generator**, beginning later on page 232 and continuing on page 233. Preserve that neighboring entry. |

Body ownership follows the named headings, continuous subject and explicit prompt/output boundaries. An identifier occurrence or a pending title is insufficient to assign a body. The correction scope is **pages 222–232**, with both subjects sharing page 228 and the RFC heading and criteria on page 232 outside the editable portion.

## Planned P-06 — Work Sample Annotator

| Source requirement | Before correction | Correction criterion |
| --- | --- | --- |
| Frozen artifact, the original work with annotations alongside it | CONTRADICTORY. Pages 223–225 accept a description without the work and can return final standalone prose. | Return the supplied work verbatim with separately anchored annotations. Lack of access or permission blocks a complete sample. |
| Frozen DECISION ANNOTATIONS at specific work points | PARTIAL. Page 224 lists decisions without a stable artifact anchor. | Identify the selected point, decision, rationale and supporting record. |
| Frozen CONSTRAINT ANNOTATIONS | PARTIAL. Pages 223–224 list project-level categories. | Tie each constraint to a point and explain its observed effect on the work. |
| Frozen ALTERNATIVE PATHS NOT TAKEN | PARTIAL. Page 224 lists rejected options but gives no source or missing-data rule. | Cite a considered alternative, rejection reason and trade-off, with missing states visible. |
| Frozen REUSABILITY NOTES | ABSENT as a required output, despite existing presentation knobs. | Give transferable parts, prerequisites, adaptations and limits at an artifact point. |
| Frozen P-04 and P-03 cross-references | PARTIAL. P-03 is present on page 227. P-04 is absent. | Retain P-03 README Quality Auditor (heading page 217). Add a follow-up to P-04 Technical Post-Mortem Publisher (219) for incident context. |
| Frozen criteria 6/10 and canonical 9 | PARTIAL. The evidence inventory provides a promising review surface, while the final prose could replace the sample. | Require an independently inspectable artifact and annotation package, with evidence and disclosure gates. |
| Additional attribution and original work, collaboration or dependencies | PARTIAL. Individual and team work are distinguished, but third-party components and corroboration are missing. | Classify contributions and cite per-claim evidence. Keep ambiguous or inseparable attribution explicit. |
| Additional traceability, impact and expertise | PARTIAL. Evidence item lists and claim boundaries exist. Impact, expertise and independent verification lack a final gate. | Cite version and location per technical claim. Require a measured result and comparison scope for impact or mark it unverified. Ground any skills in observable work. |
| Additional limitations, unresolved weaknesses and confidentiality | PARTIAL. Claim boundaries and safety notes exist, but disclosure can look optional and missing failures can invite invention. | Require limits and unresolved weaknesses, explicit missing states, and audience clearance before reproducing work or exposing sources. |

## Planned P-07 — Changelog Curation Engine

| Source requirement | Before correction | Correction criterion |
| --- | --- | --- |
| Frozen USER-FACING CHANGES with description, impact, and HIGH / MEDIUM / LOW significance | PARTIAL. Pages 229–230 classify changes but provide no mandatory impact or significance fields. | Require plain-language user impact, significance, and exact evidence for every shipped user-facing row. |
| Frozen one-sentence rationale for every HIGH item and reasoning for non-obvious changes | ABSENT. The original classification has no reason field. | Require a one-sentence rationale for each HIGH item and evidence-based reasoning for non-obvious changes. |
| Frozen INTERNAL CHANGES, separate and lower prominence | CONTRADICTORY. Page 230 makes internal notes optional, and page 231 allows suppression. | Keep a separate lower-prominence section for evidenced internal changes. |
| Frozen REMOVED/DEPRECATED | ABSENT as a named section. | Include a distinct section, distinguishing removal, deprecation and migration where applicable. |
| Frozen ADR and incident references | PARTIAL. P-04 is present on page 232. The brief says S-09 for ADR, but S-09 is Incident Report Scaffold (138). | Keep the frozen wording and route by subject to canonical **S-10 Architecture Decision Record Generator** (140), and **P-04 Technical Post-Mortem Publisher** (219). ADRs establish reasoning, not release membership. |
| Frozen criteria 6/9 and canonical 10 | PARTIAL. The artifact has useful classification and upgrade notes, but promises ready-to-publish output without a sufficient release gate. | Give a reusable curated record with auditable evidence and publication readiness conditional on coverage and support. |
| Additional traceability, version attribution and incomplete history | PARTIAL. Record references are required, but coverage and version certainty are weak. | Bind each claim to supplied records and verified release membership. Label missing history and unverified release metadata. |
| Additional shipped vs planned, duplicate and reverted work | PARTIAL. Page 231 warns against overclaiming shipped status without operational classification. | Record a status for each candidate, group duplicates with all contributing locators, and exclude reverted net-zero and planned work from shipped notes. |
| Additional breaking changes, migrations and unsupported claims | PARTIAL. Migration notes and an unverified flag exist, but the public output gate is underspecified. | Require affected users and actionable migration for each breaking change. Missing migration or release verification blocks publication. Keep unsupported claims out of shipped output. |

These additional checks strengthen the evidence boundary while retaining the frozen artifact and cross-reference requirements. Both corrections are editorial. No model output, reliability measurements, or comparative performance evidence were supplied.

## Corrected evidence and verdicts

| Frozen plan | Verdict | Corrected manuscript evidence |
| --- | --- | --- |
| P-06 Work Sample Annotator | **SUBSUMED** by canonical **P-05 Work Sample Annotator** | Page 223 binds claims and credits to versions, locations and accessible evidence. Page 224 requires point-specific decisions, constraints, alternatives, observed weaknesses and impact limits. Page 225 requires the unchanged artifact, anchored reusability notes and disclosure review. Page 226 gives the reviewer acceptance and failure conditions. Page 227 cites canonical P-03 and P-04, and pages 227–228 preserve disclosure controls. |
| P-07 Changelog Curation Engine | **SUBSUMED** by canonical **P-06 Changelog Curation Engine** | Page 229 binds each change to release evidence, exposes coverage gaps, handles planned, duplicate and reverted work, and defines migration blockers. Page 230 requires the three named sections, impact and significance, a rationale for every HIGH item, reasoning for non-obvious changes, and provisional status when evidence is incomplete. Page 231 identifies publication failures. Page 232 points to canonical S-10 for ADRs and P-04 for incident context and retains technical review for security disclosures. |

The corrected bodies satisfy the editorial requirements above. The contract for the work sample, an unchanged artifact paired with point-specific evidence, gives a reviewer an object to verify. For the changelog, a reviewer can trace each proposed release-note row and inspect the dispositions and source gaps behind it. Comparative usefulness and reliability remain unmeasured.

| Location | Before on PR #45 | Corrected requirement |
| --- | --- | --- |
| Page 225 | “The artifact itself or a description of it” | “Return the supplied work verbatim, either reproduced unchanged or as the supplied unchanged attachment, with the anchored notes alongside it.” |
| Page 230 | “INTERNAL NOTES (optional, for operators)” | “INTERNAL CHANGES — List verified internal implementation, tests or tooling in a separate, lower-prominence section.” |
| Pages 229–230 | A formatted changelog “ready to publish” | “If release evidence, migration, or coverage is unresolved, mark the draft PROVISIONAL and identify the specific blocker.” |

Both planned entries stay pending in this correction. The reader headings, canonical RFC body, pending IDs, frozen briefs, schedule and SEC-05 unresolved record retain their authority. A later disposition can reference this mapping without reassigning the canonical identifiers. The correction maintains 6 pending, 85 non-pending, 91 semantic identifiers, 315 pages, three nonempty batches, and 0/91 independently verified canonical bodies.

## Byte-level source bindings

| Artifact | SHA-256 at PR #45 | SHA-256 after correction |
| --- | --- | --- |
| Canonical `index.html` | `108d443e3f39e745bddbcbb030de1876f36f328180308a32eae2cb107d133f80` | `8e3ec363f32f200ac8b01f479986043a9854a8b4868efec8497b62a4288403d6` |
| Standalone `GNOME-Field-Manual.html` | `15b8d720aade3b1f0f5bbb0e36e879ce94a0097c66a01051caf4764761481ed8` | `778ae1a6a8412882eeb30a0433b30b089fd302394559fb1b3e0be65a57c766ec` |
| Current identity index | `168c3b1c3bc9fd564985a409568202b010e0799d49c33b2678327e533fd33804` | `034bf640bd5d2ea6e69f23188edd3689247fb1176db0916f5c811846d6ee534a` |

| Unchanged evidence | SHA-256 before and after |
| --- | --- |
| Frozen planned P-06 brief | `250bc2841a5218ce7d26506a3234573a630f626c391733cc089bde2ffa0210fc` |
| Frozen planned P-07 brief | `611090f14065fdf6b024707d5a357d058ecbdd3a3d58972932efee6ee183c879` |
| Frozen SEC-05 brief | `a56431111256a6f952f0aebdaaa6f50ef882838877377d497bfa01e0e4189123` |
| Historical PDF bytes | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |
| Other 304 canonical page cards | `e40f16938764cf49fae0fbaf1d3cb464b06a96a8fc5d425505fdaa7f6cee430a` |
| Other 304 fallback page cards | `0930ae8e9e794230fe05a595f0aa1d4daf2bc09954b75c156e0126638d638619` |
| Other 304 serialized standalone rows | `5118d1af9be8b7b73ce9b9a7d6ffd3da9cd2349314bb50befef1f8159e2ffe9b` |

The three 304-item digests hash the original byte sequences in ascending page order, separated by a single NUL byte. Regression checks compare each card and row independently to the pinned merge, compare the RFC suffix on shared page 232, and byte-compare 75 historical files under the documentation, research, examples, fixtures, and workbench evidence roots. The current-source index is regenerated from the live canonical bytes. The pinned comparison preserves the historical Batch 8 source digest.
