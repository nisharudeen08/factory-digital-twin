# Fix: Lathe Not Appearing in Game Mode

## 🔍 Problem Diagnosis

Your config file has **70 machines** (10 lathe + 10 CNC + 10 drill + 10 band_saw + 10 weld + 10 grind + 10 paint), but lathes are not appearing. Here's how to fix it.

---

## ✅ Step-by-Step Solution

### Step 1: Check Console for Errors

1. Open Unity and load your scene
2. Press **Play** button
3. Open **Console** window (Window → General → Console)
4. Look for these error messages:

```
[Spawner] CRITICAL ERROR: Config file NOT FOUND at: python/configs/factory_config.json
```
OR
```
[Spawner] No prefab for 'lathe'.
```
OR
```
[Spawner] Parse error: ...
```

**Write down the exact error** - this tells us what's wrong.

---

### Step 2: Verify Config File Path

The #1 reason machines don't spawn is **wrong config path**.

#### Check 1: File Exists
```
c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python\configs\factory_config.json
```

Navigate to this folder in File Explorer and verify the file exists.

#### Check 2: Unity Inspector Path
1. Select **GameManager** in Hierarchy
2. Find **MachineSpawner** component
3. Check **Config Path** field shows exactly:

```
python/configs/factory_config.json
```

⚠️ **Common mistakes:**
- ❌ `python\configs\factory_config.json` (backslashes)
- ❌ `Python/configs/factory_config.json` (capital P)
- ❌ `configs/factory_config.json` (missing python/)
- ❌ `c:/Users/...` (absolute path - don't use this)

✅ **Correct:** `python/configs/factory_config.json` (forward slashes, lowercase)

---

### Step 3: Verify Lathe Prefab Assignment

#### Check 1: Prefab Assigned in Inspector

1. Select **GameManager** in Hierarchy
2. Find **MachineSpawner** component
3. Look for **Lathe Prefab** field
4. It should show: `lathe (Prefab)`

If it shows **None (GameObject)**:

1. In Project window, navigate to: `Assets/prefab/`
2. Find **lathe.prefab**
3. Drag it into the **Lathe Prefab** slot in Inspector

#### Check 2: Prefab Icon Name Matching

The MachineSpawner uses icon names from the config:

```json
"icon": "lathe"
```

This must match the prefab map. Check `MachineSpawner.cs` line 333:

```csharp
{ "lathe", lathePrefab ?? genericPrefab },
```

✅ **Icon name "lathe" matches config** - this is correct.

---

### Step 4: Check Lathe Prefab Integrity

The lathe.prefab file is very large (6112 lines). It might have issues.

#### Check 1: Prefab Opens Correctly

1. In Project window, double-click **lathe.prefab**
2. It should open in Prefab Mode
3. You should see the 3D model in Scene view
4. Check Hierarchy - should have multiple child objects

If prefab shows **Missing Script** or errors:
- The prefab might be corrupted
- Try re-importing the asset

#### Check 2: Add MachineVisual Component

The lathe prefab needs the `MachineVisual` component:

1. Double-click **lathe.prefab** to open Prefab Mode
2. In Hierarchy, select the **root GameObject** (top-level object)
3. In Inspector, click **Add Component**
4. Search for: `MachineVisual`
5. Add it

#### Check 3: Configure MachineVisual

With MachineVisual component added:

1. **Body Renderer**: 
   - Expand the prefab hierarchy
   - Find the main body renderer (usually a child with MeshRenderer)
   - Drag it into **Body Renderer** slot

2. **Materials** (create these first if missing):
   - Mat Green: Create `mat_green` material
   - Mat Amber: Create `mat_amber` material
   - Mat Orange: Create `mat_orange` material
   - Mat Red: Create `mat_red` material
   - Mat Gray: Create `mat_gray` material

3. **Other fields** (leave as default for now):
   - Station ID: 0 (set at runtime)
   - Machine Type Name: "Lathe Machine"
   - Show Label: ✓ Checked

#### Check 4: Save Prefab

1. Click **Apply** button (top of Inspector)
2. This saves changes to the prefab asset
3. Exit Prefab Mode (click ← arrow at top)

---

### Step 5: Reduce Factory Size for Testing

70 machines is a lot for testing. Let's test with fewer:

#### Create Test Config

1. Navigate to: `python/configs/`
2. Copy `factory_config.json` → Rename to `factory_config_test.json`
3. Open `factory_config_test.json` in a text editor
4. Change `num_machines` to **1** for each station:

```json
{
  "factory_type": "industrial",
  "factory_name": "Test Factory",
  "mode": "static",
  "language": "en",
  "shift_hours": 8.0,
  "num_operators": 15,
  "stations": [
    {
      "id": 1,
      "name": "Lathe Station",
      "name_ta": "lathe பிரிவு",
      "icon": "lathe",
      "num_machines": 1,
      "cycle_time_sec": 40.0,
      "mtbf_hours": 10.0,
      "mttr_hours": 1.0,
      "setup_minutes": 10.0,
      "variability": 0.1,
      "position_x": 0.0,
      "position_z": 0.0
    },
    {
      "id": 2,
      "name": "Cnc Station",
      "name_ta": "cnc பிரிவு",
      "icon": "cnc",
      "num_machines": 1,
      "cycle_time_sec": 40.0,
      "mtbf_hours": 10.0,
      "mttr_hours": 1.0,
      "setup_minutes": 10.0,
      "variability": 0.1,
      "position_x": 7.0,
      "position_z": 0.0
    }
  ]
}
```

5. Save the file

#### Update MachineSpawner to Use Test Config

1. Select **GameManager** in Hierarchy
2. In **MachineSpawner** component
3. Change **Config Path** to:

```
python/configs/factory_config_test.json
```

4. Press **Play** - you should now see only 2 machines (1 lathe + 1 CNC)

---

### Step 6: Check Python Server Connection

If machines still don't appear:

#### Check 1: Python Server Running

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

#### Check 2: WebSocket URL

1. Select **GameManager** in Hierarchy
2. In **SimulationManager** component
3. Check **WebSocket Url**:

```
ws://127.0.0.1:8765
```

If testing on network, use your IP:
```
ws://192.168.x.x:8765
```

#### Check 3: Firewall

Run this in Command Prompt (as Administrator):

```cmd
netsh advfirewall firewall add rule name="DigitalTwin_WS" dir=in action=allow protocol=TCP localport=8765
```

---

### Step 7: Debug Mode - Manual Spawn Test

Let's test if the spawner works at all:

#### Add Debug Code Temporarily

1. Open `MachineSpawner.cs` in Visual Studio or your editor
2. Find the `Start()` method (around line 73)
3. Add this debug code at the end:

```csharp
void Start()
{
    // ... existing code ...
    
    // DEBUG: Force spawn one lathe
    Debug.Log("[DEBUG] Testing lathe spawn...");
    if (lathePrefab == null)
    {
        Debug.LogError("[DEBUG] LATHE PREFAB IS NULL! Please assign in Inspector.");
    }
    else
    {
        Debug.Log("[DEBUG] Lathe prefab assigned: " + lathePrefab.name);
        
        // Try to spawn one test lathe
        GameObject testLathe = Instantiate(lathePrefab, factoryParent);
        testLathe.name = "TEST_LATHE";
        testLathe.transform.localPosition = Vector3.zero;
        Debug.Log("[DEBUG] Test lathe spawned at position (0,0,0)");
    }
}
```

4. Save the script
5. Return to Unity (it will recompile)
6. Press **Play**
7. Check Console for debug messages

**Expected output:**
```
[DEBUG] Testing lathe spawn...
[DEBUG] Lathe prefab assigned: lathe
[DEBUG] Test lathe spawned at position (0,0,0)
```

If you see **LATHE PREFAB IS NULL**, go back to Step 3.

---

### Step 8: Check Camera Position

Sometimes machines spawn but camera is looking the wrong way:

1. Press **Play**
2. In Hierarchy, find **Main Camera**
3. Check its **Transform**:
   - Position: Should be around (50, 40, 50) after FocusOnFactory()
   - Rotation: Should be looking at factory center

4. Press **F** key while hovering over Scene view to focus on selected object
5. Or manually orbit: Right-click + drag to look around

---

### Step 9: Verify FactoryParent Transform

Machines spawn as children of FactoryParent:

1. In Hierarchy, find **FactoryParent**
2. Press **Play**
3. Expand **FactoryParent** in Hierarchy (click the ▶️ arrow)
4. You should see:
   ```
   FactoryParent
   ├── S1_lathe_M1
   ├── S2_cnc_M1
   └── ...
   ```

If FactoryParent is empty but no errors:
- Config file not being read
- MachineSpawner.Start() not running

---

## 🐛 Common Issues & Solutions

### Issue 1: "Config file not found"

**Solution:**
```
Wrong: python\configs\factory_config.json
Wrong: Python/configs/factory_config.json
Wrong: configs/factory_config.json
Correct: python/configs/factory_config.json
```

Also check file actually exists:
```cmd
dir "c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python\configs\factory_config.json"
```

---

### Issue 2: "No prefab for 'lathe'"

**Solution:**
1. Verify lathe.prefab exists: `Assets/prefab/lathe.prefab`
2. Assign it in MachineSpawner Inspector
3. Check prefab isn't corrupted (open it)

---

### Issue 3: Machines spawn but invisible

**Solution:**
1. Check materials are assigned to MachineVisual
2. Verify mesh renderers exist on lathe prefab
3. Check camera frustum - press F to focus

---

### Issue 4: "MissingReferenceException"

**Solution:**
1. FactoryParent transform is missing
2. Drag FactoryParent GameObject into MachineSpawner.factoryParent field

---

### Issue 5: Nothing happens when pressing Play

**Solution:**
1. Check MachineSpawner component is on GameManager
2. Verify Awake() and Start() methods exist
3. Check Console for any errors
4. Verify configPath is correct

---

## 📊 Expected Console Output (Success)

When everything works, you should see:

```
[Spawner] Start loading config from: python/configs/factory_config.json
[Spawner] Config file found. Size=2534 chars
[Spawner] Building 70 machines from 7 stations
[Spawner] Grid: 8 columns × 9 rows  |  machineSpacing=15 machineStep=12
[Spawner] Done. Factory 'Mega Factory 70' — 70 machines.
[Camera] Focused: center=(52.5,0,48) dist=78.8 machines=70
[SimManager] Connected to Python backend!
```

---

## ✅ Final Checklist

After following all steps, verify:

- [ ] Config file exists at correct path
- [ ] Config Path in Inspector is correct
- [ ] Lathe prefab assigned in MachineSpawner
- [ ] Lathe prefab has MachineVisual component
- [ ] Materials created and assigned
- [ ] Python server running
- [ ] WebSocket connects (Console shows "Connected")
- [ ] Console shows "Building XX machines"
- [ ] FactoryParent has machine children in Hierarchy
- [ ] Camera focuses on factory

---

## 🎯 Quick Test Command

Run this to verify config file:

```cmd
cd c:\Users\nisharu deen\Downloads\PROJECT\factory_digital_twin\python\configs
type factory_config.json | findstr "lathe"
```

Should show:
```
      "name": "Lathe Station",
      "name_ta": "lathe பிரிவு",
      "icon": "lathe",
```

---

**If still not working:** Post a screenshot of your Console window showing all messages when you press Play.
