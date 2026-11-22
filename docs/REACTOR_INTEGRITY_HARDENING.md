# GNOME Reactor — Integrity Hardening (Phase VIII-A repair candidate)

**Status:** tested patch candidate; not a complete Phase VIII-A product or evidence of model execution.

## Scope

This archive repairs **the user-supplied Gemini Phase VIII-A ZIP** (`gnome-phase8a-reactor.zip`). It does not modify the canonical GNOME manual or Phase VI–VII adjudication records. Install into a clean checkout of `GnomeMan4201/gnome-prompt-field-manual` on a feature branch. Reactor files are new to that repository; do **not** overwrite the publication's root `index.html`.

## Key integrity changes

1. **Baseline attribution now fails closed.** `VARIANT_INDUCED_FAILURE` requires two actual CONTROL/VARIANT observations with explicit different prompt hashes, matching experiment/input IDs, input hashes, provider, model, evaluator, temperature, seed, tools, dataset ID and rubric hash, concrete output text and boolean `passed` values. Missing or mismatched factors produce `UNATTRIBUTABLE` even when pass/fail outcomes differ. `passed` is an imported evaluator assertion, **not independently adjudicated truth**.
2. **Seed semantics are explicit.** `seed: null` in both records signifies known unsupported/unreported deterministic seed; an absent seed is missing metadata, and a different seed prevents attribution. Differences in hard identification fields are `NOT_COMPARABLE`; temperature/seed differences are disclosed limitations, but either prevents causal attribution.
3. **Repeated trials have stable slots.** Pairing is by `(inputId, trialId)` and duplicate `(experimentId,inputId,trialId,condition)` observations or `runId` values fail validation. No record may silently overwrite another.
4. **Observation contracts.** Python and JavaScript reject malformed observation records and verify prompt-hash association, dataset membership, model configuration, and—in cases where the dataset provides actual text—input content SHA-256. Missing provenance is not invented.
5. **Capsule checks include the manifest.** Python and JavaScript record and verify `manifest.json` SHA-256 and reject missing/modified files. Claims marked REPRODUCED require evidence references to known capsule components, but **capsule evidence alone does not establish independent replication**.
6. **No fake SHA-256.** JavaScript throws `SHA256_UNAVAILABLE` without Web Crypto. The Reactor requires HTTPS or localhost for hashing.
7. **Actual entry inventory.** The source adapter fetches the existing source-bound `workbench/data/entry_identity_index.json` and requires the established canonical source SHA and 91 identities. Titles stay `titleCandidate`; complete source bodies stay **unverified**. The initial prompt texts are explicitly experimental transcriptions, not copies certified by the manual.
8. **UI import guards.** An experiment must have frozen control and variant hashes before importing observations. Synthetic demonstration records cannot be exported as empirical capsules. Offline capsule import and computational replay are available, with errors surfaced instead of silently accepted.

## Test commands

```sh
python3 -m unittest discover -s tests -q
python3 tools/verify_reactor_capsule.py <path-to-capsule.json>
for file in workbench/reactor/*.js; do node --check "$file"; done
```

If `node` is missing, cross-runtime tests skip; Python-only counts must be reported separately. Formal JSON Schema contract tests require `jsonschema`. These are test-only dependencies; the Python core uses standard library only.

## Examples of claims the hardened classifier will reject

- A control that already failed cannot be counted as variant-induced failure.
- Control and variant answers to different input hashes are not a valid paired comparison.
- Temperature, seed, tool configuration, provider, model, evaluator or rubric differences cannot be silently ignored.
- A duplicated trial cannot replace the earlier record.
- A claim cannot be called supported solely because a checksum verifies copying; checksums are not signatures or evidence of independent replication.

## Boundaries and open work

- These changes do **not** verify any of the 91 canonical manual bodies. They do not resolve any of the 629 pending editorial decisions.
- They do not prove that an imported `passed` boolean is correct. A separate scorer/evaluator validation system remains necessary.
- They do not implement local Ollama execution, full causal inference, verified independent replication, authentication, signed provenance, or a complete browser accessibility evaluation.
- The supplied project still has a prototype-level user experience. The method selector loads identities but does not provide independently verified canonical prompt bodies.
- Full repository integration and a browser smoke test against its deployed GitHub Pages origin remain outstanding.
- Cross-language deterministic JSON hashing is verified on tested sample data. Exotic numeric formats (e.g., exponent and float normalizations) need an explicit RFC 8785 JSON Canonicalization Scheme implementation before general-purpose capsules can be promised interoperable.
- Changes to a checksum and the file it describes cannot be detected without a trusted external anchor or signature. This is integrity checking, not authenticity.

**Merge gate:** run the complete existing GNOME test suite in the actual repository plus these tests, inspect browser UI, confirm true 91-entry index fetch, and repeat capsule import/export tests before merging into `main`.
