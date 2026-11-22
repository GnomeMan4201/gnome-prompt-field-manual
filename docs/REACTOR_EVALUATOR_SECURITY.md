# Evaluator authority boundary — VIII-B repair

The Chamber never interprets defender output as scoring instructions. `judge` fields are advisory. The strict attribution module requires supplied deterministic and grounded score statuses to agree; it deliberately does not treat a judge score alone as verified ground truth.

**Limit:** Imported scoring assertions can be fabricated. Two agreement fields are not proof that two independent evaluations ran. Claims must not be promoted beyond the evidence supplied. Missing or inconsistent scoring returns `UNATTRIBUTABLE`.

The core comparison engine (`tools/reactor_engine.py` and `workbench/reactor/comparison-engine.js`) remains the reference for matching input hashes, model, provider, tools, seed, temperature, evaluator, rubric and trial IDs. An attack-induced failure cannot be counted when these are missing or mismatched.

No remote APIs or untrusted documents are contacted by the evaluator. The optional local Ollama runner uses numeric loopback addresses, no redirects, request/response size limits and an explicit user-requested model. It does not execute tool calls or the model's output.
