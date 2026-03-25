# Railway Deployment Guide

## Quick Setup (5 minutes)

### 1. Prepare Railway Account
- Go to [railway.app](https://railway.app)
- Sign up with GitHub
- Create a new project

### 2. Deploy Python Backend

Choose ONE deployment method:

#### Option A: Deploy from GitHub
1. Click **New Project** → **Deploy from GitHub repo**
2. Connect your GitHub repository
3. Railway auto-detects the Python server and builds `python/`

#### Option B: Direct Upload
1. Click **New Project** → **Empty Project**
2. Drag and drop the `python/` folder to Railway
3. Railway detects `requirements.txt` and auto-starts the server

### 3. Configure Environment Variables

In Railway project settings, add these variables:

```
PORT=8765
WS_PORT=8765
API_PORT=8000
```

**What they do:**
- `PORT`: Primary port (used for WebSocket and API fallback)
- `WS_PORT`: WebSocket server port (default: 8765)
- `API_PORT`: FastAPI server port (default: 8000)

> **Note:** If Railway assigns a different PORT, it overrides these defaults. Use `$PORT` environment variable for maximum compatibility.

### 4. Get Your Railway URL

After deployment completes, Railway provides:
- **API URL:** `https://factory-twin.up.railway.app`
- **WebSocket URL:** `wss://factory-twin.up.railway.app` (secure WebSocket)

### 5. Update Android App

In your Android app's network configuration, update the server URL:

```java
// Before (local development)
String API_URL = "http://192.168.1.100:8000";
String WS_URL = "ws://192.168.1.100:8765";

// After (Railway production)
String API_URL = "https://factory-twin.up.railway.app";
String WS_URL = "wss://factory-twin.up.railway.app";  // secure WebSocket
```

Or use environment-based configuration:

```java
public class ApiConfig {
    static final String API_BASE_URL = 
        BuildConfig.DEBUG 
            ? "http://192.168.1.100:8000"
            : "https://factory-twin.up.railway.app";
}
```

## Server Implementation

### Python Code Changes (Already Applied)

The following changes have been made to your Python servers:

#### `unity_bridge.py`
```python
import os

class UnityBridge:
    def __init__(self, port: int = None):
        if port is None:
            port = int(os.environ.get("PORT", 8765))
        self.port = port
        # ... rest of initialization
```

#### `run_all.py`
```python
import os

async def run_servers():
    ws_port = int(os.environ.get("WS_PORT", 8765))
    api_port = int(os.environ.get("API_PORT", int(os.environ.get("PORT", 8000))))
    
    # Servers now use these ports
    await unity_bridge.start()  # Uses ws_port internally
    # FastAPI runs on api_port
```

#### `run_server.py`
```python
import os

if __name__ == "__main__":
    api_port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api_server:app", host="0.0.0.0", port=api_port, reload=False)
```

## Monitoring & Debugging

### Railway Logs
1. Go to your Railway project
2. Click **Deployments** → latest deployment
3. View **Logs** tab for real-time output
4. Look for: `"server started on ws://0.0.0.0:xxxx"`

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection timeout | Check if Railway port matches your client URL |
| WebSocket 403/401 | Ensure CORS is enabled in `api_server.py` (already done) |
| 500 error on API call | Check Railway logs for Python exceptions |
| Android can't connect | Verify `https://` and `wss://` protocols in app config |

### Test Connectivity

From Android shell or terminal:
```bash
# Test HTTP API
curl -X GET https://factory-twin.up.railway.app/health

# Test WebSocket (requires wscat)
npm install -g wscat
wscat -c wss://factory-twin.up.railway.app
```

## Advanced: Railway Configuration File

Optionally create `railway.toml` in project root for explicit configuration:

```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "python python/run_all.py"
restartPolicyMaxRetries = 5
restartPolicyWindowSeconds = 60
```

Then create `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY python/ ./
RUN pip install -r requirements.txt
EXPOSE 8000 8765
CMD ["python", "run_all.py"]
```

## Production Checklist

- [ ] Environment variables set in Railway
- [ ] Android app URLs updated to HTTPS/WSS
- [ ] `requirements.txt` includes all dependencies
- [ ] `/health` endpoint tested successfully
- [ ] WebSocket connection tested with curl or postman
- [ ] Logs show "server started" message
- [ ] Factory configuration loads correctly
- [ ] Simulation results stream to Unity

## Rollback & Redeployment

In Railway dashboard:
1. **Revert:** Click any previous deployment → **Revert**
2. **Redeploy:** Push code to GitHub or upload folder again
3. **Manual rebuild:** Click **Deploy** button in Railway UI

## Support

- Railway docs: https://docs.railway.app
- WebSocket on Railway: https://docs.railway.app/guides/websockets
- Python FastAPI: https://fastapi.tiangolo.com/
- websockets library: https://websockets.readthedocs.io/

---

**Status:** ✅ Python servers configured for Railway deployment
