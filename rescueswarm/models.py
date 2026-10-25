"""Data models for RescueSwarm AI multi-agent coordination system."""

from __future__ import annotations
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import time
import uuid


class SourceType(str, Enum):
    CITIZEN = "CITIZEN"
    IOT_SENSOR = "IOT_SENSOR"
    RESPONDER = "RESPONDER"
    HOSPITAL = "HOSPITAL"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    WEATHER_RADAR = "WEATHER_RADAR"


class IncidentSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNVERIFIED = "UNVERIFIED"


class IncidentStatus(str, Enum):
    REPORTED = "REPORTED"
    VERIFYING = "VERIFYING"
    TRIAGED = "TRIAGED"
    DISPATCHED = "DISPATCHED"
    ON_SCENE = "ON_SCENE"
    RESOLVED = "RESOLVED"
    QUARANTINED = "QUARANTINED"


class ResourceType(str, Enum):
    AMBULANCE = "AMBULANCE"
    FIRE_TRUCK = "FIRE_TRUCK"
    RESCUE_TEAM = "RESCUE_TEAM"
    HAZMAT_UNIT = "HAZMAT_UNIT"


class ResourceStatus(str, Enum):
    IDLE = "IDLE"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"


class AgentRole(str, Enum):
    VERIFICATION = "verification"
    TRIAGE = "triage"
    ROUTING = "routing"
    RESOURCE = "resource"
    RECOVERY = "recovery"


class AgentStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRASHED = "CRASHED"
    REASSIGNED = "REASSIGNED"
    BACKUP_ACTIVE = "BACKUP_ACTIVE"


class RawReport(BaseModel):
    id: str = Field(default_factory=lambda: f"rep-{uuid.uuid4().hex[:6]}")
    source_type: SourceType
    source_id: str
    timestamp: float = Field(default_factory=time.time)
    location_name: str
    lat: float
    lng: float
    text: str
    reported_casualties: int = 0
    reported_hazard: str = "generic"
    credibility_prior: float = 0.5
    is_adversarial_or_rumor: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Incident(BaseModel):
    id: str
    title: str
    location_name: str
    lat: float
    lng: float
    nearest_node: str
    status: IncidentStatus = IncidentStatus.REPORTED
    severity: IncidentSeverity = IncidentSeverity.UNVERIFIED
    confidence: float = 0.0
    report_count: int = 1
    raw_report_ids: List[str] = Field(default_factory=list)
    verification_summary: str = ""
    estimated_casualties: int = 0
    assigned_resource_id: Optional[str] = None
    active_route: List[str] = Field(default_factory=list)
    route_coords: List[List[float]] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class Resource(BaseModel):
    id: str
    name: str
    type: ResourceType
    lat: float
    lng: float
    current_node: str
    base_node: str
    status: ResourceStatus = ResourceStatus.IDLE
    assigned_incident_id: Optional[str] = None
    current_route: List[str] = Field(default_factory=list)
    route_coords: List[List[float]] = Field(default_factory=list)
    progress_pct: float = 0.0


class RoadEdge(BaseModel):
    id: str
    u: str
    v: str
    name: str
    distance_km: float
    is_blocked: bool = False
    blockage_reason: Optional[str] = None
    hazard_level: float = 0.0  # 0.0 = clear, 1.0 = impassable


class AgentInfo(BaseModel):
    id: str
    role: AgentRole
    name: str
    status: AgentStatus = AgentStatus.HEALTHY
    last_heartbeat: float = Field(default_factory=time.time)
    heartbeat_interval: float = 1.0  # seconds
    processed_count: int = 0
    active_tasks: int = 0
    assigned_subroles: List[AgentRole] = Field(default_factory=list)
    is_backup: bool = False
    notes: str = ""


class SwarmHealth(BaseModel):
    total_agents: int = 5
    healthy_agents: int = 5
    system_health_pct: float = 100.0
    active_incidents: int = 0
    quarantined_rumors: int = 0
    self_healing_events: int = 0
    last_healing_event: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class SwarmLog(BaseModel):
    id: str = Field(default_factory=lambda: f"log-{uuid.uuid4().hex[:8]}")
    timestamp: float = Field(default_factory=time.time)
    time_str: str = ""
    agent_id: str
    agent_role: str
    level: str  # INFO, SUCCESS, WARN, CRITICAL, CHAOS
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
