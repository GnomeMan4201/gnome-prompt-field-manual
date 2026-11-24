import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
import { chromium, firefox, webkit } from 'playwright';

const browserName = process.argv[2] || 'chromium';
const engines = { chromium, firefox, webkit };
assert.ok(engines[browserName], `Unsupported browser: ${browserName}`);

const manualUrl = pathToFileURL(resolve('index.html')).href;
const standaloneUrl = pathToFileURL(resolve('GNOME-Field-Manual.html')).href;
const reviewedPages = [
  [133, 'SCHEMA/CONTRACT,'],
  [154, 'canary observations'],
  [156, 'PATTERN-ONLY MATCH'],
  [157, 'ALERT THRESHOLDS'],
  [158, 'canary investigation'],
  [158, 'SAFE DEGRADATION'],
  [159, '7. FALLBACK BEHAVIOR'],
  [161, 'Indirect Injection Tracer, page 203'],
  [182, 'EDT-00: Use'],
  [184, 'seven cases'],
  [187, 'Tool-Agent Offense Probe'],
  [188, 'AUTHORIZATION SCOPE'],
  [189, 'ATTACK SURFACE INVENTORY'],
  [190, 'TEN COVERAGE CATEGORIES'],
  [191, 'COVERAGE CATEGORIES CONTINUED'],
  [192, 'VERDICT AND COVERAGE RULES'],
  [193, 'PER-PROBE RECORDS'],
  [194, 'ILLUSTRATIVE CONTROL PAIR'],
  [195, 'FOLLOW-UP — BEFORE EVALUATION'],
  [196, 'FOLLOW-UP — AFTER EVALUATION'],
  [197, 'Authorized self-assessment'],
];
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
    await assertPartialDisposition(page);
    await assertSearch(page);
    await assertTabInteractions(page);
    await assertReflow(page, scenario);
    await assertReviewedPages(page, scenario);
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

