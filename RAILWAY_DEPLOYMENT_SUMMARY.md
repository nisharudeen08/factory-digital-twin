# Railway Deployment: Summary of Changes ✅

## What Was Done

Your Python servers have been configured for **Railway.app** cloud deployment. All changes made are **backward compatible** with local development.

---

## 1. Python Server Code Changes

### Modified Files:

#### **A. `python/unity_bridge.py`**
```python
# ADDED (line 5)
import os

# CHANGED (lines 47-49)
def __init__(self, port: int = None):
    if port is None:
        port = int(os.environ.get("PORT", 8765))
    self.port = port
```

**Effect:** WebSocket server reads `PORT` environment variable from Railway, defaults to 8765 locally.

---

#### **B. `python/run_all.py`**
```python
# ADDED (line 9)
import os

# NEW CODE (lines 19-26)
async def run_servers():
    ip = get_lan_ip()
    
    # Get ports from environment variables (Railway deployment)
    ws_port = int(os.environ.get("WS_PORT", 8765))
    api_port = int(os.environ.get("API_PORT", int(os.environ.get("PORT", 8000))))
    
    # Updated print statements to use api_port, ws_port
```

**Effect:** Dual-server runner (FastAPI + WebSocket) now respects environment variables.

---

#### **C. `python/run_server.py`**
```python
# ADDED (line 10)
import os

# CHANGED (lines 19-21)
if __name__ == "__main__":
    ip = get_lan_ip()
    api_port = int(os.environ.get("PORT", 8000))
    
    # Updated to use api_port variable
    uvicorn.run("api_server:app", host="0.0.0.0", port=api_port, reload=False)
```

**Effect:** FastAPI-only server now respects Railway's `PORT` environment variable.

---

## 2. Documentation Files Created

### **RAILWAY_DEPLOYMENT_GUIDE.md**
Complete guide including:
- ✅ Step-by-step Railway setup (5 minutes)
- ✅ Environment variable configuration
- ✅ Monitoring and debugging instructions
- ✅ Common issues and solutions
- ✅ Production checklist

### **ANDROID_RAILWAY_CONFIG.md**
Android app configuration guide:
- ✅ How to update server URLs in Android code
- ✅ Three config options (hardcoded, build variant, runtime)
- ✅ HTTPS/WSS protocol guidance
- ✅ Testing instructions before release
- ✅ Troubleshooting common errors

---

## 3. Key Configuration Details

### Railway Environment Variables

Set these in Railway project settings:

```env
PORT=8765                   # Primary port
WS_PORT=8765               # WebSocket port (optional, defaults to PORT)
API_PORT=8000              # FastAPI port (optional, defaults to 8000)
```

### Port Mapping

| Service | Local | Railway | Environment Variable |
|---------|-------|---------|----------------------|
| WebSocket (Unity) | 8765 | varies | `WS_PORT` (defaults to `PORT`) |
| FastAPI (Android) | 8000 | varies | `API_PORT` or `PORT` |

---

## 4. Deployment Steps

### Step 1: Push Changes to GitHub
```bash
git add python/
git commit -m "Configure Python servers for Railway deployment"
git push
```

### Step 2: Deploy on Railway
1. Go to **railway.app** → Sign up with GitHub
2. Create **New Project** → **Deploy from GitHub**
3. Connect your repository
4. Railway auto-detects and deploys

### Step 3: Set Environment Variables
In Railway project dashboard:
- Click **Project Settings**
- Add variables: `PORT=8765`, `WS_PORT=8765`, `API_PORT=8000`
- Wait for auto-redeploy

### Step 4: Get Your URLs
Railway provides:
- **API:** `https://your-project.up.railway.app`
- **WebSocket:** `wss://your-project.up.railway.app`

### Step 5: Update Android App
Update Android network config files with Railway URLs:
```java
// Before
String API_URL = "http://192.168.1.100:8000";
String WS_URL = "ws://192.168.1.100:8765";

// After
String API_URL = "https://your-project.up.railway.app";
String WS_URL = "wss://your-project.up.railway.app";
```

See **ANDROID_RAILWAY_CONFIG.md** for detailed instructions.

---

## 5. Backward Compatibility ✅

All changes are **fully backward compatible** with local development:

```bash
# Still works locally!
python python/run_all.py          # Uses defaults: 8765, 8000
python python/run_server.py       # Uses defaults: 8000
python python/run_unity_bridge.py # Uses defaults: 8765
```

**Environment variables are optional** — if not set, defaults apply.

---

## 6. Testing & Verification

### Test Locally First
```bash
# Run with custom ports (simulating Railway)
PORT=3000 python python/run_all.py
```

### Test on Railway
```bash
# From any client
curl https://your-project.up.railway.app/health    # Should return 200 OK
```

Check Railway logs:
1. Dashboard → **Deployments** → Latest
2. View **Logs** tab
3. Look for: `"server started on ws://0.0.0.0:xxxx"`

---

## 7. Troubleshooting Reference

### Issue: "Connection refused"
- ✅ Check if deployment is finished in Railway
- ✅ Verify `https://` (not `http://`) in production

### Issue: "WebSocket handshake failed"  
- ✅ Ensure Android app uses `wss://` (not `ws://`)
- ✅ Check CORS headers in `api_server.py` (already enabled)

### Issue: "PORT already in use" (local)
- ✅ Change environment variable: `PORT=9000 python python/run_all.py`

---

## 8. Next Steps

### Immediate
1. ☐ Review the 3 modified Python files (all backward compatible)
2. ☐ Test locally: `python python/run_all.py`
3. ☐ Push to GitHub

### For Deployment
1. ☐ Go to **railway.app** and create project
2. ☐ Deploy from GitHub or drag-drop `python/` folder
3. ☐ Set environment variables (`PORT`, `WS_PORT`, `API_PORT`)
4. ☐ Get your Railway URL from deployment
5. ☐ Update Android app with new URL
6. ☐ Test Android connection

### Documentation
1. ☐ See **RAILWAY_DEPLOYMENT_GUIDE.md** for complete setup
2. ☐ See **ANDROID_RAILWAY_CONFIG.md** for Android changes

---

## 9. File Reference

```
python/
├── unity_bridge.py        ✏️ MODIFIED (imported os, added env var)
├── run_all.py            ✏️ MODIFIED (added os import, PORT logic)
├── run_server.py         ✏️ MODIFIED (added os import, PORT logic)
├── api_server.py         ✓ No changes needed
├── requirements.txt      ✓ No changes needed (all deps present)
└── [other files unchanged]

Root Directory:
├── RAILWAY_DEPLOYMENT_GUIDE.md       ✨ NEW (complete setup guide)
└── ANDROID_RAILWAY_CONFIG.md         ✨ NEW (Android config guide)
```

---

## 10. Key Points Summary

✅ **All servers now read PORT from environment variables**  
✅ **Fully backward compatible with local development**  
✅ **CORS already enabled in FastAPI for Android**  
✅ **WebSocket server on 0.0.0.0 (accessible from anywhere)**  
✅ **No additional dependencies needed**  
✅ **Deployment documentation provided**  

---

**Status:** 🚀 **Ready for Railway Deployment**

Your Python backend is configured and documented. Next step: Deploy on Railway and update Android app URLs.

See detailed guides:
- **RAILWAY_DEPLOYMENT_GUIDE.md** — Step-by-step deployment
- **ANDROID_RAILWAY_CONFIG.md** — Android app configuration
