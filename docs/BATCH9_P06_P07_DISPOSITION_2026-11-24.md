# Batch 9 disposition — planned P-06 and P-07

| Frozen drafting brief | Editorial decision | Canonical subject | Canonical entry sharing the planned identifier |
| --- | --- | --- | --- |
| P-06 Work Sample Annotator | **SUBSUMED** | P-05 Work Sample Annotator, from its heading on page 222 to its Safety Notes on page 228 | P-06 Changelog Curation Engine starts later on page 228. |
| P-07 Changelog Curation Engine | **SUBSUMED** | P-06 Changelog Curation Engine, from its heading on page 228 to its Safety Notes on page 232 | P-07 RFC Draft Generator starts later on page 232 and remains a distinct entry. |

The [approved requirement matrices and before/after excerpts](BATCH9_P06_P07_ADJUDICATION_2026-11-24.md) establish manuscript-contract satisfaction. The [machine-readable identity crosswalk](../workbench/data/batch9_identity_crosswalk.json) records both dispositions, the preserved canonical identifiers, and the inventory transition. The [P-06 archive](../tests/fixtures/batch9-frozen-planned-p06.html) and [P-07 archive](../tests/fixtures/batch9-frozen-planned-p07.html) are the original HTML fragments preserved byte-for-byte.

## Advisory titles and reference resolution

Removing the pending rows and briefs exposes the heading-derived advisory candidates for P-06 and P-07. Their candidates now read **Changelog Curation Engine** and **RFC Draft Generator**, respectively. The exported title authority stays `reconciler-candidate-not-verified-heading`. Occurrence pages and body-verification fields are unchanged. The two planned briefs close by subject, with the same 91 identifiers in the editorial inventory.

The frozen P-07 brief identifies the Architecture Decision Record Generator as S-09. The canonical heading for that subject is **S-10 Architecture Decision Record Generator** on page 140. Canonical **S-09 Incident Report Scaffold** is on page 138. The changelog on page 232 already uses S-10. The frozen label remains intact in its archive. The active P-10 brief also retains that frozen label. The workspace notice directs readers to S-10 for the ADR subject in both cases. Legacy manuscript references outside the corrected bodies, including the ADR label on page 260 and the RFC label on page 273, retain their original bytes. Use the canonical headings on pages 140 and 232 to resolve those subjects.

The workspace disposition notice links to the canonical entry headings. Drafting order, grouping logic, schedule descriptions and README present Batch 10 identifiers as **planned** labels until its identity review. The Special Caution Entries and the SEC-05 evidence record and brief remain intact.

## Source bindings and preservation

| Binding | Exact value |
| --- | --- |
| PR #46 approved head commit | `d286682a4c78e58f74d99e9f285e837a95cc6325` |
| PR #46 merge and disposition base | `859658e479206ed3311629190a0f2f5e7e410b2d` |
| Original frozen brief source git commit | `88f1a6399eff6655bf511f24fb848f51bdb1ce88` |
| Original brief source `index.html` SHA-256 | `108d443e3f39e745bddbcbb030de1876f36f328180308a32eae2cb107d133f80` |
| Approved manuscript `index.html` SHA-256 | `8e3ec363f32f200ac8b01f479986043a9854a8b4868efec8497b62a4288403d6` |
| Approved adjudication SHA-256 | `197cc9f5f2645d0db9a10b20a27b50ef14da34705d2d95914775b02e99c17d97` |
| Frozen planned P-06 brief SHA-256 | `250bc2841a5218ce7d26506a3234573a630f626c391733cc089bde2ffa0210fc` |
| Frozen planned P-07 brief SHA-256 | `611090f14065fdf6b024707d5a357d058ecbdd3a3d58972932efee6ee183c879` |
| Disposition `index.html` SHA-256 | `208211b102aa75bf9f35fefbd2c33cf7f89365a8468058abd8567b8b442937d6` |
| Regenerated current identity index SHA-256 | `76d46193ed2956d13c02062c7938b4c08e87326146910be4e6f876fa87d546a1` |
| Batch 9 identity crosswalk SHA-256 | `df42795f1a65cf9e66ff249c849c40f20c14b0e1942af339143eda756640e2d3` |
| All 315 canonical cards in page order, NUL-separated SHA-256 | `9f1b71b85eeb4b3021f039bb4713ae398e37f2fa8580a64e33cff64734321a71` |
| Standalone reader SHA-256 | `778ae1a6a8412882eeb30a0433b30b089fd302394559fb1b3e0be65a57c766ec` |
| Historical v9 PDF SHA-256 | `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9` |

All 315 page cards and the complete standalone reader match the pinned PR #46 merge byte-for-byte. The archived fragments match both the original source and approved correction, and the other active briefs still match the approved source. The historical PDF, prior dispositions, and 76 history and research files match the merge tree. The current-source index is separately regenerated from the disposition HTML. The older digests above continue to identify their own historical artifacts.

## Remaining inventory

| Batch | Pending planned identifiers |
| --- | --- |
| 6 | SEC-05, under the [existing unresolved evidence requirement](BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md) |
| 10 | P-08, P-09, P-10 |

The two nonempty batches cover **4 pending** identifiers. There are **87 non-pending identifiers, 91 semantic identifiers, 315 canonical pages, and 0/91 independently verified canonical bodies**. Prompt reliability and comparative usefulness remain unmeasured.
