# Factory Digital Twin

Static digital twin for a small factory with an Android app, Python backend, and Unity 3D integration.

FastAPI backend for a factory digital twin with REST endpoints and single-port WebSocket streaming for Unity clients.

## Deployable Python Layout

```text
render.yaml
python/
  api_server.py
  server.py
  requirements.txt
  configs/
    factory_config.json
```

## Local Run

```bash
cd python
pip install -r requirements.txt
python server.py
```

- API: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- WebSocket: `ws://localhost:8000/ws`

## Endpoints

- `GET /health`
- `GET /config`
- `POST /config`
- `POST /simulate`
- `GET /stations`
- `GET /bottleneck`
- `WS /ws`

## Render

- Uses repo root [`render.yaml`](/c:/Users/nisharu deen/Downloads/PROJECT/factory_digital_twin/render.yaml)
- Uses `python/` as `rootDir`
- Starts with `python server.py`
