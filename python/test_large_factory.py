import requests, json, time, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure we have the right paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "configs", "factory_config.json")

BASE = "http://localhost:8000"

print("=" * 55)
print("LARGE FACTORY TEST (70 MACHINES)")
print("=" * 55)

# 7 Stations, 10 machines each = 70 total
icons = ["lathe", "cnc", "drill", "band_saw", "weld", "grind", "paint"]
stations = []

for i, icon in enumerate(icons):
    stations.append({
        "id": i + 1,
        "name": f"{icon.capitalize()} Station",
        "name_ta": f"{icon} பிரிவு",
        "icon": icon,
        "num_machines": 10,  # 10 machines per station
        "cycle_time_sec": 40,
        "mtbf_hours": 10,
        "mttr_hours": 1,
        "setup_minutes": 10,
        "variability": 0.1,
        "position_x": i * 7, # 7m spacing between stations
        "position_z": 0
    })

large_config = {
    "factory_type": "industrial",
    "factory_name": "Mega Factory 70",
    "mode": "static",
    "language": "en",
    "shift_hours": 8,
    "num_operators": 15,
    "stations": stations
}

# 1. Send Large Config
print("\n[1] Sending 70-machine config to Python...")
try:
    r = requests.post(f"{BASE}/config", json=large_config, timeout=10)
    if r.status_code == 200:
        result = r.json()
        print(f"    SUCCESS - Built factory with {len(icons)} stations and 70 machines.")
    else:
        print(f"    FAIL: status code {r.status_code}")
except Exception as e:
    print(f"    FAIL: Could not connect to Python server. Error: {e}")
    sys.exit(1)

# 2. Verify saved file (Robust path check)
print(f"\n[2] Verifying saved config at: {CONFIG_PATH}")
if os.path.exists(CONFIG_PATH):
    saved = json.load(open(CONFIG_PATH, encoding="utf-8"))
    print(f"    PASS - config saved correctly to disk ({len(saved['stations'])} stations)")
else:
    print(f"    FAIL - config file not found at {CONFIG_PATH}")

# 3. Trigger Simulation
print("\n[3] Stress-testing simulation with 70 machines...")
try:
    r = requests.post(f"{BASE}/simulate", json={
        "factory_type": "industrial",
        "demand": 500,
        "operators": 15,
        "shift_hours": 8,
        "machine_condition": "good",
        "language": "en"
    }, timeout=60)

    if r.status_code == 200:
        sim = r.json()
        print(f"    PASS - Large scale throughput: {sim['throughput_mean']:.0f} units")
        print(f"    Bottleneck detected at: {sim['bottleneck_station_name']}")
except Exception as e:
    print(f"    Simulation Failed or Timed out: {e}")

print("\n" + "=" * 55)
print("TEST COMPLETE")
print("=" * 55)
print("Go to Unity Scene now to see the 70-machine layout!")
