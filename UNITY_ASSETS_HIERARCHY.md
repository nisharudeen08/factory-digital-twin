# Unity Assets Hierarchy Structure

**Project:** Factory Digital Twin  
**Generated:** March 20, 2026  
**Root:** `unity/Assets/`

---

## Complete Asset Tree

```
Assets/
├── 📁 Editor/
│   └── FactorySetupEditor.cs                  [Auto-setup tool for scene hierarchy]
│
├── 📁 Industrial_Zone_Modular_Pack/           [Complete industrial environment pack]
│   ├── 📁 Models/
│   │   ├── Industrial_Zone_Canal.fbx
│   │   ├── Industrial_Zone_Construction_Set.fbx
│   │   ├── Industrial_Zone_Factory_Old_Set.fbx
│   │   ├── Industrial_Zone_Factory_Set.fbx
│   │   ├── Industrial_Zone_Hangar_Concrete.fbx
│   │   ├── Industrial_Zone_Hangar_Rounded.fbx
│   │   ├── Industrial_Zone_Hangar_Wooden.fbx
│   │   ├── Industrial_Zone_Props.fbx
│   │   ├── Industrial_Zone_Road_Pavement.fbx
│   │   └── Industrial_Zone_Tiles_And_Walls.fbx
│   ├── 📁 Prefabs/
│   │   ├── wall_02.prefab
│   │   └── Wooden_box_v1_LD2.prefab
│   ├── 📁 Textures/
│   │   ├── Tiles_Walls/
│   │   ├── Concrete_wall/
│   │   ├── Hangar_Concrete/
│   │   ├── Hangar_Rounded/
│   │   ├── Hangar_Wooden/
│   │   ├── Factory_Old/
│   │   ├── Factory_Small/
│   │   ├── Ground_Textures/
│   │   ├── Props/
│   │   └── Canal/
│   ├── 📁 Scenes/
│   │   ├── Industrial_Zone.unity
│   │   └── Industrial_ZoneSettings.lighting
│   ├── 📁 Misc/ (Post-Processing, FPS Controller)
│   ├── 📁 Terrains/
│   ├── 📁 Pipelines/
│   └── README.TXT
│
├── 📁 RPG_FPS_game_assets_industrial/        [Game asset library]
│   ├── Assets_showcase_scene.unity            [Showcase demo scene]
│   ├── Map_v1.unity
│   ├── 📁 Textures/
│   │   ├── Asphalt/
│   │   ├── Concrete_wall/
│   │   ├── Grass/
│   │   ├── Skyboxes/
│   │   └── Transparent/
│   ├── 📁 Buildings/ (Industrial)
│   ├── 📁 Barrels/ (v2, v3)
│   ├── 📁 Boxes/ (Wooden boxes)
│   ├── 📁 Containers/
│   ├── 📁 Dumpsters/
│   ├── 📁 Fences/
│   ├── 📁 Oil_tanks/
│   ├── 📁 Other_props/
│   └── 📁 Particles/
│
├── 📁 Materials/                              [State-based machine materials]
│   ├── brokenMat.mat                          [Machine broken/error state]
│   ├── idleMat.mat                            [Machine idle state]
│   ├── maintenanceMat.mat                     [Machine in maintenance]
│   ├── runningMat.mat                         [Machine actively running]
│   ├── Mat_Floor.mat                          [Factory floor material]
│   └── 📁 Tests/
│       ├── FactoryScenePlayModeTests.cs       [Play-mode test suite]
│       └── Tests.asmdef                       [Test assembly definition]
│
├── 📁 Scripts/                                [Core factory simulation logic]
│   ├── CameraController.cs                    [Camera movement & control]
│   ├── CameraSwapController.cs                [Multi-camera switching]
│   ├── FloorManager.cs                        [Factory floor sizing & layout]
│   ├── HeatmapController.cs                   [Bottleneck visualization heatmap]
│   ├── MachineSpawner.cs                      [Spawns machines from config]
│   ├── MachineVisual.cs                       [Machine state rendering]
│   └── SimulationManager.cs                   [WebSocket & state sync]
│
├── 📁 Scenes/                                 [Main Unity scenes]
│   ├── factory.unity                          [Factory scene v1]
│   └── factory_digital twin.unity             [Factory scene v2]
│
├── 📁 prefab/                                 [Machine & environment prefabs]
│   ├── band_saw.prefab                        [Band saw machine]
│   ├── lathe.prefab                           [Lathe machine]
│   ├── milling.prefab                         [Milling/CNC machine]
│   ├── Conveyor.prefab                        [Conveyor belt system]
│   ├── floor.prefab                           [Factory floor plane]
│   ├── station.prefab                         [Generic station]
│   ├── Canvas.prefab                          [UI Canvas]
│   ├── Conditioner_v1.prefab                  [Air conditioner model]
│   ├── queueParent.prefab                     [Queue parent/organizer]
│   ├── StationBox.prefab                      [Station box v1]
│   ├── StationBox 1.prefab                    [Station box v2]
│   ├── WIPBox.prefab                          [Work-in-progress box v1]
│   └── WIPBox 1.prefab                        [Work-in-progress box v2]
│
├── 📁 Tests/                                  [Unit & integration tests]
│   └── 📁 Editor/
│       ├── MachineSpawnerEditModeTests.cs     [Machine spawning tests]
│       └── MachineVisualEditModeTests.cs      [Visual rendering tests]
│
├── 📁 Plugins/                                [Third-party extensions]
│   └── 📁 Demigiant/                          [Animation & tweening library]
│
├── 📁 Settings/                               [Project configuration]
│   └── 📁 Build Profiles/
│       └── Android™.asset                     [Android build settings]
│
├── 📁 TextMesh Pro/                           [Text rendering (Pro version)]
│   ├── Fonts/
│   ├── Resources/
│   │   ├── Fonts & Materials/
│   │   ├── Sprite Assets/
│   │   └── Style Sheets/
│   ├── Shaders/
│   └── Sprites/
│
├── 📁 UI Toolkit/                             [ModernUI framework]
│   ├── PanelSettings.asset
│   └── 📁 UnityThemes/
│
└── 📁 3D Model Files (Root Level)             [FBX machine models]
    ├── band_saw.fbx                           [Band saw model]
    ├── lathe.fbx                              [Lathe model]
    ├── milling.fbx                            [Milling machine model]
    ├── Conveyor.fbx                           [Conveyor system model]
    ├── floor.fbx                              [Floor model]
    ├── queue_bar.fbx                          [Queue visualization bar]
    ├── Shaft.fbx                              [Mechanical shaft]
    ├── Gear.fbx                               [Gear component]
    ├── Gripper_dt.fbx                         [Robot gripper]
    ├── Indicator.fbx                          [Status indicator light]
    ├── Status_ring.fbx                        [Status ring indicator]
    ├── wall_01.fbx                            [Wall segment 1]
    ├── wall_02.fbx                            [Wall segment 2]
    └── solar_panel_cleaning_robot[1,2,6].fbx [Cleaning robot variants]
```

