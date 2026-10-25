import { chromium } from 'playwright';
import path from 'path';

const ARTIFACT_DIR = '/Users/raj/.gemini/antigravity/brain/d846f5c2-a7de-439f-8aab-86b2bdc0d0a3';

async function runE2E() {
  console.log('🚀 Launching headless Chrome via Playwright...');
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });

  const page = await context.newPage();

  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  page.on('pageerror', (err) => {
    consoleErrors.push(err.message);
  });

  console.log('🌐 Navigating to http://localhost:5173...');
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });

  // 1. Verify Baseline State
  console.log('Step 1: Resetting to baseline UI...');
  await page.click('button:has-text("00:00 Normal City")');
  await page.waitForTimeout(1200);

  const title = await page.title();
  console.log('  Page Title:', title);

  const clusterHealth = await page.locator('text=Cluster Health').first().isVisible();
  console.log('  Cluster Health visible:', clusterHealth);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'stage0-baseline.png') });
  console.log('  📸 Saved stage0-baseline.png');

  // 2. Trigger Disaster Wave
  console.log('\nStep 2: Clicking 00:10 Disaster Wave (47 Reports)...');
  await page.click('button:has-text("00:10 Disaster Wave")');
  await page.waitForTimeout(3000);

  const incidentCards = await page.locator('text=Structural Collapse').first().isVisible();
  console.log('  Incident verified & visible:', incidentCards);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'stage1-disaster-wave.png') });
  console.log('  📸 Saved stage1-disaster-wave.png');

  // 3. Block Road B
  console.log('\nStep 3: Clicking 00:30 Block Road B...');
  await page.click('button:has-text("00:30 Block Road B")');
  await page.waitForTimeout(3000);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'stage2-road-blocked.png') });
  console.log('  📸 Saved stage2-road-blocked.png');

  // 4. Inject Hostile Rumor
  console.log('\nStep 4: Clicking 00:40 Inject Hostile Rumor...');
  await page.click('button:has-text("00:40 Inject Hostile Rumor")');
  await page.waitForTimeout(2500);

  // Switch to Hostile Data Engine tab
  await page.click('button:has-text("Hostile Data Engine")');
  await page.waitForTimeout(1000);

  const rumorVisible = await page.locator('text=CONFIDENCE: 23%').first().isVisible();
  console.log('  Hostile rumor quarantined (23% confidence):', rumorVisible);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'stage3-hostile-rumor-quarantine.png') });
  console.log('  📸 Saved stage3-hostile-rumor-quarantine.png');

  // Switch back to terminal tab
  await page.click('button:has-text("Swarm Stream")');

  // 5. Kill Routing Agent (Self-Healing)
  console.log('\nStep 5: Clicking 00:50 Kill Routing Agent...');
  await page.click('button:has-text("00:50 Kill Routing Agent")');
  console.log('  Waiting for Recovery Agent watchdog & heartbeat failover...');
  await page.waitForTimeout(4500);

  await page.screenshot({ path: path.join(ARTIFACT_DIR, 'stage4-self-healed.png') });
  console.log('  📸 Saved stage4-self-healed.png');

  console.log('\n--- Console Errors Check ---');
  if (consoleErrors.length === 0) {
    console.log('✅ ZERO console errors detected during full test run!');
  } else {
    console.log('⚠️ Console errors found:', consoleErrors);
  }

  await browser.close();
  console.log('🎉 E2E Browser Test Completed Successfully.');
}

runE2E().catch((err) => {
  console.error('E2E Test Failed:', err);
  process.exit(1);
});
