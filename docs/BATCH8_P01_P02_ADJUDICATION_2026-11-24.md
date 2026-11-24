# Batch 8 adjudication — P-01 and P-02

| Entry | Verdict on corrected manuscript | Criterion left open |
| --- | --- | --- |
| P-01 Build-in-Public Post (Structured) | **PASS at manuscript-contract level** | Model adherence, comparative usefulness, and publication outcomes have not been measured. |
| P-02 Learning Log Extractor | **PASS at manuscript-contract level** | Accuracy of extracted updates, comparative usefulness, and reliability across source types have not been measured. |

The correction leaves both entries pending. Any later disposition is a separate change.

## Source and physical boundaries

Approved PR #43 head `a6981a8f368003191502bdd9da7684bd2f38cc69` matches merge `b7d97eca11e2382b01d8a09ca464f2f64da5caba`. The [merged source](https://github.com/GnomeMan4201/gnome-prompt-field-manual/blob/b7d97eca11e2382b01d8a09ca464f2f64da5caba/index.html) contains the complete frozen briefs in `div#b-p01` and `div#b-p02`. The fragments are byte-identical in the corrected workspace.

- **P-01** starts at its named heading on page 209, after the Part VI introduction, and ends with its Safety Notes on page 212. The title and scaffold subject carry through the prompt, expected output and failure mode. The next heading on page 213 starts P-02.
- **P-02** starts at its named heading on page 213 and ends after its Safety Notes immediately before **P-03 README Quality Auditor** on page 217. The notes, belief update, and reversal-condition subject link the opening prompt to those end notes. The entire shared page 217 remains byte-identical. P-04 starts on page 219 after the end of P-03.
- Pages **209–216** are the authorized correction set. The Part VI introduction and P-01 heading and criteria on page 209, and the P-02 heading and criteria on page 213, are preserved. The active inventory, schedule, briefs, and other workspace guidance still agree with these contracts. The canonical and standalone readers preserve the original surrounding entries.

The current index was regenerated. Semantic IDs, editorial statuses, and body-verification fields are unchanged. Occurrences reflect the restored W-11, R-04 and R-08 links. The AP-02 title candidate reflects the updated reference context and retains its unverified authority label.

## P-01 requirement matrix

| Frozen requirement or quality gate | Before | Corrected evidence |
| --- | --- | --- |
| Replace style preferences with structural requirements. Produce a scaffold the author fills in. | CONTRADICTORY. The introduction specified a scaffold while pages 211–212 directed the model to assemble and review a final draft. | SATISFIED. Pages 209–211 require fill-in fields and prohibit an assembled post. |
| WHAT WAS BUILT/DONE, evidence-based | PARTIAL. Current state and change were described, but there was no dedicated mandatory slot with an attached locator. | SATISFIED. Page 210 names the change, prior state if known, and supplied evidence locator. |
| ONE THING THAT WORKED, specific and measurable | ABSENT as a required slot. | SATISFIED. Page 210 requires a specific result, a measure or observable criterion, and actual evidence. |
| ONE THING THAT DIDN’T WORK, mandatory and filled by a concrete failure | CONTRADICTORY. Page 210 allowed a constraint or trade-off instead of an observed failure. | SATISFIED. Pages 210–211 require an actual attempt, expected and observed results, and evidence. Missing failure keeps the scaffold **BLOCKED** with a named marker. |
| WHAT WAS LEARNED, operational | PARTIAL. The original expected a connection to a failure or change. | SATISFIED. Page 210 ties the observation to a decision or practice that changes. |
| NEXT STEP, a specific author/team action | PARTIAL. The original required specificity. | SATISFIED. Page 210 asks for an action, owner if known, and observable completion check. It labels work as planned and excludes an audience appeal as a substitute. |
| Criteria 6 and 10, reusable artifact and reusable output. Canonical criterion 9, ship cleaner. | PARTIAL. A generated narrative was hard to inspect and the risk check treated a clean result as intrinsically invalid. | SATISFIED. Pages 211–212 make all slots, source locators, missing inputs, evidence limits and review grounds inspectable. An evidence-backed clean checklist can record **NO FLAGS** with the actual checks performed. |
| Frozen cross-references | PARTIAL. W-11 was missing and W-04 addressed a finished draft. | SATISFIED. P-04 Technical Post-Mortem Publisher (heading 219) is for post-incident accounts. W-11 The Anti-Summary (64) runs first when compression would lose necessary detail. W-04 Over-Smoothing Detector (48) reviews the scaffold and failure slot. |
| Disclose security and publication limits | PARTIAL. The original noted sensitive inputs. | SATISFIED. Page 212 requires disclosure permissions, shareable locators, and withholding or resolving unsupported public claims. |