---

## Key Architecture

### Core Scripts By Function

| Category | Scripts | Purpose |
|----------|---------|---------|
| **Simulation** | `SimulationManager.cs` | WebSocket bridge, state sync with Python backend |
| **Spawning** | `MachineSpawner.cs` | Creates factory machines from JSON config |
| **Visuals** | `MachineVisual.cs` | Updates machine appearance based on state |
| **Environment** | `FloorManager.cs`, `HeatmapController.cs` | Floor layout, bottleneck visualization |
| **Camera** | `CameraController.cs`, `CameraSwapController.cs` | Multi-view camera system |

### Prefab Relationships

```
FactoryParent (hierarchy root)
├── FactoryFloor (floor.prefab)
├── EntranceConveyor (Conveyor.prefab)
├── Machine[0] → MachineVisual component
├── Machine[1] → MachineVisual component
└── Machine[N] → MachineVisual component
```

### Material States

Machines switch between 4 state materials dynamically:
- **idleMat** — Machine awaiting input (idle)
- **runningMat** — Actively processing (green)
- **maintenanceMat** — Scheduled downtime (yellow)
- **brokenMat** — Failed/error state (red)

---

## Scene Files

| File | Purpose | Last Saved |
|------|---------|------------|
| `factory.unity` | Main factory floor with machines | 2026 |
| `factory_digital twin.unity` | Alternative view (digital twin) | 2026 |

---

## External Assets Used

1. **TextMesh Pro** — Advanced text rendering
2. **Demigiant Plugins** — Animation/tweening (DoTween likely)
3. **Industrial Zone Modular Pack** — Environment & prefabs (asset store)
4. **RPG/FPS Game Assets** — Props & scenery

---

## How to Use This Hierarchy

1. **Setup Scene:** Menu → `Factory → Setup Scene` (runs `FactorySetupEditor.cs`)
2. **Load Factory:** `MachineSpawner` reads `python/configs/factory_config.json`
3. **Sync State:** `SimulationManager` connects to Python backend at `ws://127.0.0.1:8765`
4. **View Results:** Machines update colors/state in real-time

---

## File Counts

- **Scripts:** 7 core + 2 tests + 1 editor tool
- **Scenes:** 2 main scenes
- **Prefabs:** 13 factory-specific + 2+ from asset packs
- **Materials:** 5 state-based
- **3D Models (FBX):** 16 machine/equipment models
- **Tests:** Editor mode + play mode suites
- **Asset Pack Includes:** 100+ textures, models, prefabs

