# Android App: Railway Server Configuration

## Quick Config Update

### TL;DR - Two Variables to Update

Before deployment, update your Android app's network configuration with your Railway URL.

**Find these files in your Android project:**
- `android/app/src/main/java/com/factory/*/ApiClient.java`
- `android/app/src/main/java/com/factory/*/NetworkConfig.java`
- `android/app/src/main/java/com/factory/*/Constants.java`
- Any Retrofit/OkHttp client setup file

### Option 1: Hardcoded URL (Simple)

Replace all instances of your local IP:

```java
// ❌ BEFORE - Local Development
public static final String API_BASE_URL = "http://192.168.1.100:8000";
public static final String WEBSOCKET_URL = "ws://192.168.1.100:8765";

// ✅ AFTER - Railway Production
public static final String API_BASE_URL = "https://your-project.up.railway.app";
public static final String WEBSOCKET_URL = "wss://your-project.up.railway.app";
```

### Option 2: Build Variant Config (Better)

Use BuildConfig to switch based on debug/release:

```java
public class ApiConfig {
    public static String getApiBaseUrl() {
        if (BuildConfig.DEBUG) {
            return "http://192.168.1.100:8000";  // Local development
        } else {
            return "https://your-project.up.railway.app";  // Railway production
        }
    }
    
    public static String getWebSocketUrl() {
        if (BuildConfig.DEBUG) {
            return "ws://192.168.1.100:8765";
        } else {
            return "wss://your-project.up.railway.app";
        }
    }
}
```

### Option 3: Runtime Configuration (Most Flexible)

Store URL in SharedPreferences/DataStore:

```java
// SharedPreferences
SharedPreferences prefs = context.getSharedPreferences("app_config", Context.MODE_PRIVATE);
String apiUrl = prefs.getString(
    "api_url", 
    "https://your-project.up.railway.app"  // default
);

// Usage
Retrofit retrofit = new Retrofit.Builder()
    .baseUrl(apiUrl)
    .addConverterFactory(GsonConverterFactory.create())
    .build();
```

## Common Server URL Patterns

| Scenario | HTTP API | WebSocket |
|----------|----------|-----------|
| Local development | `http://192.168.1.X:8000` | `ws://192.168.1.X:8765` |
| Railway production | `https://factory-twin.up.railway.app` | `wss://factory-twin.up.railway.app` |
| Heroku alternate | `https://factory-twin.herokuapp.com` | `wss://factory-twin.herokuapp.com` |

## Code Search: Finding Network Config

### Search for these patterns in your Android project:

```bash
# Using grep (terminal)
grep -r "api_url\|API_URL\|192.168" android/app/src/main/java/

# Using Android Studio Find:
Ctrl+Shift+F (Windows/Linux) or Cmd+Shift+F (Mac)
Search for: "192.168" or "8000" or "8765"
```

## WebSocket Configuration

If using OkHttp or custom WebSocket client:

```java
// OkHttp3 WebSocket
OkHttpClient client = new OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .build();

Request request = new Request.Builder()
    .url("wss://your-project.up.railway.app")  // Note: wss://, not ws://
    .build();

WebSocket ws = client.newWebSocket(request, new WebSocketListener() {
    @Override
    public void onOpen(WebSocket webSocket, Response response) {
        Log.d("WS", "Connected to Railway!");
    }
    // ... handle messages
});
```

## HTTPS/WSS Certificate Validation

Railway provides valid SSL certificates (auto-managed). Your Android app should:

✅ **DO:** Trust Railway's certificates (automatic with standard AndroidHttpClient)

❌ **DON'T:** Disable certificate validation in production

```java
// ❌ WRONG - Never do this in production!
if (BuildConfig.DEBUG) only:
    // Disable SSL validation (dev only)
}

// ✅ CORRECT
// Use standard OkHttpClient - Railway certificates are valid
OkHttpClient client = new OkHttpClient.Builder()
    // Default SSL validation is enabled
    .build();
```

## Testing Connection Before Release

### Manual Test in Android Studio:

```kotlin
// In a test activity or startup check
GlobalScope.launch {
    try {
        val response = httpClient.get("https://your-project.up.railway.app/health")
            .execute()
        Log.d("Server Check", "Status: ${response.statusCode}")  // Should see 200
    } catch (e: Exception) {
        Log.e("Server Check", "Failed: ${e.message}")
    }
}
```

### Check in Railway Logs:
1. Go to railway.app → Your Project → Deployments
2. Click latest deployment
3. View **Logs** tab
4. Search for your Android app's user-agent or IP

## Rollback Plan

If production breaks:

1. **Quick fix:** Update Android build to use alternative URL (if available)
2. **Emergency revert:** In Railway dashboard, click "Revert" on previous deployment
3. **Local fallback:** Keep local dev server running as backup

## Checklist Before Release

- [ ] Railway deployment is live and `/health` returns 200
- [ ] Android app URLs updated to `https://` and `wss://`
- [ ] SSL certificate validation is enabled (default)
- [ ] Tested on physical Android device (not just emulator)
- [ ] Network requests succeed with Railway URL
- [ ] WebSocket connection stabilizes after initial connection
- [ ] No hardcoded local IPs (192.168.x.x) in release build
- [ ] Retrofit/OkHttp timeouts are reasonable (30+ seconds)

## Need Help?

### Common Quick Fixes

| Error | Fix |
|-------|-----|
| `ERR_NAME_NOT_RESOLVED` | Check Railway URL spelling |
| `SSL_HANDSHAKE_FAILURE` | Ensure `https://` not `http://` |
| `Connection timeout` | Railway server may be inactive; check logs |
| `401/403 Unauthorized` | Check CORS setup in `api_server.py` |
| `WebSocket upgrade failed` | Ensure using `wss://` not `ws://` |

### Resources

- Android Networking: https://developer.android.com/develop/connectivity
- Retrofit: https://square.github.io/retrofit/
- OkHttp: https://square.github.io/okhttp/
- Railway WebSockets: https://docs.railway.app/guides/websockets
