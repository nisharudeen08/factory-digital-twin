# Integration Guide: Dynamic Factory Scaling

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANDROID APP                                  │
│  (User sets machine count: 1-70 via UI)                         │
│  Writes: factory_config.json                                    │
└────────────────────┬────────────────────────────────────────────┘
                     │ factory_config.json
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│            PYTHON BACKEND (FastAPI Server)                      │
│  • Reads factory_config.json                                    │
│  • Validates machine count (1-70)                               │
│  • Calls setup_environment_config()                             │
│  • Generates OptimalLayout + EnvironmentConfig                  │
│  • Exports unity_environment.json                               │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴─────────────┐
        │                          │
        ↓                          ↓
┌──────────────────────┐  ┌─────────────────────┐
│ Simulation Engine    │  │   UNITY 3D SCENE    │
│ (Runs with config)   │  │ (Reads JSON config) │
└──────────────────────┘  └─────────────────────┘
```

## Implementation Checklist

### 1. Android App Update (Kotlin)

**File:** `android/app/src/main/java/YourPackage/ConfigActivity.kt`

```kotlin
class ConfigActivity : AppCompatActivity() {
    private var machineCount: Int = 20
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Add machine count slider
        val machineSlider = findViewById<SeekBar>(R.id.machine_count_slider)
        machineSlider.max = 70
        machineSlider.progress = 20
        
        machineSlider.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                machineCount = maxOf(1, progress)  // Minimum 1
                updateMachineLabel(machineCount)
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })
        
        // When saving config
        findViewById<Button>(R.id.save_button).setOnClickListener {
            saveConfiguration(machineCount)
        }
    }
    
    private fun saveConfiguration(machineCount: Int) {
        val config = mapOf(
            "factory_type" to selectedType,
            "factory_name" to factoryName,
            "machine_count" to machineCount,  // NEW: Dynamic machine count
            "demand" to demand,
            "operators" to operators,
            // ... other fields
        )
        
        // Send to Python backend via HTTP
        val json = JSONObject(config)
        sendConfigToBackend(json)
    }
}
```

**Result:** User can now set machine count from 1-70 via slider.

---

### 2. Python Backend Update

**File:** `python/api_server.py`

```python
from fastapi import FastAPI, HTTPException
from config_manager import (
    load_config, setup_environment_config, 
    get_total_machine_count, validate_config,
    export_environment_for_unity
)

app = FastAPI()

