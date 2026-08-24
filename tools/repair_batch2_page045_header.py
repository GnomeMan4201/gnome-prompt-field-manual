from pathlib import Path
import hashlib

root=Path(__file__).resolve().parents[1]
index=root/'index.html'
audit=root/'docs'/'BATCH2_DISPOSITION_2026-08-24.md'
expected='0203cde07cc1b3d42323d04334d5699e9177bb11a2a7bdd96fc46ceb9cf86e76'
raw=index.read_bytes()
if hashlib.sha256(raw).hexdigest()!=expected: raise SystemExit('index hash mismatch')
text=raw.decode()
old='<div class="manual-page-head"><span>Page 045</span><em>SPECIFIC OBJECTIONS A numbered list of distinct objections this</em></div>'
new='<div class="manual-page-head"><span>Page 045</span><em>SPECIFIC OBJECTIONS A numbered list of at least three distinct objections this</em></div>'
if text.count(old)!=1: raise SystemExit(f'header match count {text.count(old)}')
text=text.replace(old,new,1)
index.write_text(text,encoding='utf-8',newline='')
post=hashlib.sha256(index.read_bytes()).hexdigest()
a=audit.read_text(encoding='utf-8')
if a.count(expected)!=1: raise SystemExit('audit hash occurrence mismatch')
audit.write_text(a.replace(expected,post,1),encoding='utf-8')
print(post)
