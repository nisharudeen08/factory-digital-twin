# Unity Setup Checklist

Follow this checklist step by step. Check off each item as you complete it.

---

## Phase 1: Pre-Setup (5 minutes)

- [ ] **Unity Hub is installed**
  - Download from: https://unity.com/download
  - Install Unity Hub

- [ ] **Unity 2022 LTS is installed**
  - Open Unity Hub → Installs → Add
  - Select: Unity 2022.3.x LTS
  - Include: Android Build Support, Android SDK & NDK, OpenJDK
  - Wait for installation (may take 20-30 min)

- [ ] **Project folder exists**
  - Verify: `c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\unity\`
  - Should contain: Assets, Packages, ProjectSettings folders

- [ ] **Python server folder exists**
  - Verify: `c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python\configs\`
  - Should contain: `factory_config.json`

---

## Phase 2: Open Unity Project (10 minutes)

- [ ] **Open Unity Hub**
  - Click on Unity Hub icon

- [ ] **Add existing project**
  - Click **Add** button (top right)
  - Navigate to: `c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\unity`
  - Click **Select Folder**

- [ ] **Wait for project to appear in Unity Hub**
  - Project name: "unity" or "factory_digital_twin"
  - Unity version should match (2022.x LTS)

- [ ] **Open the project**
  - Click on the project in Unity Hub
  - Wait for Unity Editor to launch (first time: 5-10 min)
  - Wait for console to finish compiling (watch bottom right corner)

- [ ] **Verify no critical errors in Console**
  - Window → General → Console
  - Should see: "0 Errors, 0 Warnings" (or only warnings)
  - If errors exist, note them for troubleshooting

---

## Phase 3: Install Required Packages (10 minutes)

- [ ] **Open Package Manager**
  - Menu: Window → Package Manager

- [ ] **Install NativeWebSocket**
  - Click **+** button (top left)
  - Select: **Add package from git URL**
  - Paste: `https://github.com/endel/NativeWebSocket.git#upm`
  - Click **Add**
  - Wait for: "Package installed successfully"
  - Verify in Project window: Assets/Plugins/NativeWebSocket exists

- [ ] **Verify TextMeshPro is installed**
  - In Package Manager, search: "TextMeshPro"
  - Should show: **Installed** (green checkmark)
  - If not installed, click **Install**

- [ ] **Import TextMeshPro Essentials** (if prompted)
  - A dialog may appear: "Import TMP Essentials"
  - Click **Import**
  - Wait for import to complete
  - Verify in Project window: Assets/TextMesh Pro folder exists

---

## Phase 4: Open the Scene (5 minutes)

- [ ] **Navigate to Scenes folder**
  - In Project window, scroll to: `Assets/Scenes/`
  - You should see: `factory_digital twin.unity` and `factory.unity`

- [ ] **Open the factory scene**
  - Double-click: `factory_digital twin.unity`
  - Wait for scene to load
  - Verify in Hierarchy: You see objects like Main Camera, Directional Light

- [ ] **Save the scene**
  - Menu: File → Save
  - Or press: Ctrl+S
  - This ensures no changes are lost

---

## Phase 5: Create Required GameObjects (5 minutes)

- [ ] **Create GameManager**
  - In Hierarchy window, right-click → **Create Empty**
  - Rename to: `GameManager`
  - Position: (0, 0, 0)
  - Icon: Click gear icon → Choose any color

- [ ] **Create FactoryParent**
  - In Hierarchy window, right-click → **Create Empty**
  - Rename to: `FactoryParent`
  - Position: (0, 0, 0)
  - Icon: Click gear icon → Choose different color

- [ ] **Verify both exist in Hierarchy**
  - GameManager
  - FactoryParent
  - Main Camera
  - Directional Light

---

## Phase 6: Configure SimulationManager (10 minutes)

- [ ] **Select GameManager**
  - Click on `GameManager` in Hierarchy

- [ ] **Add SimulationManager component**
  - In Inspector window, click **Add Component**
  - Type: `SimulationManager`
  - Select: `SimulationManager` from the list
  - Component should appear in Inspector

