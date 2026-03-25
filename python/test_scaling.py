import requests
import json
import time

BASE_URL = "http://localhost:8000"

def get_current_config():
    resp = requests.get(f"{BASE_URL}/config")
    return resp.json()

def simulate():
    payload = {
        "demand": 4000,
        "operators": 50,
        "shift_hours": 8.0,
        "machine_condition": "average"
    }
    resp = requests.post(f"{BASE_URL}/simulate", json=payload)
    return resp.json()

def update_config(config):
    resp = requests.post(f"{BASE_URL}/config", json=config)
    return resp.json()

def run_experiment():
    print("Step 1: Get baseline simulation...")
    baseline = simulate()
    print(f"  Baseline Throughput: {baseline['throughput_mean']}")
    print(f"  Baseline Bottleneck: {baseline['bottleneck_station_name']} (ID: {baseline['bottleneck_station_id']})")
    
    config = get_current_config()
    bn_id = baseline['bottleneck_station_id']
    
    # Increase machine count for ALL stations by 2
    for station in config['stations']:
        old_count = station['num_machines']
        station['num_machines'] += 2
        print(f"  Increasing {station['name']} from {old_count} to {station['num_machines']}...")
            
    update_config(config)
    
    print("\nStep 3: Simulating with new configuration...")
    result = simulate()
    print(f"  New Throughput: {result['throughput_mean']}")
    print(f"  New Bottleneck: {result['bottleneck_station_name']} (ID: {result['bottleneck_station_id']})")
    
    diff = result['throughput_mean'] - baseline['throughput_mean']
    pct = (diff / baseline['throughput_mean']) * 100 if baseline['throughput_mean'] > 0 else 0
    print(f"\nRESULT: Throughput increased by {round(diff, 1)} units ({round(pct, 1)}%)")

if __name__ == "__main__":
    run_experiment()
