import React from 'react';
import { Incident, RawReport } from '../types';
import { ShieldAlert, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';

interface HostileDataInspectorProps {
  incidents: Incident[];
  quarantinedRumors: RawReport[];
  totalReportCount: number;
}

export const HostileDataInspector: React.FC<HostileDataInspectorProps> = ({
  incidents,
  quarantinedRumors,
  totalReportCount,
}) => {
  return (
    <div className="space-y-4 text-xs text-slate-300">
      {/* Hostile Stream Breakdown Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 shadow-md">
        <div className="flex items-center justify-between mb-2">
          <div className="font-semibold text-slate-200 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Crisis Telemetry Funnel</span>
          </div>
          <span className="text-[10px] bg-cyan-950 text-cyan-300 px-2 py-0.5 rounded border border-cyan-800">
            {totalReportCount > 0 ? `${totalReportCount} Incoming Reports` : 'Idle Stream'}
          </span>
        </div>

        <div className="grid grid-cols-4 gap-2 text-center text-[10px] my-2">
          <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
            <div className="text-slate-400">Genuine Reports</div>
            <div className="font-bold text-emerald-400 text-sm mt-0.5">12</div>
          </div>
          <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
            <div className="text-slate-400">Duplicates</div>
            <div className="font-bold text-blue-400 text-sm mt-0.5">3</div>
          </div>
          <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
            <div className="text-slate-400">Outdated/Lag</div>
            <div className="font-bold text-amber-400 text-sm mt-0.5">2</div>
          </div>
          <div className="bg-slate-950 p-2 rounded-lg border border-slate-800/80">
            <div className="text-slate-400">Manipulated</div>
            <div className="font-bold text-red-400 text-sm mt-0.5">3</div>
          </div>
        </div>

        <div className="text-[11px] text-slate-400 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/60 leading-relaxed">
          <strong className="text-cyan-300">Swarm Verification Matrix:</strong> Spatial clustering (&lt;800m) + Cross-source Bayesian sensor weighting (Sensors: 0.95, Responders: 0.98, Social: 0.25).
        </div>
      </div>

      {/* Quarantined Hostile Rumors */}
      {quarantinedRumors.length > 0 && (
        <div className="bg-purple-950/30 border border-purple-800/60 rounded-xl p-3.5 shadow-lg">
          <div className="flex items-center gap-2 text-purple-300 font-semibold mb-2">
            <ShieldAlert className="w-4 h-4 text-purple-400" />
            <span>Adversarial & Fake Claim Quarantine</span>
          </div>

          <div className="space-y-2">
            {quarantinedRumors.map((rumor) => (
              <div
                key={rumor.id}
                className="bg-slate-950/80 border border-purple-900/80 rounded-lg p-2.5 text-[11px]"
              >
                <div className="flex items-center justify-between text-purple-200 font-medium mb-1">
                  <span>{rumor.location_name}</span>
                  <span className="px-1.5 py-0.5 bg-red-950 text-red-300 font-mono font-bold rounded border border-red-800 text-[10px]">
                    CONFIDENCE: 23%
                  </span>
                </div>
                <div className="text-slate-300 italic mb-1.5">"{rumor.text}"</div>
                <div className="text-[10px] text-slate-400 flex items-center gap-1.5">
                  <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                  <span>Decision: <strong>QUARANTINED</strong>. Zero physical sensors or responder confirmation. No resources wasted.</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Clustered Verified Incidents */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5">
        <div className="font-semibold text-slate-200 mb-2.5 flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Synthesized Ground-Truth Incidents ({incidents.length})</span>
          </span>
        </div>

        {incidents.length === 0 ? (
          <div className="text-slate-500 text-center py-4 text-[11px]">
            No verified incidents yet. Trigger emergency simulation to correlate reports.
          </div>
        ) : (
          <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                className="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 text-[11px]"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-slate-100">{inc.title}</span>
                  <span
                    className={`px-1.5 py-0.5 rounded font-bold text-[9px] ${
                      inc.severity === 'CRITICAL'
                        ? 'bg-red-950 text-red-300 border border-red-800'
                        : inc.severity === 'HIGH'
                        ? 'bg-orange-950 text-orange-300 border border-orange-800'
                        : 'bg-yellow-950 text-yellow-300 border border-yellow-800'
                    }`}
                  >
                    {inc.severity}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-400 mb-1.5">
                  <div>Casualties: <strong className="text-slate-200">{inc.estimated_casualties}</strong></div>
                  <div>Confidence: <strong className="text-emerald-400">{Math.round(inc.confidence * 100)}%</strong></div>
                  <div>Corroboration: <strong className="text-slate-200">{inc.report_count} reports</strong></div>
                  <div>Assigned: <strong className="text-cyan-400">{inc.assigned_resource_id || 'Queued'}</strong></div>
                </div>

                <div className="text-[10px] text-slate-500 truncate">{inc.verification_summary}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
