"""Verification Agent: Filters hostile data, correlates multi-source evidence, scores confidence."""

from __future__ import annotations
import math
import time
from typing import List, Dict, Tuple, Optional
from rescueswarm.models import (
    AgentRole,
    RawReport,
    Incident,
    IncidentStatus,
    IncidentSeverity,
    SourceType,
)
from rescueswarm.agents.base import BaseAgent
from rescueswarm.event_bus import SwarmEventBus


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance between two GPS coordinates in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class VerificationAgent(BaseAgent):
    """Correlates evidence, evaluates source credibility, and filters hostile/manipulated crisis data."""

    SOURCE_WEIGHTS = {
        SourceType.RESPONDER: 0.98,
        SourceType.IOT_SENSOR: 0.95,
        SourceType.HOSPITAL: 0.92,
        SourceType.WEATHER_RADAR: 0.90,
        SourceType.CITIZEN: 0.60,
        SourceType.SOCIAL_MEDIA: 0.25,
    }

    def __init__(self, agent_id: str = "verification-agent", event_bus: Optional[SwarmEventBus] = None):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.VERIFICATION,
            name="Verification Agent",
            event_bus=event_bus or SwarmEventBus(),
        )
        self.raw_reports_buffer: List[RawReport] = []
        self.verified_incidents: Dict[str, Incident] = {}
        self.quarantined_rumors: List[RawReport] = []
        self.cluster_distance_threshold_km = 0.8  # 800 meters

    async def ingest_report(self, report: RawReport) -> Tuple[bool, Optional[Incident], float]:
        """Ingest single report or add to batch."""
        if self.is_killed:
            return False, None, 0.0

        self.processed_count += 1
        self.raw_reports_buffer.append(report)

        # Immediate analysis for standalone injected rumors (e.g., 00:40 scenario)
        if report.is_adversarial_or_rumor or report.source_type == SourceType.SOCIAL_MEDIA:
            confidence = self._compute_single_source_confidence(report)
            if confidence < 0.40:
                self.quarantined_rumors.append(report)
                await self.event_bus.log(
                    agent_id=self.agent_id,
                    agent_role=self.role.value,
                    level="WARN",
                    message=(
                        f"UNVERIFIED — confidence {int(confidence * 100)}% "
                        f"[Quarantined rumor: '{report.text}' at {report.location_name}] "
                        f"(Critical resources withheld)"
                    ),
                    metadata={"confidence": confidence, "report_id": report.id},
                )
                await self.event_bus.publish("rumor_quarantined", {
                    "report": report.model_dump(),
                    "confidence": confidence,
                    "reason": "Hostile/unsubstantiated social media claim with zero sensor corroboration",
                })
                return False, None, confidence

        # Regular processing
        incidents = await self.process_batch([report])
        if incidents:
            return True, incidents[0], incidents[0].confidence
        return False, None, 0.5

    async def process_batch(self, reports: List[RawReport]) -> List[Incident]:
        """Group raw chaotic reports into verified physical incidents using multi-source correlation."""
        if self.is_killed:
            return []

        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="INFO",
            message=f"Verification Agent → analyzing {len(reports)} raw crisis reports across source credibility matrix...",
        )

        # 1. Cluster reports by spatial proximity
        clusters: List[List[RawReport]] = []
        for rep in reports:
            # Skip blatant fake rumor injections with no supporting data
            if rep.is_adversarial_or_rumor:
                self.quarantined_rumors.append(rep)
                await self.event_bus.log(
                    agent_id=self.agent_id,
                    agent_role=self.role.value,
                    level="WARN",
                    message=(
                        f"UNVERIFIED — confidence 23% [Quarantined hostile claim: '{rep.text}']"
                    ),
                    metadata={"confidence": 0.23, "report_id": rep.id},
                )
                await self.event_bus.publish("rumor_quarantined", {
                    "report": rep.model_dump(),
                    "confidence": 0.23,
                    "reason": "Uncorroborated single-source claim",
                })
                continue

            matched_cluster = None
            for cl in clusters:
                dist = haversine_distance_km(rep.lat, rep.lng, cl[0].lat, cl[0].lng)
                if dist <= self.cluster_distance_threshold_km:
                    matched_cluster = cl
                    break

            if matched_cluster is not None:
                matched_cluster.append(rep)
            else:
                clusters.append([rep])

        new_incidents: List[Incident] = []

        # 2. Score confidence for each cluster
        for idx, cluster in enumerate(clusters, start=1):
            total_reports = len(cluster)
            sources = set(r.source_type for r in cluster)

            # Robust casualty estimation: filter out extreme bot exaggerations (> 50 from social media)
            credible_casualties = [
                r.reported_casualties
                for r in cluster
                if not (r.source_type == SourceType.SOCIAL_MEDIA and r.reported_casualties > 20)
            ]
            est_casualties = max(credible_casualties) if credible_casualties else cluster[0].reported_casualties

            # Bayesian multi-source correlation formula
            prob_false = 1.0
            for r in cluster:
                w = self.SOURCE_WEIGHTS.get(r.source_type, 0.5)
                decay = 0.75 if r.source_type == SourceType.CITIZEN else 0.95
                prob_false *= (1.0 - w * decay)

            confidence = round(min(0.96, max(0.20, 1.0 - prob_false)), 2)

            rep_primary = cluster[0]
            loc_name = rep_primary.location_name
            nearest_node = rep_primary.metadata.get("nearest_node", "mall_road")
            hazard = rep_primary.reported_hazard or "Emergency Incident"

            incident_id = f"inc-{idx:02d}"
            summary = (
                f"{total_reports} corroborating reports ({', '.join(s.value for s in sources)}) "
                f"| Sensors: {'YES' if SourceType.IOT_SENSOR in sources else 'NO'} "
                f"| Responders: {'YES' if SourceType.RESPONDER in sources else 'NO'}"
            )

            incident = Incident(
                id=incident_id,
                title=f"{hazard.title()} at {loc_name}",
                location_name=loc_name,
                lat=rep_primary.lat,
                lng=rep_primary.lng,
                nearest_node=nearest_node,
                status=IncidentStatus.VERIFYING,
                severity=IncidentSeverity.UNVERIFIED,
                confidence=confidence,
                report_count=total_reports,
                raw_report_ids=[r.id for r in cluster],
                verification_summary=summary,
                estimated_casualties=est_casualties,
                created_at=time.time(),
                updated_at=time.time(),
            )

            self.verified_incidents[incident_id] = incident
            new_incidents.append(incident)
            self.processed_count += 1

            await self.event_bus.log(
                agent_id=self.agent_id,
                agent_role=self.role.value,
                level="SUCCESS",
                message=(
                    f"Confidence → {int(confidence * 100)}% (Verified Incident #{idx}: {incident.title}) "
                    f"[{total_reports} reports correlated, {est_casualties} casualties]"
                ),
                metadata={"incident_id": incident.id, "confidence": confidence},
            )

            # Publish verified incident for Triage Agent
            await self.event_bus.publish("incident_verified", incident)

        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="INFO",
            message=f"Verification Agent → Synthesized {len(reports)} raw inputs into {len(new_incidents)} verified incidents.",
        )

        return new_incidents

    def _compute_single_source_confidence(self, report: RawReport) -> float:
        """Evaluate solitary report with no corroborating evidence."""
        base_w = self.SOURCE_WEIGHTS.get(report.source_type, 0.4)
        if report.is_adversarial_or_rumor:
            return 0.23
        return round(base_w * 0.7, 2)
