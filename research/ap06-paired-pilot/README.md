# AP-06 paired pilot

**A blinded AI second reading found one fully correct case per arm.** Independent human scoring and separate-operator replication remain open. To score blind, open only REVIEWER.md, run-02/blind.json and review-sheet.csv until you have locked your sheet. The key, arm mapping and provisional operator interpretation are elsewhere in this directory. A separate reviewer should receive just those three files.

## Collection

The original protocol and collector were committed at `a024f8d46fb183ca3bfd160b863a98a520337a92` before inference. Each of six synthetic two-claim submissions was sent through both instructions. The rubric and source packet were identical within each pair. All three findings occur four times among the twelve gold claim labels per condition. The author created the cases with knowledge of the task. These cases are fresh relative to the published worked example and were never a confidential external test set.

Run 01 produced twelve successful process exits and zero captured answers. The preregistered invalid-output rule scores both arms zero; this measures capture failure. CAPTURE_AMENDMENT.md and the corrected collector were committed at `a6cbe100797fcbeba13c62d1f3cf5c95bd2b0548` before run 02. Run 02 produced twelve nonempty responses. Both runs and every request are preserved. The repeat uses the same six cases; there are six paired evaluation units.

## Provisional operator reading

| Run 02 measure | Plain-language control | AP-06 |
| --- | ---: | ---: |
| Both claims correctly assessed | 0/6 | 1/6 |
| Individually correct findings | 2/12 | 3/12 |

One paired win, zero losses, five ties on the primary endpoint. An operator who knew the cases and designed the experiment coded the shuffled outputs before looking up the arm mapping. Style could reveal the condition. Transferring a source fact to the wrong place, answering a source sentence instead of a submitted claim, and giving incompatible findings occurred in the outputs. Some answers ended mid-sentence under the common output budget. One interpretation changes the apparent lead: the AP-06 answer on case E explicitly says the reason for the increase is unavailable, but repeatedly evaluates an unrelated counting-method claim. If the reviewer codes the causal finding as absent, both arms have zero fully correct cases. Preserve disagreements with the operator record.

This is a descriptive pilot of a single 0.5B quantized model, fixed decoding and one task. The two prompts differ in length. No comparative claim about the manual as a whole or change to its release rating follows.

## Blinded AI second reading

A fresh AI reviewer (Codex-blind-second-reader) received only the reviewer guide, anonymized run-02 outputs, and blank sheet. The reviewer reported no prior exposure to the labeled outputs, key, mapping, or operator interpretations. Repeated headings and answer structures could have revealed the two instruction styles. This was a separate AI context under the same orchestration.

The [completed sheet](blind-ai-second-read.csv) was locked at commit `da791e5fef44271f6fa85e2aa6a33c084a09e587` before the scoring script applied the arm mapping and gold key. Sheet SHA-256: `58798ae3c1b0a9b4e43143d20e7cf68a9bec7264d36064958fd4ba731b2d86d0`.

| Second reading, run 02 | Plain-language control | AP-06 |
| --- | ---: | ---: |
| Fully correct cases | 1/6 | 1/6 |
| Correct individual findings | 4/12 | 3/12 |

Both arms passed case E alone. All six pairs tied on the primary endpoint. Across both arms, the two readers assigned the same label to 20 of 24 findings. All four differences were on control outputs. In case E the second reader credited the control for implicitly expressing uncertainty about shelter causation by giving alternative explanations. The operator had treated its diversion into counting methods as a missing finding. In case C the second reader also credited rejection of the obsolete opening time. Different interpretations in B and F earned zero under both readings. The AP-06 scores were identical across readers.

The initial operator advantage did not persist. These six synthetic pairs on a single quantized model provide no demonstrated improvement in fully correct cases. Human review and independent model execution remain separate evidence requirements.

## Reproduction

Use the model file and llama.cpp build named in protocol.json. Place the shared libraries next to the executable. With Python 3.11 or newer, run the following from this directory, using a fresh directory for each collection.

```sh
python collect.py /path/to/llama-cli /path/to/model.gguf new-run
python score.py run-02 operator-provisional.csv
python score.py run-02 blind-ai-second-read.csv
```

The historical collector from the first protocol commit reproduces the original logging settings. Fresh blinded runs generate new opaque IDs, so use a matching scoring sheet. Each JSON transcript includes the complete prompt, stdout, stderr, exit code and elapsed time. The model and runtime binaries are external dependencies.
