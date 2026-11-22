# Phase V — Source-region classification and ownership review

## Scope

This is a **lossless line-level classification of the 91 PARTIAL raw entry-span candidates**, not a publication of verified editorial bodies.

**Source:** `index.html` SHA-256 `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`, repo main at `78bb708` at start.

The script `tools/classify_entry_regions.py` consumes the SHA-bound identity/declaration indexes and the Phase IV candidate span reconstruction. It reconstructs the original `<pre>` content as line fragments with exact Unicode-codepoint page offsets. The concatenated fragments must equal the original raw span exactly or the tool fails.

### Observed candidate classifications

| Category | Fragment count |
| --- | ---: |
| Entry declaration candidates | 91 |
| Criteria line candidates | 92 |
| Entry section-label candidates | 675 |
| Remaining entry-text candidates | 7,233 |
| Whitespace fragments | 8,158 |
| Running page-header candidates | 149 |
| Matching trailing page-number candidates | 298 |

**447 fragments** are eligible for *proposed* exclusion (149 headers, 298 footers). They are retained in the complete diagnostic report and recorded with source offsets in the committed compact review manifest.

The manifest includes all 91 entries with raw-span hashes and candidate cleaned-text hashes, **but it does not contain authoritative canonical bodies**. `VERIFIED=0`, `PARTIAL=91`.

Only exact top-of-page `GNOME Prompt Field Manual` lines are candidates for running-header exclusion. Only trailing numeric lines matching the physical page-card index are candidates for page-number exclusion. The classifier deliberately does not remove other text, normalize words, or assert who owns each section.

## Generate the detailed report

```sh
python3 tools/classify_entry_regions.py
python3 tools/classify_entry_regions.py --require-verified
```

The first command generates `workbench/data/region_classification_review.json` locally (not committed; line-level audit artifact).

The second returns **exit code 2**, as expected, until complete editorial ownership verification is achieved.

## Tests performed

- `python3 -m unittest discover -s tests -q`: **68 tests passed**, including seven new region-classification tests.
- `python3 tools/validate_manual.py --input index.html --strict-warnings`: passed.
- `python3 tools/reconcile_entry_lineage.py --input index.html --expect-pending 14 --expect-drafted 77 --expect-total 91 --expect-pages 315 --enforce`: passed.
- `python3 tools/audit_editorial_lineage.py --input index.html`: passed.
- Strict region verification: exit **2**, expected.

## Editorial review still required

- Assess all 447 exclusion proposals against the original printed pages, especially pages with unusual layout.
- Confirm 91 end-boundaries, not merely source round trips or next-declaration proximity.
- Classify unassigned source regions including section introductions, field cards, appendix, and blank pages.
- Validate that section labels and text belong to their claimed entry.
- Inspect the unexpected 92nd criteria-line candidate, rather than treating every `Criteria:` line as declaration evidence.
- Review any page artifacts not matched by exact running-header/page-number rules.
- Only then promote any body from `PARTIAL` to `VERIFIED`.

No canonical `index.html`, version, frozen docs, or existing workbench UI was changed.