@app.post("/api/factory/config")
async def receive_config(config_data: dict):
    """
    Receive factory configuration from Android.
    Automatically sets up environment based on machine count.
    """
    try:
        # Save the config
        config_path = "configs/factory_config.json"
        save_config_from_dict(config_data, config_path)
        
        # Load config
        config = load_config(config_path)
        
        # Validate
        valid, errors = validate_config(config)
        if not valid:
            raise HTTPException(status_code=400, detail={
                "error": "Configuration invalid",
                "details": errors
            })
        
        # KEY STEP: Automatically setup environment
        # This calculates floor size, grid layout, etc.
        setup_environment_config(config)
        
        total_machines = get_total_machine_count(config)
        
        # Export for Unity
        export_environment_for_unity(
            config, 
            "configs/unity_environment.json"
        )
        
        return {
            "status": "success",
            "total_machines": total_machines,
            "grid_layout": f"{config.environment.grid_rows}×{config.environment.grid_cols}",
            "floor_size": f"{config.environment.floor_width:.1f}m × {config.environment.floor_depth:.1f}m",
            "lod_quality": config.environment.lod_quality,
            "message": "Configuration ready for Unity"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/factory/environment")
async def get_environment_config():
    """Get current environment configuration for Unity."""
    try:
        with open("configs/unity_environment.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Environment not configured")


def save_config_from_dict(config_data: dict, path: str):
    """Save config dict to JSON file."""
    config = FactoryConfig(
        factory_type=config_data.get("factory_type", "lathe"),
        factory_name=config_data.get("factory_name", "Factory"),
        stations=[...],  # Parse stations
        # ... other fields
    )
    save_config(config, path)
```

**Result:** Backend automatically sizes environment based on machine count.

---

### 3. Unity Integration

**File:** `unity/Assets/Scripts/EnvironmentSetup.cs`

```csharp
using UnityEngine;
using System.IO;
using Newtonsoft.Json.Linq;

public class EnvironmentSetup : MonoBehaviour
{
    [System.Serializable]
    public class EnvironmentConfig
    {
        public FloorConfig floor;
        public GridConfig grid;
        public CameraConfig camera;
        public RenderingConfig rendering;
    }
    
    [System.Serializable]
    public class FloorConfig
    {
        public float width, depth, height;
    }
    
    [System.Serializable]
    public class GridConfig
    {
        public int rows, cols;
        public float spacing;
    }
    
    [System.Serializable]
    public class CameraConfig
    {
        public float distance, height;
        public int fov;
    }
    
    [System.Serializable]
    public class RenderingConfig
    {
        public string lod_quality;
        public bool use_instancing;
    }
    
    public GameObject floorPrefab;
    public Camera mainCamera;
    
    public void LoadEnvironmentConfig(string configPath)
    {
        try
        {
            string json = File.ReadAllText(configPath);
            var config = JsonUtility.FromJson<EnvironmentConfig>(json);
            
            ApplyFloorConfig(config.floor);
            ApplyGridLayout(config.grid);
            ApplyCameraConfig(config.camera);
            ApplyRenderingConfig(config.rendering);
            
            Debug.Log($"Environment loaded: {config.grid.rows}×{config.grid.cols} grid");
        }
        catch (System.Exception e)
        {
            Debug.LogError($"Failed to load environment config: {e.Message}");
        }
    }
    
    private void ApplyFloorConfig(FloorConfig floor)
    {
        // Resize the floor plane
        floorPrefab.transform.localScale = new Vector3(
            floor.width / 10f,
            1f,
            floor.depth / 10f
        );
        
        // Adjust floor position (center)
        floorPrefab.transform.position = Vector3.zero;
    }
    
    private void ApplyGridLayout(GridConfig grid)
    {
        // Spawning logic will use grid.rows, cols, spacing
        // See SpawnMachines() below
        Debug.Log($"Grid: {grid.rows}×{grid.cols} with {grid.spacing}m spacing");
    }
    
    private void ApplyCameraConfig(CameraConfig camera)
    {
        // Position camera based on auto-calculated values
        mainCamera.fieldOfView = camera.fov;
        
        Vector3 cameraPos = new Vector3(
            0,
            camera.height,
            -camera.distance
        );
        mainCamera.transform.position = cameraPos;
    }
    
    private void ApplyRenderingConfig(RenderingConfig rendering)
    {
        // Set LOD quality
        int qualityLevel = rendering.lod_quality switch
        {
            "high" => 3,
            "medium" => 2,
            "low" => 1,
            _ => 2
        };
        QualitySettings.SetQualityLevel(qualityLevel, true);
        
        // Enable GPU instancing for large machine counts
        if (rendering.use_instancing)
        {
            // Enable instancing for machine materials
            foreach (var mat in GetComponentsInChildren<Renderer>())
            {
                mat.GetComponent<Renderer>().material.enableInstancing = true;
            }
        }
    }
    
    public void SpawnMachines(List<MachineConfig> machines, GridConfig grid)
    {
        float startX = -grid.spacing * grid.cols / 2;
        float startZ = -grid.spacing * grid.rows / 2;
        
        int index = 0;
        for (int row = 0; row < grid.rows; row++)
        {
            for (int col = 0; col < grid.cols; col++)
            {
                if (index >= machines.Count) return;
                
                float x = startX + col * grid.spacing;
                float z = startZ + row * grid.spacing;
                
                SpawnMachine(machines[index], x, z);
                index++;
            }
        }
    }
    
    private void SpawnMachine(MachineConfig config, float x, float z)
    {
        // Instantiate machine prefab at (x, 0, z)
        // ... implementation
    }
}
```

**In Scene Start:**
```csharp
void Start()
{
    // Load config from backend
    var environmentSetup = GetComponent<EnvironmentSetup>();
    environmentSetup.LoadEnvironmentConfig("Temp/unity_environment.json");
    // Or load from StreamingAssets if bundled
}
```

**Result:** Unity scene automatically adapts to machine count.

---

## Data Flow Example

### Scenario: User sets 50 machines in Android

#### 1. Android sends:
```json
{
  "factory_type": "textile",
  "machine_count": 50,
  "demand": 300,
  "operators": 8,
  ...
}
```

#### 2. Python receives and processes:
```python
# setup_environment_config() is called
# - Validates: 50 is between 1-70 ✓
# - Calculates: 7×8 grid for 56 slots
# - Computes floor: 28m × 26m
# - Sets camera: distance=16.8m, height=10.4m
# - Determines LOD: "medium" (21-50 machines)
```

#### 3. Python exports to Unity:
```json
{
  "machine_count": 50,
  "environment": {
    "floor": {"width": 28.0, "depth": 26.0, "height": 4.0},
    "grid": {"rows": 7, "cols": 8, "spacing": 3.0},
    "camera": {"distance": 16.8, "height": 10.4, "fov": 60},
    "rendering": {"lod_quality": "medium", "use_instancing": true}
  }
}
```

#### 4. Unity reads config:
- Creates 28m × 26m floor
- Positions camera 16.8m away at height 10.4m
- Sets up 7×8 grid for machines
- Enables GPU instancing
- Sets quality level to "medium"

#### 5. Simulation runs:
- All 50 machines visible in optimized grid
- Floor properly sized
- Performance maintained

---

## Testing Checklist

- [ ] Android can set machine count 1-70
- [ ] Backend validates and rejects >70
- [ ] Backend auto-generates environment config
- [ ] Unity reads and applies floor dimensions
- [ ] Unity positions camera correctly
- [ ] LOD quality adjusts based on count
- [ ] Instancing enabled for 50+ machines
- [ ] Simulation runs smoothly with configuration

---

## Common Issues & Solutions

**Issue:** "Machine count exceeds 70"  
**Solution:** Check Android slider max is 70, backend validation is working

**Issue:** Floor too small/too large  
**Solution:** Check `FloorLayoutCalculator` parameters (BASE_MACHINE_SPACING, etc.)

**Issue:** Machines overlapping  
**Solution:** Adjust `grid_spacing` in `EnvironmentConfig`

**Issue:** Camera too close/far  
**Solution:** Verify `calculate_camera_distance()` and `calculate_camera_height()` calculations

---

## Files Modified

| File | Changes | Status |
|------|---------|--------|
| `python/floor_layout_calculator.py` | NEW | ✓ Created |
| `python/config_manager.py` | Enhanced with environment config | ✓ Updated |
| `python/example_dynamic_scaling.py` | NEW | ✓ Created |
| `DYNAMIC_SCALING_README.md` | NEW | ✓ Created |
| `android/ConfigActivity.kt` | Add machine slider | TODO |
| `python/api_server.py` | Add environment endpoint | TODO |
| `unity/EnvironmentSetup.cs` | NEW | TODO |

---

## Next Steps

1. **Update Android UI** with machine count slider (1-70)
2. **Update Python API** to call `setup_environment_config()`
3. **Create Unity script** to read environment JSON
4. **Test end-to-end** with 10, 30, 50, 70 machines
5. **Optimize** LOD settings if needed