- [ ] **Configure WebSocket settings**
  - In SimulationManager component:
    - WebSocket Url: `ws://127.0.0.1:8765`
    - Auto Connect: ☑ **Check this box**
    - Reconnect Delay: `5`

- [ ] **Leave Spawner empty for now**
  - We'll assign it after creating MachineSpawner

---

## Phase 7: Configure MachineSpawner (15 minutes)

- [ ] **Still have GameManager selected**
  - Make sure `GameManager` is selected in Hierarchy

- [ ] **Add MachineSpawner component**
  - In Inspector, click **Add Component**
  - Type: `MachineSpawner`
  - Select: `MachineSpawner` from the list

- [ ] **Configure references**
  - Sim Manager: Drag `GameManager` from Hierarchy into this slot
  - Factory Parent: Drag `FactoryParent` from Hierarchy into this slot

- [ ] **Set Config Path**
  - Config Path: `python/configs/factory_config.json`
  - (This is relative to Unity project root)

- [ ] **Configure Grid Spacing**
  - Machine Spacing: `15`
  - Machine Step: `12`
  - Floor Margin: `10`

- [ ] **Configure Machine Sizing**
  - Target Machine Height: `3.0`
  - Enable Auto Size: ☑ **Check**
  - Size Multiplier: `(0.8, 1.0, 0.8)`

- [ ] **Configure Rotation settings**
  - Machine Global Rotation: `(0, 0, 0)`
  - Lathe Rotation Offset: `(0, 90, 0)`
  - Lathe Scale Multiplier: `(1, 1, 1)`
  - Conveyor Rotation: `(0, 0, 0)`
  - Conveyor Scale Multiplier: `(1, 1, 1)`

- [ ] **Assign Prefabs** (CRITICAL)
  - In Project window, navigate to: `Assets/prefab/`
  
  For each slot below, drag the corresponding prefab:
  
  - [ ] Lathe Prefab: Drag `lathe.prefab`
  - [ ] Cnc Prefab: Drag `milling.prefab`
  - [ ] Drill Prefab: Leave empty or create generic
  - [ ] Band Saw Prefab: Drag `band_saw.prefab`
  - [ ] Weld Prefab: Leave empty or create generic
  - [ ] Generic Prefab: Create simple cube or leave empty
  - [ ] Conveyor Prefab: Drag `Conveyor.prefab`
  - [ ] Floor Prefab: Drag `floor.prefab`

- [ ] **Debug settings**
  - Rebuild Now: ☐ **Uncheck**

---

## Phase 8: Link SimulationManager to MachineSpawner (2 minutes)

- [ ] **Select GameManager again**
  - Click `GameManager` in Hierarchy

- [ ] **Assign Spawner reference**
  - In SimulationManager component:
  - Spawner: Drag the `GameManager` object (with MachineSpawner) into this slot
  - Or click the circle icon → Select MachineSpawner component

---

## Phase 9: Configure CameraController (10 minutes)

- [ ] **Select Main Camera**
  - Click `Main Camera` in Hierarchy

- [ ] **Add CameraController component**
  - In Inspector, click **Add Component**
  - Type: `CameraController`
  - Select: `CameraController`

- [ ] **Configure Auto Position**
  - Auto Position on Start: ☑ **Check**

- [ ] **Configure Default View**
  - Default FOV: `55`
  - Default Pitch: `35`
  - Default Yaw: `0`
  - Default Dist: `40`

- [ ] **Configure Orbit Controls**
  - Orbit Speed: `120`
  - Pan Speed: `0.4`
  - Zoom Speed: `8`
  - Min Zoom Dist: `3`
  - Max Zoom Dist: `300`

- [ ] **Configure Smooth Follow**
  - Follow Factory: ☑ **Check**
  - Follow Smooth: `4`

---

## Phase 10: Create Materials for MachineVisual (15 minutes)

- [ ] **Navigate to Materials folder**
  - In Project window: `Assets/Materials/`
  - Or create: Right-click → Create → Folder → Name: "Materials"

- [ ] **Create Green Material**
  - Right-click in Materials folder → Create → Material
  - Name: `mat_green`
  - In Inspector:
    - Albedo Color: R=`0.2` G=`0.75` B=`0.3` A=`1.0`
    - Smoothness: `0.5`
    - Metallic: `0.0`

