# GNOME // EVIDENCE REACTOR — Architecture

## Three Separate Trust Domains
1. **Domain A — Source Truth (`source-adapter.js`)**: Read-only access to `entry_identity_index.json` and `manual_entries.json`. Raw source spans are labeled `RAW_CANDIDATE`, never `CANONICAL_VERIFIED`, until editorial adjudication completes.
2. **Domain B — Experimental Execution (`experiment-core.js`, `comparison-engine.js`)**: Owns experiment definitions, control/variant prompt hashes, paired trial observations, counterfactual comparability checks, and baseline failure attribution.
3. **Domain C — Evidence & Claims (`evidence-capsule.js`, `replay-engine.js`)**: Owns findings (`OBSERVED`, `EVALUATED`, `REPRODUCED`, `DISPUTED`, `INCONCLUSIVE`, `NOT_TESTED`), adversarial challenges, SHA-256 capsule checksums, and offline computational replay.
