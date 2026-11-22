# Chamber experimental method — limited offline preview

Input: an array of paired control and variant observation records, each holding Phase VIII-A metadata. A pair's observation fields must include matching experiment, input ID/hash, provider, model, evaluator ID, temperature, seed, tools, dataset and rubric hash, and **different** valid prompt hashes. Both conditions require explicit `outputText`. Duplicate `(trialId,inputId)` pairs are rejected.

Evaluation summaries are **supplied** fields: `controlEvaluation` and `variantEvaluation` require both a deterministic score and a grounded score. `PASS + SUPPORTED` means a supported-pass *assertion*; `FAIL + CONTRADICTED` means a supported-failure *assertion*. All other combinations are unscored. No live scoring is performed in the UI; users must separately substantiate evaluator evidence.

The counter `validPairedTrials` includes only matched pairs with two supported scoring assertions. `observedVariantInducedFailureProportion` is induced failures divided by that denominator; zero valid pairs produce `null`, never 0%. No confidence interval or causal proof is claimed. `UNATTRIBUTABLE` cases are reported individually with reasons. Existing canonical source bodies remain 0/91 verified; Chamber content cannot change their status.
