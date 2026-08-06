# PTSP Entry-Lineage Baseline — 2026-08-06

## Scope

This report reconciles the production-state metadata in `index.html` with the pending-entry inventory, drafting briefs, and entry-ID occurrences in the embedded manual reader. It is structural evidence, not an editorial-completion judgment.

Canonical source SHA-256:

`b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`

## Source-reported state

The committed PTSP interface reports:

- 22 pending entries;
- 70 drafted entries;
- 92 total entries;
- 10 production batches;
- 5 special-caution entries;
- 315 embedded reader page cards.

## Extracted production structure

The deterministic reconciler found:

- 22 pending inventory rows and 22 unique pending IDs;
- 22 drafting briefs and 22 unique brief IDs;
- no pending inventory row without a matching brief;
- no drafting brief without a matching pending inventory row;
- 100 distinct ID-shaped tokens across the pending inventory, briefs, and embedded reader before classification.

## Non-entry token exclusions

Eight ID-shaped tokens are not manual entries and are excluded from the entry universe:

- `AP-00` — blank anti-prompt template placeholder;
- `X-00` — blank prompt-entry template placeholder;
- `EDT-01` through `EDT-06` — embedded test-case identifiers used inside entries.

These exclusions are explicit, versioned, and retained in generated evidence rather than silently discarded.

## Reconciled entry universe

After the eight exclusions, the source supports exactly **92 manual entry IDs**:

- 70 IDs occur in the embedded reader and are not listed as pending;
- 22 IDs are listed in the pending production inventory;
- 21 of those 22 pending IDs also occur in the embedded reader;
- one pending ID, `R-10`, is absent from the embedded reader under that number.

The 70 embedded non-pending IDs plus the 22 pending inventory IDs reconcile exactly to the source-reported total of 92.

## `R-10` resolution finding

The pending inventory identifies `R-10` as **Source-of-Truth Conflict Resolver** and states:

> Body already contains this entry as R-07. Requires renumbering fix, not new draft.

The structural evidence therefore supports a numbering-conflict classification. It does not support treating `R-10` as an entirely missing draft.

No automatic renumbering is performed by the reconciler. The authoritative identifier must be decided editorially and applied through a reviewed source change.

## Interpretation boundary

An entry-ID occurrence in the embedded reader proves presence only. It does not prove that the entry is:

- complete;
- current;
- approved;
- factually correct;
- adequately sourced;
- portable across model families or versions.

The reported pending state remains authoritative for production workflow until each entry passes its editorial and evidence gates.

## Enforced non-regression baseline

The `Entry Lineage` workflow now requires:

- 22 unique pending IDs;
- 70 embedded non-pending entry IDs;
- a 92-ID reconciled entry universe;
- 315 embedded page cards;
- one-to-one pending inventory and drafting-brief coverage;
- no blank inventory or brief IDs;
- explicit classification of known non-entry ID-shaped tokens.

The workflow uses read-only repository permissions, non-persistent checkout credentials, Python 3.11, deterministic unit tests, and SHA-bound JSON and Markdown evidence artifacts.

## Remaining version-lineage work

This baseline resolves the **entry-count arithmetic and inventory structure**. It does not resolve:

- why the workspace cites a v3 DOCX source while the embedded reader identifies itself as v9;
- which version is the authoritative editorial source;
- whether the 21 pending entries already present in the reader require replacement, revision, or evidence augmentation;
- the final identifier decision for the `R-07` / `R-10` collision;
- whether the stable public product is the workspace, the publication, or an explicit combined product.

Those decisions remain release blockers.
