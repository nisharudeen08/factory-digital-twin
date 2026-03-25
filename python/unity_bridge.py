"""
unity_bridge.py — WebSocket Bridge to Unity 3D

Real-time streaming of factory state to Unity clients every 500ms.
Runs as a background task alongside FastAPI in the same asyncio loop.

Message format sent every 500ms:
{
  "type": "state_update",
  "t": simulation_time_seconds,
  "shift_pct": fraction_of_shift_complete,
  "bottleneck_id": station_id,
  "stations": [
    {"station_id": 1, "util": 0.87, "queue_length": 3, "status": "running",
     "is_bottleneck": false, "name": "Lathe", "name_ta": "கடைசல்"}
  ],
  "throughput_so_far": 87,
  "alert_en": null or "BOTTLENECK at Station 3",
  "alert_ta": null or Tamil translation,
  "mode": "static" or "realtime"
}
"""

import asyncio
import json
import time
import logging
import os
from typing import Optional, Set, Dict, Any

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class UnityBridge:
    """WebSocket server that streams factory state to Unity 3D clients.

    Attributes:
        port: Standalone WebSocket server port for local legacy mode.
        clients: Set of connected WebSocket clients.
        factory_state: Current factory state to broadcast.
        config_data: Current factory config (sent on connect).
        running: Whether the bridge is actively running.
        sim_running: Whether simulation is actively running.
        last_sim_result: Last simulation result for broadcasting.
    """

    def __init__(self, port: int = None):
        if port is None:
            port = int(os.environ.get("WS_PORT", os.environ.get("PORT", 8765)))
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.factory_state: Optional[dict] = None
        self.config_data: Optional[dict] = None
        self.running = False
        self.sim_running = False
        self.server = None
        self._last_state_time = 0.0
        self.last_sim_result: Optional[Dict[str, Any]] = None
        self._sim_time = 0.0
        self._shift_duration = 8 * 3600  # 8 hours in seconds

    async def handler(self, websocket: WebSocketServerProtocol, path: str = ""):
        """Handle a new Unity client connection.

        On connect: sends full config so Unity can rebuild scene if needed.
        On message: handles 'ping' and 'request_config'.
        On disconnect: logs and cleans up.
        """
        self.clients.add(websocket)
        client_addr = websocket.remote_address
        logger.info(f"Unity client connected: {client_addr} ({len(self.clients)} total)")

        try:
            # Send config on connect
            if self.config_data:
                await websocket.send(json.dumps({
                    "type": "config_update",
                    "config": self.config_data,
                }))

            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type", "")

                    if msg_type == "ping":
                        await websocket.send(json.dumps({
                            "type": "pong",
                            "timestamp": time.time(),
                        }))
                    elif msg_type == "request_config":
                        if self.config_data:
                            await websocket.send(json.dumps({
                                "type": "config",
                                "config": self.config_data,
                            }))
                    elif msg_type == "start_simulation":
                        # Start real-time simulation broadcast
                        self.sim_running = True
                        self._sim_time = 0.0
                        await websocket.send(json.dumps({
                            "type": "simulation_started",
                            "timestamp": time.time(),
                        }))
                    elif msg_type == "stop_simulation":
                        self.sim_running = False

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from Unity client: {message[:100]}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Unity client disconnected: {client_addr}")
        finally:
            self.clients.discard(websocket)
            logger.info(f"Unity clients remaining: {len(self.clients)}")

    async def broadcast(self, message: dict) -> None:
        """Send a JSON message to all connected Unity clients.

        Args:
            message: Dictionary to serialize and send.
        """
        if not self.clients:
            return

        payload = json.dumps(message)
        disconnected = set()

        for client in self.clients.copy():
            try:
                # Handle FastAPI WebSockets
                if hasattr(client, "send_json"):
                    await client.send_json(message)
                # Handle standard websockets
                else:
                    await client.send(payload)
            except Exception as e:
                # Check for various connection closure exceptions
                # (websockets.exceptions.ConnectionClosed, starlette.websockets.WebSocketDisconnect, etc.)
                disconnected.add(client)
                logger.debug(f"Client disconnected or broadcast error: {e}")

        self.clients -= disconnected

    def update_state(self, state: dict) -> None:
        """Update the current factory state (called by simulation engine).

        Args:
            state: Factory state dict matching the broadcast format.
        """
        self.factory_state = state
        self._last_state_time = time.time()

    def update_config(self, config: dict) -> None:
        """Update the factory config and notify Unity clients.

        Args:
            config: New factory configuration dict.
        """
        self.config_data = config

    def set_sim_result(self, result: dict, config: dict) -> None:
        """Set the latest simulation result for broadcasting.

        Args:
            result: Simulation result from run_replications().
            config: Factory config used for the simulation.
        """
        self.last_sim_result = result
        self.config_data = config
        self.sim_running = True
        self._sim_time = 0.0

    async def _broadcast_loop(self) -> None:
        """Background task: broadcast factory state every 500ms."""
        while self.running:
            if self.clients:
                state = self._build_current_state()
                if self.sim_running and state.get("stations"):
                    print(f"[WS] Streaming: {state['stations'][:3]}...", flush=True)
                await self.broadcast(state)

            # Advance simulation time
            if self.sim_running:
                self._sim_time += 0.5  # 500ms increment
                if self._sim_time >= self._shift_duration:
                    self.sim_running = False

            await asyncio.sleep(0.5)  # 500ms interval

    def _build_current_state(self) -> dict:
        """Build the current state to broadcast to Unity."""
        stations = []
        
        if self.last_sim_result and self.config_data:
            # Use real simulation data
            station_metrics = self.last_sim_result.get("station_metrics", [])
            bn_ids = self.last_sim_result.get("bottleneck_ids", [])
            
            for m in station_metrics:
                s_id = m.get("station_id", 0)
                stations.append({
                    "station_id": s_id,
                    "utilization": m.get("utilization", 0.0),
                    "queue_length": m.get("queue_length", 0),
                    "status": m.get("status", "running"),
                    "is_bottleneck": s_id in bn_ids,
                    "name": m.get("station_name", ""),
                    "name_ta": m.get("station_name_ta", ""),
                })
            
            bn_id = self.last_sim_result.get("bottleneck_station_id", -1)
            alert_en = f"BOTTLENECK at IDs {bn_ids}" if bn_ids else None
            alert_ta = None

            return {
                "type": "state_update",
                "t": self._sim_time,
                "shift_pct": min(1.0, self._sim_time / self._shift_duration),
                "bottleneck_ids": bn_ids,
                "stations": stations,
                "throughput_so_far": int(self.last_sim_result.get("throughput_mean", 0) * (self._sim_time / self._shift_duration)),
                "alert_en": alert_en,
                "alert_ta": alert_ta,
                "mode": "realtime" if self.sim_running else "static",
            }
        else:
            # Return idle state when no simulation data available
            return self._get_idle_state()

    def _get_idle_state(self) -> dict:
        """Generate idle state message when no simulation is running."""
        stations = []
        if self.config_data and "stations" in self.config_data:
            for s in self.config_data["stations"]:
                stations.append({
                    "station_id": s.get("id", 0),
                    "utilization": 0.0,
                    "queue_length": 0,
                    "status": "idle",
                    "is_bottleneck": False,
                    "name": s.get("name", ""),
                    "name_ta": s.get("name_ta", ""),
                })

        return {
            "type": "state_update",
            "t": 0,
            "shift_pct": 0.0,
            "bottleneck_id": -1,
            "stations": stations,
            "throughput_so_far": 0,
            "alert_en": None,
            "alert_ta": None,
            "mode": self.config_data.get("mode", "static") if self.config_data else "static",
        }

    async def broadcast_config_update(self, config: dict) -> None:
        """Broadcast config update to all Unity clients (triggers scene rebuild).

        Args:
            config: Full factory configuration dict.
        """
        self.config_data = config
        await self.broadcast({
            "type": "config_update",
            "config": config,
        })

    async def start(self) -> None:
        """Start the WebSocket server and broadcast loop."""
        self.running = True
        self.server = await websockets.serve(
            self.handler,
            "0.0.0.0",
            self.port,
            ping_interval=20,
            ping_timeout=20,
        )
        logger.info(f"Unity WebSocket server started on ws://0.0.0.0:{self.port}")

        # Start broadcast loop
        asyncio.create_task(self._broadcast_loop())

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("Unity WebSocket server stopped")


# Global bridge instance
bridge = UnityBridge()
