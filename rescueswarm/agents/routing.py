"""Routing Agent: Calculates dynamic paths across road graph and reroutes around obstructions."""

from __future__ import annotations
import time
from typing import Dict, List, Optional, Any
from rescueswarm.models import AgentRole, Resource, Incident
from rescueswarm.agents.base import BaseAgent
from rescueswarm.event_bus import SwarmEventBus
from rescueswarm.city_graph import CityGraph


class RoutingAgent(BaseAgent):
    """Calculates emergency routes, detects road obstructions, and computes real-time detours."""

    def __init__(
        self,
        agent_id: str = "routing-agent",
        event_bus: Optional[SwarmEventBus] = None,
        city_graph: Optional[CityGraph] = None,
    ):
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ROUTING,
            name="Routing Agent",
            event_bus=event_bus or SwarmEventBus(),
        )
        self.city_graph = city_graph or CityGraph()
        # Active dispatches: resource_id -> dispatch info
        self.active_dispatches: Dict[str, Dict[str, Any]] = {}

    async def start(self):
        await super().start()
        self.event_bus.subscribe("resource_dispatched", self.on_resource_dispatched)
        self.event_bus.subscribe("road_blocked", self.on_road_blocked)

    async def on_resource_dispatched(self, payload: Dict[str, Any]):
        """Calculate primary route for dispatched unit."""
        if self.is_killed:
            # Drop/ignore if killed (simulates hard crash)
            return

        self.processed_count += 1
        res_data = payload.get("resource", {})
        inc_data = payload.get("incident", {})

        res_id = res_data.get("id")
        start_node = res_data.get("current_node", "hospital")
        target_node = inc_data.get("nearest_node", "sub_station")

        route = self.city_graph.get_shortest_path(start_node, target_node)
        if not route:
            await self.event_bus.log(
                agent_id=self.agent_id,
                agent_role=self.role.value,
                level="WARN",
                message=f"❌ No passable route found from {start_node} to {target_node}!",
            )
            return

        coords = self.city_graph.get_route_coordinates(route)
        node_labels = [self.city_graph.node_labels.get(n, n) for n in route]
        route_str = " ➔ ".join(node_labels)

        self.active_dispatches[res_id] = {
            "resource_id": res_id,
            "incident_id": inc_data.get("id"),
            "start_node": start_node,
            "target_node": target_node,
            "route_nodes": route,
            "coords": coords,
            "route_str": route_str,
        }

        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="SUCCESS",
            message=f"🗺️ ROUTE CALCULATED for {res_id}: {route_str}",
            metadata={
                "resource_id": res_id,
                "incident_id": inc_data.get("id"),
                "route": route,
                "coordinates": coords,
            },
        )

        await self.event_bus.publish(
            "route_calculated",
            {
                "resource_id": res_id,
                "incident_id": inc_data.get("id"),
                "route_nodes": route,
                "coords": coords,
                "route_str": route_str,
                "is_reroute": False,
            },
        )

    async def on_road_blocked(self, payload: Dict[str, Any]):
        """Detect if any active route is blocked and recalculate detour."""
        if self.is_killed:
            return

        edge_name = payload.get("edge_name", "Road B")
        await self.event_bus.log(
            agent_id=self.agent_id,
            agent_role=self.role.value,
            level="WARN",
            message=f"⚠️ Road obstacle reported on '{edge_name}'. Inspecting active swarm navigation...",
        )

        for res_id, dispatch in list(self.active_dispatches.items()):
            route_nodes = dispatch.get("route_nodes", [])
            is_blocked, blocked_seg = self.city_graph.is_route_blocked(route_nodes)

            if is_blocked:
                await self.event_bus.log(
                    agent_id=self.agent_id,
                    agent_role=self.role.value,
                    level="CRITICAL",
                    message=(
                        f"🛑 ROUTE INVALIDATED for {res_id}: Traversing blocked segment '{blocked_seg}'. "
                        f"Calculating alternate swarm detour..."
                    ),
                    metadata={"resource_id": res_id, "blocked_segment": blocked_seg},
                )

                # Re-calculate path avoiding blocked edge
                start_node = dispatch["start_node"]
                target_node = dispatch["target_node"]
                new_route = self.city_graph.get_shortest_path(start_node, target_node)

                if new_route:
                    coords = self.city_graph.get_route_coordinates(new_route)
                    node_labels = [self.city_graph.node_labels.get(n, n) for n in new_route]
                    new_route_str = " ➔ ".join(node_labels)

                    dispatch["route_nodes"] = new_route
                    dispatch["coords"] = coords
                    dispatch["route_str"] = new_route_str

                    await self.event_bus.log(
                        agent_id=self.agent_id,
                        agent_role=self.role.value,
                        level="SUCCESS",
                        message=f"🔄 DETOUR ESTABLISHED for {res_id}: {new_route_str}",
                        metadata={
                            "resource_id": res_id,
                            "route": new_route,
                            "coordinates": coords,
                            "is_reroute": True,
                        },
                    )

                    await self.event_bus.publish(
                        "route_calculated",
                        {
                            "resource_id": res_id,
                            "incident_id": dispatch.get("incident_id"),
                            "route_nodes": new_route,
                            "coords": coords,
                            "route_str": new_route_str,
                            "is_reroute": True,
                        },
                    )
                else:
                    await self.event_bus.log(
                        agent_id=self.agent_id,
                        agent_role=self.role.value,
                        level="CRITICAL",
                        message=f"❌ No alternate detour found to reach {target_node}!",
                    )
