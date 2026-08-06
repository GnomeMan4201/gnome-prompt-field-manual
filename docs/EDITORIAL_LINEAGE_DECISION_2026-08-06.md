# Editorial Lineage and Identifier Decision — 2026-08-06

## Decision status

**Editorial lineage roles: resolved.**

**R-06 / R-07 / R-10 numbering decision: resolved.**

**Physical renumbering of the embedded reader: not performed in this decision change set.** It requires a dedicated mutation pass that updates headings, table-of-contents entries, field cards, chains, follow-ups, and every other affected cross-reference together.

## Canonical evidence

Canonical `index.html` SHA-256:

`b43c308c5493391a6d2b58cf3f3faf50705e2cb69ab70ebe79f11c015e6a6fb1`

Repository history relevant to provenance:

- `402c888eca4b02c434129c28ae6e685c3805ae6c` — original uploaded artifact;
- `03fdfa32f3ec08ffb757413447bf84baec06db56` — rename to `index.html` for GitHub Pages;
- `209f2f471faffbbac16c4f232fddc7d8d8062bff` — README-only update;
- later closeout commits add validation and documentation but do not supply the missing editable source documents.

The repository does not contain `GNOME_Prompt_Field_Manual_v3_final.docx`. It also does not contain a separate editable v9 manuscript source. The v9 content is embedded as a rendered reader generated from `GNOME_Prompt_Field_Manual_v9(1).pdf`.

## v3 and v9 are different artifact roles

The committed PTSP workspace repeatedly names `GNOME_Prompt_Field_Manual_v3_final.docx` as the manuscript to upload for drafting and insertion work. Its production briefs call it the **v3 master**, use it to define planned numbering, and instruct operators to update pending/drafted state there.

The same HTML labels the reader as **Complete GNOME Prompt Field Manual v9 Reader**, states that it was generated from `GNOME_Prompt_Field_Manual_v9(1).pdf`, and describes its table of contents as the locked v9 table of contents.

The evidence therefore supports this role separation:

- **v3 master:** editable manuscript and production-planning authority represented by the PTSP instructions, but not physically committed;
- **v9 reader:** rendered publication snapshot physically embedded in `index.html`;
- **1.0.0-rc.1:** repository/package validation version, not a manuscript or publication version.

This resolves the apparent naming conflict. It does **not** prove the complete transformation history from v3 to v9, because the underlying v3 DOCX and editable v9 source are absent. Any claim about all intervening editorial changes remains unsupported.

## Numbering evidence

The PTSP discrepancy note and R-10 drafting brief explicitly state:

- the planned v3 master numbering assigns **R-07** to **Competing Hypotheses Table**;
- the planned v3 master numbering assigns **R-10** to **Source-of-Truth Conflict Resolver**;
- the rendered body currently labels Competing Hypotheses Table as **R-06**;
- the rendered body currently labels Source-of-Truth Conflict Resolver as **R-07**;
- both substantive entries already exist;
- R-10 is a renumbering task, not a drafting task.

The embedded reader confirms the current body pattern: the Competing Hypotheses content is referenced under R-06 and Source-of-Truth Conflict Resolver is headed R-07. No embedded R-10 body exists.

## Frozen identifier decision

The authoritative editorial correction is:

1. **Competing Hypotheses Table: `R-06` → `R-07`.**
2. **Source-of-Truth Conflict Resolver: `R-07` → `R-10`.**
3. **Do not create a second Source-of-Truth Conflict Resolver body.**
4. **After the complete renumbering pass, mark R-10 drafted in the production master.**

This is a two-label repair. Renaming only the current R-07 to R-10 would leave the planned R-07 assignment unresolved and would preserve incorrect cross-references to R-06.

## Mutation requirements

The physical renumbering change set must inventory and update every semantic reference, including:

- entry headings and full-entry labels;
- table-of-contents entries;
- follow-up and cross-reference instructions;
- field-card trigger mappings;
- chains and workflow sequences;
- pending inventory and drafting-brief status;
- embedded page search metadata;
- any PDF/object representation that cannot be corrected by editing visible HTML alone.

The mutation must fail closed if any occurrence cannot be classified as one of:

- Competing Hypotheses semantic reference;
- Source-of-Truth Conflict Resolver semantic reference;
- historical/provenance statement that must retain the old labels;
- unrelated R-06/R-07 text.

A global string replacement is prohibited because both identifiers currently refer to different entries depending on context.

## Release consequence

The v3/v9 role conflict and editorial identifier decision are no longer open questions. Stable publication remains blocked by execution of the complete renumbering pass, verification of the corrected rendered artifact, disposition of the remaining pending entries, accessibility/browser review, and final release evidence.
