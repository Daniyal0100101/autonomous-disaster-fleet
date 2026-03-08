"""Unit tests for SimulationEngine — robot state machine, battery, and mission lifecycle."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from simulator import (
    SimulationEngine,
    Robot,
    Mission,
    ChargingStation,
    BATTERY_DRAIN_PER_MOVE,
    BATTERY_CHARGE_PER_TICK,
    MIN_BATTERY_FOR_MISSION,
)


@pytest.fixture
def engine():
    """A blank SimulationEngine with no robots, missions, or obstacles."""
    e = SimulationEngine.__new__(SimulationEngine)
    e.tick_count = 0
    e.completed_times = []
    e.robots = []
    e.missions = []
    e.obstacles = []
    e.charging_stations = []
    e.blocked = set()
    return e


# ---------------------------------------------------------------------------
# Mission Assignment
# ---------------------------------------------------------------------------


def test_idle_robot_assigned_to_pending_mission(engine):
    robot = Robot(1, 0, 0)
    robot.battery = 100.0
    mission = Mission(1, "high", 2, 0)
    engine.robots = [robot]
    engine.missions = [mission]

    engine._assign_pending_missions()

    assert mission.status == "active"
    assert mission.assigned_robot == robot.id
    assert robot.status == "moving"
    assert robot.mission_id == mission.id


def test_robot_below_battery_threshold_not_assigned(engine):
    robot = Robot(1, 0, 0)
    robot.battery = MIN_BATTERY_FOR_MISSION - 1
    mission = Mission(1, "high", 2, 0)
    engine.robots = [robot]
    engine.missions = [mission]

    engine._assign_pending_missions()

    assert mission.status == "pending"
    assert robot.status == "idle"


def test_high_priority_mission_assigned_before_low(engine):
    robot = Robot(1, 0, 0)
    robot.battery = 100.0
    low = Mission(1, "low", 3, 0)
    high = Mission(2, "high", 4, 0)
    engine.robots = [robot]
    engine.missions = [low, high]

    engine._assign_pending_missions()

    assert high.status == "active"
    assert low.status == "pending"


def test_already_active_mission_not_reassigned(engine):
    robot = Robot(1, 0, 0)
    robot.battery = 100.0
    mission = Mission(1, "high", 5, 5)
    mission.status = "active"
    mission.assigned_robot = 99
    engine.robots = [robot]
    engine.missions = [mission]

    engine._assign_pending_missions()

    # Mission was already active; robot 1 should not steal it
    assert mission.assigned_robot == 99


# ---------------------------------------------------------------------------
# Movement & Battery Drain
# ---------------------------------------------------------------------------


def test_battery_drains_on_move(engine):
    robot = Robot(1, 0, 0)
    robot.status = "moving"
    robot.path = [(1, 0)]
    robot.battery = 50.0
    engine.robots = [robot]

    engine._move_robots_one_step()

    assert robot.battery == pytest.approx(50.0 - BATTERY_DRAIN_PER_MOVE)
    assert robot.x == 1 and robot.y == 0


def test_battery_does_not_go_below_zero(engine):
    robot = Robot(1, 0, 0)
    robot.status = "moving"
    robot.path = [(1, 0)]
    robot.battery = 0.5  # less than BATTERY_DRAIN_PER_MOVE (2.0)
    engine.robots = [robot]

    engine._move_robots_one_step()

    assert robot.battery == 0.0


def test_distance_tracked_on_move(engine):
    robot = Robot(1, 0, 0)
    robot.status = "moving"
    robot.path = [(1, 0), (2, 0)]
    robot.battery = 100.0
    engine.robots = [robot]

    engine._move_robots_one_step()

    assert robot.total_distance_traveled == pytest.approx(1.0)


def test_idle_robot_does_not_move(engine):
    robot = Robot(1, 3, 3)
    robot.status = "idle"
    robot.path = [(4, 3)]
    robot.battery = 100.0
    engine.robots = [robot]

    engine._move_robots_one_step()

    assert robot.x == 3 and robot.y == 3


# ---------------------------------------------------------------------------
# Mission Completion
# ---------------------------------------------------------------------------


def test_mission_completed_when_robot_at_target(engine):
    robot = Robot(1, 5, 5)
    robot.status = "moving"
    robot.path = []
    robot.mission_id = 1
    mission = Mission(1, "high", 5, 5)
    mission.status = "active"
    mission.start_time = 0.0
    engine.robots = [robot]
    engine.missions = [mission]

    engine._process_mission_completion()

    assert mission.status == "completed"
    assert robot.mission_id is None
    assert robot.status == "idle"
    assert len(engine.completed_times) == 1


def test_mission_not_completed_when_path_not_empty(engine):
    """Robot is at target cell but still has path steps remaining — not yet complete."""
    robot = Robot(1, 5, 5)
    robot.status = "moving"
    robot.path = [(5, 6)]  # still has steps left
    robot.mission_id = 1
    mission = Mission(1, "high", 5, 5)
    mission.status = "active"
    mission.start_time = 0.0
    engine.robots = [robot]
    engine.missions = [mission]

    engine._process_mission_completion()

    assert mission.status == "active"


# ---------------------------------------------------------------------------
# Dead Robot & Mission Release
# ---------------------------------------------------------------------------


def test_robot_marked_dead_at_zero_battery(engine):
    robot = Robot(1, 0, 0)
    robot.battery = 0.0
    engine.robots = [robot]

    engine._mark_dead_robots()

    assert robot.status == "dead"


def test_robot_not_killed_above_zero_battery(engine):
    robot = Robot(1, 0, 0)
    robot.battery = 0.1
    engine.robots = [robot]

    engine._mark_dead_robots()

    assert robot.status != "dead"


def test_mission_released_when_robot_dies(engine):
    robot = Robot(1, 0, 0)
    robot.battery = 0.0
    robot.mission_id = 1
    mission = Mission(1, "high", 5, 5)
    mission.status = "active"
    mission.assigned_robot = 1
    mission.start_time = 0.0
    engine.robots = [robot]
    engine.missions = [mission]

    engine._mark_dead_robots()

    assert robot.status == "dead"
    assert mission.status == "pending"
    assert mission.assigned_robot is None


# ---------------------------------------------------------------------------
# Battery Charging
# ---------------------------------------------------------------------------


def test_battery_charges_at_station(engine):
    station = ChargingStation(5, 5)
    robot = Robot(1, 5, 5)
    robot.battery = 10.0
    robot.status = "idle"
    engine.charging_stations = [station]
    engine.robots = [robot]

    engine._manage_battery_and_charging()

    assert robot.battery == pytest.approx(10.0 + BATTERY_CHARGE_PER_TICK)
    assert robot.status == "charging"


def test_battery_does_not_exceed_100(engine):
    station = ChargingStation(5, 5)
    robot = Robot(1, 5, 5)
    robot.battery = 95.0  # + 10.0 per tick would exceed 100
    robot.status = "charging"
    engine.charging_stations = [station]
    engine.robots = [robot]

    engine._manage_battery_and_charging()

    assert robot.battery <= 100.0


def test_full_battery_robot_at_station_becomes_idle(engine):
    station = ChargingStation(5, 5)
    robot = Robot(1, 5, 5)
    robot.battery = 95.0
    robot.status = "charging"
    engine.charging_stations = [station]
    engine.robots = [robot]

    engine._manage_battery_and_charging()

    # After charging to 100, robot should become idle
    assert robot.status == "idle"
    assert robot.battery == 100.0


def test_robot_not_at_station_does_not_charge(engine):
    station = ChargingStation(5, 5)
    robot = Robot(1, 0, 0)  # at (0,0), not at (5,5)
    robot.battery = 50.0
    robot.status = "idle"
    engine.charging_stations = [station]
    engine.robots = [robot]

    engine._manage_battery_and_charging()

    assert robot.battery == pytest.approx(50.0)


# ---------------------------------------------------------------------------
# get_state snapshot
# ---------------------------------------------------------------------------


def test_get_state_returns_correct_counts(engine):
    r1 = Robot(1, 0, 0)
    r1.battery = 80.0
    r2 = Robot(2, 1, 1)
    r2.battery = 0.0
    r2.status = "dead"
    m1 = Mission(1, "high", 5, 5)
    m1.status = "completed"
    m2 = Mission(2, "low", 3, 3)  # pending
    engine.robots = [r1, r2]
    engine.missions = [m1, m2]

    state = engine.get_state()

    assert state.metrics.active_robots == 1
    assert state.metrics.completed_missions == 1
    assert state.metrics.pending_missions == 1
