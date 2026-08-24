from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "index.html").read_text(encoding="utf-8")
out = []


def emit(label: str, text: str) -> None:
    out.append(f"===== {label} =====\n{text.strip()}\n")

for brief_id in ("b-r01", "b-r03"):
    m = re.search(rf'<div class="brief" id="{brief_id}">.*?</div>\n  </div>', source, re.S)
    if not m:
        raise SystemExit(f"missing brief {brief_id}")
    emit(f"BRIEF {brief_id}", re.sub(r"<[^>]+>", " ", html.unescape(m.group(0))))

for title in ("R-01 Source Map with Contested Zones", "R-03 Replication Check"):
    positions = [m.start() for m in re.finditer(re.escape(title), source)]
    emit(f"TITLE POSITIONS {title}", repr(positions))

# Extract page cards containing either target token/title plus neighbors to recover full entries.
cards = list(re.finditer(r'<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>', source, re.S))
for i, m in enumerate(cards):
    visible = re.search(r"<pre>(.*?)</pre>", m.group(0), re.S)
    if not visible:
        continue
    text = html.unescape(re.sub(r"<[^>]+>", "", visible.group(1)))
    if "R-01" in text or "R-03" in text or "Source Map with Contested Zones" in text or "Replication Check" in text:
        for j in range(max(0, i-1), min(len(cards), i+5)):
            cm = cards[j]
            pre = re.search(r"<pre>(.*?)</pre>", cm.group(0), re.S)
            if pre:
                emit(f"PAGE {cm.group(1)}", html.unescape(re.sub(r"<[^>]+>", "", pre.group(1))))

# Remaining batch rows and first briefs for startup retarget planning.
rows = re.findall(r'<tr><td class="batch-num">(\d+)</td><td class="batch-entries">(.*?)</td>.*?</tr>', source, re.S)
emit("BATCH ROWS", "\n".join(f"{n}: {re.sub(r'<[^>]+>', '', e)}" for n,e in rows))
briefs = re.findall(r'<div class="brief" id="([^"]+)"[^>]*>\s*<div class="brief-hdr".*?<span class="brief-id">([^<]+)</span>', source, re.S)
emit("BRIEF ORDER", "\n".join(f"{bid}: {eid}" for bid,eid in briefs[:8]))
startup = re.findall(r"document\.getElementById\('([^']+)'\)\.classList\.add\('open'\);", source)
emit("STARTUP DEFAULTS", "\n".join(startup))

(ROOT / "batch3-extraction.txt").write_text("\n".join(out), encoding="utf-8")
print("wrote batch3-extraction.txt")
