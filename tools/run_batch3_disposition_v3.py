from pathlib import Path

p = Path(__file__).with_name('apply_batch3_disposition_v2.py')
s = p.read_text(encoding='utf-8')
old = "return pre_edit(card,lambda x: rx(x,r'(→Run R-09 \\(Citation\\s+Integrity Check\\).*?artifact rather than the effect\\.\\s+)(→If a replication attempt proceeds)',r'\\1→Run R-05 (Failure-to-Test Converter) on the highest-severity replication risks or blockers to convert them into concrete test specifications before attempting replication. \\2','r03 visible r05'))"
new = "return pre_edit(card,lambda x: rx(x,r'(→If a replication attempt proceeds)',r'→Run R-05 (Failure-to-Test Converter) on the highest-severity replication risks or blockers to convert them into concrete test specifications before attempting replication. \\1','r03 visible r05'))"
count = s.count(old)
if count != 1:
    raise SystemExit(f'v3 source patch expected 1 match, found {count}')
s = s.replace(old, new, 1)
code = compile(s, str(p), 'exec')
exec(code, {'__name__': '__main__', '__file__': str(p)})

test = Path(__file__).resolve().parents[1] / 'tests' / 'test_reconcile_entry_lineage.py'
t = test.read_text(encoding='utf-8')
old_assert = 'self.assertEqual(result.summary.pending_present_in_embedded, 16)'
new_assert = 'self.assertEqual(result.summary.pending_present_in_embedded, 14)'
if t.count(old_assert) != 1:
    raise SystemExit(f'stale lineage assertion expected once, found {t.count(old_assert)}')
test.write_text(t.replace(old_assert, new_assert, 1), encoding='utf-8')
