import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { RoadEdge, NodePoint, Incident, Resource, RawReport } from '../types';

interface MapComponentProps {
  nodes: NodePoint[];
  edges: RoadEdge[];
  incidents: Incident[];
  fleet: Resource[];
  activeRoutes: any[];
  quarantinedRumors: RawReport[];
  onToggleBlockRoad: (roadId: string) => void;
}

export const MapComponent: React.FC<MapComponentProps> = ({
  nodes,
  edges,
  incidents,
  fleet,
  activeRoutes,
  quarantinedRumors,
  onToggleBlockRoad,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const layerGroupRef = useRef<L.LayerGroup | null>(null);

  // Initialize Leaflet map instance
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [32.242, 77.189],
      zoom: 14,
      zoomControl: true,
      attributionControl: false,
    });

    // High-contrast crisis dark mode using OpenStreetMap with CSS dark filter (NO watermark/API key required)
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      className: 'map-tiles-dark',
    }).addTo(map);

    const layerGroup = L.layerGroup().addTo(map);
    mapInstanceRef.current = map;
    layerGroupRef.current = layerGroup;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update map overlays whenever state changes
  useEffect(() => {
    const layerGroup = layerGroupRef.current;
    if (!layerGroup || !mapInstanceRef.current) return;

    layerGroup.clearLayers();

    // 1. Draw Road Network Edges
    edges.forEach((edge) => {
      const isRoadB = edge.id === 'road_b' || edge.name.toLowerCase().includes('road b');
      const isBlocked = edge.is_blocked;

      const polyline = L.polyline(edge.coordinates, {
        color: isBlocked ? '#ef4444' : isRoadB ? '#38bdf8' : '#3b82f6',
        weight: isBlocked ? 7 : isRoadB ? 5 : 4,
        opacity: isBlocked ? 0.95 : 0.65,
        dashArray: isBlocked ? '10, 10' : undefined,
      });

      const popupContent = `
        <div style="font-family: sans-serif; min-width: 190px; color: #0f172a; padding: 4px;">
          <div style="font-weight: 700; font-size: 13px; margin-bottom: 4px;">${edge.name}</div>
          <div style="font-size: 11px; margin-bottom: 4px;">Distance: ${edge.distance_km} km</div>
          <div style="font-size: 11px; margin-bottom: 8px;">
            Status: <span style="font-weight: bold; color: ${isBlocked ? '#dc2626' : '#16a34a'};">
              ${isBlocked ? 'BLOCKED ❌' : 'CLEAR ✓'}
            </span>
            ${edge.blockage_reason ? `<br/><span style="color: #64748b; font-size: 10px;">Reason: ${edge.blockage_reason}</span>` : ''}
          </div>
          <button id="btn-toggle-${edge.id}" style="
            width: 100%;
            padding: 6px 10px;
            font-size: 11px;
            background: ${isBlocked ? '#16a34a' : '#dc2626'};
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
          ">
            ${isBlocked ? 'CLEAR / UNBLOCK' : 'BLOCK ROAD (CHAOS)'}
          </button>
        </div>
      `;

      polyline.bindPopup(popupContent);
      polyline.on('popupopen', () => {
        const btn = document.getElementById(`btn-toggle-${edge.id}`);
        if (btn) {
          btn.onclick = () => {
            onToggleBlockRoad(edge.id);
            mapInstanceRef.current?.closePopup();
          };
        }
      });

      polyline.addTo(layerGroup);
    });

    // 2. Draw Active Dispatched Routes with Glowing Trail
    activeRoutes.forEach((routeInfo) => {
      if (routeInfo.coords && routeInfo.coords.length > 1) {
        const isReroute = routeInfo.is_reroute;
        L.polyline(routeInfo.coords, {
          color: isReroute ? '#06b6d4' : '#10b981',
          weight: 5,
          opacity: 0.9,
          dashArray: isReroute ? '6, 6' : undefined,
        }).addTo(layerGroup);
      }
    });

    // 3. Draw Nodes (Hospital, Fire Station, Intersections)
    nodes.forEach((node) => {
      const isHospital = node.id === 'hospital';
      const isFireHQ = node.id === 'fire_hq';
      const isBridge = node.id === 'aleo_bridge';

      const iconHtml = isHospital
        ? `<div style="background: #dc2626; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 0 12px rgba(220, 38, 38, 0.8); border: 2px solid white;">🏥</div>`
        : isFireHQ
        ? `<div style="background: #ea580c; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 0 12px rgba(234, 88, 12, 0.8); border: 2px solid white;">🚒</div>`
        : isBridge
        ? `<div style="background: #0284c7; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px; border: 2px solid white;">🌉</div>`
        : `<div style="background: #475569; width: 10px; height: 10px; border-radius: 50%; border: 2px solid #cbd5e1;"></div>`;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: 'custom-node-icon',
        iconSize: [28, 28],
        iconAnchor: [14, 14],
      });

      L.marker([node.lat, node.lng], { icon: customIcon })
        .bindTooltip(`<strong>${node.label}</strong>`, { direction: 'top', offset: [0, -12] })
        .addTo(layerGroup);
    });

    // 4. Draw Verified Incident Beacons
    incidents.forEach((inc) => {
      const isCrit = inc.severity === 'CRITICAL';
      const isHigh = inc.severity === 'HIGH';
      const color = isCrit ? '#ef4444' : isHigh ? '#f97316' : '#eab308';

      const markerHtml = `
        <div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;">
          <div class="beacon-pulse" style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: ${color}; opacity: 0.4;"></div>
          <div style="position: relative; background: ${color}; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 12px; border: 2px solid white; box-shadow: 0 2px 10px rgba(0,0,0,0.6);">
            ${inc.estimated_casualties > 0 ? inc.estimated_casualties : '!'}
          </div>
        </div>
      `;

      const icon = L.divIcon({
        html: markerHtml,
        className: 'incident-beacon-marker',
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      });

      const popup = `
        <div style="font-family: sans-serif; min-width: 210px; color: #0f172a; padding: 4px;">
          <div style="font-weight: 800; color: ${color}; font-size: 13px; margin-bottom: 4px;">${inc.title}</div>
          <div style="font-size: 11px;"><strong>Severity:</strong> ${inc.severity}</div>
          <div style="font-size: 11px;"><strong>Casualties:</strong> ${inc.estimated_casualties} victims</div>
          <div style="font-size: 11px;"><strong>Confidence:</strong> ${Math.round(inc.confidence * 100)}%</div>
          <div style="font-size: 11px;"><strong>Corroborated:</strong> ${inc.report_count} clustered reports</div>
          <div style="font-size: 11px; color: #475569; margin-top: 4px;"><em>${inc.verification_summary}</em></div>
          ${inc.assigned_resource_id ? `<div style="margin-top: 6px; font-weight: bold; color: #059669; font-size: 11px;">🚑 Unit Dispatched: ${inc.assigned_resource_id}</div>` : ''}
        </div>
      `;

      L.marker([inc.lat, inc.lng], { icon }).bindPopup(popup).addTo(layerGroup);
    });

    // 5. Draw Quarantined Fake Rumors
    quarantinedRumors.forEach((rumor) => {
      const shieldHtml = `
        <div style="background: #7c3aed; color: white; border-radius: 6px; padding: 3px 8px; font-size: 11px; font-weight: bold; border: 1.5px solid #a78bfa; box-shadow: 0 0 12px rgba(124, 58, 237, 0.7); display: flex; align-items: center; gap: 4px;">
          <span>🛡️ UNVERIFIED (23%)</span>
        </div>
      `;
      const icon = L.divIcon({
        html: shieldHtml,
        className: 'quarantined-rumor-marker',
        iconSize: [120, 26],
        iconAnchor: [60, 13],
      });

      const popup = `
        <div style="font-family: sans-serif; min-width: 210px; color: #0f172a; padding: 4px;">
          <div style="font-weight: 800; color: #7c3aed; font-size: 12px; margin-bottom: 4px;">🛡️ HOSTILE RUMOR QUARANTINED</div>
          <div style="font-size: 11px; margin-bottom: 2px;"><strong>Claim:</strong> "${rumor.text}"</div>
          <div style="font-size: 11px; color: #dc2626; font-weight: bold;">Confidence: 23% (Threshold: 40%)</div>
          <div style="font-size: 11px; color: #475569; margin-top: 4px;"><em>Zero corroborating physical sensors or responder radios. Critical resources withheld.</em></div>
        </div>
      `;

      L.marker([rumor.lat, rumor.lng], { icon }).bindPopup(popup).addTo(layerGroup);
    });

    // 6. Draw Emergency Fleet Vehicles (with jitter/offset so overlapping units don't hide each other)
    fleet.forEach((unit, idx) => {
      const isDispatched = unit.status === 'DISPATCHED' || unit.status === 'EN_ROUTE';
      // Stagger coordinate offsets for units stationed at the same base
      const offsetLat = idx === 1 ? 0.0007 : idx === 2 ? -0.0007 : 0;
      const offsetLng = idx === 3 ? 0.0007 : 0;

      const unitIconHtml = `
        <div style="
          background: ${isDispatched ? '#059669' : '#1e293b'};
          color: white;
          border-radius: 6px;
          padding: 3px 6px;
          font-size: 10px;
          font-weight: 700;
          border: 1.5px solid ${isDispatched ? '#34d399' : '#64748b'};
          box-shadow: 0 2px 8px rgba(0,0,0,0.5);
          white-space: nowrap;
          display: flex;
          align-items: center;
          gap: 3px;
        ">
          <span>${unit.type === 'AMBULANCE' ? '🚑' : unit.type === 'FIRE_TRUCK' ? '🚒' : '🚨'}</span>
          <span>${unit.id}</span>
        </div>
      `;

      const unitIcon = L.divIcon({
        html: unitIconHtml,
        className: 'fleet-unit-marker',
        iconSize: [64, 22],
        iconAnchor: [32, 11],
      });

      L.marker([unit.lat + offsetLat, unit.lng + offsetLng], { icon: unitIcon })
        .bindTooltip(`<strong>${unit.name}</strong><br/>Status: ${unit.status}`, { direction: 'bottom' })
        .addTo(layerGroup);
    });
  }, [nodes, edges, incidents, fleet, activeRoutes, quarantinedRumors, onToggleBlockRoad]);

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Map Legend Overlay */}
      <div className="absolute bottom-4 left-4 z-[400] bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-lg p-3 text-xs text-slate-300 shadow-lg pointer-events-auto">
        <div className="font-semibold text-slate-100 mb-2 flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          Emergency Crisis Grid (Leaflet + OpenStreetMap)
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1 bg-blue-400 rounded"></span>
            <span>Passable Corridor</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1.5 border-b-2 border-red-500 border-dashed"></span>
            <span className="text-red-400 font-semibold">Blocked Road B</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-1 bg-emerald-400 rounded"></span>
            <span>Active Unit Route</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-red-600"></span>
            <span>Critical Incident</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500"></span>
            <span>High Severity</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="px-1 py-0.2 bg-purple-700 text-[9px] rounded font-bold">23%</span>
            <span className="text-purple-300">Quarantined Rumor</span>
          </div>
        </div>
      </div>
    </div>
  );
};
