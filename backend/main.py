from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SimulationState, RobotState, MapGrid

app = FastAPI()

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for the latest simulation state
# Initialize with a default empty state to avoid errors if queried before first update
current_state = SimulationState(
    step=0,
    robots=[],
    grid=MapGrid(width=10, height=10, obstacles=[], charging_stations=[]),
    active_missions=[],
)


@app.get("/")
def read_root():
    return {"message": "RescueRoute AI Backend Operating Normal"}


@app.post("/api/v1/update")
def update_simulation_state(state: SimulationState):
    global current_state
    current_state = state
    return {"status": "received", "step": state.step}


@app.get("/api/v1/state", response_model=SimulationState)
def get_simulation_state():
    return current_state
