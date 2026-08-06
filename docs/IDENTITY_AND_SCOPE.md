# Identity and Scope

## Repository identity

The repository is named `gnome-prompt-field-manual`, but the current public `index.html` is not a neutral final-manual landing page. It identifies itself as **PTSP — Pending Entry Draft Plan** and combines two surfaces:

1. a production workspace for completing and reviewing pending manual entries;
2. an embedded GNOME Prompt Field Manual reader.

The supported identity is therefore:

> **GNOME Prompt Field Manual production workspace and embedded reader**

It must not be described as a final stable manual release.

## Verified production state

The deterministic entry-lineage baseline confirms that the committed PTSP interface contains:

- 22 pending inventory IDs;
- 22 matching drafting briefs;
- 70 embedded non-pending entry IDs;
- a reconciled universe of 92 manual entry IDs;
- 10 production batches;
- 5 special-caution entries;
- 315 embedded reader page cards.

Eight additional ID-shaped tokens are explicitly excluded because they are templates or embedded test-case identifiers: `AP-00`, `X-00`, and `EDT-01` through `EDT-06`.

Twenty-one pending IDs also occur in the embedded reader. Presence does not override pending status. The remaining pending ID, `R-10`, is documented by the source as a numbering conflict with an existing `R-07`, not as a wholly absent draft.

See [PTSP Entry-Lineage Baseline — 2026-08-06](ENTRY_LINEAGE_BASELINE_2026-08-06.md) for the exact interpretation and enforcement boundary.

## Unresolved version lineage

The interface identifies the embedded reader as v9 while also naming `GNOME_Prompt_Field_Manual_v3_final.docx` as a source. The relationship among the v3 filename, v9 reader, repository package version, and any prior release artifacts remains unresolved.

The verified 92-entry arithmetic does not establish which version is the authoritative editorial source.

## Canonical boundaries

For the `1.0.0-rc.1` baseline:

- `index.html` is the canonical committed workspace artifact.
- The repository version describes the repository package and validation baseline, not the embedded manual's editorial version.
- PTSP pending/drafted state is distinct from publication-version state.
- Entry presence is distinct from editorial completion.
- Structural validation does not establish factual correctness, prompt portability, accessibility conformance, external-link health, or evidence quality.
- Existing embedded source material remains preserved until version lineage and the `R-07` / `R-10` identifier conflict are resolved.

## Stable-release decision

A stable release requires an evidence-backed decision among these outcomes:

1. **Workspace product:** retain PTSP as the primary application and publish the final manual separately.
2. **Publication product:** replace the public entry point with the final manual and archive PTSP as production history.
3. **Combined product:** keep both surfaces but make the workspace/reader relationship explicit, versioned, and navigable.

The decision must be reflected consistently in the HTML title, primary heading, README, version files, release notes, and published URL.

## Remaining release blockers

Issue #3 continues to track:

- authoritative v3/v9 editorial lineage;
- editorial disposition of the 21 pending entries already present in the reader;
- the final `R-07` / `R-10` identifier decision;
- final public-product boundary;
- stable-release versioning and publication evidence.
