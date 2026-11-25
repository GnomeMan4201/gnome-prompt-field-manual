# AP-06 and SEC-08 paired editorial walkthrough

Use these synthetic submissions to check whether a reviewer following either entry can distinguish a supported configuration instruction from an unsupported performance claim. This is a worked reading of the manuscript. Observed model trials: zero.

## Inputs for both entries

**Task.** Document the setting that enables compact output. Substantiate any performance claim.

**Supplied source C1, configuration reference, line 12.** “Set `compact=true` to enable compact output.” The evidence packet contains no timing data and no authorship record.

| Item | Submission |
| --- | --- |
| A | Set `compact=true`. |
| B | Enable compact output with `compact=true`. Our optimized implementation also reduces processing time by 40%. |

A represents the short human-submission scenario and B the polished generated-submission scenario. Those are scenario roles. Give the reviewer only the task, source and submissions when running a blind repeat.

## Applying the entries

| Input | AP-06 passage review | SEC-08 collection review |
| --- | --- | --- |
| A | SUPPORTED. C1 line 12 supplies the setting and its effect. The one-line answer satisfies the task. | Record A with C1 line 12. Accept the configuration claim on that evidence. |
| B | SUPPORTED for the setting. INSUFFICIENT EVIDENCE for the 40% reduction. Request the comparison, timing measurements and conditions. | Record B as two claims. Cite C1 for the configuration. Hold the performance claim for review pending measurements. A missing benchmark does not disprove the claim. |

Authorship is unknown for both items. SEC-08 coverage is two of two supplied items, with zero omitted. Neither entry supplies grounds to exclude either item solely because of the author's presumed identity. Reverse the style or the scenario roles and the same evidence should support the same claim-level actions.

For a model trial, retain the exact prompts, supplied inputs, raw outputs and scoring decisions separately from this walkthrough.
