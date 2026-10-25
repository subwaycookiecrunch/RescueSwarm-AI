"""SwarmEngine: Coordinates agent lifecycle, consensus, failover, and simulation states."""

from __future__ import annotations
import asyncio
import time
from typing import Dict, List, Optional, Any
from rescueswarm.models import (
    AgentRole,
    AgentStatus,
    AgentInfo,
    SwarmHealth,
    Incident,
    Resource,
    RawReport,
    SwarmLog,
)
from rescueswarm.event_bus import SwarmEventBus
from rescueswarm.city_graph import CityGraph
from rescueswarm.agents.verification import VerificationAgent
from rescueswarm.agents.triage import TriageAgent
from rescueswarm.agents.routing import RoutingAgent
from rescueswarm.agents.resource import ResourceAgent
from rescueswarm.agents.recovery import RecoveryAgent
from rescueswarm.simulation.scenarios import (
    generate_major_disaster_reports,
    generate_hostile_fake_rumor,
)


class SwarmEngine:
    """Master orchestrator for the RescueSwarm AI multi-agent fault-tolerant system."""

    def __init__(self):
        self.event_bus = SwarmEventBus()
        self.city_graph = CityGraph()

        # Instantiate the 5 Core Swarm Agents
        self.verification_agent = VerificationAgent(
            agent_id="verification-agent", event_bus=self.event_bus
        )
        self.triage_agent = TriageAgent(
            agent_id="triage-agent", event_bus=self.event_bus
        )
        self.resource_agent = ResourceAgent(
            agent_id="resource-agent",
            event_bus=self.event_bus,
            city_graph=self.city_graph,
        )
        self.routing_agent = RoutingAgent(
            agent_id="routing-agent",
            event_bus=self.event_bus,
            city_graph=self.city_graph,
        )
        self.recovery_agent = RecoveryAgent(
            agent_id="recovery-agent",
            event_bus=self.event_bus,
            heartbeat_timeout_sec=2.0,
        )

        # Standby Backup Routing Agent for autonomous failover
        self.backup_routing_agent = RoutingAgent(
            agent_id="routing-agent-backup",
            event_bus=self.event_bus,
            city_graph=self.city_graph,
        )
        self.backup_routing_agent.name = "Routing Agent (Backup Node)"
        self.backup_routing_agent.is_backup = True
        self.backup_routing_agent.status = AgentStatus.DEGRADED
        self.backup_routing_agent.notes = "Standby failover node"

        # Register agents with Recovery Watchdog
        self.recovery_agent.register_agent(
            self.verification_agent
        )
        self.recovery_agent.register_agent(
            self.triage_agent
        )
        self.recovery_agent.register_agent(
            self.resource_agent
        )
        self.recovery_agent.register_agent(
            self.routing_agent,
            failover_handler=self._failover_routing_agent,
        )

        self._active_backup = False
        self.active_reports: List[RawReport] = []
        self._is_running = False

    async def start(self):
        """Start all agents and background loops."""
        if self._is_running:
            return
        self._is_running = True

        await self.event_bus.log(
            agent_id="swarm-master",
            agent_role="system",
            level="INFO",
            message="Initializing RescueSwarm autonomous cluster...",
        )

        # Start agents in sequence
        await self.verification_agent.start()
        await self.triage_agent.start()
        await self.resource_agent.start()
        await self.routing_agent.start()
        await self.recovery_agent.start()

        await self.event_bus.log(
            agent_id="swarm-master",
            agent_role="system",
            level="SUCCESS",
            message="All 5 swarm agents operational. Heartbeat monitoring active.",
        )

    async def stop(self):
        """Gracefully stop swarm engine."""
        self._is_running = False
        await self.verification_agent.stop()
        await self.triage_agent.stop()
        await self.resource_agent.stop()
        await self.routing_agent.stop()
        if self._active_backup:
            await self.backup_routing_agent.stop()
        await self.recovery_agent.stop()

    async def _failover_routing_agent(self):
        """Autonomous failover execution when routing-agent crashes."""
        self._active_backup = True

        # Copy state & active dispatches
        self.backup_routing_agent.active_dispatches = dict(
            self.routing_agent.active_dispatches
        )
        self.backup_routing_agent.is_backup = False
        self.backup_routing_agent.status = AgentStatus.BACKUP_ACTIVE
        self.backup_routing_agent.notes = "Promoted to Primary Routing Authority"

        # Start backup agent heartbeat & event listeners
        await self.backup_routing_agent.start()

        # Update recovery watchdog
        self.recovery_agent.heartbeat_tracker[self.backup_routing_agent.agent_id] = time.time()
        self.recovery_agent.register_agent(self.backup_routing_agent)

        await self.event_bus.log(
            agent_id="recovery-agent",
            agent_role="recovery",
            level="SUCCESS",
            message=(
                f"🔄 Routing responsibility reassigned to {self.backup_routing_agent.name} "
                f"[active_routes_synced={len(self.backup_routing_agent.active_dispatches)}]"
            ),
            metadata={"backup_agent_id": self.backup_routing_agent.agent_id},
        )

    async def simulate_major_emergency(self) -> List[Incident]:
        """Trigger the 00:10 disaster wave: 47 chaotic reports clustered into physical incidents."""
        reports = generate_major_disaster_reports()
        self.active_reports = reports

        await self.event_bus.log(
            agent_id="sim-engine",
            agent_role="simulation",
            level="CRITICAL",
            message=f"⚡ CRISIS DETECTED: Sudden incoming storm of {len(reports)} chaotic reports!",
            metadata={"report_count": len(reports)},
        )

        # Verification Agent analyzes and clusters reports
        verified_incidents = await self.verification_agent.process_batch(reports)
        return verified_incidents

    async def simulate_block_road_b(self) -> Optional[Dict[str, Any]]:
        """Trigger 00:30 event: Raj clicks 'BLOCK ROAD B'."""
        edge = self.city_graph.block_road("road_b", reason="Landslide / Structural Fracture")
        if not edge:
            return None

        await self.event_bus.log(
            agent_id="sim-engine",
            agent_role="simulation",
            level="CHAOS",
            message=f"🚧 ROAD OBSTRUCTION INJECTED: '{edge.name}' is now BLOCKED!",
            metadata={"edge_id": edge.id, "road_name": edge.name},
        )

        # Notify swarm
        await self.event_bus.publish(
            "road_blocked",
            {"edge_id": edge.id, "edge_name": edge.name, "reason": edge.blockage_reason},
        )

        return edge.model_dump()

    async def simulate_unblock_road_b(self) -> Optional[Dict[str, Any]]:
        """Unblock Road B."""
        edge = self.city_graph.unblock_road("road_b")
        if not edge:
            return None

        await self.event_bus.log(
            agent_id="sim-engine",
            agent_role="simulation",
            level="SUCCESS",
            message=f"✅ ROAD CLEARED: '{edge.name}' reopened for emergency transit.",
        )

        await self.event_bus.publish(
            "road_unblocked",
            {"edge_id": edge.id, "edge_name": edge.name},
        )
        return edge.model_dump()

    async def simulate_inject_fake_news(self) -> Dict[str, Any]:
        """Trigger 00:40 event: Inject hostile rumor '100 people trapped at Location X'."""
        rumor = generate_hostile_fake_rumor()
        await self.event_bus.log(
            agent_id="sim-engine",
            agent_role="simulation",
            level="CHAOS",
            message=f"📢 ADVERSARIAL INJECTION: '{rumor.text}'",
            metadata={"text": rumor.text, "source": rumor.source_id},
        )

        # Verification agent evaluates evidence
        verified, incident, conf = await self.verification_agent.ingest_report(rumor)

        return {
            "rumor": rumor.model_dump(),
            "verified": verified,
            "confidence": conf,
            "decision": "QUARANTINED" if not verified else "ACCEPTED",
        }

    async def kill_agent(self, agent_id: str = "routing-agent") -> Dict[str, Any]:
        """Trigger 00:50 event: Terminate an agent to test fault-tolerance & self-healing."""
        target_agent = None
        if agent_id == "routing-agent":
            target_agent = self.routing_agent
        elif agent_id == "verification-agent":
            target_agent = self.verification_agent
        elif agent_id == "triage-agent":
            target_agent = self.triage_agent
        elif agent_id == "resource-agent":
            target_agent = self.resource_agent

        if not target_agent:
            return {"success": False, "error": f"Agent {agent_id} not found"}

        await target_agent.kill(reason="Chaos injection: Process terminated by operator")
        return {"success": True, "killed_agent": agent_id, "timestamp": time.time()}

    async def revive_agent(self, agent_id: str = "routing-agent") -> Dict[str, Any]:
        """Revive killed agent."""
        if agent_id == "routing-agent":
            await self.routing_agent.revive()
            self.recovery_agent.heartbeat_tracker[self.routing_agent.agent_id] = time.time()
            return {"success": True, "revived": agent_id}
        return {"success": False, "error": f"Agent {agent_id} revive not configured"}

    async def reset_simulation(self):
        """Reset entire swarm to baseline 00:00 state."""
        # Unblock roads
        self.city_graph.unblock_road("road_b")

        # Reset fleets
        self.resource_agent.reset_fleet()

        # Clear reports and incidents
        self.verification_agent.raw_reports_buffer.clear()
        self.verification_agent.verified_incidents.clear()
        self.verification_agent.quarantined_rumors.clear()
        self.active_reports.clear()

        # Reset routing state
        self.routing_agent.active_dispatches.clear()
        self.backup_routing_agent.active_dispatches.clear()

        # Stop backup if active
        if self._active_backup:
            await self.backup_routing_agent.stop()
            self._active_backup = False
            self.backup_routing_agent.status = AgentStatus.DEGRADED
            self.backup_routing_agent.notes = "Standby failover node"

        # Revive primary routing agent
        if self.routing_agent.is_killed:
            await self.routing_agent.revive()
        self.routing_agent.status = AgentStatus.HEALTHY
        self.recovery_agent.heartbeat_tracker[self.routing_agent.agent_id] = time.time()

        # Reset counters
        self.verification_agent.processed_count = 0
        self.triage_agent.processed_count = 0
        self.resource_agent.processed_count = 0
        self.routing_agent.processed_count = 0
        self.recovery_agent.healing_count = 0

        await self.event_bus.log(
            agent_id="swarm-master",
            agent_role="system",
            level="SUCCESS",
            message="🔄 Simulation reset to 00:00 baseline. All 5 agents healthy, road network clear.",
        )

    def get_health(self) -> SwarmHealth:
        """Calculate live swarm health metrics."""
        agents = [
            self.verification_agent,
            self.triage_agent,
            self.resource_agent,
            self.backup_routing_agent if self._active_backup else self.routing_agent,
            self.recovery_agent,
        ]

        healthy_count = sum(1 for a in agents if a.status in (AgentStatus.HEALTHY, AgentStatus.BACKUP_ACTIVE))
        health_pct = round((healthy_count / len(agents)) * 100.0, 1)

        return SwarmHealth(
            total_agents=len(agents),
            healthy_agents=healthy_count,
            system_health_pct=health_pct,
            active_incidents=len(self.verification_agent.verified_incidents),
            quarantined_rumors=len(self.verification_agent.quarantined_rumors),
            self_healing_events=self.recovery_agent.healing_count,
            last_healing_event=self.recovery_agent.last_healing_msg,
            timestamp=time.time(),
        )

    def get_state(self) -> Dict[str, Any]:
        """Generate comprehensive system state for API and WebSocket client."""
        # Active agents
        agent_list: List[Dict[str, Any]] = [
            self.verification_agent.get_info().model_dump(),
            self.triage_agent.get_info().model_dump(),
            self.resource_agent.get_info().model_dump(),
            self.routing_agent.get_info().model_dump(),
            self.recovery_agent.get_info().model_dump(),
        ]
        if self._active_backup:
            agent_list.append(self.backup_routing_agent.get_info().model_dump())

        # Incidents
        incidents = [
            inc.model_dump() for inc in self.verification_agent.verified_incidents.values()
        ]

        # Fleet
        fleet = [res.model_dump() for res in self.resource_agent.get_fleet()]

        # Active routes
        active_routing_agent = self.backup_routing_agent if self._active_backup else self.routing_agent
        routes = list(active_routing_agent.active_dispatches.values())

        # City graph
        nodes = self.city_graph.get_all_nodes()
        edges = self.city_graph.get_all_edges_status()

        # Quarantined rumors
        rumors = [r.model_dump() for r in self.verification_agent.quarantined_rumors]

        return {
            "health": self.get_health().model_dump(),
            "agents": agent_list,
            "incidents": incidents,
            "fleet": fleet,
            "routes": routes,
            "graph": {"nodes": nodes, "edges": edges},
            "quarantined_rumors": rumors,
            "report_count": len(self.active_reports),
            "logs": [l.model_dump() for l in self.event_bus.get_recent_logs(80)],
            "active_backup": self._active_backup,
            "timestamp": time.time(),
        }
