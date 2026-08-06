# Model and Runtime Sensitivity

Prompt behavior is an observed property of a complete execution environment, not a permanent property of prompt text alone.

## Environment record

A versioned example should record all information needed to interpret the result:

- provider and model identifier;
- model or API version/date when exposed;
- system and developer instructions that materially affect behavior;
- tool definitions and tool-selection mode;
- output schema or response-format controls;
- sampling and reasoning controls when exposed;
- context supplied before the example;
- date evaluated;
- number of trials and acceptance criteria;
- observed failures, not only the preferred output.

Secrets, private chain-of-thought, and proprietary system instructions must not be published. Their presence should be disclosed as an uncontrolled or unavailable variable when it affects reproducibility.

## Claim classes

Examples should distinguish:

1. **Syntax claim** — the prompt or schema is well formed.
2. **Single-run observation** — one execution produced the shown result.
3. **Repeated empirical result** — a stated number of trials met stated criteria.
4. **Operational pattern** — the technique has been useful across named environments.
5. **Portable guarantee** — generally unsupported unless enforced outside the model by deterministic code or protocol.

Do not silently promote a single successful run into an operational or portable claim.

## Revalidation triggers

Re-run affected examples when any of the following changes:

- model family, snapshot, or provider;
- system/developer instruction hierarchy;
- tool schema or execution environment;
- structured-output implementation;
- context-window behavior or retrieval layer;
- safety policy or refusal behavior;
- prompt wording that changes a normative instruction;
- acceptance criteria or evaluator.

## Failure interpretation

A failed example may indicate prompt ambiguity, model drift, tool failure, evaluator disagreement, context contamination, hidden instruction conflict, or an invalid original claim. The correction record should identify which explanation is supported and which remain hypotheses.

## Durable controls

Use deterministic controls outside the model for properties that must be guaranteed: schema validation, allowlists, authorization, provenance, rate limits, redaction, transaction boundaries, and human approval. Prompt text can request those properties; it does not enforce them by itself.
