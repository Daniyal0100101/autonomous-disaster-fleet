"""Unit tests for the A* pathfinding algorithm in simulator.py."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from simulator import astar


def test_same_start_and_goal():
    assert astar((5, 5), (5, 5), set()) == [(5, 5)]


def test_adjacent_cells_no_obstacles():
    path = astar((0, 0), (1, 0), set())
    assert path == [(0, 0), (1, 0)]


def test_navigates_around_obstacle():
    # Vertical wall at x=1 from y=0 to y=2; path must go around (y<0 or y>2)
    blocked = {(1, 0), (1, 1), (1, 2)}
    path = astar((0, 1), (2, 1), blocked)
    assert path is not None
    assert len(path) > 0
    assert path[0] == (0, 1)
    assert path[-1] == (2, 1)
    assert all(cell not in blocked for cell in path)


def test_goal_is_blocked_returns_empty():
    blocked = {(3, 3)}
    assert astar((0, 0), (3, 3), blocked) == []


def test_no_path_exists_returns_empty():
    # Completely wall off (0,0) with a ring of obstacles:
    # Block all neighbours of (0,0): (1,0) and (0,1)
    # On a 5x5 grid, (0,0) can only move right or down.
    blocked = {(1, 0), (0, 1)}
    result = astar((0, 0), (4, 4), blocked, grid_size=5)
    assert result == []


def test_path_stays_within_grid_bounds():
    path = astar((0, 0), (49, 49), set(), grid_size=50)
    assert len(path) > 0
    for x, y in path:
        assert 0 <= x < 50
        assert 0 <= y < 50


def test_path_start_and_end_correct():
    path = astar((2, 3), (7, 8), set())
    assert path[0] == (2, 3)
    assert path[-1] == (7, 8)


def test_path_is_connected():
    """Each step in the path must be exactly 1 cell away from the next."""
    path = astar((0, 0), (10, 10), set())
    for i in range(len(path) - 1):
        x0, y0 = path[i]
        x1, y1 = path[i + 1]
        assert abs(x1 - x0) + abs(y1 - y0) == 1, f"Non-adjacent steps: {path[i]} -> {path[i+1]}"
