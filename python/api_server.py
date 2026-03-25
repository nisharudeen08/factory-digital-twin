import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from factory_simulation import run_replications

logger = logging.getLogger("factory_digital_twin.api")
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "configs" / "factory_config.json"
DEFAULT_CONFIG = {
    "factory_type": "lathe",
    "factory_name": "Factory Digital Twin",
    "mode": "static",
    "language": "en",
    "shift_hours": 8.0,
    "num_operators": 2,
    "demand_units": 200,
    "stations": [],
}

_unity_bridge = None
last_sim_result: Optional[Dict] = None
last_sim_config: Optional[Dict] = None


def get_unity_bridge():
    """Lazy load the bridge so the API can still boot if the module is unavailable."""
    global _unity_bridge
    if _unity_bridge is None:
        try:
            from unity_bridge import bridge as unity_bridge

            _unity_bridge = unity_bridge
        except Exception as exc:
            logger.warning("Unity bridge unavailable: %s", exc)
            return None
    return _unity_bridge


def load_config() -> Dict:
    """Load the factory configuration from disk."""
    if not CONFIG_PATH.exists():
        logger.warning("Config file missing at %s; using default config", CONFIG_PATH)
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as exc:
        logger.exception("Failed to load config from %s", CONFIG_PATH)
        raise HTTPException(status_code=500, detail=f"Invalid config file: {exc}") from exc

    if "stations" not in config:
        config["stations"] = []
    return config


