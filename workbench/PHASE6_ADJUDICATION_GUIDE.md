# Phase VI — Human editorial adjudication queue

This phase implements **a review workflow**, not an automated certification engine. The canonical `index.html`, historical records and release status remain unchanged.

## Grounded baseline

Source commit: `fda9a4b` (after merged PR #21). The Phase V manifest contains 91 PARTIAL entry spans, 447 candidate exclusions (149 running headers and 298 page-number footers), and **0 independently verified editorial bodies**.

The queue generator binds every decision to the SHA-256 of the exact region review manifest and records the source HTML SHA-256. It generates **629 independent decisions**, all initially `NEEDS_REVIEW`:

| Required human review | Count |
| --- | ---: |
| Provisional header/footer exclusion | 447 |
| End-boundary adjudication | 91 |
| Entry-body ownership adjudication | 91 |
| **Total** | **629** |

## Generate review queue

```sh
python3 tools/adjudicate_entry_regions.py \
  --manifest workbench/data/region_review_summary.json \
  --queue workbench/data/adjudication_queue.json
```

The generated queue is intentionally **not committed**. A reviewer should inspect the corresponding printed page, source offsets, and surrounding context before changing any record.

Each exclusion record uses one of `ACCEPT_EXCLUSION`, `REJECT_EXCLUSION`, or `NEEDS_REVIEW`; end-boundaries use `ACCEPT_BOUNDARY`/`REJECT_BOUNDARY`/`NEEDS_REVIEW`; body ownership uses `ACCEPT_OWNERSHIP`/`REJECT_OWNERSHIP`/`NEEDS_REVIEW`.

For every non-pending decision supply:

- `reviewer`: an attributable reviewer name or stable identifier
- `rationale`: a substantive explanation of the source evidence
- `reviewedAt`: the review timestamp supplied by the reviewer
- `evidence`: one or more meaningful source references, ideally page and offset or a stable supporting editorial artifact

Do not edit the immutable `span`, `proposalId`, `sourceHtmlSha256`, `manifestSha256`, entry ID, raw span hashes, or boundary locations. On a source change, regenerate and re-adjudicate affected evidence. The tool checks that supplied metadata is present and bound to an unchanged source; it **does not independently authenticate reviewers, validate timestamps, or establish that explanations are correct**.

## Validate review records

```sh
python3 tools/adjudicate_entry_regions.py \
  --manifest workbench/data/region_review_summary.json \
  --review workbench/data/adjudication_queue.json
```

Before any review, this must exit **2** and report zero completed decisions, 629 pending. Once every record contains a valid explicit reviewer decision, the validator can report that the *review-record completeness gate* passed.

**Even a complete decision queue does not promote bodies to VERIFIED.** This tool always reports `approvedBodies: 0`; a separate audited editor must reconcile contradictory decisions, assess retained text and source coverage, sign off the correct region ownership, and then produce certified canonical-body output.

## Tests performed

- `python3 -m unittest discover -s tests -q`: **77 passed** (68 prior plus 9 new adjudication tests).
- Canonical structural validation: passed.
- 14/77/91/315 reconciliation: passed.
- Editorial lineage audit: passed.
- Generated queue: 91 entries, 447 proposed exclusions, 91 end-boundary decisions, 91 body-ownership decisions.
- Unreviewed queue verification: intentionally failed closed with exit code **2**.

## Unresolved work

This phase does not review the 629 cases on a human's behalf. An independent reviewer must adjudicate actual content ownership, section introductions and unassigned regions, and potential false exclusion candidates; the current decisions remain `NEEDS_REVIEW`. The source-manifest binding enforces traceability, not editorial correctness.

**Canonical entry bodies verified: 0/91.**
