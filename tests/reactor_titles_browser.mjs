// Reactor entry labels through the normal entry point, compared with manuscript headings
// read from the standalone reader's static pages (JavaScript disabled, separate surface).
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {resolve, sep, extname} from 'node:path';
import {chromium, firefox, webkit} from 'playwright';

const root = resolve('.'), name = process.argv[2] || 'chromium', engine = {chromium, firefox, webkit}[name];
assert.ok(engine, 'unknown browser ' + name);
const types = {'.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json'};
const server = createServer(async (req, res) => {
  try {
    const path = resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
    if (!path.startsWith(root + sep)) throw Error('outside root');
    const bytes = await readFile(path);
    res.writeHead(200, {'Content-Type': types[extname(path)] || 'application/octet-stream'}); res.end(bytes);
  } catch { res.writeHead(404); res.end(); }
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${server.address().port}`;
const reactor = base + '/workbench/reactor/index.html';
const NAMED = ['AP-04', 'R-07', 'AP-06', 'SEC-08'];
let browser;

async function expectedHeadings(context) {
  const page = await context.newPage();
  await page.goto(base + '/GNOME-Field-Manual.html#page-1');
  const found = await page.evaluate(() => {
    const out = {};
    for (const article of document.querySelectorAll('article.book-page')) {
      const blocks = [...article.querySelectorAll('.book-prose > .source-block, .book-prose > p.flowing')].map(b => b.textContent.trim());
      blocks.forEach((b, i) => {
        const m = b.match(/^([A-Z]{1,5}-\d{2})\s+(\S[\s\S]*)$/);
        if (m && /^Criteria\s*:/.test(blocks[i + 1] || '')) (out[m[1]] ||= []).push(m[2].replace(/\s+/g, ' '));
      });
    }
    return out;
  });
  await page.close();
  return found;
}

async function renderedPairs(page) {
  return page.locator('[data-sel-entry]').evaluateAll(buttons => buttons.map(b => ({
    id: b.dataset.selEntry, strong: b.querySelector('strong').textContent,
    title: b.textContent.replace(/\s+/g, ' ').trim().replace(/^\S+ — /, '').replace(/ UNVERIFIED_SOURCE_CANDIDATE$/, ''),
  })));
}

async function openReactor(context, route) {
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  if (route) await page.route('**/workbench/data/current_body_review.json', route);
  await page.goto(reactor);
  await page.locator('[data-sel-entry]').first().waitFor();
  return {page, errors};
}

try {
  browser = await engine.launch({headless: true});
  const staticContext = await browser.newContext({javaScriptEnabled: false});
  const expected = await expectedHeadings(staticContext);

  for (const [width, height] of [[1280, 900], [360, 780]]) {
    const ctx = await browser.newContext({viewport: {width, height}});
    const {page, errors} = await openReactor(ctx);
    const pairs = await renderedPairs(page);
    assert.equal(pairs.length, 91);
    assert.equal(new Set(pairs.map(p => p.id)).size, 91);
    for (const p of pairs) assert.equal(expected[p.id]?.length, 1, `${p.id}: expected exactly one manuscript heading`);
    const wrong = pairs.filter(p => p.strong !== p.id || p.title !== expected[p.id][0])
      .map(p => `${p.id}: shown "${p.title}", heading "${expected[p.id][0]}"`);
    assert.deepEqual(wrong, [], `wrong labels at ${width}px:\n${wrong.join('\n')}`);
    assert.equal(await page.locator('#heading-source-status').count(), 0);
    for (const id of NAMED) {
      await page.locator(`[data-sel-entry="${id}"]`).click();
      const selected = await page.locator('[data-sel-entry]').evaluateAll(bs =>
        bs.filter(b => b.style.borderColor.includes('amber') || b.getAttribute('style').includes('var(--amber)')).map(b => b.dataset.selEntry));
      assert.deepEqual(selected, [id], `${width}px: selecting ${id}`);
      assert.equal((await renderedPairs(page)).find(p => p.id === id).title, expected[id][0]);
    }
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
    assert.equal(overflow, false, `${width}px horizontal overflow`);
    assert.deepEqual(errors, []);
    await ctx.close();
  }

  // A missing or stale heading source stays visible; IDs remain selectable.
  const packet = JSON.parse(await readFile(resolve(root, 'workbench/data/current_body_review.json'), 'utf8'));
  const stale = {...packet, sourceHtmlSha256: '0'.repeat(64)};
  for (const [label, route, status] of [
    ['missing', r => r.fulfill({status: 404, body: ''}), 'HEADING_SOURCE_FETCH_FAILED:404'],
    ['stale', r => r.fulfill({status: 200, contentType: 'application/json', body: JSON.stringify(stale)}), 'PACKET_SOURCE_STALE'],
  ]) {
    const ctx = await browser.newContext({viewport: {width: 1280, height: 900}});
    const {page} = await openReactor(ctx, route);
    assert.match(await page.locator('#heading-source-status').innerText(), new RegExp(status), label);
    const pairs = await renderedPairs(page);
    assert.equal(pairs.length, 91);
    assert.ok(pairs.every(p => p.title.startsWith('heading unavailable; advisory candidate: ')), label);
    await page.locator('[data-sel-entry="AP-04"]').click();
    await ctx.close();
  }
  console.log(`${name}: 91 Reactor labels match manuscript headings at 1280px and 360px; ${NAMED.join(', ')} select by ID; missing and stale heading sources visible PASS`);
} finally {
  if (browser) await browser.close();
  server.close();
}