- [ ] **Create Amber Material**
  - Right-click → Create → Material
  - Name: `mat_amber`
  - Albedo: R=`1.0` G=`0.84` B=`0.2` A=`1.0`

- [ ] **Create Orange Material**
  - Right-click → Create → Material
  - Name: `mat_orange`
  - Albedo: R=`1.0` G=`0.55` B=`0.1` A=`1.0`

- [ ] **Create Red Material**
  - Right-click → Create → Material
  - Name: `mat_red`
  - Albedo: R=`0.85` G=`0.2` B=`0.2` A=`1.0`

- [ ] **Create Gray Material**
  - Right-click → Create → Material
  - Name: `mat_gray`
  - Albedo: R=`0.45` G=`0.45` B=`0.45` A=`1.0`

- [ ] **Verify all 5 materials exist**
  - mat_green
  - mat_amber
  - mat_orange
  - mat_red
  - mat_gray

---

## Phase 11: Configure Machine Prefabs (20 minutes)

### For EACH machine prefab (lathe, milling, band_saw):

- [ ] **Select lathe.prefab**
  - In Project window: `Assets/prefab/lathe.prefab`
  - Click once to select

- [ ] **Add MachineVisual component**
  - In Inspector, click **Add Component**
  - Type: `MachineVisual`
  - Select: `MachineVisual`

- [ ] **Configure Identity**
  - Station ID: `0` (will be set at runtime)
  - Machine Display Name: Leave empty
  - Machine Type Name: `Lathe Machine`

- [ ] **Assign Body Renderer**
  - Expand the prefab hierarchy in Inspector
  - Find the main body renderer (usually first child)
  - Drag it into: Body Renderer slot

- [ ] **Assign Materials**
  - Mat Green: Drag `mat_green`
  - Mat Amber: Drag `mat_amber`
  - Mat Orange: Drag `mat_orange`
  - Mat Red: Drag `mat_red`
  - Mat Gray: Drag `mat_gray`

- [ ] **Configure Queue system**
  - Queue Parent: Drag `queueParent.prefab` (or leave empty for auto-create)
  - Queue Box Prefab: Drag `StationBox.prefab` or `WIPBox.prefab`

- [ ] **Machine settings**
  - Machine Index: `0` (runtime)
  - Num Machines Total: `1` (runtime)
  - Show Label: ☑ **Check**

- [ ] **Apply changes to prefab**
  - Click **Apply** button (top of Inspector)
  - This saves changes to the prefab asset

- [ ] **Repeat for milling.prefab**
  - Machine Type Name: `CNC Machine`
  - Follow same steps as lathe

- [ ] **Repeat for band_saw.prefab**
  - Machine Type Name: `Band Saw Machine`
  - Follow same steps as lathe

---

## Phase 12: Setup FloorManager (Optional - 5 minutes)

- [ ] **Select GameManager**
  - Click `GameManager` in Hierarchy

- [ ] **Add FloorManager component**
  - Add Component → `FloorManager`

- [ ] **Configure FloorManager**
  - Floor Object: Drag `floor.prefab` from Project
  - Factory Parent: Drag `FactoryParent`
  - Min Floor Size: `10`
  - Machine Spacing: `5`
  - Floor Margin: `4`
  - Floor Material: [Optional - assign if you have one]

---

## Phase 13: Setup HeatmapController (Optional - 5 minutes)

- [ ] **Drag floor.prefab into scene**
  - From Project window, drag `floor.prefab` into Hierarchy
  - Or create a new instance

- [ ] **Select the Floor object**
  - Click on Floor in Hierarchy

- [ ] **Add HeatmapController component**
  - Add Component → `HeatmapController`

- [ ] **Configure HeatmapController**
  - Floor Renderer: Drag the Renderer component from same object
  - Low Utilization Color: R=`0.2` G=`0.8` B=`0.2` A=`0.5`
  - High Utilization Color: R=`0.8` G=`0.2` B=`0.2` A=`0.5`

---

## Phase 14: Verify Python Server (5 minutes)

