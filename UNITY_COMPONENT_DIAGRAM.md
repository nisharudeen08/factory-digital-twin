# Unity Component Connection Diagram

## 🏗️ Scene Hierarchy Structure

```
Scene: factory_digital twin
│
├── 🎮 GameManager
│   ├── 📜 SimulationManager (Component)
│   │   ├── websocketUrl: "ws://127.0.0.1:8765"
│   │   ├── autoConnect: true
│   │   ├── reconnectDelay: 5.0
│   │   └── spawner: [Reference to MachineSpawner]
│   │
│   └── 🏭 MachineSpawner (Component)
│       ├── simManager: [Reference to SimulationManager]
│       ├── factoryParent: [Transform of FactoryParent]
│       ├── configPath: "python/configs/factory_config.json"
│       ├── machineSpacing: 15.0
│       ├── machineStep: 12.0
│       ├── floorMargin: 10.0
│       ├── targetMachineHeight: 3.0
│       ├── enableAutoSize: true
│       ├── sizeMultiplier: (0.8, 1.0, 0.8)
│       ├── machineGlobalRotation: (0, 0, 0)
│       ├── latheRotationOffset: (0, 90, 0)
│       ├── latheScaleMultiplier: (1, 1, 1)
│       ├── conveyorRotation: (0, 0, 0)
│       ├── conveyorScaleMultiplier: (1, 1, 1)
│       │
│       └── Prefab References:
│           ├── lathePrefab: Assets/prefab/lathe.prefab
│           ├── cncPrefab: Assets/prefab/milling.prefab
│           ├── drillPrefab: [generic]
│           ├── bandSawPrefab: Assets/prefab/band_saw.prefab
│           ├── weldPrefab: [generic]
│           ├── genericPrefab: [simple cube]
│           ├── conveyorPrefab: Assets/prefab/Conveyor.prefab
│           └── floorPrefab: Assets/prefab/floor.prefab
│
├── 🏭 FactoryParent (Empty GameObject)
│   │   [Machines spawned here at runtime by MachineSpawner]
│   │
│   ├── S1_lathe_M1 (MachineVisual)
│   ├── S1_lathe_M2 (MachineVisual)
│   ├── S2_cnc_M1 (MachineVisual)
│   └── ... (more machines)
│
├── 📹 Main Camera
│   └── 🎮 CameraController (Component)
│       ├── autoPositionOnStart: true
│       ├── defaultFOV: 55
│       ├── defaultPitch: 35
│       ├── defaultYaw: 0
│       ├── defaultDist: 40
│       ├── orbitSpeed: 120
│       ├── panSpeed: 0.4
│       ├── zoomSpeed: 8
│       ├── minZoomDist: 3
│       ├── maxZoomDist: 300
│       ├── followFactory: true
│       └── followSmooth: 4
│
├── 🌍 Directional Light
│
└── 🖼️ Canvas (UI - optional)
    └── [UI elements for language toggle, etc.]
```

---

