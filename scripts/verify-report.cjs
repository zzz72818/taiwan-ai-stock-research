// Optional developer check: install playwright and set BROWSER_PATH if needed.
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.BROWSER_PATH ? { executablePath: process.env.BROWSER_PATH } : {}) });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 1100 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const { pathToFileURL } = require('url');
    const path = require('path');
    await page.goto(pathToFileURL(path.resolve('reports/entry-dashboard.html')).href);
    for (const symbol of ['2330', '2382', '6669', '3017']) {
      await page.getByRole('button', { name: new RegExp(symbol) }).click();
      if (await page.locator('svg').count() !== 1) throw Error('Chart missing: ' + symbol);
    }
    await page.locator('select').selectOption('9999');
    await page.getByRole('button', { name: /2330/ }).click();
    await page.screenshot({ path: 'reports/dashboard-preview.png', fullPage: true });
    if (errors.length) throw Error(errors.join('\n'));
    console.log('PASS: four stock tabs, range selection, chart rendering, no JS errors');
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