**Practical utility.** The scaffold solves a review problem for an author who has real work to report. A second reader can inspect each claim against a locator, see where an attempt failed, and verify the planned action separately from observed results. An ordinary request to “write an update” supplies no fixed gate for skipping the failure, filling gaps, or turning a plan into an accomplishment. No comparative performance claim is made.

## P-02 requirement matrix

| Frozen requirement or quality gate | Before | Corrected evidence |
| --- | --- | --- |
| NEW UNDERSTANDINGS with change, cause/evidence and confidence | PARTIAL. The fields existed, but the prompt permitted reconstructing the prior belief from the contradictory result. | SATISFIED. Pages 213–215 trace each accepted understanding from documented expectation to observation, evidence locator, bounded update, and justified confidence. Unconfirmed prior beliefs go to the filter pending support. |
| DISPROVEN ASSUMPTIONS mandatory, including prior assumption, observed outcome and disproof strength | PARTIAL. The original combined weakened and disproven assumptions without a separate required section or an explicit evidence gap. | SATISFIED. Page 214 distinguishes weakened from disproven. An experimental or uncertain log needs at least one evidenced disproof for completion. Otherwise the section remains present with **DISPROOF NOT ESTABLISHED** and the inventory is **INCOMPLETE**. |
| REVERSAL CONDITIONS for every accepted update | SATISFIED in principle. The original required a future observation but gave no missing-condition status. | SATISFIED. Pages 214–215 require a linked observable finding and the decision it changes, with an incomplete marker for a missing condition. |
| OPEN QUESTIONS GENERATED | ABSENT as an output section. | SATISFIED. Pages 214–215 link questions to accepted learnings and specify the evidence needed to answer them. Explicit none is allowed where the input supports it. |
| Criteria 3 and 6, signal/noise and reusable artifact. Canonical criteria 1 and 10, assumptions and reusable output. | PARTIAL. Activity filtering existed, but reconstructing prior beliefs could create unsupported entries. | SATISFIED. Pages 213–216 preserve the non-learning filter, require a source-backed before-state, and fail fabricated, overconfident, or unfalsifiable entries. Confidence and interpretations remain separate from observations. |
| Frozen cross-references | PARTIAL. The P-01 handoff existed, but R-08 and R-04 were absent. | SATISFIED. R-08 Artifact Extraction Protocol (heading 96) is the prior route for raw notes needing an artifact inventory. R-04 Research Artifact Generator (Schema-Locked) (86) is the follow-up for supported reusable findings. Page 216 routes publishable findings to P-01 (209) while preserving its other gates. |
| Disclosure and uncertainty | PARTIAL. Page 217 already covered sensitive evidence and untested reversal conditions. | SATISFIED. This note stays intact. Pages 213–216 add explicit handling for inaccessible evidence, unconfirmed priors, confounds, absence of disproof, and missing reversal conditions. |

**Practical utility.** The inventory solves the distinction between work performed and understanding changed. A reviewer can inspect a prior belief, its observed counterevidence, the strength of the update, and the proposed reversal condition. The output makes uncertainty and rejected activities visible. Its structured checks are editorial requirements, with no model-reliability measurement supplied.

## Preservation and source bindings

| Artifact | SHA-256 |
| --- | --- |
| Merged PR #43 `index.html` | `3b02599e745910f647d4800160b6f22ef0192ff9520d61e4e08ae6f63ddd63ef` |
| Merged PR #43 standalone reader | `1b2a203eb8e252b6e8539fca78e82317e083a731ac08fdbc4d4e352ce66b259b` |
| Frozen P-01 brief fragment | `fb0169e2f36a8acc6f08c6d029f2b5a12b394f372ac077a9e2ecf97587273324` |
| Frozen P-02 brief fragment | `1a63750729d32551b40f5d19a185f7493eec7a5d89690bebfe5e4b9ea3122bc4` |
| Corrected `index.html` | `8cd1a08d1763506dcd2c567fb116a34ea9527b8ac862f63592f3c4a6dfdc448f` |
| Corrected standalone reader | `68712b7fd49911c763f9eafa1b4e71bca05e8bd6a3517c421ceb65b128178b0d` |
| Regenerated current identity index | `9e51f9fdeee966c3b47d5f5acd974af452645079dde457d127d447219ac7fc40` |
| 307 unaffected cards, physical order, NUL-separated | `7189b7bf3b1bf15eec827b2ea2b4665852e0187b4c1b70e9a5faa43882f5d8d5` |
| Historical v9 PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |

The correction leaves **8 pending, 83 non-pending, 91 semantic IDs, 315 pages, four nonempty batches, and 0/91 independently verified canonical bodies**. SEC-05 remains independently pending under its unchanged evidence record.
