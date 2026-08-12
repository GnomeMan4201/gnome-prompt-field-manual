# Field Journal Identifier Decision — 2026-08-12

## Decision

`Field Journal Entry` has no live identifier in the canonical reader.
`manual-page-213` must not map it to either `R-05` or `W-04`. The unsupported
entry reference is removed while the surrounding operational guidance remains.

## Authoritative evidence

The evidence is internally consistent across the initial uploaded artifact and
the current canonical searchable reader:

- `R-05 Failure-to-Test Converter` has a full live body beginning at
  `manual-page-089` and has multiple valid semantic references.
- `W-04 Over-Smoothing Detector` has a full live body beginning at
  `manual-page-048`.
- The editorial audit at `manual-page-313` identifies the predecessor as
  `W-04 Field Journal Scaffolder`.
- The audit summary at `manual-page-315` explicitly records that predecessor as
  cut because it was too open-ended.
- No full `Field Journal Entry` or `Field Journal Scaffolder` body exists in the
  91-entry canonical reader.

The historical `W-04` label is therefore provenance, not an available current
identifier. Replacing `R-05` with `W-04` would create a new collision rather
than repair the existing one.

## Source provenance

- Initial upload commit:
  `402c888eca4b02c434129c28ae6e685c3805ae6c`
- Initial uploaded HTML SHA-256:
  `b576496ce0f496536b50e07526c081174e032cd38eb8f4659b67e517c3f950d5`
- Pre-correction main commit:
  `743db77665f6a3fa366d594b667bf85c9dd286e8`
- Pre-correction `index.html` Git blob:
  `1fff93c9c9a53d473de84f3054bc35a1721f169f`
- Pre-correction `index.html` SHA-256:
  `28cd45de449957572fe8cb007e3a5fdceb4f1493f1df2bb3a8bf098ef959055c`
- Historical v9 PDF SHA-256, preserved unchanged:
  `97482787a2471cbea5a837a0023a0aa5d0317eb149d8dd6c47e6924222b7f1e9`
- Post-correction implementation commit: recorded in the pull request and issue
  closeout evidence because a commit cannot contain its own final SHA.
- Post-correction `index.html` SHA-256:
  `4ac0157df83a7deed06583da6d9f000d4ec2220490fa07e03de4bd6759d65243`

## Mutation

At `manual-page-213`, update both `data-manual-text` and visible `<pre>` text:

```text
use R-05 (Field Journal Entry) for structured session records
```

becomes:

```text
use a structured session record
```

No entry heading, pending row, drafting brief, semantic counter, or historical
PDF byte is changed.

## Fail-closed verification

The editorial audit requires metadata/visible parity at `manual-page-213`, the
replacement phrase, absence of both `R-05 (Field Journal Entry)` and
`W-04 (Field Journal Entry)`, and exactly one live
`R-05 Failure-to-Test Converter` body. A negative regression fixture restores
the false `R-05` pairing to both surfaces and must fail semantic validation even
though surface parity remains intact.

The entry-lineage invariant remains:

```text
21 pending + 70 embedded non-pending = 91 semantic entries
```

The reader remains 315 page cards.
