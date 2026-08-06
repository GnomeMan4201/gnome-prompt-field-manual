# Corrections and Evidence Policy

## Correction record

A material correction must preserve enough context to understand the original claim and the reason it changed. Record:

- affected version, section, and source commit;
- original claim or behavior in paraphrased form;
- trigger for review;
- decisive evidence;
- correction made;
- impact on examples, guidance, or downstream use;
- reviewer and date;
- replacement commit and release.

Do not silently rewrite a substantive claim after publication. Typographical changes that do not alter meaning may be summarized in the changelog.

## Evidence levels

Use the strongest accurate label:

- **Demonstration** — illustrates a pattern but is not a reliability result.
- **Observed** — reproduced in a named environment.
- **Measured** — evaluated under stated criteria across stated trials.
- **Externally supported** — linked to an appropriate primary source or specification.
- **Operationally validated** — used in a real workflow with recorded outcomes and limitations.

Absence of a label must not be interpreted as high-confidence validation.

## Citation rules

- Prefer primary documentation, standards, specifications, and original research.
- Cite the exact claim rather than attaching a general source to an entire section.
- Record access date or version for mutable documentation.
- Separate source-derived facts from interpretation and recommendation.
- Avoid long quotations when a precise paraphrase is sufficient.
- Preserve archived evidence when a mutable external page is decisive and archiving is lawful.

## Security and privacy

Examples must use synthetic, public, or explicitly authorized data. Remove secrets, personal data, private prompts, hidden policies, tokens, and live credentials. Redaction must not change the technical property being demonstrated; when it does, publish a faithful synthetic reconstruction and state that fact.

## Disagreement and uncertainty

When reviewers disagree, record the disagreement and the evidence each interpretation depends on. Use inconclusive when the available evidence does not support a defensible resolution. The manual should expose uncertainty rather than convert it into false precision.
