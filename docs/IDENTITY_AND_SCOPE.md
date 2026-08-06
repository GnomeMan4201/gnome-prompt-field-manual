# Identity and Scope

## Repository identity

The repository is named `gnome-prompt-field-manual`, but the current public `index.html` is not a neutral final-manual landing page. It identifies itself as **PTSP — Pending Entry Draft Plan** and combines two surfaces:

1. a production workspace for completing and reviewing pending manual entries;
2. an embedded reader containing a complete GNOME Prompt Field Manual source representation.

Until the lineage review in issue #3 is complete, the supported identity is therefore:

> **GNOME Prompt Field Manual production workspace and embedded reader**

It must not be described as a final stable manual release.

## Current source-reported state

The committed PTSP interface reports:

- 22 pending entries;
- 70 drafted entries;
- 92 total entries;
- 10 production batches;
- an embedded GNOME Prompt Field Manual v9 reader containing 315 pages.

The same interface also names `GNOME_Prompt_Field_Manual_v3_final.docx` as a source. The relationship among the v3 filename, v9 embedded reader, PTSP entry counts, repository version, and any prior release artifacts has not yet been proven.

These values are source-reported production metadata. They are not independently verified completion claims.

## Canonical boundaries

For the `1.0.0-rc.1` baseline:

- `index.html` is the canonical committed workspace artifact.
- The repository version describes the repository package and validation baseline, not the embedded manual's editorial version.
- PTSP pending/drafted state is distinct from publication-version state.
- Structural validation does not establish editorial completeness, factual correctness, prompt portability, accessibility conformance, or external-link health.
- Existing embedded source material remains preserved until the version and entry inventory is reconciled.

## Stable-release decision

A stable release requires an evidence-backed decision among these outcomes:

1. **Workspace product:** retain PTSP as the primary application and publish the final manual separately.
2. **Publication product:** replace the public entry point with the final manual and archive PTSP as production history.
3. **Combined product:** keep both surfaces but make the workspace/reader relationship explicit, versioned, and navigable.

The decision must be reflected consistently in the HTML title, primary heading, README, version files, release notes, and published URL.

## Open reconciliation work

Issue #3 tracks the required inventory and version-lineage analysis. No stable-release label should be created until that issue establishes:

- which of the 92 entries exist in the embedded source;
- which 22 entries remain genuinely pending;
- whether any entries are duplicated, superseded, or omitted;
- the authoritative editorial version;
- the supported public entry point.
