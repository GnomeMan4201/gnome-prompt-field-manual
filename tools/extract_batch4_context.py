from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'index.html').read_text(encoding='utf-8')
out = []

for bid in ('b-s01', 'b-s02', 'b-s03'):
    m = re.search(rf'(<div class="brief" id="{bid}">.*?</div>\s*</div>)', source, re.S)
    if not m:
        raise SystemExit(f'missing brief {bid}')
    raw_text = re.sub(r'<[^>]+>', ' ', m.group(1))
    normalized = html.unescape(re.sub(r'\s+', ' ', raw_text)).strip()
    out.append(f'===== BRIEF {bid} =====\n{normalized}\n')

cards = re.findall(r'(<article class="manual-page-card" id="manual-page-(\d{3})"[^>]*>.*?</article>)', source, re.S)
plain = []
for card, n in cards:
    p = re.search(r'<pre>(.*?)</pre>', card, re.S)
    txt = html.unescape(re.sub(r'<[^>]+>', '', p.group(1))) if p else ''
    plain.append((int(n), txt))

titles = {
    'S-01': 'System Map with Trust Boundaries',
    'S-02': 'Failure Injection Planner',
    'S-03': 'Observability Gap Finder',
}
starts = {}
for eid, title in titles.items():
    hits = [n for n, txt in plain if eid in txt and title in txt]
    if not hits:
        raise SystemExit(f'{eid} title not found')
    starts[eid] = min(hits)
    out.append(f'===== TITLE HITS {eid} =====\n{hits}\n')

ordered = sorted((n, eid) for eid, n in starts.items())
for idx, (start, eid) in enumerate(ordered):
    next_start = ordered[idx + 1][0] if idx + 1 < len(ordered) else None
    selected = []
    for n, txt in plain:
        if n < start:
            continue
        if next_start is not None and n >= next_start:
            break
        if next_start is None and n > start and re.search(r'\n\s*S-\d{2}\s+[^\n]+', txt):
            break
        selected.append((n, txt))
    out.append(f'===== BODY {eid} START PAGE {start:03d} =====')
    for n, txt in selected:
        out.append(f'===== PAGE {n:03d} =====\n{txt}')

(ROOT / 'batch4-context.txt').write_text('\n\n'.join(out), encoding='utf-8')
print('wrote batch4-context.txt')
