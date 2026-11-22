# Phase IV — Conservative raw body-span candidates

This development pass repairs the Phase IV candidate extractor to **reuse PR #19's real-source declaration locations**, not Gemini's synthetic colon/dash heading recognition.

## Verified scope

Baseline: canonical `index.html` SHA-256 `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`; repository main at `f53688b` before this branch.

- 91 reconciled entry IDs and 91 unique declaration starts.
- 91 **raw contiguous span candidates** with reproducible start/end page and Unicode-codepoint offsets.
- 91 round-trip span checks completed using the exact captured `<pre>` text.
- 91 per-span SHA-256 digests.
- **0 independently verified canonical entry bodies.** All 91 remain marked `PARTIAL`; none is `VERIFIED`.
- The final `AP-20` span stops at the Part IX beginning (page 307), not at the end of the historical appendix.
- Section heading transitions can end spans before the next entry heading.
- Source/identity/declaration hash mismatches and invalid declaration offsets fail closed.

## Run

```sh
python3 tools/reconstruct_body_candidates.py
python3 tools/reconstruct_body_candidates.py --require-verified
```

The first produces a **diagnostic** `workbench/data/raw_body_candidates.json` containing raw source spans. It is intentionally not committed or named `manual_entries.json`.

The second exits with code **2** while any body lacks full editorial ownership verification. This is expected; do not bypass it to claim completed extraction.

The committed `workbench/data/body_boundary_review.json` is a compact **review-only** manifest with 91 start/end offset pairs, span hashes, and boundary heuristic labels, but no complete raw text.

## Test evidence

Against the clean GitHub checkout at `f53688b`:

- Unit tests: **61/61 passed**, including seven new span-extraction checks.
- Canonical structural validation: passed.
- Canonical lineage reconciliation (14 pending, 77 drafted, 91 IDs, 315 pages): passed.
- Editorial audit: passed.
- Strict body verification flag: **exited 2 as expected**.

## Remaining limitations

A hash/round-trip confirms copied source text and offset integrity, not that every character belongs editorially to the entry. Candidate spans may include running headers, printed page numbers, or text outside the entry. Explicit region classification, end-boundary review, and independent ownership evidence are still required. In particular, this is **not an upgrade of the live reader or a verified full-body dataset**.

No changes to root `index.html`, frozen docs, existing lineage tools, release version, or workbench UI.
