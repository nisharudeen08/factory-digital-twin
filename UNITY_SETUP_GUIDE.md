# Unity Setup Guide - Factory Digital Twin

This guide will walk you through setting up the Unity scripts correctly for the factory digital twin project.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Unity Hub installed
- [ ] Unity 2022 LTS installed (with Android Build Support)
- [ ] NativeWebSocket package installed
- [ ] TextMeshPro package installed
- [ ] Project folder structure ready

---

## Step 1: Open Unity Project

1. Open **Unity Hub**
2. Click **Add** → Navigate to: `c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\unity`
3. Wait for Unity to import the project (may take 5-10 minutes first time)
4. Once imported, double-click to open the project

---

## Step 2: Install Required Packages

### 2.1 NativeWebSocket (CRITICAL)

1. Go to **Window** → **Package Manager**
2. Click the **+** button (top left)
3. Select **Add package from git URL**
4. Paste: `https://github.com/endel/NativeWebSocket.git#upm`
5. Click **Add**
6. Wait for installation to complete

### 2.2 TextMeshPro Essentials

1. In **Package Manager**, search for **TextMeshPro**
2. If not installed, click **Install**
3. When prompted, click **Import TMP Essentials**
4. Wait for import to complete

---

## Step 3: Open the Factory Scene

1. In the **Project** window, navigate to: `Assets/Scenes/`
2. Double-click **factory_digital twin.unity** (or **factory.unity**)
3. Wait for the scene to load

---

## Step 4: Configure the Scripts in Hierarchy

### 4.1 Create Empty GameObjects (if not present)

In the **Hierarchy** window, check if these exist. If not, create them:

1. Right-click in Hierarchy → **Create Empty**
2. Rename to: `GameManager`
3. Right-click → **Create Empty**
4. Rename to: `FactoryParent`

### 4.2 Setup SimulationManager

1. Select the **GameManager** GameObject in Hierarchy
2. In **Inspector**, click **Add Component**
3. Search for and add: `SimulationManager`
4. Configure these properties:

```
┌─────────────────────────────────────────────────┐
│ SimulationManager Component                     │
├─────────────────────────────────────────────────┤
│ WebSocket Url: ws://127.0.0.1:8765             │
│ Auto Connect: ✓ (checked)                       │
│ Reconnect Delay: 5                              │
│ Spawner: [Drag MachineSpawner here]            │
└─────────────────────────────────────────────────┘
```

### 4.3 Setup MachineSpawner

1. Select the **GameManager** GameObject (or create separate if preferred)
2. Add Component: `MachineSpawner`
3. Configure these properties:

```
┌─────────────────────────────────────────────────┐
│ MachineSpawner Component                        │
├─────────────────────────────────────────────────┤
│ Sim Manager: [Drag GameManager here]           │
│ Factory Parent: [Drag FactoryParent here]      │
│ Config Path: python/configs/factory_config.json│
│                                                   │
│ Grid Spacing:                                   │
│   Machine Spacing: 15                           │
│   Machine Step: 12                              │
│   Floor Margin: 10                              │
│                                                   │
│ Machine Sizing:                                 │
│   Target Machine Height: 3.0                    │
│   Enable Auto Size: ✓                           │
│   Size Multiplier: (0.8, 1.0, 0.8)             │
│                                                   │
│ Rotation:                                       │
│   Machine Global Rotation: (0, 0, 0)           │
│   Lathe Rotation Offset: (0, 90, 0)            │
│   Lathe Scale Multiplier: (1, 1, 1)            │
│   Conveyor Rotation: (0, 0, 0)                 │
│   Conveyor Scale Multiplier: (1, 1, 1)         │
│                                                   │
│ Prefabs (assign from Assets/prefab/):          │
│   Lathe Prefab: [Drag lathe.prefab]            │
│   Cnc Prefab: [Drag milling.prefab]            │
│   Drill Prefab: [Create or use generic]        │
│   Band Saw Prefab: [Drag band_saw.prefab]      │
│   Weld Prefab: [Create or use generic]         │
│   Generic Prefab: [Create simple cube]         │
│   Conveyor Prefab: [Drag Conveyor.prefab]      │
│   Floor Prefab: [Drag floor.prefab]            │
│                                                   │
│ Debug:                                          │
│   Rebuild Now: ☐ (unchecked)                    │
└─────────────────────────────────────────────────┘
```

### 4.4 Setup CameraController

1. Find **Main Camera** in Hierarchy
2. Add Component: `CameraController`
3. Configure:

```
┌─────────────────────────────────────────────────┐
│ CameraController Component                      │
├─────────────────────────────────────────────────┤
│ Auto Position on Start: ✓                       │
│                                                   │
│ Default View:                                   │
│   Default FOV: 55                               │
│   Default Pitch: 35                             │
│   Default Yaw: 0                                │
│   Default Dist: 40                              │
│                                                   │
│ Orbit Controls:                                 │
│   Orbit Speed: 120                              │
│   Pan Speed: 0.4                                │
│   Zoom Speed: 8                                 │
│   Min Zoom Dist: 3                              │
│   Max Zoom Dist: 300                            │
│                                                   │
│ Smooth Follow:                                  │
│   Follow Factory: ✓                             │
│   Follow Smooth: 4                              │
└─────────────────────────────────────────────────┘
```

