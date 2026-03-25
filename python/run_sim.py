import os

import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def simulate():
    payload = {
        "demand": 1000,
        "operators": 50,
        "shift_hours": 8.0,
        "machine_condition": "average",
    }
    response = requests.post(f"{BASE_URL}/simulate", json=payload, timeout=300)
    data = response.json()
    print("\n========================================")
    print("SHIPPING UPDATE: MIXED CONFIGURATION")
    print("========================================")
    print(f"Throughput: {data['throughput_mean']} units/shift")
    print(
        f"Bottleneck: {data.get('bottleneck_station_name', 'Unknown')} "
        f"(ID: {data['bottleneck_station_id']})"
    )
    print("----------------------------------------")
    for metric in data.get("station_metrics", []):
        print(
            f"Station {metric['station_id']} ({metric['station_name']}): "
            f"{metric['utilization'] * 100}% Util"
        )
    print("========================================\n")


if __name__ == "__main__":
    simulate()
