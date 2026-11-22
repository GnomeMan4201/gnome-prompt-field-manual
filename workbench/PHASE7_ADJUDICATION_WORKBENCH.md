# Phase VII — Source-bound adjudication workbench

This is a **repaired** implementation based on the uploaded Gemini Phase VII prototype. It is a separate, static GitHub Pages review tool and does not modify the canonical reader.

## Open

Host the repository with a local HTTP server or GitHub Pages and open:

`workbench/adjudication/index.html`

It loads the **actual authoritative nested Phase VI queue** from `workbench/data/adjudication_queue.json`, which is generated unmodified by:

```sh
python3 tools/adjudicate_entry_regions.py \
  --manifest workbench/data/region_review_summary.json \
  --queue workbench/data/adjudication_queue.json
```

The queue contains 91 entries, 447 candidate exclusions, 91 end-boundary decisions, and 91 ownership decisions. **All 629 decisions begin pending.**

## Source verification

The UI requests `../../index.html`, computes the SHA-256 of the received **bytes** using the Web Crypto API, and compares it against the queue's source hash. It then parses all 315 original page cards. The same source may be provided through local file input.

Until the hash and page count agree, completed decisions are blocked. No button can simply set the verification flag. Use HTTPS or `localhost` because Web Crypto requires a secure context.

Source highlighting slices page text using codepoint offsets. The source map measures each page separately, avoiding comparisons of offsets from different pages.

## Decision workflow

1. Open **Queue**, choose a pending record.
2. Inspect the exact original source context in **Microscope**. Boundary records show a position, not a region to delete.
3. Record an accept/reject decision with reviewer ID, rationale, and source evidence; or defer as `NEEDS_REVIEW`.
4. Export from **Continuity** to preserve your work.
5. Re-import the JSON after another session; the application checks source and manifest hashes, entry order, all immutable spans, and required review fields.
6. From the repository root, independently verify your export:

```sh
python3 tools/adjudicate_entry_regions.py \
  --manifest workbench/data/region_review_summary.json \
  --review path/to/gnome-reviewed-queue.json
```

**Initial queue verification exits 2** with 629 pending and zero approved bodies, as designed. The browser does not automatically complete, sign, or certify any records. The Python tool checks review-record completeness, not reviewer identity authenticity or whether editorial determinations are correct.

## Tests executed

- `python3 -m unittest discover -s tests -q` — **84/84 passed** (77 existing, 7 new).
- Structural validator: passed.
- Identity reconciliation (14 pending, 77 non-pending, 91 total, 315 pages): passed.
- Editorial audit: passed.
- Python validator against the exported-by-generator baseline queue: `valid=true`, `reviewComplete=false`, `pendingDecisions=629`, `approvedBodies=0`, exit 2.
- JavaScript parsing/syntax checks on all three application scripts: passed.
- Source-markup compatibility inspection: all 315 canonical `<pre>` elements lack a leading newline that HTML parsing could otherwise strip.

**Not executed:** end-to-end graphical browser interaction, cross-browser accessibility, downloaded queue to Python round trip, or formal security review. These remain acceptance gates before production use.

## Limitations

- No authentication, reviewer signature, server-side persistence, or independently authenticated timestamps.
- Reviewer decisions and evidence references are local assertions; they are not checked for substantive truth.
- Proposed exclusion regions do not prove end-boundary correctness, clean text ownership, or canonical body verification.
- No full entry-body dataset is issued. **Verified bodies remain 0/91.**
- Part introductions and text outside reconstructed raw entry spans still require separate editorial ownership coverage.
- On narrow screens the microscope panels stack; mobile usability still requires device testing.

The canonical root `index.html`, release identity, and editorial source remain unchanged.
