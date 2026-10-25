import React from 'react';
import { AgentInfo } from '../types';
import { Shield, Activity, Radio, AlertOctagon, RefreshCw, Zap, Cpu } from 'lucide-react';

interface AgentCardProps {
  agent: AgentInfo;
  onKill: (agentId: string) => void;
  onRevive: (agentId: string) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onKill, onRevive }) => {
  const isCrashed = agent.status === 'CRASHED';
  const isBackup = agent.status === 'BACKUP_ACTIVE' || agent.is_backup;
  const isHealthy = agent.status === 'HEALTHY' || agent.status === 'BACKUP_ACTIVE';

  const getRoleIcon = () => {
    switch (agent.role) {
      case 'verification':
        return <Shield className="w-4 h-4 text-cyan-400" />;
      case 'triage':
        return <AlertOctagon className="w-4 h-4 text-amber-400" />;
      case 'resource':
        return <Radio className="w-4 h-4 text-emerald-400" />;
      case 'routing':
        return <Zap className="w-4 h-4 text-blue-400" />;
      case 'recovery':
        return <RefreshCw className="w-4 h-4 text-purple-400" />;
      default:
        return <Cpu className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div
      className={`relative p-3.5 rounded-xl border transition-all duration-300 ${
        isCrashed
          ? 'bg-red-950/40 border-red-800/80 shadow-lg shadow-red-950/50'
          : isBackup
          ? 'bg-purple-950/40 border-purple-600/80 shadow-lg shadow-purple-950/40'
          : 'bg-slate-900/80 border-slate-800 hover:border-slate-700'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/50">
            {getRoleIcon()}
          </div>
          <div>
            <div className="font-semibold text-xs text-slate-100 flex items-center gap-1.5">
              <span>{agent.name}</span>
              {agent.is_backup && (
                <span className="text-[9px] px-1.5 py-0.5 rounded bg-purple-900 text-purple-200 border border-purple-700">
                  FAILOVER NODE
                </span>
              )}
            </div>
            <div className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">
              {agent.id}
            </div>
          </div>
        </div>

        {/* Status Pill */}
        <div className="flex items-center gap-1.5">
          <div
            className={`w-2 h-2 rounded-full ${
              isCrashed
                ? 'bg-red-500 animate-ping'
                : isBackup
                ? 'bg-purple-400 animate-pulse'
                : 'bg-emerald-400 animate-pulse'
            }`}
          />
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
              isCrashed
                ? 'bg-red-900/60 text-red-300 border-red-700'
                : isBackup
                ? 'bg-purple-900/60 text-purple-200 border-purple-600'
                : 'bg-emerald-900/40 text-emerald-300 border-emerald-700'
            }`}
          >
            {agent.status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300 bg-slate-950/50 rounded-lg p-2 border border-slate-800/60 mb-2.5">
        <div>
          <span className="text-slate-500 text-[10px] block">Heartbeat Watchdog</span>
          <span className="font-mono text-emerald-400 flex items-center gap-1">
            <Activity className="w-3 h-3" />
            {isCrashed ? 'MISSED ❌' : 'PULSE 0.6s ✓'}
          </span>
        </div>
        <div>
          <span className="text-slate-500 text-[10px] block">Tasks Handled</span>
          <span className="font-mono font-semibold text-slate-200">{agent.processed_count} events</span>
        </div>
      </div>

      {agent.notes && (
        <div className="text-[10px] text-slate-400 mb-2.5 font-mono truncate">
          Note: {agent.notes}
        </div>
      )}

      {/* Operator Chaos Trigger */}
      {agent.id !== 'recovery-agent' && !agent.is_backup && (
        <div className="pt-1">
          {isHealthy ? (
            <button
              onClick={() => onKill(agent.id)}
              className="w-full py-1 px-2.5 rounded-lg text-[11px] font-medium bg-red-950/60 hover:bg-red-900 text-red-300 border border-red-800/70 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <AlertOctagon className="w-3.5 h-3.5" />
              <span>KILL AGENT (CHAOS MONKEY)</span>
            </button>
          ) : (
            <button
              onClick={() => onRevive(agent.id)}
              className="w-full py-1 px-2.5 rounded-lg text-[11px] font-medium bg-emerald-950/60 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/70 transition-colors flex items-center justify-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>REVIVE & REJOIN SWARM</span>
            </button>
          )}
        </div>
      )}
    </div>
  );
};
