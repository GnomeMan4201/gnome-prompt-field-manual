# Phase 12 — Current-source canonical body review foundation

**Status: PARTIAL_REVIEW_REQUIRED.** The current-source candidate inventory is complete, not the independent verification. No existing identity flag, manuscript, historical record, or editorial disposition changes.

## Pinned source and outputs

Baseline main: `cce15ddb8981a4b4a160d4d2caf1c5e91aad659b` (merged Phase 11 PR #50), tree `b54f6b71a9d2ce8c377c01001f914ccd490ab6c2`.

| Artifact | SHA-256 |
| --- | --- |
| Canonical `index.html` | `fd76d2727545b202968664cbba4137537859536c979b3597ab943abd283858cf` |
| Standalone reader | `cfa5a6bff04cc1d4ada3c1ce410ee6bc8893db2bc903599927de15115ca95393` |
| Historical PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |
| Live identity index | `cfda18b9934fb9e27fc4f4d6b37aa4fa4a2370690390255a5acc9ce1ccd0a61a` |
| New [current body review](../workbench/data/current_body_review.json) | `da2c6a03d12f1af1e9ed8363aea7a66666c8cdda7353683b18d934e323135336` |

The historic declaration, boundary and region manifests and 629-decision adjudication queue remain bound to the earlier Batch 3 source (`1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`). The new manifest binds their exact bytes as separate provenance, not current authority. Both Batch 5 and Batch 9 crosswalks were checked against actual candidate headings and physical start pages. SEC-05 stays editorially pending independently of its reconstructed span.

## Measured candidate coverage

| Measure | Result |
| --- | ---: |
| Physical pages | 315 |
| Exact-heading-plus-adjacent-Criteria declaration candidates | 91/91 |
| Missing / duplicate candidate IDs | 0 / 0 |
| Raw body spans reconstructed | 91/91 |
| Independently verified bodies | 0/91 |
| PARTIAL / UNRESOLVED / CONFLICT | 91 / 0 / 0 |
| Advisory identity title differences | 31 |
| Entries missing expected section-label markers | 0 |
| Entries with repeated expected section-label markers | 1 |
| Proposed running-header/footer exclusions | 447 |
| Pending decisions in regenerated compatible review queue | 629 |
| Additional unassigned source regions needing review | 9 |

The 629 count is coincidentally equal to the historical queue count. The regenerated current queue has a different source and manifest hash; no historical review outcome transfers automatically. It contains 447 exclusion proposals, 91 end-boundary decisions, and 91 body-ownership decisions. The nine unassigned regions (front matter, seven part introductions, and Part IX/appendices) are separate pending partition decisions and are not silently counted as body content or included in the 629.

## Implementation and review method

[build_current_body_review.py](../tools/build_current_body_review.py) reuses the existing heading discovery, span reconstruction, region classifier, and fail-closed adjudication validator. The historical scripts and files remain unchanged. The new packet contains a heading candidate and original heading line; half-open Unicode-codepoint offsets within decoded page `pre` text; adjacent entry IDs; per-page slice SHA-256; raw span SHA-256; proposed header/footer exclusions and proposed-clean text hash; section-marker offsets; title disagreements; and explicit pending ownership/end-boundary statuses. The proposed clean hash is a byte-copy-with-proposed-exclusions result, not a normalized canonical prompt or verified semantic text. Page-by-page marker inspection avoids false missing headings caused by concatenation of a trailing physical page number and the next page's first line. An adjacent Criteria declaration, not incidental identifier occurrence, identifies a candidate heading. A source partition check accounts for every codepoint exactly once as candidate or unassigned region.

Section profiles are candidate review checklists for standard entries, chains and anti-prompts, not an independently established editorial requirement for every entry. Presence of a marker does not prove completeness, correct ownership, or useful content. SEC-06 has two explicit follow-up headings (before/after evaluation), recorded as repeated markers rather than silently merged. The 31 advisory title differences are exposed for review; many advisory strings are cross-reference prose, not headings. They remain untouched in the existing index. The generator cannot authenticate reviewer identity or promote any body. No decisions have been supplied by an independent reviewer.

## How to reproduce and review

From a clean checkout:

```sh
python tools/build_current_body_review.py --verify
python tools/build_current_body_review.py --entry T-01 > /tmp/T-01-review.json
python tools/build_current_body_review.py --output /tmp/current-body-review.json \
  --manifest /tmp/current-region-manifest.json --queue /tmp/current-adjudication-queue.json
python tools/adjudicate_entry_regions.py --manifest /tmp/current-region-manifest.json \
  --review /tmp/current-adjudication-queue.json
```

The last command intentionally exits 2 on the pending queue; this is not a failed reconstruction. All output destinations must be new files. The single-entry command returns exact source slices and exclusion evidence for a reviewer with specific questions about alternatives and ambiguous ownership. Review the raw excerpts against the rendered page, neighboring sections and established subject crosswalks. Record evidence, rationale, reviewer identity and timestamp for each actual decision in a separate review artifact. Confirm the front/back matter and transition partitions independently. A reviewer may reject any proposed exclusion or boundary; do not force acceptance. A later promotion gate must be separately designed and authorized, including review provenance and rejected decisions; the existing queue validator checks record structure, not independent identity or verified text.

For example SEC-05 is bounded from page 179 offset 0 through page 187 offset 683 exclusive, before the SEC-06 heading. Its body candidate does not imply satisfaction of the frozen independent behavioral requirement. P-05/P-06/P-07 preserve their distinct subjects at shared boundaries. The final AP-20 candidate ends at Part IX page 307 offset 0.

## Validation

- All 47 Python test modules executed in isolated processes: 325 tests, zero skips or failures. Eight new focused tests passed, including source mismatch, offset, overlap, identity, marker removal, exclusion removal, unauthorized promotion, historical binding, and unassigned-region negative controls. Existing protected artifact bytes compared against the immutable main baseline.
- Dedicated Reactor: 131/131. Strict manual validation: zero errors and warnings. Editorial lineage: 34/34. Entry reconciliation: 1 pending / 90 non-pending / 91 / 315, one batch and body coverage 0. Locked replication kit: both hashes and eight harness tests passed.
- A dedicated Current Body Review workflow reproduces the packet and executes its negative controls. Browser engines were not rerun because both reader files are byte-identical; prior browser results remain historical. New PR CI is a separate gate.

This is an additive candidate/review foundation, not canonical ownership adjudication. Future manuscript/identity changes must deliberately regenerate a new current-source packet and preserve this phase's pinned evidence; baseline-specific preservation assertions must be updated only with the new authorized source transition, never by relabeling past evidence. No automatic merge or independent verification promotion is authorized.