- [ ] **Open Command Prompt**
  - Press Win+R
  - Type: `cmd`
  - Press Enter

- [ ] **Navigate to Python folder**
  ```
  cd c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python
  ```

- [ ] **Check config file exists**
  ```
  dir configs\factory_config.json
  ```
  - Should show the file

- [ ] **Start Python server**
  ```
  python run_server.py
  ```

- [ ] **Verify server starts**
  - Look for these lines:
  ```
  INFO:     Uvicorn running on http://0.0.0.0:8000
  INFO:     WebSocket server on ws://0.0.0.0:8765
  ```
  - Keep this window open

- [ ] **Test WebSocket port**
  - Open browser
  - Go to: `http://localhost:8000/health`
  - Should see: `{"status":"ok",...}`

---

## Phase 15: Test in Unity (10 minutes)

- [ ] **Return to Unity**
  - Switch back to Unity Editor

- [ ] **Open Console window**
  - Window → General → Console
  - Keep this visible

- [ ] **Press Play button**
  - Click the ▶️ Play button (top center)
  - Scene view will enter Play Mode (blue border)

- [ ] **Watch Console for messages**
  - Expected messages:
  ```
  [Spawner] Start load config from: python/configs/factory_config.json
  [Spawner] Config file found. Size=XXXX chars
  [Spawner] Building XX machines from X stations
  [Camera] Focused: center=(x,y,z) dist=XX.X machines=XX
  [SimManager] Connected to Python backend!
  ```

- [ ] **Check Scene/Game view**
  - You should see:
    - Multiple machines arranged in a grid
    - Floor underneath machines
    - Labels above machines
    - Machines colored (green/amber/orange/red)

- [ ] **Test camera controls**
  - Right-click + drag: Orbit around factory
  - Middle-click + drag: Pan camera
  - Scroll wheel: Zoom in/out

- [ ] **Verify machine colors update**
  - Watch Console for state updates
  - Machines should change color based on utilization

- [ ] **Stop Play mode**
  - Press ▶️ Play button again to exit
  - Or press Ctrl+P

---

## Phase 16: Troubleshooting (If needed)

### If WebSocket fails to connect:

- [ ] Verify Python server is running
- [ ] Check WebSocket URL: `ws://127.0.0.1:8765`
- [ ] Check Windows Firewall:
  ```
  netsh advfirewall firewall add rule name="DigitalTwin_WS" dir=in action=allow protocol=TCP localport=8765
  ```

### If machines don't appear:

- [ ] Check MachineSpawner has prefabs assigned
- [ ] Verify config file path is correct
- [ ] Check Console for errors
- [ ] Ensure FactoryParent exists

### If materials don't show:

- [ ] Verify materials are assigned to MachineVisual
- [ ] Check prefabs were saved (click Apply)
- [ ] Ensure renderers are assigned

### If camera doesn't focus:

- [ ] Check CameraController is on Main Camera
- [ ] Verify Auto Position on Start is checked
- [ ] Check machines exist in scene

---

## ✅ Final Verification

- [ ] NativeWebSocket installed
- [ ] TextMeshPro installed
- [ ] Scene opens without errors
- [ ] GameManager has SimulationManager + MachineSpawner
- [ ] FactoryParent exists
- [ ] Main Camera has CameraController
- [ ] All machine prefabs have MachineVisual
- [ ] All 5 materials created and assigned
- [ ] Python server running
- [ ] WebSocket connects (Console shows "Connected")
- [ ] Machines appear in scene when pressing Play
- [ ] Camera focuses on factory
- [ ] Machine colors update based on simulation data
- [ ] Camera controls work (orbit, pan, zoom)

---

## 🎉 Setup Complete!

If all items are checked, your Unity setup is complete!

### Next Steps:

1. **Customize factory layout**: Edit `python/configs/factory_config.json`
2. **Test different scenarios**: Change machine count, utilization
3. **Integrate with Android**: Connect Android app for unified control
4. **Add features**: Heatmaps, analytics, custom UI

---

**Total Estimated Time**: 90-120 minutes (first time)
**Difficulty**: Intermediate

**Save this checklist and check off items as you go!**
