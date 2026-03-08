"""Unit tests for pure helper functions in backend/main.py."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch

from main import (
    _status_to_ui,
    _priority_to_ui,
    _mission_status_to_ui,
    _parse_allowed_origins,
    _convert_simulation_state,
    _build_metrics_snapshot,
)
from models import MapGrid, RobotState, SimulationState


# ---------------------------------------------------------------------------
# _status_to_ui
# ---------------------------------------------------------------------------


def test_status_to_ui_idle():
    assert _status_to_ui("idle") == "IDLE"


def test_status_to_ui_moving():
    assert _status_to_ui("moving") == "MOVING"


def test_status_to_ui_charging():
    assert _status_to_ui("charging") == "CHARGING"


def test_status_to_ui_dead():
    assert _status_to_ui("dead") == "DEAD"


def test_status_to_ui_unknown_uppercases():
    assert _status_to_ui("broken") == "BROKEN"


def test_status_to_ui_case_insensitive():
    assert _status_to_ui("IDLE") == "IDLE"
    assert _status_to_ui("Moving") == "MOVING"


# ---------------------------------------------------------------------------
# _priority_to_ui
# ---------------------------------------------------------------------------


def test_priority_to_ui_high():
    assert _priority_to_ui("high") == "High"


def test_priority_to_ui_medium():
    assert _priority_to_ui("medium") == "Medium"


def test_priority_to_ui_low():
    assert _priority_to_ui("low") == "Low"


def test_priority_to_ui_unknown_passthrough():
    assert _priority_to_ui("critical") == "critical"


# ---------------------------------------------------------------------------
# _mission_status_to_ui
# ---------------------------------------------------------------------------


def test_mission_status_pending():
    assert _mission_status_to_ui("pending") == "PENDING"


def test_mission_status_active_maps_to_in_progress():
    assert _mission_status_to_ui("active") == "IN_PROGRESS"


def test_mission_status_completed():
    assert _mission_status_to_ui("completed") == "COMPLETED"


def test_mission_status_unknown_uppercases():
    assert _mission_status_to_ui("queued") == "QUEUED"


# ---------------------------------------------------------------------------
# _parse_allowed_origins
# ---------------------------------------------------------------------------


def test_parse_allowed_origins_from_env():
    with patch.dict(os.environ, {"FRONTEND_ORIGINS": "http://a.com,http://b.com"}):
        origins = _parse_allowed_origins()
    assert origins == ["http://a.com", "http://b.com"]


def test_parse_allowed_origins_strips_whitespace():
    with patch.dict(os.environ, {"FRONTEND_ORIGINS": " http://a.com , http://b.com "}):
        origins = _parse_allowed_origins()
    assert "http://a.com" in origins
    assert "http://b.com" in origins


def test_parse_allowed_origins_defaults_when_empty():
    with patch.dict(os.environ, {"FRONTEND_ORIGINS": ""}):
        origins = _parse_allowed_origins()
    assert "http://localhost:3000" in origins
    assert len(origins) >= 2


def test_parse_allowed_origins_ignores_blank_entries():
    with patch.dict(os.environ, {"FRONTEND_ORIGINS": "http://a.com,,http://b.com"}):
        origins = _parse_allowed_origins()
    assert "" not in origins
    assert len(origins) == 2


# ---------------------------------------------------------------------------
# _convert_simulation_state
# ---------------------------------------------------------------------------


def test_convert_splits_active_and_completed():
    payload = {
        "robots": [],
        "missions": [
            {"id": 1, "priority": "high", "target": {"x": 1, "y": 1}, "status": "active"},
            {"id": 2, "priority": "low", "target": {"x": 2, "y": 2}, "status": "completed"},
        ],
        "obstacles": [],
        "charging_stations": [],
    }
    state = _convert_simulation_state(payload, step=1)
    assert len(state.active_missions) == 1
    assert len(state.completed_missions) == 1


def test_convert_active_mission_status_normalized():
    payload = {
        "robots": [],
        "missions": [
            {"id": 1, "priority": "high", "target": {"x": 1, "y": 1}, "status": "active"},
        ],
        "obstacles": [],
        "charging_stations": [],
    }
    state = _convert_simulation_state(payload, step=1)
    assert state.active_missions[0].status == "IN_PROGRESS"


def test_convert_robot_status_normalized():
    payload = {
        "robots": [{"id": 1, "x": 3, "y": 4, "battery": 80.0, "status": "moving"}],
        "missions": [],
        "obstacles": [],
        "charging_stations": [],
    }
    state = _convert_simulation_state(payload, step=1)
    assert state.robots[0].status == "MOVING"


def test_convert_obstacles_and_stations_parsed():
    payload = {
        "robots": [],
        "missions": [],
        "obstacles": [{"x": 5, "y": 6, "type": "debris"}],
        "charging_stations": [{"x": 10, "y": 20}],
    }
    state = _convert_simulation_state(payload, step=1)
    assert (5, 6) in state.grid.obstacles
    assert (10, 20) in state.grid.charging_stations


def test_convert_step_incremented():
    payload = {"robots": [], "missions": [], "obstacles": [], "charging_stations": []}
    state = _convert_simulation_state(payload, step=42)
    assert state.step == 42


# ---------------------------------------------------------------------------
# _build_metrics_snapshot
# ---------------------------------------------------------------------------


def _make_state(robots):
    return SimulationState(
        step=1,
        robots=robots,
        grid=MapGrid(width=50, height=50, obstacles=[], charging_stations=[]),
        active_missions=[],
        completed_missions=[],
    )


def test_build_metrics_excludes_dead_from_active_count():
    robots = [
        RobotState(id="1", position=(0, 0), battery=80.0, status="IDLE"),
        RobotState(id="2", position=(1, 1), battery=0.0, status="DEAD"),
    ]
    metrics = _build_metrics_snapshot(_make_state(robots), {})
    assert metrics.active_robots == 1


def test_build_metrics_fleet_battery_average():
    robots = [
        RobotState(id="1", position=(0, 0), battery=60.0, status="IDLE"),
        RobotState(id="2", position=(1, 1), battery=40.0, status="IDLE"),
    ]
    metrics = _build_metrics_snapshot(_make_state(robots), {})
    assert metrics.fleet_battery == pytest.approx(50.0)


def test_build_metrics_zero_robots():
    metrics = _build_metrics_snapshot(_make_state([]), {})
    assert metrics.fleet_battery == 0.0
    assert metrics.active_robots == 0


def test_build_metrics_avg_delivery_time_from_simulator():
    robots = [RobotState(id="1", position=(0, 0), battery=100.0, status="IDLE")]
    metrics = _build_metrics_snapshot(_make_state(robots), {"avg_completion_time": 42.5})
    assert metrics.avg_delivery_time == pytest.approx(42.5)


def test_build_metrics_total_battery_used():
    # One robot at 60% — 40% used out of 100% baseline
    robots = [RobotState(id="1", position=(0, 0), battery=60.0, status="IDLE")]
    metrics = _build_metrics_snapshot(_make_state(robots), {})
    assert metrics.total_battery_used == pytest.approx(40.0)
