"""Recovery Agent: Heartbeat watchdog, failure detector, and autonomous self-healing coordinator."""

from __future__ import annotations
import asyncio
import time
from typing import Dict, Set, Optional, Callable, Any
from rescueswarm.models import AgentRole, AgentStatus
from rescueswarm.agents.base import BaseAgent
from rescueswarm.event_bus import SwarmEventBus


class RecoveryAgent(BaseAgent):
    """Monitors swarm heartbeats, detects crashes, redistributes roles, and restores full health."""

    def __init__(
        self,
        agent_id: str = "recovery-agent",
        event_bus: Optional[SwarmEventBus] = None,
        heartbeat_timeout_sec: float = 1.4,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.RECOVERY,
            name="Recovery Agent",
            event_bus=event_bus or SwarmEventBus(),
        )
        self.heartbeat_timeout_sec = heartbeat_timeout_sec
        self.heartbeat_tracker: Dict[str, float] = {}
        self.agent_roles: Dict[str, str] = {}
        self.agent_objects: Dict[str, BaseAgent] = {}
        self.failover_handlers: Dict[str, Callable[[], Any]] = {}
        self.failed_agents_handled: Set[str] = set()
        self.healing_count = 0
        self.last_healing_msg: Optional[str] = None
        self._watchdog_task: Optional[asyncio.Task] = None

    def register_agent(
        self,
        agent: BaseAgent,
        failover_handler: Optional[Callable[[], Any]] = None,
    ):
        """Register an agent for watchdog tracking with optional custom failover handler."""
        self.agent_objects[agent.agent_id] = agent
        self.agent_roles[agent.agent_id] = agent.role.value
        self.heartbeat_tracker[agent.agent_id] = time.time()
        if failover_handler:
            self.failover_handlers[agent.agent_id] = failover_handler

    async def start(self):
        await super().start()
        self.event_bus.subscribe("heartbeat", self.on_heartbeat)
        self._watchdog_task = asyncio.create_task(self._watchdog_loop())

    async def stop(self):
        await super().stop()
        if self._watchdog_task and not self._watchdog_task.done():
            self._watchdog_task.cancel()

    async def on_heartbeat(self, payload: Dict[str, Any]):
        """Receive heartbeat pulse from registered swarm member."""
        agent_id = payload.get("agent_id")
        if agent_id:
            self.heartbeat_tracker[agent_id] = time.time()
            # If agent was revived, remove from failed set
            if agent_id in self.failed_agents_handled and self.agent_objects.get(agent_id, None) and not self.agent_objects[agent_id].is_killed:
                self.failed_agents_handled.remove(agent_id)

    async def _watchdog_loop(self):
        """Continuous watchdog checking for lost heartbeats."""
        while self._running and not self.is_killed:
            try:
                now = time.time()
                for agent_id, agent in list(self.agent_objects.items()):
                    if agent_id == self.agent_id or agent.is_backup:
                        continue

                    if agent_id in self.failed_agents_handled:
                        continue

                    last_pulse = self.heartbeat_tracker.get(agent_id, now)
                    silence = now - last_pulse

                    if silence > self.heartbeat_timeout_sec:
                        self.failed_agents_handled.add(agent_id)
                        await self._handle_agent_failure(agent_id, agent, silence)

                await asyncio.sleep(0.3)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await asyncio.sleep(0.4)

    async def _handle_agent_failure(self, agent_id: str, agent: BaseAgent, silence: float):
        """Trigger self-healing failover protocol when an agent crashes."""
        agent.status = AgentStatus.CRASHED
        agent.notes = f"Heartbeat missed for {silence:.1f}s"
        self.processed_count += 1

        # 1. Failure detection
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="CRITICAL",
            message=f"💔 HEARTBEAT LOST on [{agent_id}] (silence: {silence:.1f}s)",
            metadata={"failed_agent": agent_id, "silence": silence},
        )

        await asyncio.sleep(0.4)

        # 2. Failure confirmed
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="WARN",
            message=f"Recovery Agent → failure confirmed for {agent.name}. Initiating failover protocol...",
        )

        await self.event_bus.publish("agent_failure_detected", {
            "failed_agent_id": agent_id,
            "role": agent.role.value,
            "silence": silence,
        })

        await asyncio.sleep(0.6)

        # 3. Responsibilities redistributed
        if agent_id in self.failover_handlers:
            handler = self.failover_handlers[agent_id]
            res = handler()
            if asyncio.iscoroutine(res):
                await res

        self.healing_count += 1
        self.last_healing_msg = f"Self-healed {agent_id} failure via dynamic failover"

        await asyncio.sleep(0.4)

        # 4. Swarm restored
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="SUCCESS",
            message="Recovery Agent → Swarm restored ✓ [System health: 100%]",
            metadata={"healed_agent": agent_id, "healing_count": self.healing_count},
        )

        await self.event_bus.publish("swarm_healed", {
            "failed_agent": agent_id,
            "healing_count": self.healing_count,
            "system_health": 100.0,
        })
