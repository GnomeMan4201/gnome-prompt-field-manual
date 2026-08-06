# Identity and Scope

## Repository identity

The public `index.html` identifies itself as **PTSP — Pending Entry Draft Plan** and combines:

1. a production workspace for completing and reviewing manual entries;
2. an embedded GNOME Prompt Field Manual reader.

The supported identity is:

> **GNOME Prompt Field Manual production workspace and embedded reader**

It is not yet a final stable manual release.

## Verified production state

The deterministic entry-lineage baseline confirms:

- 22 pending inventory IDs;
- 22 matching drafting briefs;
- 70 embedded non-pending entry IDs;
- 92 reconciled manual entry IDs;
- 10 production batches;
- 5 special-caution entries;
- 315 embedded reader page cards.

Eight additional ID-shaped tokens are templates or embedded test-case identifiers: `AP-00`, `X-00`, and `EDT-01` through `EDT-06`.

## Resolved version roles

The apparent v3/v9 conflict is a role distinction:

- **v3 master:** the editable manuscript and production-planning authority named throughout PTSP. It defines planned numbering and pending/drafted disposition. The named DOCX is not committed.
- **v9 reader:** the rendered publication snapshot embedded in `index.html`, generated from a v9 PDF. It is the observation source for the currently rendered body, not an editable editorial master.
- **1.0.0-rc.1:** the repository/package validation baseline, not the manuscript or publication version.

The repository does not prove the complete editorial transformation history between v3 and v9 because the underlying editable documents are absent. See [Editorial Lineage and Identifier Decision — 2026-08-06](EDITORIAL_LINEAGE_DECISION_2026-08-06.md).

## Resolved numbering authority

The PTSP instructions explicitly define the planned numbering and identify the rendered-body mismatch:

- Competing Hypotheses Table currently appears as `R-06`, but planned numbering assigns it `R-07`.
- Source-of-Truth Conflict Resolver currently appears as `R-07`, but planned numbering assigns it `R-10`.
- `R-10` is not a missing substantive entry and must not receive a duplicate body.

The frozen correction is therefore:

- `R-06` → `R-07` for Competing Hypotheses Table;
- `R-07` → `R-10` for Source-of-Truth Conflict Resolver.

The decision is resolved; physical mutation of the embedded reader and every affected cross-reference remains a dedicated release-blocking pass.

## Canonical boundaries

For the `1.0.0-rc.1` baseline:

- `index.html` is the canonical committed workspace artifact.
- PTSP production state is distinct from publication-version state.
- Entry presence is distinct from editorial completion.
- The v3 master is the strongest committed authority for planned numbering and pending state.
- The embedded v9 reader is the strongest committed evidence of the currently rendered body.
- Structural and lineage validation do not establish factual correctness, prompt portability, accessibility conformance, external-link health, or evidence quality.

## Stable public-product decision

A stable release still requires choosing and implementing one public boundary:

1. **Workspace product:** retain PTSP as primary and publish the final manual separately.
2. **Publication product:** publish the corrected manual as primary and archive PTSP as production history.
3. **Combined product:** retain both surfaces with explicit navigation and independent version metadata.

## Remaining release blockers

Issue #3 continues to track:

- complete R-06/R-07/R-10 renumbering and cross-reference repair;
- editorial disposition of remaining pending entries;
- final public-product boundary;
- accessibility and browser validation;
- stable-release versioning and publication evidence.