def save_config_to_disk(config: Dict) -> None:
    """Persist config into python/configs regardless of current working directory."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as config_file:
        json.dump(config, config_file, indent=2, ensure_ascii=False)


def resolve_station_name(config: Dict, station_id: int) -> str:
    """Resolve a station name from the active config."""
    for station in config.get("stations", []):
        if station.get("id") == station_id:
            return station.get("name", "")
    return ""


def build_simulation_response(result: Dict, config: Dict) -> Dict:
    """Normalize simulation payload returned by the API and WebSocket bridge."""
    bottleneck_ids = result.get("bottleneck_ids", [])
    bottleneck_station_id = result.get("bottleneck_station_id", -1)
    bottleneck_station_name = resolve_station_name(config, bottleneck_station_id)

    return {
        "throughput_mean": result.get("throughput_mean", 0),
        "bottleneck_station_id": bottleneck_station_id,
        "bottleneck_station_name": bottleneck_station_name,
        "bottleneck_ids": bottleneck_ids,
        "station_metrics": result.get("station_metrics", []),
        "replications": result.get("replications", 30),
        "alert_enabled": bool(bottleneck_ids),
        "alert_en": f"Bottleneck at {bottleneck_station_name}" if bottleneck_station_name else None,
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    config = load_config()
    bridge = get_unity_bridge()
    if bridge:
        bridge.update_config(config)
    logger.info("Factory Digital Twin API startup complete")
    yield
    logger.info("Factory Digital Twin API shutdown complete")


app = FastAPI(
    title="Factory Digital Twin API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimRequest(BaseModel):
    demand: int = Field(default=200, ge=1)
    operators: int = Field(default=2, ge=1)
    shift_hours: float = Field(default=8.0, gt=0)
    machine_condition: str = "average"
    language: str = "en"


class StationSchema(BaseModel):
    id: int
    name: str
    name_ta: str = ""
    icon: str
    num_machines: int = Field(ge=1)
    cycle_time_sec: float = Field(gt=0)
    mtbf_hours: float = Field(gt=0)
    mttr_hours: float = Field(gt=0)
    setup_minutes: float = Field(default=10.0, ge=0)
    variability: float = Field(default=0.15, ge=0)
    workflow_order: int = Field(default=1, ge=1)
    position_x: float = 0.0
    position_z: float = 0.0


class FactoryConfigSchema(BaseModel):
    factory_type: str
    factory_name: str
    mode: str
    language: str
    shift_hours: float = Field(gt=0)
    num_operators: int = Field(ge=1)
    demand_units: int = Field(default=200, ge=0)
    stations: List[StationSchema]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.warning("Request validation failed: %s", exc.errors())
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled application error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/")
async def root():
    """Minimal service metadata for smoke tests."""
    return {
        "service": "factory-digital-twin",
        "status": "ok",
        "websocket_path": "/ws",
    }


@app.get("/health")
async def health():
    """Render health endpoint."""
    return {"status": "ok"}


@app.get("/config")
async def get_config():
    """Return the active factory config."""
    return load_config()


@app.post("/config")
async def save_config(config: FactoryConfigSchema):
    """Validate, persist, and broadcast a new configuration."""
    config_data = config.model_dump()
    if not config_data["stations"]:
        raise HTTPException(status_code=400, detail="At least one station is required")

    save_config_to_disk(config_data)

    bridge = get_unity_bridge()
    if bridge:
        bridge.update_config(config_data)
        try:
            await bridge.broadcast_config_update(config_data)
        except Exception:
            logger.exception("Failed to broadcast config update to WebSocket clients")

    total_machines = sum(station["num_machines"] for station in config_data["stations"])
    logger.info(
        "Config saved: %s stations, %s total machines",
        len(config_data["stations"]),
        total_machines,
    )
    return {
        "valid": True,
        "station_count": len(config_data["stations"]),
        "total_machines": total_machines,
        "message": "Config saved and broadcast to connected WebSocket clients",
    }


@app.post("/simulate")
async def simulate(req: SimRequest):
    """Run the simulation without blocking the main event loop."""
    global last_sim_result, last_sim_config

    config = load_config()
    if not config.get("stations"):
        raise HTTPException(status_code=400, detail="No stations configured")

    logger.info(
        "Simulation requested: demand=%s shift_hours=%s condition=%s",
        req.demand,
        req.shift_hours,
        req.machine_condition,
    )

    try:
        result = await asyncio.to_thread(
            run_replications,
            config,
            req.demand,
            req.shift_hours,
            req.machine_condition,
            30,
        )
    except Exception as exc:
        logger.exception("Simulation failed")
        raise HTTPException(status_code=500, detail="Simulation failed") from exc

    response_data = build_simulation_response(result, config)
    last_sim_result = response_data
    last_sim_config = config

    bridge = get_unity_bridge()
    if bridge:
        try:
            bridge.set_sim_result(response_data, config)
        except Exception:
            logger.exception("Failed to update WebSocket bridge with simulation result")

    logger.info(
        "Simulation completed: throughput=%s bottlenecks=%s",
        response_data["throughput_mean"],
        response_data["bottleneck_ids"],
    )
    return response_data


@app.get("/stations")
async def get_stations():
    """Return the configured stations."""
    return load_config().get("stations", [])


@app.get("/bottleneck")
async def get_bottleneck():
    """Return the latest bottleneck data after a simulation run."""
    if not last_sim_result:
        return {
            "bottleneck_station_id": -1,
            "bottleneck_station_name": "",
            "bottleneck_ids": [],
            "message": "Run /simulate first",
        }

    return {
        "bottleneck_station_id": last_sim_result.get("bottleneck_station_id", -1),
        "bottleneck_station_name": last_sim_result.get("bottleneck_station_name", ""),
        "bottleneck_ids": last_sim_result.get("bottleneck_ids", []),
    }


async def handle_websocket_connection(websocket: WebSocket):
    """Single-port WebSocket endpoint used by Unity and browser clients."""
    bridge = get_unity_bridge()
    if not bridge:
        await websocket.close(code=1011, reason="WebSocket bridge unavailable")
        return

    await websocket.accept()
    bridge.clients.add(websocket)
    logger.info("WebSocket client connected: %s", websocket.client)

    if bridge.config_data is None:
        bridge.update_config(load_config())

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "websocket_path": "/ws",
                "secure_transport_supported": True,
            }
        )

        if bridge.config_data:
            await websocket.send_json(
                {
                    "type": "config_update",
                    "config": bridge.config_data,
                }
            )

        if last_sim_result:
            await websocket.send_json(bridge._build_current_state())

        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "detail": "Invalid JSON payload"})
                continue

            msg_type = data.get("type", "")
            if msg_type == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                        "timestamp": time.time(),
                    }
                )
            elif msg_type == "request_config":
                await websocket.send_json(
                    {
                        "type": "config",
                        "config": bridge.config_data or load_config(),
                    }
                )
            elif msg_type == "request_state":
                await websocket.send_json(bridge._build_current_state())
            elif msg_type == "start_simulation":
                bridge.sim_running = True
                bridge._sim_time = 0.0
                await websocket.send_json(
                    {
                        "type": "simulation_started",
                        "timestamp": time.time(),
                    }
                )
            elif msg_type == "stop_simulation":
                bridge.sim_running = False
                await websocket.send_json(
                    {
                        "type": "simulation_stopped",
                        "timestamp": time.time(),
                    }
                )
            else:
                await websocket.send_json(
                    {"type": "error", "detail": f"Unknown message type: {msg_type}"}
                )
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected: %s", websocket.client)
    except Exception:
        logger.exception("WebSocket connection error")
    finally:
        bridge.clients.discard(websocket)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket_connection(websocket)


@app.websocket("/")
async def websocket_root_alias(websocket: WebSocket):
    await handle_websocket_connection(websocket)
