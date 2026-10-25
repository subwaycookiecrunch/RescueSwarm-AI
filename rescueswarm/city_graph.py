"""Graph representation of the city road network, with live blockage and dynamic rerouting."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx
from rescueswarm.models import RoadEdge


class CityGraph:
    """Graph of city road network for shortest-path routing, edge blockage and rerouting."""

    def __init__(self):
        self.graph = nx.Graph()
        self.node_positions: Dict[str, Tuple[float, float]] = {}
        self.node_labels: Dict[str, str] = {}
        self.edges_meta: Dict[str, RoadEdge] = {}
        self._init_network()

    def _init_network(self):
        """Initialize nodes and edges for the emergency response zone."""
        nodes = [
            ("hospital", 32.2415, 77.1895, "Central Trauma Hospital"),
            ("fire_hq", 32.2465, 77.1840, "Civil Emergency & Fire Depot"),
            ("mall_road", 32.2390, 77.1880, "Mall Road Intersection (Road A)"),
            ("aleo_bridge", 32.2355, 77.1950, "Aleo River Bridge (Road B)"),
            ("old_town", 32.2490, 77.1825, "Old Town Sector 4"),
            ("vashisht_jct", 32.2540, 77.1960, "Vashisht Northern Arterial"),
            ("bypass_north", 32.2580, 77.1880, "Northern Bypass Highway"),
            ("river_south", 32.2280, 77.1850, "Beas River South Causeway"),
            ("industrial_gate", 32.2340, 77.1780, "West Logistics & Supply Depot"),
            ("sub_station", 32.2425, 77.2030, "East Colony & Health Sub-Station"),
        ]

        for node_id, lat, lng, label in nodes:
            self.node_positions[node_id] = (lat, lng)
            self.node_labels[node_id] = label
            self.graph.add_node(node_id, lat=lat, lng=lng, label=label)

        # Define roads with realistic distances (km)
        edges = [
            ("road_hosp_mall", "hospital", "mall_road", "Hospital Accessway", 0.6),
            ("road_fire_mall", "fire_hq", "mall_road", "Station Main Arterial", 1.2),
            ("road_fire_old", "fire_hq", "old_town", "Old Town Link", 0.8),
            ("road_old_bypass", "old_town", "bypass_north", "Upper Hill Climb", 1.4),
            ("road_bypass_vashisht", "bypass_north", "vashisht_jct", "Bypass Connector", 1.1),
            ("road_hosp_vashisht", "hospital", "vashisht_jct", "East Valley Ridge Route", 1.8),
            ("road_b", "mall_road", "aleo_bridge", "Aleo River Bridge (Road B)", 1.0),
            ("road_aleo_sub", "aleo_bridge", "sub_station", "Aleo-East Substation Road", 1.3),
            ("road_vashisht_sub", "vashisht_jct", "sub_station", "North-East Bypass Detour", 1.9),
            ("road_mall_river", "mall_road", "river_south", "Riverbank Boulevard", 1.5),
            ("road_river_industrial", "river_south", "industrial_gate", "South Industrial Spur", 1.2),
            ("road_industrial_mall", "industrial_gate", "mall_road", "Logistics Access Highway", 1.4),
            ("road_river_aleo", "river_south", "aleo_bridge", "South Causeway Bridge Link", 1.7),
        ]

        for edge_id, u, v, name, dist in edges:
            meta = RoadEdge(
                id=edge_id,
                u=u,
                v=v,
                name=name,
                distance_km=dist,
                is_blocked=False,
                blockage_reason=None,
            )
            self.edges_meta[edge_id] = meta
            self.graph.add_edge(u, v, id=edge_id, weight=dist, name=name, is_blocked=False)

    def get_shortest_path(self, start_node: str, end_node: str) -> Optional[List[str]]:
        """Calculate shortest path avoiding blocked roads."""
        if start_node == end_node:
            return [start_node]
        if start_node not in self.graph or end_node not in self.graph:
            return None

        # Build active subgraph excluding blocked edges
        active_subgraph = nx.Graph()
        for u, v, data in self.graph.edges(data=True):
            if not data.get("is_blocked", False):
                active_subgraph.add_edge(u, v, weight=data.get("weight", 1.0), name=data.get("name", ""))

        if not active_subgraph.has_node(start_node) or not active_subgraph.has_node(end_node):
            return None

        try:
            path = nx.shortest_path(active_subgraph, source=start_node, target=end_node, weight="weight")
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def get_route_coordinates(self, node_ids: List[str]) -> List[List[float]]:
        """Return list of [lat, lng] for all nodes in the path."""
        coords = []
        for nid in node_ids:
            if nid in self.node_positions:
                coords.append([self.node_positions[nid][0], self.node_positions[nid][1]])
        return coords

    def block_road(self, edge_id_or_name: str, reason: str = "Debris / Landslide / Blockage") -> Optional[RoadEdge]:
        """Block a specific road edge and return updated metadata."""
        target_edge: Optional[RoadEdge] = None

        # Match by ID or road name
        for edge_id, meta in self.edges_meta.items():
            if edge_id == edge_id_or_name or meta.name.lower() == edge_id_or_name.lower() or (
                "road b" in edge_id_or_name.lower() and "road b" in meta.name.lower()
            ):
                target_edge = meta
                break

        if not target_edge:
            return None

        target_edge.is_blocked = True
        target_edge.blockage_reason = reason
        # Update networkx graph edge
        if self.graph.has_edge(target_edge.u, target_edge.v):
            self.graph[target_edge.u][target_edge.v]["is_blocked"] = True

        return target_edge

    def unblock_road(self, edge_id_or_name: str) -> Optional[RoadEdge]:
        """Unblock a road edge."""
        target_edge: Optional[RoadEdge] = None
        for edge_id, meta in self.edges_meta.items():
            if edge_id == edge_id_or_name or meta.name.lower() == edge_id_or_name.lower():
                target_edge = meta
                break

        if not target_edge:
            return None

        target_edge.is_blocked = False
        target_edge.blockage_reason = None
        if self.graph.has_edge(target_edge.u, target_edge.v):
            self.graph[target_edge.u][target_edge.v]["is_blocked"] = False

        return target_edge

    def is_route_blocked(self, route_nodes: List[str]) -> Tuple[bool, Optional[str]]:
        """Check if any segment in the route traverses a blocked road."""
        if len(route_nodes) < 2:
            return False, None
        for i in range(len(route_nodes) - 1):
            u, v = route_nodes[i], route_nodes[i + 1]
            if self.graph.has_edge(u, v) and self.graph[u][v].get("is_blocked", False):
                return True, self.graph[u][v].get("name", f"{u}-{v}")
        return False, None

    def get_all_edges_status(self) -> List[Dict[str, Any]]:
        """Export edge list for frontend visualization."""
        result = []
        for edge_id, meta in self.edges_meta.items():
            u_coords = self.node_positions.get(meta.u, (0.0, 0.0))
            v_coords = self.node_positions.get(meta.v, (0.0, 0.0))
            result.append({
                "id": meta.id,
                "name": meta.name,
                "u": meta.u,
                "v": meta.v,
                "coordinates": [[u_coords[0], u_coords[1]], [v_coords[0], v_coords[1]]],
                "distance_km": meta.distance_km,
                "is_blocked": meta.is_blocked,
                "blockage_reason": meta.blockage_reason,
            })
        return result

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Export nodes for frontend visualization."""
        return [
            {"id": nid, "lat": lat, "lng": lng, "label": self.node_labels.get(nid, nid)}
            for nid, (lat, lng) in self.node_positions.items()
        ]
