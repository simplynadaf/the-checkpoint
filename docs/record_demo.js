// Automated gameplay recording for The Checkpoint.
// Records a webm of two playthroughs: an honest traveler (cleared) and a lying traveler
// (suspicion climbs). Uses Playwright's native video capture. Convert to mp4 with ffmpeg.
//
// Run from ~/repopilot-recording (where playwright-core resolves):
//   node /home/ec2-user/checkpoint/docs/record_demo.js
const { chromium } = require('playwright-core');

const CHROME = '/home/ec2-user/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';
const URL = 'http://127.0.0.1:8080/';
const OUT_DIR = '/home/ec2-user/checkpoint/docs/recording';

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
  await page.fill('#say', text);
  await page.waitForTimeout(500);
  await page.click('button[type=submit]');
  // wait for the readout to update (consistent value changes from the placeholder)
  await page.waitForFunction(
    () => {
      const el = document.getElementById('consVal');
      return el && el.textContent && el.textContent !== '\u00b7';
    },
    { timeout: 90000 }
  ).catch(() => {});
  await page.waitForTimeout(2500); // hold so the gauge animation reads on camera
}

(async () => {
  const browser = await chromium.launch({ executablePath: CHROME, headless: true, args: ['--no-sandbox'] });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    recordVideo: { dir: OUT_DIR, size: { width: 1280, height: 800 } },
  });
  const page = await context.newPage();
  await page.goto(URL, { waitUntil: 'load' });
  await page.waitForTimeout(3000); // title + opening guard line

  // Honest run
  for (const line of HONEST) await type(page, line);
  await page.waitForTimeout(3000); // let "Cleared" sit

  // Restart, lying run
  await page.click('#restart');
  await page.waitForTimeout(2500);
  for (const line of LIAR) {
    await type(page, line);
    const meter = await page.evaluate(() => parseInt(document.getElementById('meterPct').textContent) || 0);
    if (meter >= 80) break; // alarm reached
  }
  await page.waitForTimeout(3500); // hold final state

  await context.close(); // flushes the video file
  await browser.close();
  console.log('recording complete ->', OUT_DIR);
})().catch((e) => { console.error('ERR', e.message); process.exit(1); });
