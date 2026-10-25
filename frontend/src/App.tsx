import React, { useState, useEffect, useRef } from 'react';
import { SwarmState } from './types';
import { MapComponent } from './components/MapComponent';
import { AgentCard } from './components/AgentCard';
import { HostileDataInspector } from './components/HostileDataInspector';
import { TerminalLogs } from './components/TerminalLogs';
import {
  Activity,
  Radio,
  Play,
  RotateCcw,
  Sparkles,
  Layers,
  Terminal,
  Cpu,
} from 'lucide-react';
import confetti from 'canvas-confetti';

export const App: React.FC = () => {
  const [state, setState] = useState<SwarmState | null>(null);
  const [activeTab, setActiveTab] = useState<'terminal' | 'hostile_data'>('terminal');
  const [autoDemoRunning, setAutoDemoRunning] = useState<boolean>(false);
  const [demoStep, setDemoStep] = useState<number>(0);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to RescueSwarm WebSocket');
      ws.send(JSON.stringify({ action: 'GET_STATE' }));
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'FULL_STATE' && msg.data) {
          setState(msg.data);
        } else if (msg.type === 'LOG' && msg.log) {
          setState((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              logs: [...prev.logs, msg.log],
            };
          });
        } else if (msg.type === 'EVENT') {
          // Re-fetch full state on significant events
          fetch('/api/state')
            .then((r) => r.json())
            .then((data) => setState(data))
            .catch(() => {});
        }
      } catch (err) {
        console.error('WS parse error:', err);
      }
    };

    ws.onerror = () => {
      // Fallback REST fetch if WS fails
      fetchState();
    };

    const interval = setInterval(() => {
      if (ws.readyState !== WebSocket.OPEN) {
        fetchState();
      }
    }, 2500);

    return () => {
      clearInterval(interval);
      ws.close();
    };
  }, []);

  const fetchState = async () => {
    try {
      const res = await fetch('/api/state');
      const data = await res.json();
      setState(data);
    } catch (e) {
      console.error('Fetch state error:', e);
    }
  };

  // Actions
  const handleTriggerDisaster = async () => {
    await fetch('/api/simulation/disaster', { method: 'POST' });
    fetchState();
  };

  const handleToggleBlockRoad = async (roadId: string) => {
    const currentEdge = state?.graph.edges.find((e) => e.id === roadId);
    if (currentEdge?.is_blocked) {
      await fetch('/api/simulation/unblock-road', { method: 'POST' });
    } else {
      await fetch('/api/simulation/block-road', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ road_name: roadId }),
      });
    }
    fetchState();
  };

  const handleInjectFakeNews = async () => {
    await fetch('/api/simulation/inject-fake', { method: 'POST' });
    fetchState();
  };

  const handleKillAgent = async (agentId: string) => {
    await fetch('/api/chaos/kill-agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId }),
    });
    fetchState();
  };

  const handleReviveAgent = async (agentId: string) => {
    await fetch('/api/chaos/revive-agent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_id: agentId }),
    });
    fetchState();
  };

  const handleResetSimulation = async () => {
    await fetch('/api/simulation/reset', { method: 'POST' });
    fetchState();
    setDemoStep(0);
    setAutoDemoRunning(false);
  };

  // Automated Finale Demo Player
  const runFullFinaleDemo = async () => {
    setAutoDemoRunning(true);

    // 00:00 Reset baseline
    setDemoStep(1);
    await handleResetSimulation();
    await new Promise((r) => setTimeout(r, 2000));

    // 00:10 Trigger Major Disaster (47 chaotic reports)
    setDemoStep(2);
    await handleTriggerDisaster();
    await new Promise((r) => setTimeout(r, 3500));

    // 00:30 Block Road B (Aleo Bridge)
    setDemoStep(3);
    await handleToggleBlockRoad('road_b');
    await new Promise((r) => setTimeout(r, 3500));

    // 00:40 Inject Fake News (100 trapped rumor)
    setDemoStep(4);
    await handleInjectFakeNews();
    await new Promise((r) => setTimeout(r, 3500));

    // 00:50 Kill Routing Agent (Autonomous Self-Healing)
    setDemoStep(5);
    await handleKillAgent('routing-agent');

    // Wait for self-healing failover & celebrate
    await new Promise((r) => setTimeout(r, 4500));
    setDemoStep(6);
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
    });
    setAutoDemoRunning(false);
  };

  const healthPct = state?.health.system_health_pct ?? 100;

  return (
    <div className="flex flex-col h-screen w-screen bg-[#070b14] text-slate-100 overflow-hidden font-sans">
      {/* Top Navigation & System Status Header */}
      <header className="h-14 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md px-4 flex items-center justify-between shrink-0 z-30">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-700 shadow-md shadow-cyan-900/40">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-wider text-base bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-300 bg-clip-text text-transparent">
                RESCUESWARM AI
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                Fault-Tolerant Crisis Grid
              </span>
            </div>
            <div className="text-[11px] text-slate-400 italic">
              “When everything goes wrong, the swarm reorganizes.”
            </div>
          </div>
        </div>

        {/* System Health Gauge & Vital Stats */}
        <div className="flex items-center gap-4 text-xs">
          <div className="bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1 flex items-center gap-3">
            <div>
              <span className="text-slate-400 text-[10px] block">Cluster Health</span>
              <span
                className={`font-mono font-bold ${
                  healthPct === 100 ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                {healthPct}% {healthPct === 100 ? 'OPTIMAL' : 'SELF-HEALING'}
              </span>
            </div>
            <div className="w-14 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${
                  healthPct === 100 ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
                style={{ width: `${healthPct}%` }}
              />
            </div>
          </div>

          <div className="hidden lg:flex items-center gap-3 bg-slate-900/90 border border-slate-800 rounded-lg px-3 py-1 text-[11px]">
            <div>
              <span className="text-slate-400 block text-[10px]">Active Incidents</span>
              <span className="font-mono font-bold text-red-400">
                {state?.incidents.length || 0}
              </span>
            </div>
            <div className="w-px h-6 bg-slate-800" />
            <div>
              <span className="text-slate-400 block text-[10px]">Quarantined Rumors</span>
              <span className="font-mono font-bold text-purple-400">
                {state?.quarantined_rumors.length || 0}
              </span>
            </div>
            <div className="w-px h-6 bg-slate-800" />
            <div>
              <span className="text-slate-400 block text-[10px]">Self-Healing Events</span>
              <span className="font-mono font-bold text-cyan-400">
                {state?.health.self_healing_events || 0}
              </span>
            </div>
          </div>

          <button
            onClick={handleResetSimulation}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset 00:00</span>
          </button>
        </div>
      </header>

      {/* Finale Demo Director Ribbon (Interactive Pitch Workflow) */}
      <div className="bg-slate-900/60 border-b border-slate-800/80 px-4 py-2 shrink-0 flex items-center justify-between text-xs overflow-x-auto gap-2">
        <div className="flex items-center gap-1.5 font-bold text-slate-300 uppercase tracking-wider text-[11px] shrink-0">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Finale Pitch Storyboard:</span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto py-0.5">
          <button
            onClick={handleResetSimulation}
            className={`px-3 py-1 rounded-lg font-medium text-[11px] transition whitespace-nowrap cursor-pointer border ${
              demoStep === 1
                ? 'bg-cyan-600 text-white border-cyan-400 shadow-md shadow-cyan-900'
                : 'bg-slate-800/90 hover:bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            00:00 Normal City
          </button>

          <button
            onClick={handleTriggerDisaster}
            className={`px-3 py-1 rounded-lg font-medium text-[11px] transition whitespace-nowrap cursor-pointer border ${
              demoStep === 2
                ? 'bg-red-600 text-white border-red-400 shadow-md shadow-red-900'
                : 'bg-slate-800/90 hover:bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            00:10 Disaster Wave (47 Reports)
          </button>

          <button
            onClick={() => handleToggleBlockRoad('road_b')}
            className={`px-3 py-1 rounded-lg font-medium text-[11px] transition whitespace-nowrap cursor-pointer border ${
              demoStep === 3
                ? 'bg-amber-600 text-white border-amber-400 shadow-md shadow-amber-900'
                : 'bg-slate-800/90 hover:bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            00:30 Block Road B
          </button>

          <button
            onClick={handleInjectFakeNews}
            className={`px-3 py-1 rounded-lg font-medium text-[11px] transition whitespace-nowrap cursor-pointer border ${
              demoStep === 4
                ? 'bg-purple-600 text-white border-purple-400 shadow-md shadow-purple-900'
                : 'bg-slate-800/90 hover:bg-slate-800 text-slate-300 border-slate-700'
            }`}
          >
            00:40 Inject Hostile Rumor
          </button>

          <button
            onClick={() => handleKillAgent('routing-agent')}
            className={`px-3 py-1 rounded-lg font-medium text-[11px] transition whitespace-nowrap cursor-pointer border ${
              demoStep === 5
                ? 'bg-rose-600 text-white border-rose-400 shadow-md shadow-rose-900'
                : 'bg-red-950/80 hover:bg-red-900 text-red-200 border-red-800'
            }`}
          >
            00:50 Kill Routing Agent (Self-Heal)
          </button>
        </div>

        <button
          onClick={runFullFinaleDemo}
          disabled={autoDemoRunning}
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg font-semibold text-[11px] bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-md shadow-emerald-950 transition cursor-pointer shrink-0 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5 fill-current" />
          <span>{autoDemoRunning ? 'Running Swarm Demo...' : '▶ Auto Run Entire Pitch Demo'}</span>
        </button>
      </div>

      {/* Main 3-Column Command Center Workspace */}
      <div className="flex-1 flex overflow-hidden p-3 gap-3">
        {/* LEFT COLUMN: Autonomous Swarm Agents & Heartbeats */}
        <div className="w-80 flex flex-col shrink-0 bg-slate-950/70 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="px-3.5 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
            <div className="font-semibold text-xs text-slate-200 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Autonomous Swarm Cluster</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
              {state?.agents.length || 5} Active Nodes
            </span>
          </div>

          <div className="flex-1 p-3 overflow-y-auto space-y-2.5">
            {state?.agents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                onKill={handleKillAgent}
                onRevive={handleReviveAgent}
              />
            ))}
          </div>

          {/* Recovery Watchdog Banner */}
          <div className="p-3 bg-slate-900/90 border-t border-slate-800 text-[11px] text-slate-400">
            <div className="flex items-center justify-between mb-1">
              <span className="text-slate-300 font-semibold flex items-center gap-1">
                <Activity className="w-3.5 h-3.5 text-purple-400" />
                Recovery Watchdog
              </span>
              <span className="text-[10px] text-purple-300 font-mono">0.4s TICK</span>
            </div>
            <div className="text-[10px] text-slate-500">
              Heartbeat deadline: 1.4s silence triggers automatic role redistribution and state failover.
            </div>
          </div>
        </div>

        {/* CENTER COLUMN: Interactive Crisis Map */}
        <div className="flex-1 flex flex-col rounded-xl overflow-hidden shadow-2xl relative">
          <MapComponent
            nodes={state?.graph.nodes || []}
            edges={state?.graph.edges || []}
            incidents={state?.incidents || []}
            fleet={state?.fleet || []}
            activeRoutes={state?.routes || []}
            quarantinedRumors={state?.quarantined_rumors || []}
            onToggleBlockRoad={handleToggleBlockRoad}
          />
        </div>

        {/* RIGHT COLUMN: Swarm Terminal & Hostile Data Engine */}
        <div className="w-96 flex flex-col shrink-0 bg-slate-950/70 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          {/* Tab Selector */}
          <div className="flex border-b border-slate-800 bg-slate-900 text-xs">
            <button
              onClick={() => setActiveTab('terminal')}
              className={`flex-1 py-2.5 px-3 font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer border-b-2 ${
                activeTab === 'terminal'
                  ? 'border-cyan-400 text-cyan-300 bg-slate-950/50'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              <span>Swarm Stream</span>
            </button>
            <button
              onClick={() => setActiveTab('hostile_data')}
              className={`flex-1 py-2.5 px-3 font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer border-b-2 ${
                activeTab === 'hostile_data'
                  ? 'border-purple-400 text-purple-300 bg-slate-950/50'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Hostile Data Engine</span>
            </button>
          </div>

          <div className="flex-1 overflow-hidden p-2">
            {activeTab === 'terminal' ? (
              <TerminalLogs logs={state?.logs || []} />
            ) : (
              <div className="h-full overflow-y-auto p-1">
                <HostileDataInspector
                  incidents={state?.incidents || []}
                  quarantinedRumors={state?.quarantined_rumors || []}
                  totalReportCount={state?.report_count || 0}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
