# Phase VIII-C — Evidence-bound repair candidate

**Status:** additive implementation candidate, subject to PR review and CI. **No genuine model experiment is supplied.** This repair is not a peer-reviewed empirical result, model exploit, or independently authenticated research platform.

## Why the Gemini VIII-C archive could not be merged

The prior archive's nine independent acceptance tests all failed. It could label an attack as induced on missing comparability data, use substring matching to score a contradictory answer as correct, self-certify an independent reviewer, approve a positive claim with no model execution, accept arbitrarily typed capsule fields, and follow HTTP redirects outside the intended endpoint.

This patch **does not replace** Phase VIII-A/B source adapters, SHA-256 enforcement, Evidence Spine v2 evaluation or v2 capsule code. It adds strict v3 functions on top of those existing contracts. All nine original independent regression cases are included in new tests and should pass.

## Engine boundaries

- `tools/reactor_reference_registry.py`: explicit content hash and evidence span checks; different declared reviewer required. A second reviewer must supply the exact source bytes for `SOURCE_CHECKED`. **Names and blind-review assertions cannot authenticate independence**. This offline implementation refuses the stronger `INDEPENDENTLY_CHECKED` authority without external identity proof.
- `tools/reactor_campaign_runner.py`: intervention-specific provenance. `PROMPT_VARIANT` binds prompt and task hashes. `LOWER_TRUST_DOCUMENT` restricts mutations to one explicitly recorded insertion and checks the resulting control/variant prompt bytes. Observation `interventionProvenance` must match the plan for both arms. Uses the existing numeric-loopback-only Ollama runner, with no redirects, proxies, hidden API calls, or code execution. The actual adapter's model identity and parameter use remain unverified provider reports.
- `tools/reactor_empirical_evaluator.py`: exploratory wrapper refuses attribution without a pinned plan; scoring uses `reactor_evidence_v2.evaluate_text` rather than substring success. Imported `passed`, `evaluation` and `disposition` fields remain rejected by v2's validation engine.
- `tools/reactor_campaign_replay.py`: v3 capsule integrity includes a hashed manifest; replay validates source references, intervention, observations, scores, counters, claims and challenge links, then independently recalculates the v2 evaluation from the raw outputs. Rehashing a forged analysis cannot make it valid. `NOT_EXECUTED` can be a valid recorded state only with no observations and no empirical success claim.
- `schemas/reactor-evidence-v3.schema.json`: typed v3 envelope with strict top-level and section-specific fields. Schema is an initial structural contract; Python validation enforces additional scientific restrictions.
- `workbench/reactor/campaign-lab.html`: local read-only capsule inspector. It checks SHA-256 section consistency in a secure-context browser and visibly labels all imported scoring as unverified until independently replayed with Python. It never contacts a provider, alters files or treats checksum matches as experiment authenticity.

## Reproduction

From the repository root with Python 3.12+, Node 22, and jsonschema 4.23.0:

```bash
python3 -m unittest discover -s tests -v
for f in workbench/reactor/*.js; do node --check "$f"; done
python3 tools/validate_manual.py --input index.html --strict-warnings
python3 tools/reconcile_entry_lineage.py --input index.html --expect-pending 14 --expect-drafted 77 --expect-total 91 --expect-pages 315 --enforce
python3 tools/audit_editorial_lineage.py --input index.html
```

Create and verify a **NOT EXECUTED** capsule using the JSON files under `examples/phase8c`:

```bash
python3 tools/reactor_campaign_replay.py build \
  --campaign examples/phase8c/campaign.json \
  --intervention examples/phase8c/intervention.json \
  --execution examples/phase8c/not-executed.json \
  --findings examples/phase8c/findings.json \
  --out /tmp/gnome-v3-capsule.json
python3 tools/reactor_campaign_replay.py verify /tmp/gnome-v3-capsule.json
```

For **opt-in genuine local inference** (only from the user's own machine running Ollama):

```bash
ollama list
# Edit campaign.json to select an actual local model name; keep model/provider and source data consistent.
python3 tools/reactor_campaign_runner.py \
  --campaign examples/phase8c/campaign.json \
  --intervention examples/phase8c/intervention.json \
  --endpoint http://127.0.0.1:11434 --trials 3 \
  --out /tmp/gnome-run-record.json
```

The command never downloads or starts a model, never issues remote API requests, and never produces synthetic fallback output. When the local model is absent the resulting state is **NOT EXECUTED**, not a successful experiment. The example campaign's provider is `ollama-local` and model is a **placeholder**; replace with a local model tag that actually exists before running. Inspect raw observations before building a v3 capsule. The runner's results are *not scored* automatically; use `reactor_campaign_replay.py build` to re-evaluate after reviewing the run records.

## Scope limitations (merge and publication gates)

1. The v3 capsule replay is **Python-first**. There is no equivalent JavaScript v3 scientific replay in this patch. The browser inspector verifies checksums only; it is never allowed to claim its own scientific scores are verified.
2. The source registry verifies declared bytes and spans, **not external source authenticity or human reviewer identity**. Reviewer separation is a recorded declaration, not an authenticated independent replication. A perfectly rehashed fabricated capsule cannot be distinguished from authentic data without an external trust anchor.
3. The existing local model execution adapter does not prove that a provider honored the requested seed or temperature, report a model digest, or establish actual remote/network execution beyond the local connection. Runtimes should label those as unknown.
4. Comparisons are controlled within the pinned v2 rubric; this is not causal statistical proof. Confidence intervals are descriptive binomial intervals with assumptions, not guarantees. Trial ordering is currently CONTROL then VARIANT and is not randomized.
5. An eight-digit-looking "100%" from synthetic fixtures would be meaningless: no synthetic scores are presented as empirical facts. Any model findings report must contain actual unaltered output bytes and known provenance.
6. Web UI is inspection-only. The complete live campaign editor, authenticated multi-person verification, API-managed execution, and visual trial-run orchestration are outside this scoped repair.
7. Canonical GNOME manuscript is unchanged. **0/91 canonical bodies independently verified, 629 editorial decisions pending**.

**Merge gate:** independent code review; real full-repository no-skip CI; HTML/CSS/keyboard/accessibility checks; optional mock local runner integration; confirmation of zero change to original root `index.html` SHA-256 `1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19`.
