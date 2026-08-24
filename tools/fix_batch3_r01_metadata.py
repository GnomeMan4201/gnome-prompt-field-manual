from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EXPECTED_SHA = "3eca54a3302731227115f9bdf9d8df7df38b044cea9dea4a4c13c4221e65559f"

raw = INDEX.read_bytes()
actual = hashlib.sha256(raw).hexdigest()
if actual != EXPECTED_SHA:
    raise SystemExit(f"index hash mismatch: expected {EXPECTED_SHA}, got {actual}")

text = raw.decode("utf-8")
old = "if no institutional interest map aggregate the source-level disclosures above by conclusion or outcome. for each identified interest: conclusion / outcome: [the conclusion or outcome an institution has a stake in] sources with an identified stake: [named sources] nature of interest: [funding / regulatory / commercial / organizational / other] evidentiary implication: [what must be disclosed or independently verified; interest alone is not evidence the source is wrong] if none are identified, state: none identified. contested zones are identified on a mature research topic"
new = "institutional interest map aggregate the source-level disclosures above by conclusion or outcome. for each identified interest: conclusion / outcome: [the conclusion or outcome an institution has a stake in] sources with an identified stake: [named sources] nature of interest: [funding / regulatory / commercial / organizational / other] evidentiary implication: [what must be disclosed or independently verified; interest alone is not evidence the source is wrong] if none are identified, state: none identified. contested zones if no contested zones are identified on a mature research topic"
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected exactly one malformed R-01 metadata fragment, found {count}")
text = text.replace(old, new, 1)

# Fail closed on both the old corruption and expected section ordering.
if old in text:
    raise SystemExit("malformed R-01 metadata fragment remains")
page_start = text.index('id="manual-page-073"')
page_end = text.index('</article>', page_start)
page = text[page_start:page_end]
for token in ("institutional interest map", "contested zones", "if no contested zones are identified on a mature research topic"):
    if token not in page:
        raise SystemExit(f"R-01 metadata missing required token: {token}")
if not (page.index("institutional interest map") < page.index("contested zones") < page.index("if no contested zones are identified on a mature research topic")):
    raise SystemExit("R-01 metadata section ordering invalid")

INDEX.write_text(text, encoding="utf-8", newline="")
print(hashlib.sha256(INDEX.read_bytes()).hexdigest())
