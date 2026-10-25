import React, { useState, useEffect, useRef } from 'react';
import { SwarmLog } from '../types';
import { Terminal, ArrowDown } from 'lucide-react';

interface TerminalLogsProps {
  logs: SwarmLog[];
  onClearLogs?: () => void;
}

export const TerminalLogs: React.FC<TerminalLogsProps> = ({ logs }) => {
  const [filterRole, setFilterRole] = useState<string>('ALL');
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const filteredLogs = filterRole === 'ALL'
    ? logs
    : logs.filter((l) => l.agent_role.toLowerCase() === filterRole.toLowerCase());

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'CHAOS':
        return <span className="bg-red-950 text-red-300 border border-red-700 px-1.5 py-0.2 rounded text-[9px] font-bold">CHAOS</span>;
      case 'CRITICAL':
        return <span className="bg-red-900/60 text-red-200 border border-red-600 px-1.5 py-0.2 rounded text-[9px] font-bold">CRIT</span>;
      case 'SUCCESS':
        return <span className="bg-emerald-950 text-emerald-300 border border-emerald-700 px-1.5 py-0.2 rounded text-[9px] font-bold">SUCCESS</span>;
      case 'WARN':
        return <span className="bg-amber-950 text-amber-300 border border-amber-700 px-1.5 py-0.2 rounded text-[9px] font-bold">WARN</span>;
      default:
        return <span className="bg-slate-800 text-slate-300 px-1.5 py-0.2 rounded text-[9px]">INFO</span>;
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-950 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      {/* Terminal Title Bar */}
      <div className="flex items-center justify-between px-3.5 py-2.5 bg-slate-900 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2 text-slate-200 font-mono font-medium">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span>Swarm Event Stream</span>
          <span className="text-[10px] text-slate-500 font-normal">({logs.length} events)</span>
        </div>

        {/* Filter Badges */}
        <div className="flex items-center gap-1.5">
          <select
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
            className="bg-slate-950 border border-slate-700 text-slate-300 rounded px-2 py-0.5 text-[10px] focus:outline-none"
          >
            <option value="ALL">All Agents</option>
            <option value="verification">Verification</option>
            <option value="triage">Triage</option>
            <option value="resource">Resource</option>
            <option value="routing">Routing</option>
            <option value="recovery">Recovery</option>
            <option value="simulation">Chaos/Sim</option>
          </select>
        </div>
      </div>

      {/* Log Entries Viewport */}
      <div
        ref={logContainerRef}
        className="flex-1 p-3 overflow-y-auto font-mono text-[11px] space-y-1.5 bg-slate-950/95"
      >
        {filteredLogs.length === 0 ? (
          <div className="text-slate-600 text-center py-8">
            No events logged yet. Waiting for swarm stream...
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className={`p-1.5 rounded transition-colors ${
                log.level === 'CHAOS'
                  ? 'bg-red-950/40 text-red-300 border-l-2 border-red-500'
                  : log.level === 'CRITICAL'
                  ? 'bg-red-950/20 text-red-200 border-l-2 border-red-500'
                  : log.level === 'SUCCESS'
                  ? 'bg-emerald-950/20 text-emerald-200 border-l-2 border-emerald-500'
                  : 'text-slate-300 hover:bg-slate-900/50'
              }`}
            >
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-slate-500 text-[10px]">[{log.time_str}]</span>
                {getLevelBadge(log.level)}
                <span className="text-cyan-400 font-bold text-[10px]">
                  [{log.agent_role.toUpperCase()}]
                </span>
              </div>
              <div className="pl-1 text-slate-200 break-words leading-relaxed">
                {log.message}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Terminal Footer */}
      <div className="px-3 py-1.5 bg-slate-900 border-t border-slate-800 text-[10px] text-slate-500 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>WebSocket Stream Connected</span>
        </div>
        <button
          onClick={() => setAutoScroll(!autoScroll)}
          className={`flex items-center gap-1 cursor-pointer hover:text-slate-300 ${autoScroll ? 'text-emerald-400' : 'text-slate-500'}`}
        >
          <ArrowDown className="w-3 h-3" />
          <span>Auto-scroll {autoScroll ? 'ON' : 'OFF'}</span>
        </button>
      </div>
    </div>
  );
};
