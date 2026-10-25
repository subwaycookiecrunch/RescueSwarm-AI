"""Unit and integration tests for RescueSwarm multi-agent system."""

import pytest
import asyncio
from rescueswarm.engine import SwarmEngine
from rescueswarm.models import AgentStatus, IncidentSeverity


@pytest.mark.asyncio
async def test_swarm_initialization():
    engine = SwarmEngine()
    await engine.start()
    health = engine.get_health()
    assert health.healthy_agents == 5
    assert health.system_health_pct == 100.0
    await engine.stop()


@pytest.mark.asyncio
async def test_disaster_verification_and_clustering():
    engine = SwarmEngine()
    await engine.start()
    incidents = await engine.simulate_major_emergency()
    assert len(incidents) == 4

    # Allow async event bus to propagate verification -> triage -> dispatch
    await asyncio.sleep(0.5)

    crit = [inc for inc in engine.verification_agent.verified_incidents.values() if inc.severity == IncidentSeverity.CRITICAL]
    assert len(crit) >= 1
    assert crit[0].confidence > 0.85
    assert crit[0].assigned_resource_id is not None
    await engine.stop()


@pytest.mark.asyncio
async def test_hostile_fake_news_quarantined():
    engine = SwarmEngine()
    await engine.start()
    res = await engine.simulate_inject_fake_news()
    assert res["decision"] == "QUARANTINED"
    assert res["confidence"] < 0.35
    assert len(engine.verification_agent.quarantined_rumors) == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_road_blockage_and_rerouting():
    engine = SwarmEngine()
    await engine.start()
    await engine.simulate_major_emergency()
    await asyncio.sleep(0.5)

    # Block Road B
    blocked = await engine.simulate_block_road_b()
    assert blocked is not None
    assert blocked["is_blocked"] is True

    # Active dispatches should not use blocked road
    await asyncio.sleep(0.5)
    for dispatch in engine.routing_agent.active_dispatches.values():
        is_blocked, _ = engine.city_graph.is_route_blocked(dispatch["route_nodes"])
        assert not is_blocked

    await engine.stop()


@pytest.mark.asyncio
async def test_self_healing_failover():
    engine = SwarmEngine()
    await engine.start()
    await engine.simulate_major_emergency()
    await asyncio.sleep(0.5)

    # Terminate routing agent
    await engine.kill_agent("routing-agent")
    assert engine.routing_agent.is_killed is True

    # Wait for Recovery Agent watchdog to detect silence & failover
    await asyncio.sleep(3.0)

    health = engine.get_health()
    assert health.self_healing_events >= 1
    assert health.system_health_pct == 100.0
    assert engine.routing_agent.status == AgentStatus.CRASHED
    assert engine.backup_routing_agent.status == AgentStatus.BACKUP_ACTIVE

    await engine.stop()
