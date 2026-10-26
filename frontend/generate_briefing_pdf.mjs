import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const OUTPUT_PDF_LOCAL = '/Users/raj/Desktop/manali hack/RescueSwarm_AI_Executive_Briefing.pdf';
const OUTPUT_PDF_ARTIFACT = '/Users/raj/.gemini/antigravity/brain/d846f5c2-a7de-439f-8aab-86b2bdc0d0a3/RescueSwarm_AI_Executive_Briefing.pdf';

const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>RescueSwarm AI — Executive Briefing</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');

    @page {
      size: A4;
      margin: 16mm 14mm 16mm 14mm;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      color: #0f172a;
      background-color: #ffffff;
      line-height: 1.5;
      font-size: 10.5pt;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    .header {
      background: linear-gradient(135deg, #090d16 0%, #0f172a 100%);
      color: #ffffff;
      padding: 22px 24px;
      border-radius: 12px;
      margin-bottom: 20px;
      border-left: 6px solid #06b6d4;
    }

    .badge-bar {
      display: flex;
      gap: 8px;
      margin-bottom: 10px;
    }

    .badge {
      display: inline-block;
      font-size: 7.5pt;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      padding: 3px 8px;
      border-radius: 4px;
    }

    .badge-cyan {
      background-color: rgba(6, 182, 212, 0.2);
      color: #22d3ee;
      border: 1px solid rgba(6, 182, 212, 0.4);
    }

    .badge-amber {
      background-color: rgba(245, 158, 11, 0.2);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.4);
    }

    .title {
      font-size: 24pt;
      font-weight: 900;
      letter-spacing: -0.5px;
      color: #ffffff;
      line-height: 1.1;
      margin-bottom: 4px;
    }

    .tagline {
      font-size: 11pt;
      font-style: italic;
      color: #94a3b8;
      margin-bottom: 12px;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      padding-top: 12px;
      border-top: 1px solid rgba(255, 255, 255, 0.12);
      font-size: 8.5pt;
      color: #cbd5e1;
    }

    .meta-item strong {
      color: #ffffff;
      display: block;
      font-size: 7.5pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #38bdf8;
    }

    h2 {
      font-size: 13pt;
      font-weight: 800;
      color: #0f172a;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 5px;
      margin-top: 22px;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    h2 .icon {
      color: #0284c7;
    }

    h3 {
      font-size: 10.5pt;
      font-weight: 700;
      color: #1e293b;
      margin-top: 12px;
      margin-bottom: 6px;
    }

    p {
      margin-bottom: 8px;
      font-size: 9.5pt;
      color: #334155;
    }

    .problem-box {
      background-color: #fef2f2;
      border: 1px solid #fecaca;
      border-left: 4px solid #ef4444;
      padding: 12px 14px;
      border-radius: 8px;
      margin-bottom: 14px;
    }

    .problem-box h4 {
      color: #991b1b;
      font-size: 9.5pt;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 14px;
    }

    .card {
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px;
      page-break-inside: avoid;
    }

    .card-title {
      font-size: 9.5pt;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .table-container {
      margin-bottom: 16px;
      page-break-inside: avoid;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 8.5pt;
      border: 1px solid #cbd5e1;
    }

    th {
      background-color: #0f172a;
      color: #ffffff;
      text-align: left;
      padding: 8px 10px;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 7.5pt;
      letter-spacing: 0.5px;
    }

    td {
      padding: 8px 10px;
      border-bottom: 1px solid #e2e8f0;
      color: #334155;
      vertical-align: top;
    }

    tr:nth-child(even) {
      background-color: #f8fafc;
    }

    .pill {
      display: inline-block;
      font-size: 7pt;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }

    .pill-red { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
    .pill-cyan { background: #cffafe; color: #0e7490; border: 1px solid #a5f3fc; }
    .pill-green { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .pill-purple { background: #f3e8ff; color: #7e22ce; border: 1px solid #d8b4fe; }

    .timeline {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 16px;
      page-break-inside: avoid;
    }

    .timeline-item {
      display: grid;
      grid-template-columns: 60px 1fr;
      gap: 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 8.5pt;
    }

    .time-badge {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      color: #0284c7;
      background: #e0f2fe;
      padding: 4px 6px;
      border-radius: 4px;
      text-align: center;
      height: fit-content;
      font-size: 8pt;
    }

    .footer {
      margin-top: 24px;
      padding-top: 10px;
      border-top: 1px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      font-size: 7.5pt;
      color: #64748b;
    }

    .code-pill {
      font-family: 'JetBrains Mono', monospace;
      font-size: 7.5pt;
      background: #f1f5f9;
      padding: 2px 5px;
      border-radius: 4px;
      border: 1px solid #cbd5e1;
      color: #0f172a;
    }

    .page-break {
      page-break-after: always;
    }
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="header">
    <div class="badge-bar">
      <span class="badge badge-cyan">Autonomous AI Swarm</span>
      <span class="badge badge-amber">Hostile Data Resilient</span>
      <span class="badge badge-cyan">Defense & Crisis Coordination</span>
    </div>
    <div class="title">RESCUESWARM AI</div>
    <div class="tagline">“When everything goes wrong, the swarm reorganizes.”</div>

    <div class="meta-grid">
      <div class="meta-item">
        <strong>GitHub Repository</strong>
        subwaycookiecrunch/RescueSwarm-AI
      </div>
      <div class="meta-item">
        <strong>Team & Roles</strong>
        Daksh (Backend) • Raj (AI & Swarm) • Somesh (Domain & Pitch)
      </div>
      <div class="meta-item">
        <strong>Status</strong>
        Full Stack Live (FastAPI + React + WebSockets)
      </div>
    </div>
  </div>

  <!-- SECTION 1: THE CRISIS PROBLEM -->
  <h2><span class="icon">⚡</span> 1. The Real-World Crisis Problem</h2>
  <div class="problem-box">
    <h4>Why Normal Emergency Software Fails During Large Catastrophes</h4>
    <p>
      During disasters (landslides, flash floods, quakes, urban structural collapses), crisis centers aren't bottlenecked by lack of data. They are overwhelmed by a <strong>hostile information environment</strong>:
    </p>
    <ul style="margin-left: 20px; font-size: 8.5pt; color: #450a0a;">
      <li><strong>Incomplete & Contradictory:</strong> One caller reports 5 casualties; panic tweets claim 500 dead.</li>
      <li><strong>Duplicated & Stale:</strong> 20 calls describe the same building collapse from 25 minutes ago.</li>
      <li><strong>Manipulated / Fake Rumors:</strong> Social media bots inject dramatic fake distress alerts that drain scarce units.</li>
      <li><strong>Rapid Terrain Shifting:</strong> Key bridges and roads collapse mid-transit, invalidating human dispatcher plans.</li>
    </ul>
  </div>

  <!-- SECTION 2: THE SOLUTION ARCHITECTURE -->
  <h2><span class="icon">🏛️</span> 2. The Solution: RescueSwarm Multi-Agent Swarm</h2>
  <p>
    RescueSwarm converts chaotic, hostile crisis streams into synchronized, ground-truth physical emergency actions via an autonomous 5-agent coordination architecture:
  </p>

  <div class="table-container">
    <table>
      <thead>
        <tr>
          <th style="width: 22%;">Swarm Agent</th>
          <th style="width: 38%;">Core Function</th>
          <th style="width: 40%;">Underlying Intelligence Engine</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Verification Agent</strong><br/><span class="pill pill-cyan">Noise Defense</span></td>
          <td>Filters adversarial rumors, deduplicates repeated citizen calls, correlates multi-source evidence.</td>
          <td>Spatial clustering (&lt;800m), temporal windowing (&lt;15m), and Bayesian source weighting (Sensors: 0.95, Responders: 0.98, Social: 0.25).</td>
        </tr>
        <tr>
          <td><strong>2. Triage Agent</strong><br/><span class="pill pill-red">Severity Matrix</span></td>
          <td>Assesses verified casualties, structural hazards, and determines crisis response priorities.</td>
          <td>Dynamic priority queue classifying scenes into <code>CRITICAL — MULTIPLE CASUALTIES</code>, <code>HIGH</code>, <code>MEDIUM</code>, or <code>LOW</code>.</td>
        </tr>
        <tr>
          <td><strong>3. Resource Agent</strong><br/><span class="pill pill-green">Fleet Dispatch</span></td>
          <td>Assigns nearest qualified emergency vehicles (ALS Ambulances, USAR Rescue Teams, Fire Tenders).</td>
          <td>Real-time nearest-neighbor fleet allocation matrix matching vehicle medical capability to scene severity.</td>
        </tr>
        <tr>
          <td><strong>4. Routing Agent</strong><br/><span class="pill pill-purple">Dynamic Graph</span></td>
          <td>Calculates optimal navigation across road graph. Reacts to landslides by computing detours.</td>
          <td>NetworkX Dijkstra/A* graph algorithm with dynamic edge invalidation and real-time rerouting around hazards.</td>
        </tr>
        <tr>
          <td><strong>5. Recovery Agent</strong><br/><span class="pill pill-cyan">Self-Healing</span></td>
          <td>Heartbeat watchdog. Detects node deaths, transfers roles, and syncs state to standby nodes.</td>
          <td>400ms heartbeat polling. Detects silence &gt;1.4s, executes automated state failover with zero packet loss.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="page-break"></div>

  <!-- SECTION 3: THE TWO KILLER DIFFERENTIATORS -->
  <h2><span class="icon">🛡️</span> 3. The Two Core Differentiators</h2>

  <div class="grid-2">
    <div class="card" style="border-left: 4px solid #7c3aed;">
      <div class="card-title">
        <span style="color: #7c3aed;">★</span> Differentiator 1: Self-Healing AI Swarm
      </div>
      <p style="font-size: 8.5pt;">
        Normal multi-agent architectures are brittle: if the Routing Agent process crashes, all navigation halts.
      </p>
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px; font-family: 'JetBrains Mono', monospace; font-size: 7.5pt; margin-top: 6px;">
        Routing Agent Crashes 💥<br/>
        &nbsp;&nbsp;↓ Heartbeat silence &gt; 1.4s<br/>
        Recovery Watchdog Detects Failure<br/>
        &nbsp;&nbsp;↓ Responsibilities redistributed<br/>
        Backup Standby Node Promoted<br/>
        &nbsp;&nbsp;↓ Active routes & graph synchronized<br/>
        Swarm Restored (Health: 100%) ✓
      </div>
    </div>

    <div class="card" style="border-left: 4px solid #0284c7;">
      <div class="card-title">
        <span style="color: #0284c7;">★</span> Differentiator 2: Hostile Data Immunity
      </div>
      <p style="font-size: 8.5pt;">
        When 47 chaotic reports hit the system, RescueSwarm cross-validates them against physical IoT sensors and responder ground units.
      </p>
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px; font-family: 'JetBrains Mono', monospace; font-size: 7.5pt; margin-top: 6px;">
        Injected: "100 TRAPPED AT LOCATION X"<br/>
        Source: Anonymous Telegram post<br/>
        Sensor Corroboration: 0<br/>
        Responder Radio: 0<br/>
        Calculated Confidence: 23%<br/>
        <strong style="color: #dc2626;">STATUS: QUARANTINED (No units wasted)</strong>
      </div>
    </div>
  </div>

  <!-- SECTION 4: THE FINALE PITCH DEMO -->
  <h2><span class="icon">🎬</span> 4. The Finale Pitch Demonstration (“Try to Break It”)</h2>
  <p>
    Rather than a passive presentation, the team challenges the judges: <em>“Instead of showing you RescueSwarm, we're going to try to break it.”</em>
  </p>

  <div class="timeline">
    <div class="timeline-item">
      <div class="time-badge">00:00</div>
      <div>
        <strong>Baseline Normal City:</strong> 0 Incidents, 5/5 Agents Active, Cluster Health: 100%. Road network clear.
      </div>
    </div>
    <div class="timeline-item">
      <div class="time-badge">00:10</div>
      <div>
        <strong>Disaster Wave Injected:</strong> 47 chaotic incoming reports hit the stream. Verification Agent clusters them into 4 real incidents with 96% confidence.
      </div>
    </div>
    <div class="timeline-item">
      <div class="time-badge">00:20</div>
      <div>
        <strong>Triage & Dispatch:</strong> Mall Road classified as <code>CRITICAL — MULTIPLE CASUALTIES</code>. Resource Agent assigns <code>Ambulance-03</code>; Routing Agent plots route through Aleo Bridge (Road B).
      </div>
    </div>
    <div class="timeline-item">
      <div class="time-badge">00:30</div>
      <div>
        <strong>Chaos #1 — BLOCK ROAD B:</strong> Operator triggers road collapse. Active route invalidated immediately; swarm calculates dynamic detour around river.
      </div>
    </div>
    <div class="timeline-item">
      <div class="time-badge">00:40</div>
      <div>
        <strong>Chaos #2 — HOSTILE FAKE NEWS:</strong> Operator injects <em>“100 PEOPLE TRAPPED AT LOCATION X”</em>. Verification Agent calculates 23% confidence and quarantines the claim. Zero units wasted.
      </div>
    </div>
    <div class="timeline-item">
      <div class="time-badge">00:50</div>
      <div>
        <strong>Chaos #3 — KILL ROUTING AGENT:</strong> Hard process termination. Heartbeat ceases. Recovery Watchdog detects failure within 1.4s, transfers authority to Backup Node, and restores health to 100%.
      </div>
    </div>
  </div>

  <!-- SECTION 5: WHAT NOT TO BUILD PHILOSOPHY -->
  <h2><span class="icon">🚫</span> 5. What This Project Is NOT</h2>
  <div style="background: #f1f5f9; padding: 10px 14px; border-radius: 8px; font-size: 8.5pt;">
    <p style="margin-bottom: 4px;"><strong>Strict Architectural Principles:</strong></p>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; color: #475569;">
      <div>❌ Not a disaster prediction tool</div>
      <div>❌ Not a chatbot pretending to be agents</div>
      <div>❌ Not a static non-interactive map</div>
      <div>❌ Not generic emergency reporting</div>
      <div>✅ Real event-driven asynchronous pub/sub</div>
      <div>✅ Deterministic NetworkX pathfinding</div>
      <div>✅ Bayesian sensor correlation matrix</div>
      <div>✅ Live WebSocket command center dashboard</div>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <div>RescueSwarm AI • Official Project Briefing • Generated October 2026</div>
    <div>Codebase: <span class="code-pill">https://github.com/subwaycookiecrunch/RescueSwarm-AI</span></div>
  </div>

</body>
</html>`;

async function generatePDF() {
  console.log('🚀 Launching headless Chrome via Playwright to generate PDF...');
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });

  const page = await browser.newPage();
  await page.setContent(htmlContent, { waitUntil: 'networkidle' });

  // Generate PDF locally
  await page.pdf({
    path: OUTPUT_PDF_LOCAL,
    format: 'A4',
    printBackground: true,
    margin: {
      top: '12mm',
      bottom: '12mm',
      left: '12mm',
      right: '12mm',
    },
  });

  // Also copy to artifact directory
  fs.copyFileSync(OUTPUT_PDF_LOCAL, OUTPUT_PDF_ARTIFACT);

  await browser.close();
  console.log('✅ PDF generated successfully:');
  console.log('   Local path:   ', OUTPUT_PDF_LOCAL);
  console.log('   Artifact path:', OUTPUT_PDF_ARTIFACT);
}

generatePDF().catch(console.error);
