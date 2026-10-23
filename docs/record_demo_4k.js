// 4K recording for The Checkpoint — whole UI in one frame, no scrolling.
// Records at a 2560x1440 viewport with deviceScaleFactor 1.5 => true 3840x2160 device pixels.
// A small record-only CSS override trims vertical spacing so header + chat + gauge +
// readout + footer all fit in a single frame. Outputs WebM; convert to 4K mp4 with ffmpeg.
//
// Run from ~/repopilot-recording:
//   node /home/ec2-user/checkpoint/docs/record_demo_4k.js
const { chromium } = require('playwright-core');

const CHROME = '/home/ec2-user/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const URL = 'http://127.0.0.1:8080/';
const OUT_DIR = '/home/ec2-user/checkpoint/docs/recording4k';

// Record-only CSS: trim the generous spacing so the full page fits one 1440p frame.
const FIT_CSS = `
  main { padding-top: 28px !important; padding-bottom: 20px !important; }
  header { margin-bottom: 28px !important; }
  .inner { height: auto !important; }
  #tiltChat .inner { height: 760px !important; min-height: 0 !important; }
  footer { margin-top: 18px !important; padding-top: 18px !important; }
  p.reveal { margin-top: 20px !important; }
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
  // wait until the input is actually enabled before typing (post-restart / post-preloader)
  await page.waitForSelector('#say:not([disabled])', { timeout: 30000 }).catch(() => {});
  await page.fill('#say', text);
  await page.waitForTimeout(600);
  await page.click('button[type=submit]');
  await page.waitForFunction(
    () => { const el = document.getElementById('consVal'); return el && el.textContent && el.textContent !== '\u00b7'; },
    { timeout: 90000 }
  ).catch(() => {});
  await page.waitForTimeout(2800); // hold so the gauge animation reads on camera
}

(async () => {
  const browser = await chromium.launch({
    executablePath: CHROME, headless: true,
    args: ['--no-sandbox', '--force-device-scale-factor=1.5', '--high-dpi-support=1']
  });
  const context = await browser.newContext({
    viewport: { width: 2560, height: 1440 },
    deviceScaleFactor: 1.5,
    recordVideo: { dir: OUT_DIR, size: { width: 3840, height: 2160 } },
  });
  const page = await context.newPage();
  // inject the fit CSS before the page paints
  await page.addInitScript((css) => {
    const s = document.createElement('style'); s.textContent = css;
    document.addEventListener('DOMContentLoaded', () => document.head.appendChild(s));
  }, FIT_CSS);
  await page.goto(URL, { waitUntil: 'load' });
  await page.addStyleTag({ content: FIT_CSS }); // ensure applied
  await page.waitForTimeout(3200); // preloader + title + opening line

  // Honest run
  for (const line of HONEST) await type(page, line);
  await page.waitForTimeout(3200);

  // Restart, lying run
  await page.click('#restart');
  await page.waitForSelector('#say:not([disabled])', { timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(2600);
  for (const line of LIAR) {
    await type(page, line);
    const meter = await page.evaluate(() => parseInt(document.getElementById('meterPct').textContent) || 0);
    if (meter >= 80) break;
  }
  await page.waitForTimeout(3800); // hold final

  await context.close();
  await browser.close();
  console.log('4K recording complete ->', OUT_DIR);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
