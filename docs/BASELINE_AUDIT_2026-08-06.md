# Auditable Baseline Report — 2026-08-06

## Judgment

The repository now has a reproducible structural quality baseline suitable for continued closeout work. It is **not** a final stable manual release because the PTSP production state, embedded-reader editorial version, and source lineage remain unresolved.

## Canonical artifact measured

- Artifact: `index.html`
- SHA-256: `b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`
- Size: 2,208,371 bytes
- Parsed elements: 2,399
- Unique IDs: 348
- Headings: 8
- Internal anchors: 23
- Scripts: 1
- Stylesheets: 1 embedded style block
- Structural errors: 0
- Structural warnings: 0

The validator is deterministic and network-free. These results cover committed HTML structure and local references only.

## Semantic repair applied

The original source was preserved by hash before a bounded transformation:

- Original SHA-256: `b576496ce0f496536b50e07526c081174e032cd38eb8f4659b67e517c3f950d5`
- Output SHA-256: `b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`

The transformation changed element semantics without rewriting section text:

- added one meta description;
- converted the visible PTSP title to the single document `h1`;
- marked the primary workspace container as the single main landmark;
- converted seven section-title spans to `h2` headings;
- added margin resets so heading semantics did not introduce default-layout drift.

The generated diff was constrained to `index.html`, passed `git diff --check`, passed strict structural validation, and was committed through a one-time branch-only migration step. The write-capable migration workflow and migration script were then removed.

## Automated evidence

The permanent `Manual Quality` workflow now uses:

- read-only repository permissions;
- non-persistent checkout credentials;
- Python 3.11;
- maintained GitHub Actions runtimes;
- syntax compilation;
- eight validator unit tests;
- bounded DOM inventory output;
- strict validation where warnings fail the job;
- SHA-bound JSON and Markdown evidence artifacts.

The final branch workflow completed successfully after all temporary write authority was removed.

## Identity finding

The public artifact is **PTSP — Pending Entry Draft Plan**, combining:

1. a production workspace;
2. an embedded GNOME Prompt Field Manual v9 reader.

The interface reports 22 pending entries, 70 drafted entries, 92 total entries, 10 batches, and 315 embedded reader pages. It also identifies `GNOME_Prompt_Field_Manual_v3_final.docx` as a source. Those values are source-reported metadata and do not prove the authoritative editorial version or entry completeness.

Issue #3 tracks the required v3/v9 and 92-entry reconciliation.

## Verified completion in this baseline

- Repository identity is stated honestly as a production workspace and embedded reader.
- Structural validation is reproducible from a clean checkout.
- Validation success and failure paths are tested.
- Generated evidence is bound to the exact canonical source hash.
- Correction, evidence, model-sensitivity, accessibility, and release gates are documented.
- No temporary write-capable migration machinery remains in the proposed change set.
- Release-candidate status is explicit in `README.md`, `VERSION`, and `CHANGELOG.md`.

## Work that remains before stable release

- Reconcile v3 source, v9 embedded reader, repository package version, and any historical release artifacts.
- Produce an exact inventory of all 92 entries and prove the status of the 22 reported pending entries.
- Decide whether the stable public product is the workspace, the manual publication, or an explicit combined product.
- Add source-grounded, versioned examples and counterexamples.
- Review technical claims for evidence, scope, and model/runtime sensitivity.
- Complete accessibility testing and a current Chromium, Firefox, and WebKit browser matrix.
- Record the final release commit, source hash, limitations, and independent editorial review.

## Final baseline status

**Release candidate baseline: pass.**

**Final stable publication: not yet eligible.**
