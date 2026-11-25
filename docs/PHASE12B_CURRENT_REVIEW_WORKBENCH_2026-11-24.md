# Phase 12B — Current-source review workbench

**Status:** implemented review interface; independent adjudication not performed. The live identity inventory remains 0/91 independently verified bodies, 90 non-pending semantic identifiers and SEC-05 pending. PR #53 corrects the manuscript and rebuilds its review packet.

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

Pre-correction baseline main: `03285ac8c57bfa8c40bddd2b2c53c0692927f8d3`, tree `b655aca7f0e0fc6ccc192016165ed7a73cba47c5` (merged PR #51).

Reader and packet for the SEC-08 and SEC-05 status correction. These hashes identify the exact inputs used by the current workbench.

| Artifact | SHA-256 |
| --- | --- |
| Canonical HTML | `fef4f9812014d1970d67151db49ee0aff82b03ea19dafc5a70a579b90a624625` |
| Standalone reader | `1b33983d0d5346f0f140cc4558641374c8305e91d60315b52f825ce183b9b9b8` |
| Historical PDF | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |
| Current candidate packet | `db6e1a5e0380be3b791e89d68aab60d5fc50ec735d60c4ec142b0900b0c1133b` |
| Live identity index | `55a6f03bdab55a57248fcce54df424ee3d4ff7656328af694fc101d9e8c4efd4` |

The workbench binds each session to its source packet. After a manuscript correction, reproduce the packet and update the pins before collecting decisions. Retain exports against the original source. A stale tab must reload before saving over a newer session.

## Validation and limitations

At `7d6c5a8`, 336 Python tests passed. All seven GitHub Actions workflows passed, including reader and review-workbench tests in Chromium, Firefox and WebKit. The two-tab test verifies that a stale save preserves the draft and the first tab’s recorded decision. See the [revision checks](https://github.com/GnomeMan4201/gnome-prompt-field-manual/commit/7d6c5a8e13f480ddd9fa86109ecd18910f2c40df/checks).

The SEC-08 and SEC-05 status revision passed 338 local Python tests. The [paired walkthrough](AP06_SEC08_PAIRED_WALKTHROUGH.md) exercises the two reading instructions with the same supplied evidence.

The source packet reproduces with 91 candidate bodies and zero independently verified bodies. Screen-reader acceptance, independent adjudication and SEC-05 remain open.
