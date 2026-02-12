from pydantic import BaseModel
from typing import List, Tuple, Optional


class RobotState(BaseModel):
    id: str
    position: Tuple[int, int]
    battery: float
    status: str  # "IDLE", "MOVING", "CHARGING"
    current_mission: Optional[str] = None


class MapGrid(BaseModel):
    width: int
    height: int
    obstacles: List[Tuple[int, int]]
    charging_stations: List[Tuple[int, int]]


class SimulationState(BaseModel):
    step: int
    robots: List[RobotState]
    grid: MapGrid
    active_missions: List[dict]  # Placeholder for mission details
