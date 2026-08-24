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
selected = 0
for card, n_text in cards:
    n = int(n_text)
    if 104 <= n <= 132:
        p = re.search(r'<pre>(.*?)</pre>', card, re.S)
        txt = html.unescape(re.sub(r'<[^>]+>', '', p.group(1))) if p else ''
        out.append(f'===== PAGE {n:03d} =====\n{txt}')
        selected += 1
if selected != 29:
    raise SystemExit(f'expected 29 pages 104-132, extracted {selected}')

(ROOT / 'batch4-context.txt').write_text('\n\n'.join(out), encoding='utf-8')
print('wrote batch4-context.txt')
