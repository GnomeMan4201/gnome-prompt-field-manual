# Phase VIII-D — Independent Replication

This directory contains the original, locked standalone
replication kit for GNOME's Qwen2.5 0.5B synthetic
instruction-contamination research case.

## Research status

- Original exploratory findings: Phase VIII-C
- Preregistered internal repeat: 6/6 matched blocks
- Independent operator replication: NOT YET ESTABLISHED

The internal result is not evidence of independent replication.

## External researcher invitation

https://github.com/GnomeMan4201/gnome-prompt-field-manual/issues/30

Original preregistration:
https://github.com/GnomeMan4201/gnome-prompt-field-manual/pull/29#issuecomment-7092432423

## Locked research files

Protocol SHA-256:
91e4bae7df36dee69ed8f97beb5ee0fc3cbad61a06607156ff6d2db6a0f6adc5

Runner SHA-256:
f019dc294ac5927383f7e6c7862c19a9655497bcfcc8a77ac11c9f26ec002ef2

Do not change the runner, prompts, conditions, ordering,
expected answers, or scoring rule for the registered run.

## Researcher setup

On a separately controlled machine, install Ollama and
the preregistered Qwen2.5 0.5B model, then:

```bash
cd research/phase8d-independent-replication/kit

sha256sum -c LOCK.sha256

python3 -B -m unittest discover -s tests -p 'test_*.py' -q

python3 -B replicate.py --show-plan

python3 -B replicate.py --preflight
```

After reviewing the protocol, an independent operator may
run and archive the full 18-request experiment:

```bash
OUT="$HOME/gnome-phase8d-$(date -u +%Y%m%dT%H%M%SZ)"

python3 -B replicate.py --run "$OUT" \
  --independent-host-ack

python3 -B replicate.py --verify "$OUT"

python3 -B replicate.py --pack "$OUT"

sha256sum "$OUT.zip"
```

Only use the independence acknowledgement when the operator
and host are separately controlled from the originating work.
The acknowledgement is self-reported, not authenticated.

Review all raw evidence before uploading it. Retain every
result, including invalid outputs, baseline failures and
negative findings.

## Claim limits

This is one synthetic task and one model configuration.
Neither perfect reproduction nor computational replay proves
a universal bypass rate, cross-model transfer, independent
execution authenticity, or a unique causal mechanism.
