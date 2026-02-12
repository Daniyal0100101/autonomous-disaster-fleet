import requests
import time
import random

API_URL = "http://localhost:8000/api/v1/update"


def generate_mock_state(step):
    return {
        "step": step,
        "robots": [
            {
                "id": "R1",
                "position": (step % 10, 0),
                "battery": max(0, 100 - step),
                "status": "MOVING",
            },
            {
                "id": "R2",
                "position": (0, step % 10),
                "battery": max(0, 90 - step),
                "status": "IDLE",
            },
        ],
        "grid": {
            "width": 10,
            "height": 10,
            "obstacles": [[2, 2], [3, 3], [4, 4]],
            "charging_stations": [[0, 0], [9, 9]],
        },
        "active_missions": [],
    }


def run_mock_simulation():
    step = 0
    print(f"Starting mock simulation, pushing to {API_URL}...")
    try:
        while True:
            state = generate_mock_state(step)
            response = requests.post(API_URL, json=state)
            if response.status_code == 200:
                print(f"Step {step}: Success")
            else:
                print(f"Step {step}: Failed {response.status_code} - {response.text}")

            step += 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping mock simulation.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    run_mock_simulation()
