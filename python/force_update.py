import os

import requests

url = os.environ.get("CONFIG_URL", "http://localhost:8000/config")
config = {
    "factory_type": "lathe",
    "factory_name": "Test Factory",
    "mode": "static",
    "language": "en",
    "shift_hours": 8.0,
    "num_operators": 10,
    "stations": [
        {
            "id": 1,
            "name": "Lathe Machine",
            "name_ta": "Lathe Machine",
            "icon": "lathe",
            "num_machines": 10,
            "cycle_time_sec": 45.0,
            "mtbf_hours": 8.0,
            "mttr_hours": 0.5,
            "setup_minutes": 10.0,
            "variability": 0.15,
            "position_x": 0.0,
            "position_z": 0.0,
        },
        {
            "id": 2,
            "name": "CNC Milling",
            "name_ta": "CNC Milling",
            "icon": "cnc",
            "num_machines": 10,
            "cycle_time_sec": 60.0,
            "mtbf_hours": 12.0,
            "mttr_hours": 0.5,
            "setup_minutes": 15.0,
            "variability": 0.15,
            "position_x": 5.0,
            "position_z": 0.0,
        },
    ],
}

try:
    response = requests.post(url, json=config, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as exc:
    print(f"Error: {exc}")