### 4.5 Setup FloorManager (Optional)

1. Select **GameManager** GameObject
2. Add Component: `FloorManager`
3. Configure:

```
┌─────────────────────────────────────────────────┐
│ FloorManager Component                          │
├─────────────────────────────────────────────────┤
│ Floor Object: [Drag floor from scene]          │
│ Factory Parent: [Drag FactoryParent here]      │
│                                                   │
│ Floor Settings:                                 │
│   Min Floor Size: 10                            │
│   Machine Spacing: 5                            │
│   Floor Margin: 4                               │
│                                                   │
│ Floor Material: [Optional - assign material]   │
└─────────────────────────────────────────────────┘
```

### 4.6 Setup HeatmapController (Optional)

1. Select the **Floor** GameObject in scene
2. Add Component: `HeatmapController`
3. Configure:

```
┌─────────────────────────────────────────────────┐
│ HeatmapController Component                     │
├─────────────────────────────────────────────────┤
│ Floor Renderer: [Drag floor Renderer here]     │
│                                                   │
│ Low Utilization Color: (0.2, 0.8, 0.2, 0.5)    │
│ High Utilization Color: (0.8, 0.2, 0.2, 0.5)   │
└─────────────────────────────────────────────────┘
```

---

## Step 5: Setup MachineVisual Prefab

The `MachineVisual` script goes on each machine prefab:

### 5.1 For Each Machine Prefab (lathe, milling, band_saw, etc.)

1. In **Project** window, navigate to `Assets/prefab/`
2. Click on **lathe.prefab**
3. In **Inspector**, click **Add Component**
4. Search and add: `MachineVisual`
5. Configure:

```
┌─────────────────────────────────────────────────┐
│ MachineVisual Component                         │
├─────────────────────────────────────────────────┤
│ Station ID: 0 (default - set at runtime)       │
│ Machine Display Name: [Leave empty]            │
│ Machine Type Name: Lathe Machine               │
│ Body Renderer: [Drag the main body renderer]   │
│ Status Text: [Will be created at runtime]      │
│ Bottleneck Arrow: [Create/Drag arrow object]   │
│ Queue Parent: [Drag queueParent.prefab]        │
│ Queue Box Prefab: [Drag StationBox.prefab]     │
│                                                   │
│ Machine Index: 0 (set at runtime)              │
│ Num Machines Total: 1 (set at runtime)         │
│ Show Label: ✓                                   │
│                                                   │
│ Materials:                                      │
│   Mat Green: [Create green material]           │
│   Mat Amber: [Create amber material]           │
│   Mat Orange: [Create orange material]         │
│   Mat Red: [Create red material]               │
│   Mat Gray: [Create gray material]             │
└─────────────────────────────────────────────────┘
```

### 5.2 Create Status Materials

1. In **Project** window, right-click in `Assets/Materials/` folder
2. Create → **Material**
3. Name it: `mat_green`
4. Set Albedo color: `(0.2, 0.75, 0.3)` - Green
5. Repeat for other colors:

```
mat_green:   R:0.2  G:0.75 B:0.3  (Green - low util)
mat_amber:   R:1.0  G:0.84 B:0.2  (Amber - medium util)
mat_orange:  R:1.0  G:0.55 B:0.1  (Orange - high util)
mat_red:     R:0.85 G:0.2  B:0.2  (Red - critical)
mat_gray:    R:0.45 G:0.45 B:0.45 (Gray - broken)
```

6. Assign these materials to the MachineVisual component on each prefab

### 5.3 Apply to All Prefabs

Repeat Step 5.1 for these prefabs:
- [ ] lathe.prefab
- [ ] milling.prefab
- [ ] band_saw.prefab
- [ ] Conveyor.prefab (if needed)
- [ ] Any other machine prefabs

**Click "Apply" after configuring each prefab** to save changes.

---

## Step 6: Setup Queue System

### 6.1 Queue Parent Setup

1. In **Hierarchy**, create Empty GameObject
2. Name it: `QueueParent`
3. Add a small visual marker (optional):
   - Create → 3D Object → Cube
   - Scale: (0.1, 0.1, 0.1)
   - Make it a child of QueueParent
4. In **Project**, right-click `Assets/prefab/`
5. Drag **QueueParent** from Hierarchy to create prefab
6. Delete QueueParent from scene (it will be instantiated at runtime)

### 6.2 Queue Box Prefab

1. Use existing **StationBox.prefab** or **WIPBox.prefab** from `Assets/prefab/`
2. This will represent each item in queue

---

## Step 7: Configure WebSocket URL

### For Local Testing (Same Computer)

In **SimulationManager** component:
```
WebSocket Url: ws://127.0.0.1:8765
```

### For Network Testing (Different Devices)

