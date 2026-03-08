"""Integration tests for backend FastAPI endpoints.

Uses httpx.AsyncClient with ASGITransport so no network calls are made.
The background poller is not started (lifespan is bypassed).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

import main
from main import app
from models import MapGrid, SimulationState, RobotState


def _blank_state():
    return SimulationState(
        step=0,
        robots=[],
        grid=MapGrid(width=50, height=50, obstacles=[], charging_stations=[]),
        active_missions=[],
        completed_missions=[],
    )


def _state_with_robots():
    return SimulationState(
        step=5,
        robots=[
            RobotState(id="1", position=(0, 0), battery=80.0, status="IDLE"),
            RobotState(id="2", position=(5, 5), battery=40.0, status="MOVING"),
        ],
        grid=MapGrid(width=50, height=50, obstacles=[], charging_stations=[]),
        active_missions=[],
        completed_missions=[],
    )


@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state to blank before each test."""
    main.current_state = _blank_state()
    main.latest_simulator_metrics = {"avg_completion_time": 0.0, "total_distance_traveled": 0.0}
    yield


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.anyio
async def test_health_check(client):
    r = await client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data


@pytest.mark.anyio
async def test_get_state_returns_schema(client):
    r = await client.get("/api/v1/state")
    assert r.status_code == 200
    data = r.json()
    assert "robots" in data
    assert "active_missions" in data
    assert "grid" in data


@pytest.mark.anyio
async def test_get_robots_returns_empty_list(client):
    r = await client.get("/api/v1/robots")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.anyio
async def test_get_robots_returns_populated_list(client):
    main.current_state = _state_with_robots()
    r = await client.get("/api/v1/robots")
    assert r.status_code == 200
    robots = r.json()
    assert len(robots) == 2
    assert robots[0]["id"] == "1"


@pytest.mark.anyio
async def test_get_missions_returns_list(client):
    r = await client.get("/api/v1/missions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.anyio
async def test_get_metrics_returns_schema(client):
    main.current_state = _state_with_robots()
    r = await client.get("/api/v1/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "active_robots" in data
    assert "fleet_battery" in data
    assert "completed_missions" in data


@pytest.mark.anyio
async def test_get_metrics_active_robot_count(client):
    main.current_state = _state_with_robots()
    r = await client.get("/api/v1/metrics")
    assert r.status_code == 200
    # Both robots are not DEAD
    assert r.json()["active_robots"] == 2


@pytest.mark.anyio
async def test_ai_decide_returns_400_when_no_robots(client):
    # current_state has no robots (blank state from fixture)
    r = await client.post("/api/v1/ai/decide")
    assert r.status_code == 400
    assert "no robots" in r.json()["detail"].lower()


@pytest.mark.anyio
async def test_update_state_accepted(client):
    payload = _state_with_robots().model_dump()
    r = await client.post("/api/v1/update", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "received"
    assert data["step"] == 5


@pytest.mark.anyio
async def test_update_state_persists(client):
    payload = _state_with_robots().model_dump()
    await client.post("/api/v1/update", json=payload)
    r = await client.get("/api/v1/robots")
    assert r.status_code == 200
    assert len(r.json()) == 2
