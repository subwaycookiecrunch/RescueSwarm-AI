# 🚨 RescueSwarm AI

> **Working tagline:** *“When everything goes wrong, the swarm reorganizes.”*

**RescueSwarm AI** is a fault-tolerant multi-agent coordination system that converts chaotic, hostile crisis information streams into synchronized, real-time emergency actions during large-scale urban and mountainous disasters.

---

## ⚡ The Core Differentiator: A Self-Healing Swarm

Normal multi-agent architectures are brittle: if an agent fails or crashes, its capability dies with it.

RescueSwarm is built with an **autonomous self-healing recovery loop**:
1. Five specialized agents run asynchronously across an event-driven pub/sub bus.
2. The **Recovery Agent** acts as a heartbeat watchdog (every 400ms).
3. If an agent crashes (e.g. killed via Chaos Injection):
   - Silence is detected within 1.4s.
   - Heartbeat loss confirmed.
   - Responsibilities are dynamically redistributed to an active backup node.
   - Graph routing caches and pending vehicle dispatches are preserved with zero packet loss.
   - Swarm operational health restored to 100%.

In hostile data streams (contradictory rumors, bot attacks, panicking callers), the **Verification Agent** performs spatial-temporal clustering and multi-source Bayesian weighting (Sensors: 0.95, Responders: 0.98, Social: 0.25) to synthesize 47 chaotic inputs into verified ground-truth incidents, while **quarantining unsubstantiated rumors** (e.g., *"100 people trapped at Location X"* — confidence 23%) so critical ambulances are never wasted.

---

## 🏛️ Swarm Agent Architecture

```
 Citizens ─────┐
 Sensors ──────┤
 Hospitals ────┤
 Responders ───┤
 Weather ──────┤
 Road data ────┘
       ↓
  CHAOTIC EVENT STREAM (47 Reports)
       ↓
┌───────────────────────────────────────────────┐
│               RESCUESWARM AI                  │
│                                               │
│ 1. Verification Agent (Credibility & Fusion)  │
│ 2. Triage Agent       (Severity & Priority)   │
│ 3. Routing Agent      (Dynamic Road Graph)    │
│ 4. Resource Agent     (Fleet Dispatch Match)  │
│ 5. Recovery Agent     (Watchdog & Failover)   │
└───────────────────────────────────────────────┘
       ↓
 Autonomous Decisions & Detour Recalculation
       ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
↓              ↓              ↓              ↓              ↓
Ambulance-03   Detour Route   Rescue Teams   Quarantined    Swarm
Dispatch       around Road B  Deployed       Rumor (23%)    Restored ✓
```

---

## 🚀 Quickstart & Milestone Execution

### 1. Milestone 1 — Interactive Terminal CLI
To experience the pure terminal demonstration:
```bash
./venv/bin/python -m rescueswarm.cli --demo
```
Or launch the interactive command shell:
```bash
./venv/bin/python -m rescueswarm.cli
```

### 2. Full Visual Command Center (React + FastAPI + Leaflet)

Start the Backend (FastAPI + WebSockets):
```bash
./venv/bin/python -m uvicorn rescueswarm.api:app --reload --port 8000
```

Start the Frontend (React + Vite + Tailwind):
```bash
cd frontend && npm run dev
```

Open `http://localhost:5173` in your browser.

---

## 🎬 The Finale Demo Sequence (Interactive Storyboard)

| Time | Stage | Action & System Reaction |
|---|---|---|
| **00:00** | **Baseline Normal City** | 0 Incidents, 5/5 Agents Active, Cluster Health: 100%. |
| **00:10** | **Major Emergency Wave** | 47 chaotic reports hit the cluster. The **Verification Agent** clusters them into 4 physical incidents with 96% confidence. |
| **00:20** | **Triage & Dispatch** | Classified as `CRITICAL — MULTIPLE CASUALTIES`. **Resource Agent** assigns `Ambulance-03`. **Routing Agent** generates path: `Hospital ➔ Road A ➔ Road B ➔ Incident`. |
| **00:30** | **Road B Blocked** | Operator clicks `BLOCK ROAD B`. Route is invalidated immediately; **Routing Agent** calculates alternate mountain detour around the blockage in real time. |
| **00:40** | **Hostile Rumor Injected** | *"100 PEOPLE TRAPPED AT LOCATION X"*. Zero physical sensors or responder confirmation. System outputs `UNVERIFIED — confidence 23% [QUARANTINED]`. No ambulances wasted. |
| **00:50** | **KILL ROUTING AGENT** | Hard process crash injected. Heartbeats cease. **Recovery Agent** detects failure, confirms heartbeat lost, synchronizes state, redistributes role to Backup Node, and restores cluster health to 100%! |

---

## 🧪 Automated Test Suite

Run unit and integration tests:
```bash
./venv/bin/pytest tests/
```
All tests verify fault-tolerance, hostile data quarantine, dynamic detour recalculation, and self-healing failover.
