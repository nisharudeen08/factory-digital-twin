import asyncio
import json
import time
from typing import Set, Dict, Any
from websockets.server import WebSocketServerProtocol
from math_engine import ShiftResult

class WebSocketBridge:
    """Manages WebSocket connections and broadcasts factory state."""
    def __init__(self):
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.current_state: Dict[str, Any] = {
            "t": int(time.time()),
            "shift_pct": 0.0,
            "throughput_so_far": 0,
            "stations": [],
            "alert_en": None,
            "alert_ta": None,
            "mode": "static"
        }
        self.running = True
        self.speed = 1.0

    async def register(self, ws: WebSocketServerProtocol):
        self.connected_clients.add(ws)
        # Send immediate initial state
        await ws.send(json.dumps(self.current_state))
        
    async def unregister(self, ws: WebSocketServerProtocol):
        self.connected_clients.remove(ws)

    async def broadcast_loop(self):
        while True:
            if self.running and self.connected_clients:
                self.current_state["t"] = int(time.time())
                msg = json.dumps(self.current_state)
                # Gather broadcast tasks
                tasks = [asyncio.create_task(ws.send(msg)) for ws in self.connected_clients]
                # Send to all without failing if one disconnects
                if tasks:
                    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            await asyncio.sleep(0.5 / max(0.1, self.speed))

    def update_state(self, result: ShiftResult):
        """Update the global state to be broadcasted."""
        self.current_state["shift_pct"] = result.shift_completion_pct
        self.current_state["throughput_so_far"] = result.throughput
        
        b_alert_en = None
        b_alert_ta = None
        
        stations_data = []
        for s in result.stations:
            stations_data.append({
                "id": s.id, "name": s.name, "name_ta": s.name_ta,
                "util": s.utilization, "queue": s.queue_length,
                "status": s.status, "is_bottleneck": s.is_bottleneck,
                "position_x": 0.0, "position_z": 0.0 # Will be populated config side if needed
            })
            if s.is_bottleneck:
                b_alert_en = f"Bottleneck at {s.name}"
                b_alert_ta = f"{s.name_ta} இல் தடை"
                
        self.current_state["stations"] = stations_data
        self.current_state["alert_en"] = b_alert_en
        self.current_state["alert_ta"] = b_alert_ta

bridge = WebSocketBridge()

async def ws_handler(websocket: WebSocketServerProtocol, path: str):
    await bridge.register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "ping":
                await websocket.send(json.dumps({"type": "pong"}))
    except Exception as e:
        pass
    finally:
        await bridge.unregister(websocket)
