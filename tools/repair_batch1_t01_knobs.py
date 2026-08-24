from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
AUDIT = ROOT / "docs" / "BATCH1_DISPOSITION_2026-08-24.md"
EXPECTED_PRE_SHA256 = "e8a197606485e2ccf9c29d237de8b24e1dca6694851706262ae4983ee210ecbb"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


raw = INDEX.read_bytes()
pre_sha = sha256(raw)
if pre_sha != EXPECTED_PRE_SHA256:
    raise SystemExit(f"index hash mismatch: expected {EXPECTED_PRE_SHA256}, got {pre_sha}")

text = raw.decode("utf-8")
visible_old = """Add “run the weakest-link selection twice: once before reading recommended
actions, once after” to check whether remediation changes which highest-
severity finding dominates."""
visible_new = """Add “Assume a competent adversary knows this idea is being de-
veloped” to sharpen Lens 2. Add “Historical analog must be from
a domain different from the one this idea operates in” to prevent
the analog from being the obvious one everyone already knows.
Add “Weight lenses by: [technical / market / regulatory / human
factors]” to focus the stress test on the highest-risk domain. Add
“run the weakest-link selection twice: once before reading recommended
actions, once after” to check whether remediation changes which highest-
severity finding dominates."""
text = replace_once(text, visible_old, visible_new, "visible T-01 knob restoration")

INDEX.write_text(text, encoding="utf-8", newline="")
post_sha = sha256(INDEX.read_bytes())

audit = AUDIT.read_text(encoding="utf-8")
audit = replace_once(audit, EXPECTED_PRE_SHA256, post_sha, "audit final reader hash")
AUDIT.write_text(audit, encoding="utf-8")

print(f"T-01 knob repair staged: {pre_sha} -> {post_sha}")
