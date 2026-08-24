from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
AUDIT = ROOT / "docs" / "BATCH1_DISPOSITION_2026-08-24.md"
TEST = ROOT / "tests" / "test_batch1_disposition.py"

# Exact artifact produced by the initial Batch 1 migration before prose repair.
EXPECTED_PRE_SHA256 = "23587eff709f0c4e2cbe4ebc78a3809ad937f1f5e7bdd5ca87f52e8090d44c22"


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

# Restore only the prose accidentally consumed by the page-016 line-wrap matcher.
visible_old = "If the dissue a COLLAPSE verdict without specifying what specifically"
visible_new = """If the dis-
section does not change what you understand about the claim’s
structure, it failed. Rerun with the instruction: “For each com-
ponent, tell me something about this claim that a casual reader
would not have noticed.” Secondary failure: The model will is-
sue a COLLAPSE verdict without specifying what specifically"""
text = replace_once(text, visible_old, visible_new, "visible page-016 repair")

metadata_old = "if the dissue a collapse verdict without specifying what specifically"
metadata_new = "if the dis- section does not change what you understand about the claim’s structure, it failed. rerun with the instruction: “for each com- ponent, tell me something about this claim that a casual reader would not have noticed.” secondary failure: the model will is- sue a collapse verdict without specifying what specifically"
text = replace_once(text, metadata_old, metadata_new, "metadata page-016 repair")

if "dissue a collapse verdict" in text.lower():
    raise SystemExit("corrupted page-016 token survived repair")

INDEX.write_text(text, encoding="utf-8", newline="")
post_sha = sha256(INDEX.read_bytes())

# Keep the SHA-bound disposition record bound to the actual final reader artifact.
audit = AUDIT.read_text(encoding="utf-8")
audit = replace_once(audit, EXPECTED_PRE_SHA256, post_sha, "audit post-mutation hash")
AUDIT.write_text(audit, encoding="utf-8")

# Strengthen the permanent regression gate so this exact truncation cannot recur.
# The metadata intentionally preserves the PDF-derived "dis- section" line wrap.
test = TEST.read_text(encoding="utf-8")
anchor = '        self.assertNotIn("a collapses verdict", metadata)\n'
addition = anchor + '        self.assertNotIn("dissue", metadata)\n        self.assertIn("dis- section does not change what you understand about the claim", metadata)\n'
test = replace_once(test, anchor, addition, "page-016 regression assertions")
TEST.write_text(test, encoding="utf-8")

print(f"page-016 repair staged: {pre_sha} -> {post_sha}")
