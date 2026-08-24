from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
AUDIT = ROOT / "docs" / "BATCH1_DISPOSITION_2026-08-24.md"
EXPECTED_PRE_SHA256 = "35da23093a45b13e1e9aca6748314c5a8faba2be0a7df349e470c5ae0afb8949"


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
text = replace_once(
    text,
    "document.getElementById('b-t01').classList.add('open');",
    "document.getElementById('b-w01').classList.add('open');",
    "first default brief target",
)
text = replace_once(
    text,
    "document.getElementById('b-t02').classList.add('open');",
    "document.getElementById('b-w02').classList.add('open');",
    "second default brief target",
)
INDEX.write_text(text, encoding="utf-8", newline="")
post_sha = sha256(INDEX.read_bytes())

audit = AUDIT.read_text(encoding="utf-8")
audit = replace_once(audit, EXPECTED_PRE_SHA256, post_sha, "audit final reader hash")
AUDIT.write_text(audit, encoding="utf-8")

print(f"reader startup repair staged: {pre_sha} -> {post_sha}")
