"""FastAPI REST and WebSocket server for RescueSwarm AI Command Center."""

from __future__ import annotations
import asyncio
import json
from contextlib import asynccontextmanager
from typing import Set, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rescueswarm.engine import SwarmEngine


# Global shared SwarmEngine instance
engine = SwarmEngine()
connected_websockets: Set[WebSocket] = set()


async def ws_broadcaster(payload: Dict[str, Any]):
    """Broadcast state updates and logs to all connected frontend clients."""
    if not connected_websockets:
        return

    # Convert non-serializable objects to dict/json
    msg_str = json.dumps(payload, default=str)
    dead_sockets = set()

    for ws in list(connected_websockets):
        try:
            await ws.send_text(msg_str)
        except Exception:
            dead_sockets.add(ws)

    for ws in dead_sockets:
        connected_websockets.discard(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: register ws broadcaster and start engine
    engine.event_bus.register_ws_broadcaster(ws_broadcaster)
    await engine.start()
    yield
    # Shutdown
    await engine.stop()


app = FastAPI(
    title="RescueSwarm AI API",
    description="Multi-agent fault-tolerant crisis coordination system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def get_health():
    return engine.get_health().model_dump()


@app.get("/api/state")
async def get_state():
    return engine.get_state()


@app.post("/api/simulation/disaster")
async def trigger_disaster():
    incidents = await engine.simulate_major_emergency()
    return {
        "status": "DISASTER_TRIGGERED",
        "incidents_count": len(incidents),
        "incidents": [i.model_dump() for i in incidents],
    }


class BlockRoadRequest(BaseModel):
    road_name: str = "road_b"
    reason: str = "Debris / Landslide / Structural Fracture"


@app.post("/api/simulation/block-road")
async def block_road(req: Optional[BlockRoadRequest] = None):
    road = req.road_name if req else "road_b"
    reason = req.reason if req else "Obstruction"
    edge = engine.city_graph.block_road(road, reason=reason)
    if not edge:
        return {"status": "ERROR", "message": f"Road {road} not found"}

    await engine.event_bus.log(
        agent_id="sim-engine",
        agent_role="simulation",
        level="CHAOS",
        message=f"🚧 ROAD OBSTRUCTION INJECTED: '{edge.name}' is now BLOCKED!",
    )
    await engine.event_bus.publish(
        "road_blocked",
        {"edge_id": edge.id, "edge_name": edge.name, "reason": edge.blockage_reason},
    )
    return {"status": "ROAD_BLOCKED", "edge": edge.model_dump()}


@app.post("/api/simulation/unblock-road")
async def unblock_road(road_name: str = "road_b"):
    edge = await engine.simulate_unblock_road_b()
    return {"status": "ROAD_UNBLOCKED", "edge": edge}


@app.post("/api/simulation/inject-fake")
async def inject_fake_rumor():
    res = await engine.simulate_inject_fake_news()
    return res


class KillAgentRequest(BaseModel):
    agent_id: str = "routing-agent"


@app.post("/api/chaos/kill-agent")
async def kill_agent(req: Optional[KillAgentRequest] = None):
    aid = req.agent_id if req else "routing-agent"
    res = await engine.kill_agent(aid)
    return res


@app.post("/api/chaos/revive-agent")
async def revive_agent(req: Optional[KillAgentRequest] = None):
    aid = req.agent_id if req else "routing-agent"
    res = await engine.revive_agent(aid)
    return res


@app.post("/api/simulation/reset")
async def reset_simulation():
    await engine.reset_simulation()
    return {"status": "RESET_SUCCESS", "state": engine.get_state()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)

    # Immediately push full system state snapshot on connect
    try:
        initial_state = engine.get_state()
        await websocket.send_text(
            json.dumps({"type": "FULL_STATE", "data": initial_state}, default=str)
        )
    except Exception:
        pass

    try:
        while True:
            # Receive client commands from WebSocket
            data_text = await websocket.receive_text()
            try:
                cmd_data = json.loads(data_text)
                action = cmd_data.get("action")

                if action == "GET_STATE":
                    await websocket.send_text(
                        json.dumps({"type": "FULL_STATE", "data": engine.get_state()}, default=str)
                    )
                elif action == "TRIGGER_DISASTER":
                    await engine.simulate_major_emergency()
                elif action == "BLOCK_ROAD":
                    await engine.simulate_block_road_b()
                elif action == "UNBLOCK_ROAD":
                    await engine.simulate_unblock_road_b()
                elif action == "INJECT_FAKE":
                    await engine.simulate_inject_fake_news()
                elif action == "KILL_AGENT":
                    agent_id = cmd_data.get("agent_id", "routing-agent")
                    await engine.kill_agent(agent_id)
                elif action == "REVIVE_AGENT":
                    agent_id = cmd_data.get("agent_id", "routing-agent")
                    await engine.revive_agent(agent_id)
                elif action == "RESET":
                    await engine.reset_simulation()
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)
    except Exception:
        connected_websockets.discard(websocket)
