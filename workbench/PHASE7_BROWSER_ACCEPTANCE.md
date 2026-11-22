# Phase VII — Live browser acceptance evidence

**Test date:** November 22, 2026.

**Scope:** Temporary HTTPS HTTP-server instance of the Phase VII feature branch from PR #23. This report does **not** claim independent editorial verification or completion of all browser-to-Python round-trip requirements.

## Live browser smoke test

A browser automation agent navigated to `workbench/adjudication/index.html` on a temporary hosted copy of the PR branch and observed:

| Check | Browser observation |
| --- | --- |
| Workbench loads and initializes | Passed |
| Review records | 629 pending, 0 completed |
| Source SHA-256 | Verified against `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19` |
| Parsed original page cards | 315 |
| Source microscope | First T-01 proposed exclusion selected, page 9, offsets [1069,1126) |
| Source highlight | Appeared in original source pane, 57-character segment |
| Decision editor | Three exclusion choices and reviewer, rationale, evidence controls visible |
| Errors | No visible browser errors during tested steps |

The automated test then entered an **ephemeral, non-editorial QA fixture** for the first T-01 proposal:

- `REJECT_EXCLUSION`
- reviewer: `QA-TEST-ONLY`
- rationale: `Temporary browser export/import QA fixture; not an editorial finding.`
- evidence: `qa-fixture:page-9`

On clicking **Record decision**, the workbench showed **1/629 complete**, **628 pending**, and the correct QA ledger entry.

The browser then opened Continuity and activated **Export Python-compatible queue**. A blob download link with filename `gnome-reviewed-queue.json` was triggered.

**Unverified:** The browser automation environment did not expose the downloaded JSON bytes or permit selecting that downloaded file for import, so an exact *browser-export → Python validation → browser reimport* round trip was **not executed**.

## Independent Python schema compatibility check

Using the real Phase VI baseline queue and authoritative Python validator, a separate Python test fixture with the same decision category, reviewer, rationale, and evidence produced:

```text
valid: true
reviewComplete: false
approvedBodies: 0
completedDecisions: 1
pendingDecisions: 628
issues: []
```

This is a **structurally equivalent independent fixture**, not the browser's downloaded JSON file. It demonstrates that the record shape is accepted by Python, not that the exact browser export has passed cross-tool validation.

## Repository tests and remaining release gates

PR #23 had passed 84/84 Python unit tests, canonical structural and editorial gates, and JavaScript syntax checks before this live-browser session. The test browser demonstrated first-load, source verification, source selection, temporary decision save, progress counter, and export initiation.

Still needed for full acceptance:

- Capture the exact browser-exported file bytes and pass them to the authoritative Python validator.
- Reimport the same downloaded file in a browser and confirm the edited review record persists.
- Test source-hash mismatch and malformed import handling interactively.
- Test a mobile viewport and keyboard-only review workflow.
- Validate enough source spans to assess Unicode normalization and unusual page layouts beyond the first T-01 span.

Do not count QA-TEST-ONLY as a real editorial decision or commit this temporary fixture to the canonical queue.

**Current production baseline remains 629 pending human decisions and 0/91 verified canonical bodies.**
