# 🚀 Railway Deployment Checklist

## Pre-Deployment (LOCAL)

- [ ] Python code changes reviewed (see RAILWAY_DEPLOYMENT_SUMMARY.md)
  - [ ] `python/unity_bridge.py` — reads `PORT` env var
  - [ ] `python/run_all.py` — reads `WS_PORT` and `API_PORT`
  - [ ] `python/run_server.py` — reads `PORT` env var

- [ ] Test locally:
  ```bash
  cd python/
  python run_all.py
  # Should see: "server started on ws://0.0.0.0:8765"
  ```

- [ ] All dependencies in `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  # Verify no errors
  ```

- [ ] Git repository updated:
  ```bash
  git add -A
  git commit -m "Configure for Railway deployment"
  git push origin main
  ```

---

## Railway Setup (CLOUD)

### Account & Project
- [ ] Go to **railway.app**
- [ ] Sign up with GitHub
- [ ] Create **New Project**
- [ ] Connect GitHub repo OR drag-drop `python/` folder

### Environment Variables
Set in Railway **Project Settings**:
```
PORT = 8765
WS_PORT = 8765
API_PORT = 8000
```

### Verify Deployment
- [ ] Deploy status: **Green/Success**
- [ ] View logs (Deployments → Latest → Logs)
- [ ] Look for: `"server started on ws://0.0.0.0:xxxx"`

---

## Android App Update

### Get Railway URL
From Railway dashboard:
- **Your URL:** `https://[your-project].up.railway.app`
- **WebSocket:** `wss://[your-project].up.railway.app`

### Update Android Code
Find these files:
- `android/app/src/main/java/.../ApiClient.java`
- `android/app/src/main/java/.../NetworkConfig.java`
- Or search for: `"192.168"` or `"8000"` or `"8765"`

**Replace:**
```java
// OLD - Local development
String API_URL = "http://192.168.1.100:8000";
String WS_URL = "ws://192.168.1.100:8765";

// NEW - Railway production
String API_URL = "https://your-project.up.railway.app";
String WS_URL = "wss://your-project.up.railway.app";
```

**Important:**
- ✅ Use `https://` NOT `http://`
- ✅ Use `wss://` NOT `ws://`
- ✅ Only do this in release/production build
- See **ANDROID_RAILWAY_CONFIG.md** for detailed options

---

## Testing

### Test API Endpoint
```bash
curl https://your-project.up.railway.app/health
# Should return: 200 OK with JSON response
```

### Test WebSocket
From Android Studio terminal or Ubuntu:
```bash
npm install -g wscat
wscat -c wss://your-project.up.railway.app
# Should connect successfully
```

### Test on Device
- [ ] Build Android app with new Railway URL
- [ ] Install APK on physical device
- [ ] Check network logs for successful connection
- [ ] Verify data streams from server

---

## Production Checklist

- [ ] Railway deployment shows GREEN/ACTIVE
- [ ] `/health` endpoint responds with 200
- [ ] WebSocket connects without SSL errors
- [ ] Android app uses HTTPS/WSS URLs
- [ ] No hardcoded `192.168.x.x` in release build
- [ ] Tested on physical Android device (not emulator)
- [ ] Railway logs show active connections
- [ ] Factory config loads correctly

---

## Troubleshooting

| Problem | Check |
|---------|-------|
| "Connection refused" | Is Railway deployment finished? Check logs. |
| "SSL certificate error" | Ensure `https://` not `http://` |
| "WebSocket 403" | Check CORS in `api_server.py` (already enabled) |
| "Timeout" | May take 1-2 min for server to fully start. Retry. |
| "Port in use" (local) | Change port: `PORT=9000 python run_all.py` |

---

## Rollback

If something goes wrong:

1. **Quick fix (Android):** Revert URL to local dev server temporarily
2. **Server rollback:** Railway Dashboard → Deployments → Select previous → Click Revert
3. **Emergency:** Keep local development server running as fallback

---

## Documentation Files

📄 **RAILWAY_DEPLOYMENT_GUIDE.md**  
→ Complete setup guide with all details

📄 **ANDROID_RAILWAY_CONFIG.md**  
→ Multiple Android config options

📄 **RAILWAY_DEPLOYMENT_SUMMARY.md**  
→ Summary of code changes made

---

## Quick Links

- **Railway Docs:** https://docs.railway.app
- **WebSocket Guide:** https://docs.railway.app/guides/websockets
- **Your Project Dashboard:** https://railway.app (after created)

---

## Timeline

**Estimated Total Time: 30-45 minutes**

| Step | Time |
|------|------|
| Local testing (python) | 5 min |
| Railway setup & deploy | 10-15 min |
| Android code update | 10 min |
| Build & test Android APK | 10-15 min |
| Final verification | 5 min |

---

**You're all set! 🎉**

Start with **RAILWAY_DEPLOYMENT_GUIDE.md** for detailed step-by-step instructions.
