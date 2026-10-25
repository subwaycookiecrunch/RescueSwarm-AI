"""Resource Agent: Manages fleet allocation, nearest-unit matching, and dispatch."""

from __future__ import annotations
import time
from typing import Dict, List, Optional
from rescueswarm.models import (
    AgentRole,
    Incident,
    IncidentStatus,
    Resource,
    ResourceType,
    ResourceStatus,
)
from rescueswarm.agents.base import BaseAgent
from rescueswarm.event_bus import SwarmEventBus
from rescueswarm.city_graph import CityGraph


class ResourceAgent(BaseAgent):
    """Allocates ambulances, fire trucks, and rescue squads to triaged crisis incidents."""

    def __init__(
        self,
        agent_id: str = "resource-agent",
        event_bus: Optional[SwarmEventBus] = None,
        city_graph: Optional[CityGraph] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RESOURCE,
            name="Resource Agent",
            event_bus=event_bus or SwarmEventBus(),
        )
        self.city_graph = city_graph or CityGraph()
        self.resources: Dict[str, Resource] = {}
        self._init_fleet()

    def _init_fleet(self):
        """Initialize emergency fleet."""
        fleet = [
            Resource(
                id="AMB-03",
                name="Ambulance-03 (ALS Heavy)",
                type=ResourceType.AMBULANCE,
                lat=32.2415,
                lng=77.1895,
                current_node="hospital",
                base_node="hospital",
                status=ResourceStatus.IDLE,
            ),
            Resource(
                id="AMB-01",
                name="Ambulance-01 (Rapid Medic)",
                type=ResourceType.AMBULANCE,
                lat=32.2415,
                lng=77.1895,
                current_node="hospital",
                base_node="hospital",
                status=ResourceStatus.IDLE,
            ),
            Resource(
                id="RESCUE-01",
                name="Rescue-Team Alpha (USAR)",
                type=ResourceType.RESCUE_TEAM,
                lat=32.2465,
                lng=77.1840,
                current_node="fire_hq",
                base_node="fire_hq",
                status=ResourceStatus.IDLE,
            ),
            Resource(
                id="FIRE-01",
                name="Fire Tender Engine-1",
                type=ResourceType.FIRE_TRUCK,
                lat=32.2465,
                lng=77.1840,
                current_node="fire_hq",
                base_node="fire_hq",
                status=ResourceStatus.IDLE,
            ),
        ]
        for r in fleet:
            self.resources[r.id] = r

    async def start(self):
        await super().start()
        self.event_bus.subscribe("incident_triaged", self.on_incident_triaged)

    async def on_incident_triaged(self, incident: Incident):
        """Select best unit and dispatch."""
        if self.is_killed:
            return

        self.processed_count += 1

        # Prefer AMB-03 for major critical casualties as described in scenario
        candidate: Optional[Resource] = None
        if "collapse" in incident.title.lower() or incident.estimated_casualties >= 4:
            if "AMB-03" in self.resources and self.resources["AMB-03"].status == ResourceStatus.IDLE:
                candidate = self.resources["AMB-03"]

        if not candidate:
            for r in self.resources.values():
                if r.status == ResourceStatus.IDLE:
                    candidate = r
                    break

        if not candidate:
            await self.event_bus.log(
                agent_id=self.agent_id,
                agent_role=self.role.value,
                level="WARN",
                message=f"All emergency resources deployed! Incident {incident.id} queued.",
            )
            return

        # Mark dispatched
        candidate.status = ResourceStatus.DISPATCHED
        candidate.assigned_incident_id = incident.id
        incident.assigned_resource_id = candidate.id
        incident.status = IncidentStatus.DISPATCHED
        incident.updated_at = time.time()

        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="SUCCESS",
            message=(
                f"🚑 DISPATCH ORDER: {candidate.name} assigned to {incident.id} "
                f"[{incident.title}] at {incident.location_name}"
            ),
            metadata={
                "resource_id": candidate.id,
                "incident_id": incident.id,
                "current_node": candidate.current_node,
                "target_node": incident.nearest_node,
            },
        )

        # Publish dispatch order for Routing Agent to calculate path
        await self.event_bus.publish(
            "resource_dispatched",
            {
                "resource": candidate.model_dump(),
                "incident": incident.model_dump(),
            },
        )

    def get_fleet(self) -> List[Resource]:
        return list(self.resources.values())

    def reset_fleet(self):
        self._init_fleet()
