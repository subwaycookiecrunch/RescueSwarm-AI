export interface SwarmHealth {
  total_agents: number;
  healthy_agents: number;
  system_health_pct: number;
  active_incidents: number;
  quarantined_rumors: number;
  self_healing_events: number;
  last_healing_event: string | null;
  timestamp: number;
}

export interface AgentInfo {
  id: string;
  role: 'verification' | 'triage' | 'routing' | 'resource' | 'recovery';
  name: string;
  status: 'HEALTHY' | 'DEGRADED' | 'CRASHED' | 'REASSIGNED' | 'BACKUP_ACTIVE';
  last_heartbeat: number;
  heartbeat_interval: number;
  processed_count: number;
  active_tasks: number;
  assigned_subroles: string[];
  is_backup: boolean;
  notes: string;
}

export interface Incident {
  id: string;
  title: string;
  location_name: string;
  lat: number;
  lng: number;
  nearest_node: string;
  status: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNVERIFIED';
  confidence: number;
  report_count: number;
  raw_report_ids: string[];
  verification_summary: string;
  estimated_casualties: number;
  assigned_resource_id: string | null;
  active_route: string[];
  route_coords: [number, number][];
  created_at: number;
  updated_at: number;
}

export interface Resource {
  id: string;
  name: string;
  type: 'AMBULANCE' | 'FIRE_TRUCK' | 'RESCUE_TEAM' | 'HAZMAT_UNIT';
  lat: number;
  lng: number;
  current_node: string;
  base_node: string;
  status: 'IDLE' | 'DISPATCHED' | 'EN_ROUTE' | 'ON_SCENE';
  assigned_incident_id: string | null;
  current_route: string[];
  route_coords: [number, number][];
  progress_pct: number;
}

export interface RoadEdge {
  id: string;
  name: string;
  u: string;
  v: string;
  coordinates: [[number, number], [number, number]];
  distance_km: number;
  is_blocked: boolean;
  blockage_reason: string | null;
}

export interface NodePoint {
  id: string;
  lat: number;
  lng: number;
  label: string;
}

export interface SwarmLog {
  id: string;
  timestamp: number;
  time_str: string;
  agent_id: string;
  agent_role: string;
  level: 'INFO' | 'SUCCESS' | 'WARN' | 'CRITICAL' | 'CHAOS';
  message: string;
  metadata: Record<string, any>;
}

export interface RawReport {
  id: string;
  source_type: string;
  source_id: string;
  timestamp: number;
  location_name: string;
  lat: number;
  lng: number;
  text: string;
  reported_casualties: number;
  reported_hazard: string;
  is_adversarial_or_rumor: boolean;
}

export interface SwarmState {
  health: SwarmHealth;
  agents: AgentInfo[];
  incidents: Incident[];
  fleet: Resource[];
  routes: any[];
  graph: {
    nodes: NodePoint[];
    edges: RoadEdge[];
  };
  quarantined_rumors: RawReport[];
  report_count: number;
  logs: SwarmLog[];
  active_backup: boolean;
  timestamp: number;
}
