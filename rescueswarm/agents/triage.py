"""Triage Agent: Evaluates urgency, casualty severity, and assigns crisis priorities."""

from __future__ import annotations
import time
from typing import Optional
from rescueswarm.models import AgentRole, Incident, IncidentSeverity, IncidentStatus
from rescueswarm.agents.base import BaseAgent
from rescueswarm.event_bus import SwarmEventBus


class TriageAgent(BaseAgent):
    """Assesses urgency and casualty impact to set emergency priority tiers."""

    def __init__(self, agent_id: str = "triage-agent", event_bus: Optional[SwarmEventBus] = None):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.TRIAGE,
            name="Triage Agent",
            event_bus=event_bus or SwarmEventBus(),
        )

    async def start(self):
        await super().start()
        self.event_bus.subscribe("incident_verified", self.on_incident_verified)

    async def on_incident_verified(self, incident: Incident):
        """Handle incoming verified incident."""
        if self.is_killed:
            return

        self.processed_count += 1

        # Check confidence safety threshold
        if incident.confidence < 0.40:
            incident.severity = IncidentSeverity.UNVERIFIED
            incident.status = IncidentStatus.QUARANTINED
            await self.event_bus.log(
                agent_id=self.agent_id,
                agent_role=self.role.value,
                level="WARN",
                message=(
                    f"⛔ Triage HOLD on {incident.id}: Confidence {int(incident.confidence * 100)}% "
                    f"below threshold (40%). Critical resources withheld."
                ),
            )
            return

        # Determine severity
        casualties = incident.estimated_casualties
        title_lower = incident.title.lower()

        if casualties >= 4 or "collapse" in title_lower or "explosion" in title_lower:
            severity = IncidentSeverity.CRITICAL
            severity_desc = "CRITICAL — MULTIPLE CASUALTIES"
        elif casualties >= 1 or "fire" in title_lower or "flood" in title_lower:
            severity = IncidentSeverity.HIGH
            severity_desc = "HIGH — ACTIVE HAZARD"
        else:
            severity = IncidentSeverity.MEDIUM
            severity_desc = "MEDIUM — LOCALIZED DAMAGE"

        incident.severity = severity
        incident.status = IncidentStatus.TRIAGED
        incident.updated_at = time.time()

        level_str = "CRITICAL" if severity == IncidentSeverity.CRITICAL else "INFO"
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level=level_str,
            message=(
                f"🚨 Triage classified {incident.id} [{incident.title}] as {severity_desc} "
                f"| Estimated Victims: {casualties} | Confidence: {int(incident.confidence * 100)}%"
            ),
            metadata={"incident_id": incident.id, "severity": severity.value},
        )

        # Publish for Resource Agent to assign units
        await self.event_bus.publish("incident_triaged", incident)