async function assertPartialDisposition(page) {
  const inventory = page.locator('#inventory');
  const sec05 = inventory.locator('.entry-row').filter({ hasText: 'SEC-05' });
  assert.equal(await inventory.locator('.entry-row').count(), 9);
  assert.equal(await inventory.locator('.er-id').filter({ hasText: 'SEC-02' }).count(), 0);
  assert.equal(await page.locator('#b-sec02').count(), 0);
  assert.ok(await sec05.isVisible());
  assert.equal(await sec05.getByRole('link', { name: 'Unresolved evidence record' }).getAttribute('href'),
    'docs/BATCH6_SEC05_UNRESOLVED_EVIDENCE_2026-11-24.md');
  await sec05.getByRole('link', { name: 'Open drafting brief' }).click();
  assert.ok(await page.locator('#b-sec05.open:target .brief-body').isVisible());

  await page.getByRole('link', { name: 'SEC-02 disposition and current guidance' }).click();
  const disposition = page.locator('#sec02-disposition:target');
  assert.ok(await disposition.isVisible());
  assert.equal(await disposition.getByRole('link', { name: 'the superseding interpretation' }).getAttribute('href'),
    'docs/BATCH6_ADJUDICATION_AMENDMENT_2026-11-24.md');
  await disposition.getByRole('link', { name: 'current canary evidence guidance on page 156' }).click();
  assert.ok(await page.locator('#manual-page-156:target').isVisible());

  assert.equal(await page.locator('.batch-table tbody tr').count(), 5);
  assert.deepEqual(await page.locator('.batch-table tbody tr').first().locator('td').allTextContents(),
    ['6', 'SEC-05', '1', 'Batch 6 remains open pending independent evidence for the SEC-05 blocking requirement.']);
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

      await page.goto(url + '#book/page-130');
      const summaryPage = page.locator('#main-root .book-page');
      await summaryPage.waitFor();
      const summary = normalize(await summaryPage.innerText()).toUpperCase();
      for (const category of [
        'MANDATORY FOUR-CATEGORY RISK SUMMARY',
        'DATA COMPATIBILITY RISK',
        'BEHAVIORAL RISK',
        'INTEGRATION RISK',
        'ROLLBACK COMPLEXITY RISK',
        'UNASSESSED',
      ]) {
        assert.ok(summary.includes(category), `${layout.name}: page 130 missing ${category}`);
      }
      await page.goto(url + '#book/page-133');
      await rendered.waitFor();

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

async function assertReviewedPages(canonical, scenario) {
  const dynamic = await browser.newPage({ viewport: scenario.viewport });
  const offline = await browser.newPage({
    javaScriptEnabled: false, viewport: scenario.viewport, reducedMotion: 'reduce',
  });
  const errors = [];
  dynamic.on('pageerror', error => errors.push(String(error)));
  try {
    await dynamic.goto(standaloneUrl + '#book/page-133');
    await offline.goto(standaloneUrl + '#page-directory');
    const staticDirectory = offline.locator('#page-directory');

    for (const [number, phrase] of reviewedPages) {
      const scope = `${scenario.name} page ${number}`;
      const card = canonical.locator('#manual-page-' + number);
      await canonical.getByLabel('Search manual text', { exact: true }).fill(phrase.toLowerCase());
      assert.ok(await card.isVisible(), `${scope}: canonical search`);
      await canonical.goto(manualUrl + '#manual-page-' + number);
      assert.ok(canonical.url().endsWith('#manual-page-' + number));
      assert.ok(await card.evaluate(element => element.matches(':target')), `${scope}: canonical anchor`);
      await assertPageBody(card.locator('pre'), phrase, `${scope}: canonical`);

      const directory = dynamic.locator('#book-contents');
      if (await directory.getAttribute('open') === null) {
        await directory.locator('summary').click();
      }
      await directory.locator('#book-search').fill(phrase);
      await directory.locator(`[data-pnum="${number}"]`).click();
      assert.ok(dynamic.url().endsWith('#book/page-' + number), `${scope}: standalone search navigation`);
      const dynamicCard = dynamic.locator('#main-root .book-page');
      assert.match(await dynamicCard.locator('h2').innerText(), new RegExp(`^Page ${number}\\b`));
      await assertPageBody(dynamicCard.locator('.book-prose'), phrase, `${scope}: standalone dynamic`);

      const pageLink = offline.locator(`nav a[href="#page-${number}"]`);
      const chapter = staticDirectory.locator('details').filter({ has: pageLink });
      for (const section of [staticDirectory, chapter]) {
        if (await section.getAttribute('open') === null) {
          await section.locator(':scope > summary').click();
        }
      }
      await chapter.locator(pageLink).click();
      const staticCard = offline.locator(`#page-${number}:target`);
      const staticBody = staticCard.locator('.book-prose');
      await assertPageBody(staticBody, phrase, `${scope}: standalone static`);
      assert.equal(normalize(await dynamicCard.locator('.book-prose').textContent()),
        normalize(await staticBody.textContent()), `${scope}: standalone presentation parity`);
      await staticCard.getByRole('link', { name: 'Page directory', exact: true }).click();
    }
    assert.deepEqual(errors, [], `${scenario.name}: standalone page errors`);
  } finally {
    await dynamic.close();
    await offline.close();
  }
}

async function assertPageBody(body, phrase, scope) {
  const passage = body.getByText(phrase, { exact: false });
  // The canonical pre is itself the text element. Standalone bodies contain blocks.
  assert.ok(await body.isVisible() && (
    await passage.count() ? await passage.first().isVisible()
      : normalize(await body.textContent()).includes(phrase)
  ), `${scope}: missing visible text ${phrase}`);
  const geometry = await body.evaluate(element => {
    const box = element.getBoundingClientRect();
    const clipped = [element, ...element.children].some(node =>
      node.scrollWidth > node.clientWidth + 1 || node.scrollHeight > node.clientHeight + 1
    );
    return {
      left: box.left, right: box.right, viewport: innerWidth,
      documentWidth: document.documentElement.scrollWidth, clipped,
    };
  });
  assert.ok(!geometry.clipped && geometry.left >= -1 && geometry.right <= geometry.viewport + 1
    && geometry.documentWidth <= geometry.viewport + 1, `${scope}: clipping ${JSON.stringify(geometry)}`);
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
  for (const [number, phrase] of reviewedPages) {
    assert.ok(pages[number - 1].text.toLowerCase().includes(phrase.toLowerCase()),
      `Page ${number}: search phrase must be continuous in the standalone dataset`);
  }
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