## 🔄 Runtime Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                         PYTHON SERVER                            │
│  simpy + FastAPI + WebSocket                                     │
│  Port: 8765                                                      │
│                                                                  │
│  Sends: {"type":"state_update", "stations":[...]}               │
│  Receives: Simulation config from Android/Unity                 │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket
                              │ ws://127.0.0.1:8765
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    UNITY - SimulationManager                     │
│  - Connects to Python WebSocket                                 │
│  - Receives state updates                                       │
│  - Parses JSON: utilization, queue_length, status, bottleneck   │
│  - Routes data to MachineVisual components                      │
│                                                                  │
│  Methods:                                                        │
│  - ConnectWebSocket()                                           │
│  - ProcessMessage(json)                                         │
│  - UpdateMachines(WSStateUpdate)                                │
│  - RegisterMachine(stationId, machineIndex, MachineVisual)      │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ Calls BuildFactory()
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    UNITY - MachineSpawner                        │
│  - Reads factory_config.json                                    │
│  - Parses StationConfig array                                   │
│  - Expands stations → individual machines                       │
│  - Calculates grid layout                                       │
│  - Spawns floor, machines, conveyor                             │
│  - Adds MachineVisual component to each machine                 │
│  - Registers machines with SimulationManager                    │
│                                                                  │
│  Methods:                                                        │
│  - BuildFactory(json)                                           │
│  - ExtractConfig(json)                                          │
│  - ExpandStations(StationConfig[])                              │
│  - SpawnMachine(MachineEntry, Vector3 pos)                      │
│  - SpawnFloor(cols, rows)                                       │
│  - SpawnEntranceConveyor(cols)                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ Instantiates & Configures
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    UNITY - MachineVisual                         │
│  - Attached to each machine GameObject                          │
│  - Updates visual state based on simulation data                │
│  - Changes material color based on utilization                  │
│  - Shows/hides bottleneck arrow                                 │
│  - Spawns queue boxes                                           │
│  - Displays label with stats                                    │
│                                                                  │
│  Methods:                                                        │
│  - UpdateStatus(util, queue, status, isBottleneck)              │
│  - UpdateState(util, queueLength, isBottleneck, status)         │
│  - RefreshLabel(lang)                                           │
│  - ResolveTargetMaterial()                                      │
│  - PulseArrow() [Coroutine]                                     │
│                                                                  │
│  Color Mapping:                                                  │
│  - Green:  util < 0.15                                          │
│  - Amber:  0.15 ≤ util < 0.30                                   │
│  - Orange: 0.30 ≤ util < 0.40                                   │
│  - Red:    util ≥ 0.40 OR queue ≥ 3 OR isBottleneck             │
│  - Gray:   status == "broken"                                   │
└──────────────────────────────────────────────────────────────────┘
                              │
                              │ Updates transform.position & rotation
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    UNITY - CameraController                      │
│  - Auto-focuses on factory after spawn                          │
│  - Handles user input for orbit/pan/zoom                        │
│  - Smoothly follows factory center                              │
│                                                                  │
│  Methods:                                                        │
│  - FocusOnFactory()                                             │
│  - HandleOrbit()                                                │
│  - HandlePan()                                                  │
│  - HandleZoom()                                                 │
│  - SmoothPivot()                                                │
│  - RefocusAfterRebuild()                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📦 Prefab Structure

### Machine Prefab (lathe, milling, band_saw, etc.)

```
MachinePrefab (e.g., lathe.prefab)
│
├── [Main 3D Model]
│   └── Renderer → Assigned to MachineVisual.bodyRenderer
│
├── MachineVisual (Component) ← ADD THIS
│   ├── stationId: 0 (runtime)
│   ├── machineDisplayName: "Lathe Station"
│   ├── machineTypeName: "Lathe Machine"
│   ├── bodyRenderer: [Main body renderer]
│   ├── label: [auto-created at runtime]
│   ├── bottleneckArrow: [optional arrow object]
│   ├── queueParent: [queueParent prefab reference]
│   ├── queueBoxPrefab: [StationBox prefab]
│   ├── machineIndex: 0 (runtime)
│   ├── numMachinesTotal: 1 (runtime)
│   ├── showLabel: true
│   │
│   └── Materials:
│       ├── matGreen: mat_green
│       ├── matAmber: mat_amber
│       ├── matOrange: mat_orange
│       ├── matRed: mat_red
│       └── matGray: mat_gray
│
└── [Optional Child Objects]
    ├── ControlPanel
    ├── Base
    └── Details
```

### Queue System Prefabs

```
queueParent.prefab
│
└── [Empty GameObject with Transform]
    └── Used as parent for queue box instances
        Queue boxes spawned at runtime:
        - Position: queueParent.position + Vector3.right * i * 0.4


StationBox.prefab (or WIPBox.prefab)
│
└── [Small cube/box visual]
    └── Represents one item in queue
        Instantiated by MachineVisual.UpdateStatus()
```

### Floor Prefab

```
floor.prefab
│
├── [Plane or Cube mesh]
│
├── Renderer → Assigned to FloorManager.floorRenderer
│
└── HeatmapController (Component) ← Optional
    ├── floorRenderer: [self]
    ├── lowUtilizationColor: (0.2, 0.8, 0.2, 0.5)
    └── highUtilizationColor: (0.8, 0.2, 0.2, 0.5)
```

---

## 🎯 Inspector Assignment Map

