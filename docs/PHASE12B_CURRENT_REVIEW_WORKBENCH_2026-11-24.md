# Phase 12B — Current-source review workbench

**Status:** implemented review interface; independent adjudication not performed. The live identity inventory remains 0/91 independently verified bodies, 90 non-pending semantic identifiers and SEC-05 pending. No manuscript or historical review record is changed.

## Entry point

Serve the repository root, for example:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/workbench/adjudication/current/`. The same relative path is suitable for the GitHub Pages reader deployment. HTTPS or localhost is required for Web Crypto. The historic workbench at `workbench/adjudication/index.html` remains untouched and uses its original Batch 3 source. Do not import its queue into the current workbench.

## Review workflow

1. Boot verifies the exact current candidate packet SHA-256, then the canonical HTML SHA-256, all 315 page IDs, all 91 candidate slice/raw-span hashes and all nine unassigned-region hashes. A mismatch disables the interface; no override is provided.
2. Filter by entry ID, decision type or record status. The queue contains 447 proposed header/footer exclusions, 91 end-boundary decisions, 91 ownership decisions, 31 title discrepancies and nine unassigned regions: **669 records**. The first 629 correspond to the current regenerated compatible adjudication queue, not the historical 629-decision queue.
3. Select a record. The original page highlights the exact proposal or end coordinate, with page-local Unicode codepoint offsets and neighboring entry IDs. The candidate preview preserves raw source text, removing only exclusions the reviewer has accepted. Page labels in the preview are presentation aids, not part of the reconstructed source. Pending and rejected exclusions remain visible. Title records compare advisory versus actual heading candidates; region records display the unassigned range.
4. Accept, reject or defer. A completed decision requires a self-declared reviewer identifier, nonblank rationale, evidence references and UTC timestamp. Deferring removes the completion metadata. Rejection records disagreement, not an automatic replacement span or title. Decisions do not change canonical HTML, the live identity index, the candidate packet or independent body status.
5. Recorded sessions are saved to browser local storage where available, under the packet-specific key. Reload resumes the recorded state. Export a JSON backup; unrecorded form edits are not included. Import checks exact schema, source, packet, manifest, record order, decision vocabulary and review metadata before replacing the current session. Failed imports retain the existing session. The browser does not authenticate the reviewer; no server write or automatic promotion exists. Local storage is not encrypted or shared between browsers; avoid sensitive notes and retain an authorized export. Import/export is limited to 8 MiB.

## External validation and interoperability

```sh
python tools/validate_current_review_session.py gnome-current-review-session.json
python tools/validate_current_review_session.py gnome-current-review-session.json \
  --queue-out /tmp/current-compatible-review.json
```

The validator regenerates the candidate basis using the existing current-source reconstruction. The optional queue output contains the 629 core decisions converted to the existing adjudication schema; the 31 title and nine region decisions remain in the full session, which must be preserved. Output refuses to overwrite an existing file. The validator reports review-record completeness only, always zero independently verified bodies. Neither a syntactically valid record nor all records being completed proves independent ownership, reviewer identity or correctness. A separate human/independent decision and promotion process remains required. Rejecting a proposal is not resolved by recording the rejection.

## Source bindings and preservation

Baseline main: `03285ac8c57bfa8c40bddd2b2c53c0692927f8d3`, tree `b655aca7f0e0fc6ccc192016165ed7a73cba47c5` (merged PR #51).

| Artifact | SHA-256 |
| --- | --- |
| Canonical HTML | `fd76d2727545b202968664cbba4137537859536c979b3597ab943abd283858cf` |
| Standalone reader | `cfa5a6bff04cc1d4ada3c1ce410ee6bc8893db2bc903599927de15115ca95393` |
| Historical PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |
| Current candidate packet | `da2c6a03d12f1af1e9ed8363aea7a66666c8cdda7353683b18d934e323135336` |
| Live identity index | `cfda18b9934fb9e27fc4f4d6b37aa4fa4a2370690390255a5acc9ce1ccd0a61a` |

The only existing file edited is README for discoverability. New workbench files are a separate route under the existing adjudication directory, sharing the historic stylesheet without modifying it. The historical app, manifests, archives, frozen briefs, crosswalks and reader files are unchanged. Future authorized source transitions require a newly reproduced candidate packet and updated pinned hash/decision inventory; old local sessions must not be rebound automatically.

## Validation and limitations

- 331/331 Python tests across 48 isolated modules, zero skips or failures; six added session validation tests. Includes existing 131 Reactor regressions and historical preservation tests.
- Direct Node state test passed using the exact canonical source, all candidate/gap hashes, 669 keys, Unicode offsets, accepted versus rejected exclusions, defer, metadata and source mutations, and cross-runtime Python validation of a synthetic session. JavaScript syntax checks passed.
- Current body packet reproduced; strict manual validation zero errors/warnings; editorial lineage 34/34; entry reconciliation unchanged (1 pending / 90 non-pending / 91 / 315, one batch). No independent reviewer decisions were collected.
- Local Playwright browser installation attempts were interrupted in the resource-limited sandbox. The full browser workflow was **not** executed locally. A dedicated Chromium/Firefox/WebKit CI matrix exercises boot, filters, source selection, record save/reload, accepted/rejected/deferred decisions, source-bound export and Python validation, stale imports, tampered source/packet rejection and mobile/desktop/reflow widths. CI and independent review are separate gates; no browser conformance or accessibility certification is claimed.

This workbench enables review, not verified-body export. Keep the release candidate status and the open SEC-05 requirement intact.
