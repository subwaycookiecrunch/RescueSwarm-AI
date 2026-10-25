"""Asynchronous in-process Pub/Sub Event Bus for RescueSwarm AI."""

from __future__ import annotations
import asyncio
from typing import Callable, Dict, List, Any, Optional
import time
from rescueswarm.models import SwarmLog


class SwarmEventBus:
    """Central event bus connecting swarm agents, logging, and WebSocket broadcast."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], Any]]] = {}
        self._logs: List[SwarmLog] = []
        self._ws_broadcast_callback: Optional[Callable[[Dict[str, Any]], Any]] = None
        self._log_listeners: List[Callable[[SwarmLog], Any]] = []
        self._max_log_history: int = 500

    def register_ws_broadcaster(self, callback: Callable[[Dict[str, Any]], Any]):
        """Register the WebSocket broadcast callback."""
        self._ws_broadcast_callback = callback

    def add_log_listener(self, listener: Callable[[SwarmLog], Any]):
        """Register a callback for every log event (e.g. for terminal printing)."""
        self._log_listeners.append(listener)

    def subscribe(self, topic: str, handler: Callable[[Any], Any]):
        """Subscribe an agent or handler to a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    async def publish(self, topic: str, data: Any):
        """Publish an event to all subscribers of a topic."""
        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            try:
                res = handler(data)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception as e:
                await self.log(
                    agent_id="event-bus",
                    agent_role="system",
                    level="WARN",
                    message=f"Handler error on topic {topic}: {str(e)}",
                )

        if self._ws_broadcast_callback:
            try:
                payload = {
                    "type": "EVENT",
                    "topic": topic,
                    "data": data if isinstance(data, (dict, list, str, int, float, bool)) else (
                        data.model_dump() if hasattr(data, "model_dump") else str(data)
                    ),
                    "timestamp": time.time(),
                }
                res = self._ws_broadcast_callback(payload)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

    async def log(
        self,
        agent_id: str,
        agent_role: str,
        level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Append to system log history, notify listeners, and emit to WebSocket."""
        t_now = time.time()
        time_str = time.strftime("%H:%M:%S", time.localtime(t_now))
        log_entry = SwarmLog(
            timestamp=t_now,
            time_str=time_str,
            agent_id=agent_id,
            agent_role=agent_role,
            level=level,
            message=message,
            metadata=metadata or {},
        )
        self._logs.append(log_entry)
        if len(self._logs) > self._max_log_history:
            self._logs.pop(0)

        # Notify direct log listeners (e.g. CLI)
        for listener in self._log_listeners:
            try:
                res = listener(log_entry)
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

        # WebSocket broadcast
        if self._ws_broadcast_callback:
            try:
                res = self._ws_broadcast_callback({
                    "type": "LOG",
                    "log": log_entry.model_dump(),
                })
                if asyncio.iscoroutine(res):
                    asyncio.create_task(res)
            except Exception:
                pass

        return log_entry

    def get_recent_logs(self, limit: int = 100) -> List[SwarmLog]:
        return self._logs[-limit:]
