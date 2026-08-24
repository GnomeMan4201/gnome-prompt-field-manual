from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
EXPECTED_SHA = "3eca54a3302731227115f9bdf9d8df7df38b044cea9dea4a4c13c4221e65559f"
SEP = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

raw = INDEX.read_bytes()
actual = hashlib.sha256(raw).hexdigest()
if actual != EXPECTED_SHA:
    raise SystemExit(f"index hash mismatch: expected {EXPECTED_SHA}, got {actual}")

text = raw.decode("utf-8")
page_match = re.search(
    r'(<article class="manual-page-card" id="manual-page-073" data-manual-text=")([^"]*)(">.*?</article>)',
    text,
    re.S,
)
if not page_match:
    raise SystemExit("manual-page-073 article not found")
meta = page_match.group(2)

map_body = (
    "aggregate the source-level disclosures above by conclusion or outcome. "
    "for each identified interest: conclusion / outcome: [the conclusion or outcome an institution has a stake in] "
    "sources with an identified stake: [named sources] "
    "nature of interest: [funding / regulatory / commercial / organizational / other] "
    "evidentiary implication: [what must be disclosed or independently verified; interest alone is not evidence the source is wrong] "
    "if none are identified, state: none identified."
)
malformed = f"if no institutional interest map {map_body} contested zones are identified on a mature research topic"
if meta.count(malformed) != 1:
    raise SystemExit(f"expected one malformed R-01 metadata fragment, found {meta.count(malformed)}")
meta = meta.replace(
    malformed,
    "if no contested zones are identified on a mature research topic",
    1,
)

anchor = f"explicitly, or state: none identified] {SEP}contested zones {SEP}"
if meta.count(anchor) != 1:
    raise SystemExit(f"expected one R-01 contested-zone anchor, found {meta.count(anchor)}")
meta = meta.replace(
    anchor,
    f"explicitly, or state: none identified] {SEP}institutional interest map {SEP} {map_body} {SEP}contested zones {SEP}",
    1,
)

required = (
    "institutional interest map",
    "contested zones",
    "if no contested zones are identified on a mature research topic",
    "known gaps",
    "source flattening warnings",
)
for token in required:
    if token not in meta:
        raise SystemExit(f"R-01 metadata missing required token: {token}")
if meta.count("institutional interest map") != 1:
    raise SystemExit(f"R-01 metadata institutional map count is {meta.count('institutional interest map')}, expected 1")
if not (
    meta.index("institutional interest map")
    < meta.index("contested zones")
    < meta.index("if no contested zones are identified on a mature research topic")
    < meta.index("known gaps")
    < meta.index("source flattening warnings")
):
    raise SystemExit("R-01 metadata section ordering invalid")

new_page = page_match.group(1) + meta + page_match.group(3)
text = text[: page_match.start()] + new_page + text[page_match.end() :]
INDEX.write_text(text, encoding="utf-8", newline="")
print(hashlib.sha256(INDEX.read_bytes()).hexdigest())
