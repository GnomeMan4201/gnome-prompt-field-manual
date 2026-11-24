import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { chromium, firefox, webkit } from 'playwright';

const browserName = process.argv[2] || 'chromium';
const engines = { chromium, firefox, webkit };
assert.ok(engines[browserName], `Unsupported browser: ${browserName}`);

const manualUrl = pathToFileURL(resolve('index.html')).href;
const browser = await engines[browserName].launch({ headless: true });

const scenarios = [
  { name: 'desktop', viewport: { width: 1365, height: 936 } },
  { name: 'mobile', viewport: { width: 390, height: 844 } },
  // At 200% browser zoom, the available CSS-pixel viewport is approximately halved.
  { name: 'zoom-200-reflow-equivalent', viewport: { width: 683, height: 468 } },
];

try {
  await assertReaderPublication();
  await assertBatch5MigrationPage();
  await assertPromptCopy();
  for (const scenario of scenarios) {
    const page = await browser.newPage({ viewport: scenario.viewport });
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(String(error)));

    await page.goto(manualUrl, { waitUntil: 'domcontentloaded' });

    await assertInitialState(page);
    await assertSearch(page);
    await assertTabInteractions(page);
    await assertReflow(page, scenario);
    assert.deepEqual(pageErrors, [], `${scenario.name}: page errors`);

    console.log(`PASS ${browserName} ${scenario.name}`);
    await page.close();
  }
} finally {
  await browser.close();
}

async function assertInitialState(page) {
  assert.equal(await page.locator('.manual-page-card').count(), 315);
  assert.equal(await page.locator('#manualSearchMeta').innerText(), 'Showing all 315 pages.');
  await assertTabState(page, 'text');

  const page091 = normalize(await page.locator('#manual-page-091').innerText());
  const page093 = normalize(await page.locator('#manual-page-093').innerText());
  assert.ok(page091.includes('R-07 Competing Hypotheses Table'));
  assert.ok(page093.includes('R-10 Source-of-Truth Conflict Resolver'));
}

async function assertSearch(page) {
  const search = page.getByLabel('Search manual text', { exact: true });
  await search.fill('source-of-truth conflict resolver');
  assert.equal(
    await page.locator('#manualSearchMeta').innerText(),
    'Showing 1 of 315 pages matching “source-of-truth conflict resolver”.',
  );
  assert.equal(await page.locator('.manual-page-card:not(.hidden)').count(), 1);
  assert.ok(await page.locator('#manual-page-093').isVisible());
  await assertTabState(page, 'text');

  await page.getByRole('button', { name: 'Clear', exact: true }).click();
  assert.equal(await page.locator('.manual-page-card:not(.hidden)').count(), 315);
}

async function assertTabInteractions(page) {
  const textTab = page.getByRole('tab', { name: 'Searchable Text · Canonical', exact: true });
  const pdfTab = page.getByRole('tab', { name: 'Historical v9 PDF', exact: true });

  await pdfTab.click();
  await assertTabState(page, 'pdf');

  await textTab.focus();
  await textTab.press('Enter');
  await assertTabState(page, 'text');

  await textTab.press('ArrowRight');
  await assertTabState(page, 'pdf');
  assert.equal(await pdfTab.evaluate(element => element === document.activeElement), true);

  await pdfTab.press('ArrowLeft');
  await assertTabState(page, 'text');
  assert.equal(await textTab.evaluate(element => element === document.activeElement), true);
}

async function assertTabState(page, selected) {
  const textSelected = selected === 'text';
  const textTab = page.locator('#manualTextTab');
  const pdfTab = page.locator('#manualPdfTab');
  const textPanel = page.locator('#manualTextView');
  const pdfPanel = page.locator('#manualPdfView');

  assert.equal(await textTab.getAttribute('aria-selected'), String(textSelected));
  assert.equal(await pdfTab.getAttribute('aria-selected'), String(!textSelected));
  assert.equal(await textTab.getAttribute('tabindex'), textSelected ? '0' : '-1');
  assert.equal(await pdfTab.getAttribute('tabindex'), textSelected ? '-1' : '0');
  assert.equal(await textPanel.isVisible(), textSelected);
  assert.equal(await pdfPanel.isVisible(), !textSelected);
  assert.equal(await textPanel.getAttribute('hidden'), textSelected ? null : '');
  assert.equal(await pdfPanel.getAttribute('hidden'), textSelected ? '' : null);
}

async function assertReflow(page, scenario) {
  const metrics = await page.evaluate(() => ({
    viewportWidth: window.innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    toolbarWidth: document.querySelector('.manual-toolbar').getBoundingClientRect().width,
    readerWidth: document.querySelector('.manual-reader-main').getBoundingClientRect().width,
  }));

  assert.ok(
    metrics.scrollWidth <= metrics.viewportWidth + 1,
    `${scenario.name}: horizontal overflow ${metrics.scrollWidth}px > ${metrics.viewportWidth}px`,
  );
  assert.ok(metrics.toolbarWidth <= metrics.viewportWidth + 1);
  assert.ok(metrics.readerWidth <= metrics.viewportWidth + 1);
}

