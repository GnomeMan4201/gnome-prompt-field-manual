# Phase III — actual-source declaration discovery

**Status: 91/91 unique declaration candidates located. 0/91 full entry bodies independently validated.**

The earlier Gemini Phase III extractor required a punctuation separator such as `S-01: Title`. The canonical 315-page reader actually uses headings like `T-01 Idea Stress-Test` followed by a `Criteria:` line. Running its original declaration expression against the real manual yielded zero declarations.

The new `tools/discover_entry_boundaries.py` performs a strict structural discovery pass against the current committed `index.html` and the merged, SHA-bound identity inventory. A candidate must meet **all** of the following:

- Its entry ID is present in the reconciled 91-identity universe.
- A line starts with that ID followed by its candidate title.
- The **next nonempty line** begins `Criteria:`.
- The occurrence is within manual pages 1–306. Part IX quick-reference field cards and the historical editorial appendix are excluded.
- The input HTML SHA-256 matches the identity inventory's source hash.
- The final set has exactly 91 unique IDs, no omissions, and no duplicates.

Results with the canonical HTML source hash `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`:

| Measure | Observed |
| --- | ---: |
| Page cards | 315 |
| Reconciled identities | 91 |
| Declaration candidates | 91 |
| Unique matched IDs | 91 |
| Missing/duplicate IDs | 0 / 0 |
| Independently verified full entry bodies | **0** |

The active `W-04 Over-Smoothing Detector` is found on page 48, `R-07 Competing Hypotheses Table` on page 91, and `R-10 Source-of-Truth Conflict Resolver` on page 93.

The dataset `workbench/data/entry_declaration_candidates.json` is a **candidate-heading location index**, not a verified body dataset, and it must **not** be substituted for `manual_entries.json`. It contains source and inventory hashes, 91 candidate start offsets measured in Unicode code points within each rendered `<pre>`, and rejected heading-like locations.

## Verification executed

In a clean repository checkout at source commit `b5dfabd`:

- `python3 tools/discover_entry_boundaries.py` — success, 91 unique declaration candidates.
- `python3 -m unittest discover -s tests -q` — 54/54 passed (47 existing plus seven new checks).
- `python3 tools/validate_manual.py --input index.html --strict-warnings` — zero errors and warnings.
- `python3 tools/reconcile_entry_lineage.py --input index.html --expect-pending 14 --expect-drafted 77 --expect-total 91 --expect-pages 315 --enforce` — passed.
- `python3 tools/audit_editorial_lineage.py --input index.html` — passed.

## Still unresolved

The next engineering stage must adjudicate accurate end boundaries, page header/footer contamination, section introductions and the final anti-prompt-to-field-card transition, and source span ownership. A correct declaration count cannot prove any full text body belongs to the detected entry.

No canonical `index.html`, original editorial tooling, publication version, or live reader was modified.
