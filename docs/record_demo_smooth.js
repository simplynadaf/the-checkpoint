// Smooth 1080p recording for The Checkpoint — whole UI in one frame.
// Records at a 1920x1080 viewport (deviceScaleFactor 1) so the headless browser can hit a
// steady, high real frame rate on CPU. Smooth motion beats choppy 4K for a demo.
// The record-only CSS trims vertical spacing so the full page fits one 1080p frame.
//
// Run from ~/repopilot-recording:
//   NODE_PATH=~/repopilot-recording/node_modules node /home/ec2-user/checkpoint/docs/record_demo_smooth.js
const { chromium } = require('playwright-core');

const CHROME = '/home/ec2-user/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const URL = 'http://127.0.0.1:8080/';
const OUT_DIR = '/home/ec2-user/checkpoint/docs/recording_smooth';

// Fit the whole page into one 1080p frame.
const FIT_CSS = `
  main { padding-top: 22px !important; padding-bottom: 16px !important; }
  header { margin-bottom: 22px !important; }
  #tiltChat .inner { height: 560px !important; min-height: 0 !important; }
  footer { margin-top: 14px !important; padding-top: 14px !important; }
  p.reveal { margin-top: 16px !important; }
`;

const HONEST = [
  'Evening officer, I am just heading home after visiting my mother in the next town.',
];
const LIAR = [
  'Evening. I am a tourist, just arrived today for a short holiday.',
  'I have lived in this city my whole life, officer, you can trust me.',
  'That bag is not mine. I have never seen it before in my life.',
  'There is nothing inside it, and also it is full of my own clothes.',
];

async function type(page, text) {
  await page.waitForSelector('#say:not([disabled])', { timeout: 30000 }).catch(() => {});
  // type char by char so the recording shows real typing motion
  await page.click('#say');
  await page.type('#say', text, { delay: 28 });
  await page.waitForTimeout(400);
  await page.click('button[type=submit]');
  await page.waitForFunction(
    () => { const el = document.getElementById('consVal'); return el && el.textContent && el.textContent !== '\u00b7'; },
    { timeout: 90000 }
  ).catch(() => {});
  await page.waitForTimeout(2200); // hold so the gauge animation reads, but keep it tight
}

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true, args: ['--no-sandbox']
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
    recordVideo: { dir: OUT_DIR, size: { width: 1920, height: 1080 } },
  });
  const page = await context.newPage();
  await page.addInitScript((css) => {
    const s = document.createElement('style'); s.textContent = css;
    document.addEventListener('DOMContentLoaded', () => document.head.appendChild(s));
  }, FIT_CSS);
  await page.goto(URL, { waitUntil: 'load' });
  await page.addStyleTag({ content: FIT_CSS });
  await page.waitForTimeout(3000);

  for (const line of HONEST) await type(page, line);
  await page.waitForTimeout(2600);

  await page.click('#restart');
  await page.waitForSelector('#say:not([disabled])', { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(2200);
  for (const line of LIAR) {
    await type(page, line);
    const meter = await page.evaluate(() => parseInt(document.getElementById('meterPct').textContent) || 0);
    if (meter >= 80) break;
  }
  await page.waitForTimeout(3200);

  await context.close();
  await browser.close();
  console.log('smooth recording complete ->', OUT_DIR);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
