# Stable Release Quality Gate

The manual is a publication artifact and an operational reference. A page that renders is not sufficient evidence of completion.

## Structural gate

- `index.html` passes the committed deterministic validator.
- IDs are unique and local anchors resolve.
- Referenced local assets exist and remain within the repository root.
- The document has language, title, responsive viewport, one main landmark, and one primary heading.
- Images have explicit alternative text.
- New-tab links use `rel="noopener"`.
- Generated validation evidence records the exact source SHA-256.

## Editorial gate

- Every section has an explicit operational purpose.
- Examples show inputs, constraints, expected output shape, and verification procedure.
- Counterexamples explain the failure mechanism rather than merely labeling a prompt as bad.
- Normative words such as must, should, and may are used deliberately.
- Claims about reliability, determinism, safety, or model behavior state their scope and evidence.
- Uncertainty and known failure modes are visible at the point of use.
- No unresolved placeholders or unsupported superlatives remain.

## Model-behavior gate

- Patterns are not presented as universally portable across providers, model families, versions, context lengths, tool runtimes, or system prompts.
- Version-sensitive examples record the evaluated environment.
- A prompt that requires tools, structured output, hidden policy, or persistent state names that dependency.
- Safety controls are treated as layered controls, not as proof that prompt text alone creates a security boundary.

## Accessibility and browser gate

- Keyboard navigation reaches every interactive control.
- Focus is visible and logical.
- Reading order remains coherent without CSS.
- Text remains usable at 200% zoom and narrow mobile widths.
- Contrast and reduced-motion behavior are reviewed.
- Current Chromium, Firefox, and WebKit desktop/mobile smoke checks pass or documented limitations are published.

## Release gate

- `VERSION`, `CHANGELOG.md`, README status, and the published artifact agree.
- A clean checkout reproduces validation results.
- The final commit hash and `index.html` SHA-256 are recorded.
- Known limitations and deferred work are explicit.
- No critical structural, accessibility, or factual defect remains open.
- Stable versioning occurs only after independent editorial review or a documented equivalent review process.
