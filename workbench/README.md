# Operational Workbench — beta

This is an **additive, experimental** static workbench. It does **not** replace the canonical `../index.html` reader or change the repository's release status.

## Authority and limitations

- The **canonical manual** remains the existing production workspace and embedded reader at [../index.html](../index.html). Its entry numbering, pending statuses, provenance, and 315 embedded page cards have not been modified.
- This beta contains **six illustrative sheets adapted for demonstration**, **not** the original 91-entry manual dataset. Their summaries and patterns are not verbatim canonical extracts. Do not cite them as authoritative manual text.
- The **Anatomy Lab** checks blank fields; it does not validate prompt semantics, safety, or empirical model reliability.
- The **Stress Matrix** checks configured scenario rules deterministically. Its passing/failing states are hypothetical workflow paths; no LLM was run, and a checked defense does not prove resistance to prompt injection.
- **Diff & Export** performs explicitly limited keyword-presence probes, not semantic comparison. Its JSON exports preserve user-entered text and optional pasted outputs; users must independently verify provenance and may wish to remove sensitive input.
- All work is client-side; no model API keys or live remote inference are required. Do not paste secrets or private information without considering local-browser risk.

## Review checklist

1. Open `workbench/index.html` from a static server or GitHub Pages.
2. Confirm all four modes work and the official manual link opens `../index.html`.
3. Check search, Anatomy Lab, each Stress Matrix scenario, editable Diff inputs, JSON export, clipboard success/failure, and keyboard controls.
4. Test 390px mobile and 200% zoom; test reduced-motion behavior.
5. From an unmodified checkout, run the existing tests and validation scripts before a merge.

## Next gated milestone

Build a deterministic entry extraction tool that reads canonical data and produces an integrity-checked JSON artifact **without rewriting existing canonical `index.html`**, then test ID mapping, pending status, source references, cross-references, and checksum equivalence before claiming 91-entry coverage. Do not treat the historical v9 PDF as canonical or use synthetic entry summaries as source text.

This beta is deliberately kept separate from the stable-release Issue #1 closeout.
