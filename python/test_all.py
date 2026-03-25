#!/usr/bin/env python3
"""
test_all.py - Integration test suite for Factory Digital Twin.
"""
import json
import os
import time

import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def test_health():
    """Test /health endpoint."""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert data["status"] == "ok", f"Status should be 'ok', got {data['status']}"
        print(f"PASS: {json.dumps(data, indent=2)}")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def test_config():
    """Test /config endpoint."""
    print("\n" + "=" * 60)
    print("TEST 2: Get Configuration")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/config", timeout=5)
        data = response.json()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "stations" in data, "Config should have 'stations' key"
        assert len(data["stations"]) > 0, "Expected at least 1 station"
        print(f"PASS: Config loaded with {len(data['stations'])} stations")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def test_simulate():
    """Test /simulate endpoint."""
    print("\n" + "=" * 60)
    print("TEST 3: Factory Simulation")
    print("=" * 60)
    try:
        payload = {
            "demand": 200,
            "operators": 2,
            "shift_hours": 8.0,
            "machine_condition": "average",
            "language": "en",
        }
        response = requests.post(f"{BASE_URL}/simulate", json=payload, timeout=300)
        data = response.json()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "throughput_mean" in data, "Response should have throughput_mean"
        assert "bottleneck_station_id" in data, "Response should have bottleneck info"
        assert "station_metrics" in data, "Response should have station metrics"
        assert len(data["station_metrics"]) > 0, "Should have metrics for stations"
        print("PASS: Simulation complete")
        print(f"  Throughput: {data['throughput_mean']} units/shift")
        print(f"  Bottleneck: Station {data['bottleneck_station_id']}")
        print(f"  Replications: {data.get('replications', 0)}")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def test_bottleneck():
    """Test /bottleneck endpoint."""
    print("\n" + "=" * 60)
    print("TEST 4: Get Bottleneck Info")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/bottleneck", timeout=5)
        data = response.json()
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "bottleneck_station_id" in data, "Response should have bottleneck info"
        print("PASS: Got bottleneck info")
        return True
    except Exception as exc:
        print(f"FAIL: {exc}")
        return False


def main():
    print("\n" + "=" * 60)
    print("FACTORY DIGITAL TWIN - INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\nWaiting for server to respond...")
    max_retries = 10
    for attempt in range(max_retries):
        try:
            requests.get(f"{BASE_URL}/health", timeout=2)
            print("PASS: Server is ready")
            break
        except Exception:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1}/{max_retries}: server not ready, waiting...")
                time.sleep(1)
            else:
                print("FAIL: Server did not respond after multiple attempts")
                return False

    results = [
        ("Health Check", test_health()),
        ("Get Config", test_config()),
        ("Simulation", test_simulate()),
        ("Bottleneck", test_bottleneck()),
    ]

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    success = main()
    raise SystemExit(0 if success else 1)
