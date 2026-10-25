"""Base class for all autonomous agents in RescueSwarm."""

from __future__ import annotations
import asyncio
import time
from typing import Optional, List, Dict, Any
from rescueswarm.models import AgentRole, AgentStatus, AgentInfo
from rescueswarm.event_bus import SwarmEventBus


class BaseAgent:
    """Base autonomous agent with life-cycle, heartbeat loop, and chaos failure injection."""

    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        name: str,
        event_bus: SwarmEventBus,
        heartbeat_interval: float = 0.6,
    ):
        self.agent_id = agent_id
        self.role = role
        self.name = name
        self.event_bus = event_bus
        self.heartbeat_interval = heartbeat_interval

        self.status = AgentStatus.HEALTHY
        self.is_killed = False
        self.last_heartbeat = time.time()
        self.processed_count = 0
        self.assigned_subroles: List[AgentRole] = []
        self.is_backup = False
        self.notes = "Operational"

        self._heartbeat_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start agent background routines (heartbeat transmitter)."""
        self._running = True
        self.is_killed = False
        if self.is_backup or self.status == AgentStatus.BACKUP_ACTIVE:
            self.status = AgentStatus.BACKUP_ACTIVE
        else:
            self.status = AgentStatus.HEALTHY
        self.last_heartbeat = time.time()
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="INFO",
            message=f"{self.name} initialized and listening to event stream.",
        )

    async def stop(self):
        """Gracefully stop agent."""
        self._running = False
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()

    async def kill(self, reason: str = "Simulated process crash / kill signal"):
        """Simulate unexpected agent death (stops heartbeats immediately)."""
        self.is_killed = True
        self.notes = f"TERMINATED: {reason}"
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()

        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="CHAOS",
            message=f"💥 PROCESS TERMINATED: {self.name} [{self.agent_id}] died! Heartbeats ceased.",
            metadata={"killed": True, "reason": reason},
        )

    async def revive(self):
        """Revive a crashed agent."""
        if not self.is_killed:
            return
        self.is_killed = False
        self.status = AgentStatus.HEALTHY
        self.last_heartbeat = time.time()
        self.notes = "Re-initialized after failover"
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="SUCCESS",
            message=f"♻️ {self.name} reconnected and operational.",
        )

    async def _heartbeat_loop(self):
        """Continuous heartbeat emission for swarm watchdog monitoring."""
        while self._running and not self.is_killed:
            try:
                self.last_heartbeat = time.time()
                await self.event_bus.publish(
                    "heartbeat",
                    {
                        "agent_id": self.agent_id,
                        "role": self.role.value,
                        "status": self.status.value,
                        "timestamp": self.last_heartbeat,
                    },
                )
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(0.5)

    def get_info(self) -> AgentInfo:
        """Export current agent state snapshot."""
        return AgentInfo(
            id=self.agent_id,
            role=self.role,
            name=self.name,
            status=self.status,
            last_heartbeat=self.last_heartbeat,
            heartbeat_interval=self.heartbeat_interval,
            processed_count=self.processed_count,
            assigned_subroles=self.assigned_subroles,
            is_backup=self.is_backup,
            notes=self.notes,
        )
