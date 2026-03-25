# Antigravity IDE — Pre-Flight Requirements
### Digital Twin: Cell Factory (Python + Android + Unity)

---

## ✅ CHECKLIST OVERVIEW

| # | Category | Item | Status |
|---|----------|------|--------|
| 1 | Software | Python 3.10+ installed | ☐ |
| 2 | Software | Android Studio (latest) installed | ☐ |
| 3 | Software | Unity 2022 LTS installed | ☐ |
| 4 | Software | Antigravity IDE installed | ☐ |
| 5 | Software | Git installed | ☐ |
| 6 | Python | Core packages installed | ☐ |
| 7 | Android | SDK API 31+ ready | ☐ |
| 8 | Android | Kotlin plugin enabled | ☐ |
| 9 | Android | Device / Emulator ready | ☐ |
| 10 | Unity | TextMeshPro package installed | ☐ |
| 11 | Unity | NativeWebSocket package installed | ☐ |
| 12 | Unity | Noto Sans Tamil font downloaded | ☐ |
| 13 | Network | Local IP address noted | ☐ |
| 14 | Network | All devices on same Wi-Fi | ☐ |
| 15 | Folder | Root project folder created | ☐ |

---

## 1. SOFTWARE INSTALLATION

### 1.1 Python 3.10+
```bash
# Check version
python --version   # must show 3.10.x or higher

# Download from
https://www.python.org/downloads/
```
> **Why:** SimPy, FastAPI, asyncio WebSocket all require Python 3.10+.

---

### 1.2 Android Studio
```
Download: https://developer.android.com/studio
Version:  Hedgehog (2023.1.1) or newer
```
During install, ensure these are checked:
- Android SDK
- Android SDK Platform (API 31 minimum)
- Android Virtual Device (AVD)

---

### 1.3 Unity 2022 LTS
```
Download via: Unity Hub → Installs → Add → 2022.x LTS
```
During install, add these modules:
- Android Build Support
- Android SDK & NDK Tools
- OpenJDK

---

### 1.4 Git
```bash
# Check if installed
git --version

# Download from
https://git-scm.com/downloads
```

---

## 2. PYTHON PACKAGES

Run this command **before** pasting any prompt into Antigravity IDE:

```bash
pip install simpy fastapi uvicorn websockets numpy scipy paho-mqtt asyncua
```

### Verify each package:
```bash
python -c "import simpy; print('SimPy OK:', simpy.__version__)"
python -c "import fastapi; print('FastAPI OK:', fastapi.__version__)"
python -c "import numpy; print('NumPy OK:', numpy.__version__)"
python -c "import scipy; print('SciPy OK:', scipy.__version__)"
```

All four must print OK before proceeding.

### Full requirements.txt (reference):
```
simpy>=4.1.1
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
websockets>=12.0
numpy>=1.26.0
scipy>=1.11.0
paho-mqtt>=1.6.1
asyncua>=1.0.6
python-multipart>=0.0.6
```

---

## 3. ANDROID STUDIO SETUP

### 3.1 SDK Configuration
```
Android Studio → Settings → SDK Manager
Ensure installed:
  ✓ Android 12 (API 31)
  ✓ Android 13 (API 33)  ← recommended target
  ✓ Android SDK Build-Tools 33.0.0+
```

### 3.2 Kotlin Plugin
```
Android Studio → Settings → Plugins → Kotlin
Version: 1.9.0 or newer
```

### 3.3 Gradle Version
In `build.gradle` (Project level), ensure:
```gradle
classpath 'com.android.tools.build:gradle:8.1.0'
```

### 3.4 Required Dependencies
These go in `app/build.gradle` — Antigravity IDE will generate this,
but confirm these versions are available:
```gradle
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
implementation 'com.squareup.okhttp3:okhttp:4.12.0'
implementation 'androidx.room:room-runtime:2.6.0'
implementation 'org.java-websocket:Java-WebSocket:1.5.4'
implementation 'androidx.navigation:navigation-fragment-ktx:2.7.5'
```

### 3.5 AndroidManifest.xml — CRITICAL SETTING
Without this, Android 9+ **blocks all HTTP connections** to Python:
```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```
> Add this line manually to your AndroidManifest.xml after the prompt generates the project.

---

## 4. UNITY SETUP

### 4.1 TextMeshPro
```
Unity Editor → Window → Package Manager
→ Search: TextMeshPro
→ Install version 3.0.6 or newer
→ When prompted: Import TMP Essentials  ← click YES
```

### 4.2 NativeWebSocket (for Unity ↔ Python communication)
```
Unity Editor → Window → Package Manager
→ Click "+" → Add package from Git URL
→ Paste: https://github.com/endel/NativeWebSocket.git#upm
→ Click Add
```

### 4.3 Noto Sans Tamil Font
```
1. Download from:
   https://fonts.google.com/noto/specimen/Noto+Sans+Tamil

2. Extract the ZIP — find NotoSansTamil-Regular.ttf

3. Copy into Unity project:
   Assets/FactoryDigitalTwin/Fonts/NotoSansTamil-Regular.ttf

4. Create Tamil Font Asset:
   Window → TextMeshPro → Font Asset Creator
     Font Source:       NotoSansTamil-Regular.ttf
     Sampling Point:    90
     Atlas Resolution:  4096 × 4096   ← Tamil needs large atlas
     Character Set:     Custom Range
     Custom Range:      0B80-0BFF     ← Tamil Unicode block
     Render Mode:       SDFAA
   → Click Generate Font Atlas → Save As: NotoSansTamil_SDF
```