### Step-by-Step Assignment Order

```
1. Create GameManager
   │
   ├─ Add Component: SimulationManager
   │  └─ Set: websocketUrl = "ws://127.0.0.1:8765"
   │  └─ Set: autoConnect = true
   │  └─ Set: reconnectDelay = 5
   │  └─ spawner: [Leave empty for now]
   │
   └─ Add Component: MachineSpawner
      └─ simManager: [Drag GameManager here]
      └─ factoryParent: [Drag FactoryParent here]
      └─ configPath: "python/configs/factory_config.json"
      └─ Assign all prefabs
      └─ Set grid spacing values

2. Go back to SimulationManager
   └─ spawner: [Drag MachineSpawner component here]

3. Main Camera
   └─ Add Component: CameraController
      └─ Set default values (see Quick Reference)

4. FactoryParent
   └─ Create empty GameObject
   └─ Name: "FactoryParent"
   └─ Position: (0, 0, 0)

5. Each Machine Prefab
   └─ Add Component: MachineVisual
      └─ Assign bodyRenderer
      └─ Create & assign 5 materials
      └─ Assign queueParent prefab
      └─ Assign queueBoxPrefab
      └─ Click "Apply" to save prefab
```

---

## 🔗 Cross-References

```
┌─────────────────────────────────────────────────────────────┐
│                   CIRCULAR REFERENCES                       │
└─────────────────────────────────────────────────────────────┘

SimulationManager.spawner  ──────► MachineSpawner
       ▲                                  │
       │                                  │
       └──────────────────────────────────┘
            (MachineSpawner.simManager)


MachineSpawner ──────► Spawns machines with MachineVisual
       │                      │
       │                      │ Registers via
       │                      ▼
       │              SimulationManager.RegisterMachine()
       │
       └──────────────► Calls BuildFactory(json)
                        which extracts config and
                        instantiates prefabs


CameraController ──────► FocusOnFactory() finds all MachineVisual
       │                        │
       │                        │ Calculates bounds
       │                        │
       └────────────────────────┘
            Sets camera position based on
            factory bounds
```

---

## 🎨 Color Coding Legend

### Machine Status Colors

```
Utilization Level    Color      RGB Values          Material
─────────────────────────────────────────────────────────────
< 15% (Low)         🟢 Green   (0.2, 0.75, 0.3)    mat_green
15-30% (Medium)     🟡 Amber   (1.0, 0.84, 0.2)    mat_amber
30-40% (High)       🟠 Orange  (1.0, 0.55, 0.1)    mat_orange
≥ 40% (Critical)    🔴 Red     (0.85, 0.2, 0.2)    mat_red
Broken/Maintenance  ⚫ Gray    (0.45, 0.45, 0.45)  mat_gray
```

### Queue Length Indicators

```
Queue Count    Visual Representation
─────────────────────────────────────
0              No boxes
1              □ (1 box)
2              □□ (2 boxes)
3              □□□ (3 boxes)
4+             □□□... (spawns more boxes)
```

### Bottleneck Indicator

```
Is Bottleneck    Arrow State
─────────────────────────────────────
true             🔺 Pulsing arrow (scale 1.0 → 1.5)
false            Arrow hidden (inactive)
```

---

## 📊 Factory Config → Unity Mapping

```
JSON Config (factory_config.json)
│
├─ factory_name          → Used in debug logs
├─ shift_hours           → Display in UI (optional)
├─ num_operators         → Display in UI (optional)
├─ language              → Initial language setting
│
└─ stations[] (array)
   │
   └─ Each station:
      │
      ├─ id              → MachineVisual.stationId
      ├─ name            → MachineVisual.stationName
      ├─ name_ta         → MachineVisual.stationNameTa
      ├─ icon            → Selects prefab (lathe, cnc, etc.)
      ├─ num_machines    → How many instances to spawn
      ├─ cycle_time_sec  → Used by Python simulation
      ├─ mtbf_hours      → Used by Python simulation
      ├─ mttr_hours      → Used by Python simulation
      ├─ position_x      → (Optional) Manual X position
      └─ position_z      → (Optional) Manual Z position
```

---

**This diagram shows how all components connect and communicate at runtime.**
