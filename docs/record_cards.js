// Record the intro and outro cards (GSAP animations) to WebM.
// NODE_PATH=~/repopilot-recording/node_modules node /home/ec2-user/checkpoint/docs/record_cards.js
const { chromium } = require('playwright-core');
const CHROME = '/home/ec2-user/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';

async function recordCard(file, outDir, holdMs) {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: outDir, size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();
  await page.goto('file://' + file, { waitUntil: 'load' });
  await page.waitForTimeout(holdMs); // let the animation play + hold
  await context.close();
  await browser.close();
  console.log('card done ->', outDir);
}

(async () => {
  const dir = '/home/ec2-user/checkpoint/docs/cards';
  await recordCard('/home/ec2-user/checkpoint/docs/card-intro.html', dir + '/intro', 7000);  // ~7s
  await recordCard('/home/ec2-user/checkpoint/docs/card-outro.html', dir + '/outro', 10000); // ~10s
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