> **Important:** Tamil characters will show as empty boxes without this step.

---

## 5. NETWORK PREPARATION

### 5.1 Find Your Local IP Address

**Windows:**
```cmd
ipconfig
# Look for: IPv4 Address . . . . . : 192.168.x.x
```

**Mac / Linux:**
```bash
ifconfig | grep "inet "
# Look for: inet 192.168.x.x
```

Write it down — you will need it in both Android and Unity:
```
My Server IP: ________________
Python API URL: http://________________:8000
WebSocket URL: ws://________________:8765
```

### 5.2 Firewall Rule (Windows only)
Python's FastAPI server needs port 8000 open:
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="DigitalTwin_Python" ^
  dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="DigitalTwin_WS" ^
  dir=in action=allow protocol=TCP localport=8765
```

### 5.3 Same Wi-Fi Network Check
All three must be on the same network:
```
✓ Development laptop running Python server
✓ Android phone/tablet running the app
✓ Unity tablet showing 3D view
```
> If using an emulator instead of a real phone, use `10.0.2.2` instead of your IP.

---

## 6. PROJECT FOLDER STRUCTURE

Create this folder manually **before** pasting into Antigravity IDE:

```
factory_digital_twin/
  python/
    configs/
  android/
  unity/
  configs/
```

**Windows:**
```cmd
mkdir factory_digital_twin\python\configs
mkdir factory_digital_twin\android
mkdir factory_digital_twin\unity
mkdir factory_digital_twin\configs
```

**Mac / Linux:**
```bash
mkdir -p factory_digital_twin/{python/configs,android,unity,configs}
```

---

## 7. ANTIGRAVITY IDE WORKSPACE SETTINGS

Before pasting the mega prompt, configure Antigravity IDE:

```
Language Model:     GPT-4 / Claude (highest available)
Max Output Tokens:  Set to MAXIMUM (prompt generates 17 files)
Temperature:        0.2  ← lower = more consistent code
Code Mode:          ON
Auto-save:          ON
```

> If Antigravity IDE has a **context window limit warning**, split the
> prompt at Part D (API server) and use the follow-up prompts.

---

## 8. AFTER THE PROMPT RUNS — VERIFICATION ORDER

Run these checks in **this exact order**:

### Step 1 — Verify Python math engine
```bash
cd factory_digital_twin/python
python -c "from math_engine import calc_bni, run_monte_carlo, identify_bottleneck; print('Math engine OK')"
```

### Step 2 — Start Python server
```bash
python run_server.py
# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     WebSocket server on ws://0.0.0.0:8765
# INFO:     Simulation engine ready
```

### Step 3 — Test API from browser
```
Open browser → http://localhost:8000/health
Expected: { "status": "ok", "mode": "static", "last_sim_time": null }
```

### Step 4 — Test simulation endpoint
```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"factory_type":"lathe","demand":200,"operators":2,"shift_hours":8,"machine_condition":"average"}'
# Expected: JSON with throughput, bottleneck_station_id, bni_scores
```

### Step 5 — Open Android in Android Studio
```
File → Open → factory_digital_twin/android
Wait for Gradle sync to complete (2–5 min first time)
Run on device/emulator
Enter server IP when prompted
```

### Step 6 — Open Unity
```
Unity Hub → Open → factory_digital_twin/unity
Open Scenes/FactoryScene
Press Play
WebSocket should connect and machines should start showing colors
```

---

## 9. COMMON FIRST-RUN ERRORS

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: simpy` | Packages not installed | Run `pip install simpy` |
| `Address already in use: 8000` | Old server still running | Kill it: `pkill -f uvicorn` |
| Android: `CLEARTEXT not permitted` | Manifest missing flag | Add `usesCleartextTraffic="true"` |
| Unity: Tamil shows as boxes | Font asset not created | Follow Section 4.3 fully |
| Unity: WebSocket never connects | Wrong IP in SimulationManager | Update IP string in Inspector |
| `BNI always returns same station` | Lq_max calculated wrong | Use follow-up Debug Prompt D1 |

---

## 10. QUICK REFERENCE CARD

```
╔══════════════════════════════════════════════════════╗
║          DIGITAL TWIN — QUICK REFERENCE              ║
╠══════════════════════════════════════════════════════╣
║  Python server start:   python run_server.py         ║
║  API health check:      http://localhost:8000/health ║
║  WebSocket address:     ws://[YOUR-IP]:8765          ║
║  Android connect IP:    [YOUR-IP]:8000               ║
║  Unity WS URL:          ws://[YOUR-IP]:8765          ║
╠══════════════════════════════════════════════════════╣
║  BNI Formula:                                        ║
║  0.5×U + 0.3×(Lq/Lq_max) + 0.2×(cv²/cv²_max)       ║
╠══════════════════════════════════════════════════════╣
║  Kingman VUT:                                        ║
║  Wq = (ca²+cs²)/2 × ρ/(1−ρ) × 1/μ                  ║
╠══════════════════════════════════════════════════════╣
║  Monte Carlo: 10,000 trials, numpy vectorised        ║
║  Replications: 30 runs, 95% CI = x̄ ± t×s/√30       ║
╚══════════════════════════════════════════════════════╝
```

---

*Complete this checklist top to bottom before opening Antigravity IDE.*
*All 15 items must be checked before pasting the mega prompt.*