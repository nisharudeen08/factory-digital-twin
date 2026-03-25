import requests, json, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "http://localhost:8000"

print("=" * 55)
print("CONFIG FLOW TEST")
print("=" * 55)

# Test the exact example from requirements:
# 2 Lathe + 2 CNC + 1 Band Saw + 1 Drilling

test_config = {
    "factory_type": "lathe",
    "factory_name": "Test Factory",
    "mode": "static",
    "language": "en",
    "shift_hours": 8,
    "num_operators": 2,
    "stations": [
        {
            "id": 1, "name": "Lathe Machine",
            "name_ta": "தட்டு இயந்திரம்",
            "icon": "lathe", "num_machines": 2,
            "cycle_time_sec": 45, "mtbf_hours": 8,
            "mttr_hours": 0.5, "setup_minutes": 10,
            "variability": 0.15,
            "position_x": 0, "position_z": 0
        },
        {
            "id": 2, "name": "CNC Milling",
            "name_ta": "சி.என்.சி. மில்லிங்",
            "icon": "cnc", "num_machines": 2,
            "cycle_time_sec": 60, "mtbf_hours": 12,
            "mttr_hours": 0.5, "setup_minutes": 15,
            "variability": 0.15,
            "position_x": 5, "position_z": 0
        },
        {
            "id": 3, "name": "Band Saw",
            "name_ta": "பேண்ட் சா",
            "icon": "band_saw", "num_machines": 1,
            "cycle_time_sec": 35, "mtbf_hours": 10,
            "mttr_hours": 0.5, "setup_minutes": 8,
            "variability": 0.15,
            "position_x": 10, "position_z": 0
        },
        {
            "id": 4, "name": "Drilling",
            "name_ta": "துளையிடும் இயந்திரம்",
            "icon": "drill", "num_machines": 1,
            "cycle_time_sec": 30, "mtbf_hours": 10,
            "mttr_hours": 0.3, "setup_minutes": 5,
            "variability": 0.15,
            "position_x": 15, "position_z": 0
        }
    ]
}

# Send config
print("\n[1] Sending config to Python...")
r = requests.post(f"{BASE}/config",
    json=test_config, timeout=10)
assert r.status_code == 200, f"FAIL: {r.text}"
result = r.json()
assert result["valid"] == True
assert result["station_count"] == 4
assert result["total_machines"] == 6
print(f"    PASS - {result['station_count']} stations, "
      f"{result['total_machines']} total machines")

# Verify saved file
print("\n[2] Verifying saved config file...")
saved = json.load(open("configs/factory_config.json", encoding="utf-8"))
assert len(saved["stations"]) == 4
assert saved["stations"][0]["num_machines"] == 2
assert saved["stations"][0]["icon"] == "lathe"
assert saved["stations"][2]["icon"] == "band_saw"
print("    PASS - config saved correctly to disk")

# Run simulation with new config
print("\n[3] Running simulation with new config...")
r = requests.post(f"{BASE}/simulate", json={
    "factory_type": "lathe",
    "demand": 100,
    "operators": 2,
    "shift_hours": 8,
    "machine_condition": "average",
    "language": "en"
}, timeout=60)
assert r.status_code == 200
sim = r.json()
assert sim["throughput_mean"] > 0
assert len(sim["station_metrics"]) == 4
print(f"    PASS - throughput: {sim['throughput_mean']:.0f} units")
print(f"    Bottleneck: {sim['bottleneck_station_name']}")

print("\n" + "=" * 55)
print("ALL TESTS PASSED")
print("=" * 55)
print("\nNow test in Unity:")
print("  1. Press Play in Unity")
print("  2. Console must show: [Spawner] Building factory: 4 stations")
print("  3. Scene must show:")
print("     [Lathe][Lathe] -> [CNC][CNC] -> [BandSaw] -> [Drill]")
print("  4. Change config in Android app")
print("  5. Unity scene must rebuild automatically")
