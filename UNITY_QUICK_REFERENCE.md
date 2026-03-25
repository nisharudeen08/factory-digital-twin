# Unity Quick Setup Reference Card

## 🎯 Critical Script Connections

```
┌─────────────────────────────────────────────────────────────────┐
│                    HIERARCHY STRUCTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GameManager (Empty GameObject)                                │
│  ├── SimulationManager (Component)                             │
│  │   ├── WebSocket Url: ws://127.0.0.1:8765                   │
│  │   ├── Auto Connect: ✓                                       │
│  │   └── Spawner: [MachineSpawner]                            │
│  │                                                             │
│  └── MachineSpawner (Component)                                │
│      ├── Sim Manager: [SimulationManager]                     │
│      ├── Factory Parent: [FactoryParent Transform]            │
│      ├── Config Path: python/configs/factory_config.json      │
│      └── Prefabs: [Drag all prefabs here]                     │
│                                                                 │
│  FactoryParent (Empty GameObject)                              │
│  └── [Machines spawned here at runtime]                        │
│                                                                 │
│  Main Camera                                                   │
│  └── CameraController (Component)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 Component Inspector Settings

### SimulationManager
```
WebSocket Url:      ws://127.0.0.1:8765
Auto Connect:       ☑ ✓
Reconnect Delay:    5
Spawner:            [Drag MachineSpawner here]
```

### MachineSpawner
```
Sim Manager:        [Drag GameManager here]
Factory Parent:     [Drag FactoryParent here]
Config Path:        python/configs/factory_config.json

[Grid Spacing]
Machine Spacing:    15
Machine Step:       12
Floor Margin:       10

[Prefabs - Drag from Assets/prefab/]
Lathe Prefab:       lathe.prefab
Cnc Prefab:         milling.prefab
Drill Prefab:       [generic or create]
Band Saw Prefab:    band_saw.prefab
Weld Prefab:        [generic or create]
Generic Prefab:     [create cube]
Conveyor Prefab:    Conveyor.prefab
Floor Prefab:       floor.prefab
```

### CameraController (on Main Camera)
```
Auto Position on Start:  ☑ ✓

[Default View]
Default FOV:        55
Default Pitch:      35
Default Yaw:        0
Default Dist:       40

[Orbit Controls]
Orbit Speed:        120
Pan Speed:          0.4
Zoom Speed:         8
Min Zoom Dist:      3
Max Zoom Dist:      300

[Smooth Follow]
Follow Factory:     ☑ ✓
Follow Smooth:      4
```

### MachineVisual (on each machine prefab)
```
Station ID:         0 (set at runtime)
Machine Display Name: [leave empty]
Machine Type Name:  [e.g., "Lathe Machine"]
Body Renderer:      [Drag main body renderer]
Status Text:        [auto-created]
Bottleneck Arrow:   [create/drag arrow]
Queue Parent:       [Drag queueParent.prefab]
Queue Box Prefab:   [Drag StationBox.prefab]

Machine Index:      0 (runtime)
Num Machines Total: 1 (runtime)
Show Label:         ☑ ✓

[Materials - Create in Assets/Materials/]
Mat Green:          mat_green (R:0.2 G:0.75 B:0.3)
Mat Amber:          mat_amber (R:1.0 G:0.84 B:0.2)
Mat Orange:         mat_orange (R:1.0 G:0.55 B:0.1)
Mat Red:            mat_red (R:0.85 G:0.2 B:0.2)
Mat Gray:           mat_gray (R:0.45 G:0.45 B:0.45)
```

---

## 🎨 Material Colors (RGB)

| Material | Red | Green | Blue | Alpha | Purpose |
|----------|-----|-------|------|-------|---------|
| mat_green | 0.2 | 0.75 | 0.3 | 1.0 | Low utilization |
| mat_amber | 1.0 | 0.84 | 0.2 | 1.0 | Medium utilization |
| mat_orange | 1.0 | 0.55 | 0.1 | 1.0 | High utilization |
| mat_red | 0.85 | 0.2 | 0.2 | 1.0 | Critical/Bottleneck |
| mat_gray | 0.45 | 0.45 | 0.45 | 1.0 | Broken/Maintenance |

---

## 🚀 Quick Start Sequence

```
1. Open Unity Project
   ↓
2. Install NativeWebSocket (Package Manager → + → Git URL)
   ↓
3. Open Scene: Assets/Scenes/factory_digital twin.unity
   ↓
4. Create GameObjects: GameManager, FactoryParent
   ↓
5. Add Components to GameManager:
   - SimulationManager
   - MachineSpawner
   ↓
6. Add Component to Main Camera:
   - CameraController
   ↓
7. Configure all components (see settings above)
   ↓
8. Add MachineVisual to each prefab
   ↓
9. Create and assign materials
   ↓
10. Start Python server: cd python && python run_server.py
    ↓
11. Press Play in Unity
```

---

## 🎮 Camera Controls

| Input | Action |
|-------|--------|
| 🖱️ **Right Button + Drag** | Orbit around factory |
| 🖱️ **Middle Button + Drag** | Pan camera |
| 🖱️ **Scroll Wheel** | Zoom in/out |
| ⌨️ **W / S Keys** | Zoom in/out |

---

## 📡 WebSocket URLs

| Scenario | URL |
|----------|-----|
| Local (same PC) | `ws://127.0.0.1:8765` |
| Network (different device) | `ws://192.168.x.x:8765` |
| Android Emulator | `ws://10.0.2.2:8765` |

---

## ✅ Verification Checklist

```
☐ NativeWebSocket installed
☐ TextMeshPro installed
☐ Scene opens without errors
☐ GameManager has SimulationManager + MachineSpawner
☐ FactoryParent exists
☐ Main Camera has CameraController
☐ All prefabs have MachineVisual component
☐ Materials created and assigned (5 colors)
☐ Python server running (check console)
☐ WebSocket connects (Console shows "Connected")
☐ Machines appear in scene
☐ Camera focuses on factory
☐ Machine colors update in real-time
```

---

## 🐛 Common Errors & Fixes

| Error | Fix |
|-------|-----|
| `WebSocket connection failed` | Start Python server, check firewall |
| `Config file not found` | Verify path: `python/configs/factory_config.json` |
| `Machines not showing` | Assign prefabs in MachineSpawner |
| `NativeWebSocket not found` | Reinstall from git URL |
| `Tamil text shows boxes` | Create TMP Tamil font asset |
| `MachineVisual not updating` | Assign Body Renderer, check materials |

---

## 📁 File Locations

```
Unity Project Root:
  c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\unity\

Scripts:
  Assets/Scripts/SimulationManager.cs
  Assets/Scripts/MachineSpawner.cs
  Assets/Scripts/MachineVisual.cs
  Assets/Scripts/CameraController.cs
  Assets/Scripts/FloorManager.cs
  Assets/Scripts/HeatmapController.cs

Prefabs:
  Assets/prefab/lathe.prefab
  Assets/prefab/milling.prefab
  Assets/prefab/band_saw.prefab
  Assets/prefab/floor.prefab
  Assets/prefab/Conveyor.prefab

Scenes:
  Assets/Scenes/factory_digital twin.unity
  Assets/Scenes/factory.unity

Config:
  python/configs/factory_config.json
```

---

## 🔧 Python Server Commands

```bash
# Navigate to Python folder
cd c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python

# Start server
python run_server.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     WebSocket server on ws://0.0.0.0:8765
```

---

**Print this card for quick reference while setting up!**