1. Find your PC's IP address:
   - Open Command Prompt
   - Type: `ipconfig`
   - Note IPv4 Address (e.g., 192.168.1.100)

2. In **SimulationManager**, update:
```
WebSocket Url: ws://192.168.1.100:8765
```

---

## Step 8: Verify Python Server

Before testing Unity, ensure Python server is running:

1. Open Command Prompt
2. Navigate to Python folder:
   ```
   cd c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python
   ```
3. Start server:
   ```
   python run_server.py
   ```
4. Verify you see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     WebSocket server on ws://0.0.0.0:8765
   ```

---

## Step 9: Test in Unity

1. Make sure Python server is running
2. In Unity, press **Play** button (top center)
3. Check **Console** window for messages:

**Expected Console Output:**
```
[Spawner] Start load config from: python/configs/factory_config.json
[Spawner] Config file found. Size=XXXX chars
[Spawner] Building XX machines from X stations
[Camera] Focused: center=(x,y,z) dist=XX.X machines=XX
[SimManager] Connected to Python backend!
```

4. In **Scene** or **Game** view, you should see:
   - Machines arranged in a grid
   - Floor underneath
   - Machines colored based on status
   - Labels above machines showing utilization and queue

---

## Step 10: Test Controls

### Camera Controls

| Input | Action |
|-------|--------|
| **Right Mouse Button + Drag** | Orbit around factory |
| **Middle Mouse Button + Drag** | Pan camera |
| **Scroll Wheel** | Zoom in/out |
| **W/S Keys** | Zoom in/out |

### Verify Machine Colors

Machines should show different colors based on utilization:
- 🟢 **Green**: Low utilization (<15%)
- 🟡 **Amber**: Medium utilization (15-30%)
- 🟠 **Orange**: High utilization (30-40%)
- 🔴 **Red**: Critical/Bottleneck (>40%)
- ⚫ **Gray**: Broken/Maintenance

---

## 🔧 Troubleshooting

### Issue: "WebSocket connection failed"

**Solution:**
1. Verify Python server is running
2. Check WebSocket URL in SimulationManager
3. Check Windows Firewall - allow port 8765
4. Try: `netsh advfirewall firewall add rule name="DigitalTwin_WS" dir=in action=allow protocol=TCP localport=8765`

### Issue: "Config file not found"

**Solution:**
1. Verify path in MachineSpawner: `python/configs/factory_config.json`
2. Check file exists: `c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python\configs\factory_config.json`
3. Path is relative to Unity project root

### Issue: "Machines not showing"

**Solution:**
1. Check MachineSpawner has prefabs assigned
2. Verify FactoryParent transform exists
3. Check Console for errors
4. Ensure config JSON has stations array

### Issue: "Tamil text shows as boxes"

**Solution:**
1. Download Noto Sans Tamil font
2. Create TMP Font Asset (see digital_twin.md section 4.3)
3. Assign Tamil font in MachineVisual script

### Issue: "NativeWebSocket not found"

**Solution:**
1. Reinstall package from git URL
2. Restart Unity
3. Check Assets/Plugins folder exists

### Issue: "MachineVisual not updating"

**Solution:**
1. Verify Body Renderer is assigned
2. Check materials are assigned
3. Ensure Station ID matches config
4. Check WebSocket is connected (Console logs)

---

## 📊 Final Checklist

Before considering setup complete, verify:

- [ ] NativeWebSocket package installed
- [ ] TextMeshPro installed
- [ ] Scene opens without errors
- [ ] SimulationManager component added and configured
- [ ] MachineSpawner component added and configured
- [ ] CameraController on Main Camera
- [ ] All prefabs have MachineVisual component
- [ ] Materials assigned (green, amber, orange, red, gray)
- [ ] Python server running
- [ ] WebSocket connects (check Console)
- [ ] Machines appear in scene
- [ ] Camera focuses on factory
- [ ] Machine colors update based on simulation

---

## 🎯 Quick Reference - Component Assignments

```
GameManager
├── SimulationManager
│   ├── WebSocket Url: ws://127.0.0.1:8765
│   └── Spawner: [MachineSpawner]
│
└── MachineSpawner
    ├── Sim Manager: [SimulationManager]
    ├── Factory Parent: [FactoryParent Transform]
    ├── Config Path: python/configs/factory_config.json
    └── All Prefabs Assigned

Main Camera
└── CameraController
    └── Auto Position: ✓

Each Machine Prefab
└── MachineVisual
    ├── Body Renderer: [Assigned]
    ├── Materials: [All 5 colors]
    └── Queue Parent: [Assigned]
```

---

## 📞 Next Steps

After Unity setup is complete:

1. **Test with Python Server**: Run simulation and watch real-time updates
2. **Integrate with Android**: Connect Android app for unified control
3. **Customize Factory**: Edit `factory_config.json` for different layouts
4. **Add Features**: Extend with heatmaps, analytics, etc.

---

**Setup Time**: 30-60 minutes (first time)
**Difficulty**: Intermediate
**Unity Version**: 2022 LTS recommended
