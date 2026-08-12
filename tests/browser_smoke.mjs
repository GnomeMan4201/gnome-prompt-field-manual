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

function normalize(value) {
  return value.replace(/\s+/g, ' ').trim();
}