async function assertBatch5MigrationPage() {
  const url = pathToFileURL(resolve('GNOME-Field-Manual.html')).href;
  const layouts = [
    { name: 'desktop', viewport: { width: 1365, height: 936 } },
    { name: 'mobile', viewport: { width: 390, height: 844 } },
    { name: 'zoom-200-reflow-equivalent', viewport: { width: 683, height: 468 } },
  ];

  for (const layout of layouts) {
    const page = await browser.newPage({ viewport: layout.viewport });
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(String(error)));
    try {
      await page.goto(url + '#book/page-133');
      const rendered = page.locator('#main-root .book-page');
      await rendered.waitFor();

      const pageText = normalize(await rendered.innerText()).toUpperCase();
      for (const required of [
        'ROLLBACK TRIGGER CONDITIONS',
        'OBSERVABLE FAILURE SIGNAL',
        'EVALUATION WINDOW',
        'IMMEDIATE HALT OR ROLLBACK ACTION',
        'ESCALATION PROCEDURE',
        'DOES NOT MONITOR PRODUCTION',
      ]) {
        assert.ok(pageText.includes(required), `${layout.name}: page 133 missing ${required}`);
      }

      const metrics = await page.evaluate(() => {
        const card = document.querySelector('#main-root .book-page').getBoundingClientRect();
        return { viewport: innerWidth, scroll: document.documentElement.scrollWidth,
          cardLeft: card.left, cardRight: card.right };
      });
      assert.ok(metrics.scroll <= metrics.viewport + 1,
        `${layout.name}: page 133 horizontal overflow ${JSON.stringify(metrics)}`);
      assert.ok(metrics.cardLeft >= -1 && metrics.cardRight <= metrics.viewport + 1,
        `${layout.name}: page 133 clipped horizontally ${JSON.stringify(metrics)}`);
      assert.deepEqual(pageErrors, [], `${layout.name}: page 133 script errors`);
    } finally {
      await page.close();
    }
  }
}

function normalize(value) {
  return value.replace(/\s+/g, ' ').trim();
}

async function assertPromptCopy() {
  const url = pathToFileURL(resolve('GNOME-Field-Manual.html')).href;
  const cases = [[9, 'T-01'], [10, 'T-01'], [11, 'T-01'], [19, 'T-04'], [20, 'T-04']];
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const offline = await browser.newPage({ javaScriptEnabled: false });
  await offline.goto(url);
  if (browserName === 'chromium') {
    await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
  } else {
    await page.addInitScript(() => Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText: async text => { window.copiedPrompt = text; } }
    }));
  }
  for (const [number, entry] of cases) {
    const expected = readFileSync(resolve('tests/fixtures/reader-prompts', entry + '.txt'), 'utf8').trimEnd();
    await page.goto(url + '#book/page-' + number);
    const button = page.locator('#main-root [data-action="copy-prompt"]');
    await button.click();
    await page.getByText('Prompt copied.', { exact: true }).waitFor();
    const copy = browserName === 'chromium'
      ? await page.evaluate(() => navigator.clipboard.readText())
      : await page.evaluate(() => window.copiedPrompt);
    assert.equal(copy, expected);
    const tools = offline.locator('#page-' + number + ' .prompt-tools');
    await tools.locator('summary').click();
    assert.equal(await tools.locator('textarea').inputValue(), expected);
    assert.ok(await tools.locator('button').isHidden());
  }
  await page.evaluate(() => Object.defineProperty(navigator, 'clipboard', { value: undefined }));
  await page.locator('#main-root [data-action="copy-prompt"]').click();
  const selected = page.locator('#main-root textarea:focus');
  assert.ok(await selected.isVisible());
  assert.ok(await selected.evaluate(field => field.selectionStart === 0 && field.selectionEnd === field.value.length));
  await page.close();
  await offline.close();
}

async function assertReaderPublication() {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(manualUrl);
  const canonical = await page.locator('article.manual-page-card').evaluateAll(cards =>
    cards.map(card => [card.id, card.querySelector('pre').textContent])
  );
  const file = resolve('GNOME-Field-Manual.html');
  const html = readFileSync(file, 'utf8');
  const match = html.match(/^ *var BOOK_PAGES = (.+);$/m);
  assert.ok(match, 'Expected the embedded search dataset');
  const pages = JSON.parse(match[1]);
  assert.equal(pages.length, 315);
  assert.deepEqual(pages.map(p => [p.cardId, p.text]), canonical);
  assert.deepEqual(pages.map(p => p.pageNumber), canonical.map((_, i) => i + 1));

  const url = pathToFileURL(file).href;
  await page.goto(url + '#page-1');
  await page.locator('#main-root .book-page').waitFor();
  assert.ok(page.url().endsWith('#book/page-1'));
  await page.locator('#book-contents summary').click();
  await page.locator('#book-search').fill('Weakest Link Isolator');
  await page.locator('[data-pnum="19"]').click();
  assert.ok(page.url().endsWith('#book/page-19'));
  await page.locator('#toggle-bm').press('Enter');
  assert.equal(await page.locator('#toggle-bm').getAttribute('aria-pressed'), 'true');
  assert.equal(await page.locator('#toggle-bm').evaluate(b => b === document.activeElement), true);
  await page.reload();
  assert.equal(await page.locator('#toggle-bm').getAttribute('aria-pressed'), 'true');
  await assertStandaloneWidth(page);
  await page.close();

  const staticPage = await browser.newPage({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  await staticPage.goto(url + '#page-1');
  const directory = staticPage.locator('#page-directory');
  const links = await directory.locator('nav a').evaluateAll(nodes => nodes.map(a => a.hash));
  assert.deepEqual(links, pages.map(p => '#page-' + p.pageNumber));
  for (const selector of ['#page-1', '#page-3', '#page-19', '#page-315']) {
    assert.ok(await staticPage.locator(selector).isVisible(), selector);
  }
  await assertStandaloneWidth(staticPage);
  await staticPage.close();
}

async function assertStandaloneWidth(page) {
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
    'Standalone reader should fit the mobile viewport');
}
