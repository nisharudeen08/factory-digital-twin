"""
test_integration.py - End-to-end connectivity check.
"""

import asyncio
import json
import os
import sys
import urllib.error
import urllib.request

import websockets

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
WS_URL = os.environ.get("WS_URL", "ws://127.0.0.1:8000/ws")


def check_api_health():
    print("1. Checking API health...")
    try:
        request = urllib.request.Request(f"{API_URL}/health")
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            assert data["status"] == "ok"
            print("   OK: API is running")
    except Exception as error:
        print(f"   FAIL: API health check failed: {error}")
        sys.exit(1)


def trigger_simulation():
    print("2. Triggering simulation...")
    payload = json.dumps(
        {
            "demand": 100,
            "operators": 2,
            "shift_hours": 8.0,
            "machine_condition": "average",
            "language": "en",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{API_URL}/simulate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode())
            assert data["throughput_mean"] >= 0
            print("   OK: Simulation completed")
            return data
    except urllib.error.HTTPError as error:
        print(f"   FAIL: Simulation request failed: {error.code} {error.reason}")
    except Exception as error:
        print(f"   FAIL: Simulation request failed: {error}")

    sys.exit(1)


async def check_websocket_bridge():
    print("3. Checking WebSocket send/receive...")

    received_pong = False
    received_config = False
    received_state = False

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("   OK: Connected to WebSocket")

            await websocket.send(json.dumps({"type": "ping"}))
            await websocket.send(json.dumps({"type": "request_config"}))
            await websocket.send(json.dumps({"type": "request_state"}))

            for _ in range(8):
                raw_message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(raw_message)

                if data.get("type") == "pong":
                    received_pong = True
                    print("   OK: Received pong")
                elif data.get("type") in {"config", "config_update"}:
                    received_config = True
                    station_count = len(data.get("config", {}).get("stations", []))
                    print(f"   OK: Received config with {station_count} stations")
                elif "t" in data and "stations" in data:
                    received_state = True
                    print(f"   OK: Received state update for {len(data['stations'])} stations")

                if received_pong and received_config and received_state:
                    break

    except Exception as error:
        print(f"   FAIL: WebSocket check failed: {error}")
        sys.exit(1)

    missing = []
    if not received_pong:
        missing.append("pong")
    if not received_config:
        missing.append("config")
    if not received_state:
        missing.append("state")

    if missing:
        print("   FAIL: Missing WebSocket messages: " + ", ".join(missing))
        sys.exit(1)


def main():
    print("Starting end-to-end integration test\n" + "=" * 40)
    check_api_health()
    trigger_simulation()
    asyncio.run(check_websocket_bridge())
    print("=" * 40 + "\nTest suite complete")


if __name__ == "__main__":
    main()
