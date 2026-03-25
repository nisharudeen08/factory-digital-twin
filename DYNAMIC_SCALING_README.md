# Dynamic Factory Environment Scaling System

## Overview

Your Digital Twin system now supports **dynamic machine scaling (1-70 machines)** with **automatic floor sizing and environment adaptation**.

When you change the number of machines, the entire 3D environment automatically adjusts:
- Floor dimensions scale to fit all machines
- Grid layout optimizes based on machine count
- Camera position adjusts for optimal viewing
- Rendering quality adapts for performance
- Grid spacing and lighting automatically tune

## Maximum Limits

| Setting | Minimum | Maximum |
|---------|---------|---------|
| **Machines Per Factory** | 1 | **70** |
| **Machines Per Station** | 1 | Configurable |
| **Floor Width** | ~10m | ~60m (auto-calculated) |
| **Floor Depth** | ~10m | ~60m (auto-calculated) |

## Core Components

### 1. **floor_layout_calculator.py**
Calculates optimal layouts for any machine count.

```
FloorLayoutCalculator(machine_count)
├─ calculate_grid_dimensions()     → (rows, cols)
├─ calculate_floor_dimensions()    → FloorDimensions
├─ generate_machine_positions()    → List[MachinePosition]
└─ get_environment_config()        → dict
```

**Key Features:**
- Balances grid dimensions (reduces aspect ratio)
- Scales floor size automatically
- Calculates optimal camera distance
- Determines Level of Detail (LOD) quality

### 2. **config_manager.py (Enhanced)**
Updated with environment configuration and validation.

**New Dataclass:**
```python
@dataclass
class EnvironmentConfig:
    floor_width: float          # X dimension (meters)
    floor_depth: float          # Z dimension (meters)
    floor_height: float         # Y dimension (ceiling)
    grid_spacing: float         # Distance between machines
    grid_rows: int              # Grid layout rows
    grid_cols: int              # Grid layout columns
    camera_distance: float      # Camera from center
    camera_height: float        # Camera height
    camera_fov: int             # Field of view
    ambient_intensity: float    # Ambient light (0.0-1.0)
    main_light_intensity: float # Main light (0.0-2.0)
    lod_quality: str            # "high", "medium", "low"
```

**New Functions:**
```python
setup_environment_config(config)      # Main setup function
get_total_machine_count(config)       # Sum all machines
validate_machine_count(config)        # Check 1-70 limit
export_environment_for_unity(config, path)  # Export for Unity
```

## Usage Examples

### Example 1: Create Factory with 50 Machines

```python
from config_manager import (
    get_default_config, 
    setup_environment_config, 
    get_total_machine_count
)

# Start with default
config = get_default_config("lathe")

# Adjust to 50 machines
total = get_total_machine_count(config)
scale_factor = 50 / total

for station in config.stations:
    station.num_machines = max(1, int(station.num_machines * scale_factor))

# Setup automatic environment
setup_environment_config(config)

# Now config.environment has:
# - Optimal floor dimensions
# - Grid layout (8×7 for 50 machines)
# - Camera position tuned for view
# - LOD quality set to "medium"
```

### Example 2: Validate Machine Count

```python
from config_manager import validate_machine_count

valid, error = validate_machine_count(config)

if not valid:
    print(f"Error: {error}")
    # Error will be like: "Total machines (75) exceeds maximum of 70"
```

### Example 3: Export for Unity

```python
from config_manager import export_environment_for_unity

export_environment_for_unity(config, "configs/unity_config.json")

# Output structure:
# {
#   "factory_name": "...",
#   "machine_count": 50,
#   "environment": {
#     "floor": { "width": 28.0, "depth": 26.0, "height": 4.0 },
#     "grid": { "rows": 7, "cols": 8, "spacing": 3.0 },
#     "camera": { "distance": 16.8, "height": 10.4, "fov": 60 },
#     "rendering": { "lod_quality": "medium", "use_instancing": true }
#   }
# }
```

## Grid Layout Algorithm

The system calculates a balanced grid that:

1. **Minimizes aspect ratio** (prefers square layouts)
   - 50 machines → 7×8 grid (not 1×50)
   - 70 machines → 8×9 grid (not 2×35)

2. **Constrains per-side maximum** (max 10 per side)
   - Prevents extremely long corridors
   - Maintains visibility

3. **Respects margin** (2m around edges)
   - Prevents machines from touching walls
   - Allows navigation space

## Floor Sizing Examples

| Machines | Grid | Floor Size | Spacing | Camera Distance | LOD |
|----------|------|-----------|---------|-----------------|-----|
| 5 | 2×3 | 11m × 11m | 3.0m | 6.6m | high |
| 10 | 3×4 | 14m × 14m | 3.0m | 8.4m | high |
| 25 | 5×5 | 17m × 17m | 3.0m | 10.2m | high |
| 50 | 7×8 | 28m × 26m | 3.0m | 16.8m | medium |
| 70 | 8×9 | 32m × 30m | 3.0m | 19.2m | low |

## LOD (Level of Detail) Quality

Automatically set based on machine count:

| Machine Count | LOD Quality | Details |
|---------------|------------|---------|
| 1-20 | **high** | Full details, shadows, reflections |
| 21-50 | **medium** | Reduced textures, soft shadows |
| 51-70 | **low** | Simplified geometry, basic lighting |

## Integration with Android UI

The Android app can now handle machine count input:

```kotlin
// In Android configuration UI
val machineCount = intent.getIntExtra("machine_count", 20)

if (machineCount < 1 || machineCount > 70) {
    showError("Machine count must be 1-70")
} else {
    saveConfig(machineCount)  // Send to Python backend
}
```

Python backend receives it:
```python
config = load_config("factory_config.json")
assert 1 <= get_total_machine_count(config) <= 70

setup_environment_config(config)  # Auto-sizes everything
```

## Integration with Unity

Unity reads the exported configuration:

```json
// configs/unity_environment.json (auto-generated)
{
  "environment": {
    "floor": {
      "width": 28.0,
      "depth": 26.0,
      "height": 4.0
    },
    "grid": {
      "rows": 7,
      "cols": 8,
      "spacing": 3.0
    },
    "camera": {
      "distance": 16.8,
      "height": 10.4,
      "fov": 60,
      "type": "isometric"
    },
    "rendering": {
      "lod_quality": "medium",
      "use_instancing": true
    }
  }
}
```

Unity C# script reads this:
```csharp
public class EnvironmentSetup : MonoBehaviour
{
    public void LoadFromConfig(string configPath)
    {
        var config = JsonUtility.FromJson<UnityEnvironmentConfig>(
            File.ReadAllText(configPath)
        );
        
        // Resize floor
        floorCollider.size = new Vector3(
            config.environment.floor.width,
            config.environment.floor.depth,
            1f
        );
        
        // Adjust camera
        mainCamera.transform.position = new Vector3(
            0, 
            config.environment.camera.height,
            -config.environment.camera.distance
        );
        
        // Apply LOD
        switch (config.environment.rendering.lod_quality)
        {
            case "high": QualitySettings.SetQualityLevel(3); break;
            case "medium": QualitySettings.SetQualityLevel(2); break;
            case "low": QualitySettings.SetQualityLevel(1); break;
        }
    }
}
```

## Validation Checks

The system validates:

✓ Machine count 1-70  
✓ Grid layout feasibility  
✓ Floor size adequacy  
✓ Camera positioning  
✓ Performance (LOD quality)  

```python
from config_manager import validate_config

valid, errors = validate_config(config)

for error in errors:
    print(f"❌ {error}")

# Example errors:
# ❌ Total machines (75) exceeds maximum of 70
# ❌ Total machines (0) must be >= 1
```

## Performance Considerations

For large machine counts:

| Count | Recommendation |
|-------|---|
| 1-20 | Full quality, no optimizations needed |
| 21-50 | Use GPU instancing (use_instancing=true) |
| 51-70 | LOD textures, billboarded distant machines |

Configuration auto-enables instancing:
```python
"use_instancing": grid_rows * grid_cols > 30
```

## File Structure

```
python/
├── floor_layout_calculator.py           ← New: Grid layout engine
├── config_manager.py                    ← Updated: Environment config
├── example_dynamic_scaling.py           ← New: 5+ usage examples
├── DYNAMIC_SCALING_README.md            ← This file
└── configs/
    ├── factory_config.json              ← Main config
    ├── unity_environment.json           ← Exported for Unity
    └── lathe_default.json
```

## Running Examples

```bash
python python/example_dynamic_scaling.py
```

Outputs:
1. Machine count scaling (1-70)
2. Grid layout calculations
3. Environment adaptation details
4. Custom configuration creation
5. Unity export example

## Troubleshooting

**Problem:** "Total machines (81) exceeds maximum of 70"  
**Solution:** Reduce machine count or distribute across fewer stations

**Problem:** "Grid has low occupancy"  
**Solution:** This is a warning, not an error. Grid can have empty cells.

**Problem:** "Floor is very large (100×100m)"  
**Solution:** Reduce machine count. Large floors may impact performance.

**Problem:** FloorLayoutCalculator module not found  
**Solution:** System falls back to formula-based calculation. No error, just less optimized.

## API Reference

### FloorLayoutCalculator

```python
from floor_layout_calculator import FloorLayoutCalculator

calc = FloorLayoutCalculator(50)  # 50 machines

# Get grid layout
rows, cols = calc.calculate_grid_dimensions()
# Returns: (7, 8)

# Get floor dimensions
floor = calc.calculate_floor_dimensions()
# Returns: FloorDimensions(
#     width=28.0, depth=26.0, height=4.0, 
#     grid_spacing=3.0
# )

# Get machine positions
positions = calc.generate_machine_positions(machines_list)
# Returns: [MachinePosition(...), ...]

# Get complete environment config
env = calc.get_environment_config()
# Returns: {
#     'machine_count': 50,
#     'grid_rows': 7,
#     'grid_cols': 8,
#     'floor': {...},
#     'camera': {...},
#     'lighting': {...}
# }
```

### config_manager

```python
from config_manager import (
    setup_environment_config,
    get_total_machine_count,
    validate_machine_count,
    export_environment_for_unity,
)

# Setup auto-sizing
config = get_default_config("lathe")
setup_environment_config(config)

# Get total
total = get_total_machine_count(config)

# Validate
valid, error = validate_machine_count(config)

# Export
export_environment_for_unity(config, "path/to/output.json")
```

## Future Enhancements

- Dynamic machine addition/removal at runtime
- Multi-floor factory support
- Custom grid patterns (circular, U-shape, etc.)
- Machine clustering and grouping
- Performance metrics monitoring
- Real-time environment adjustment during simulation

## Questions?

See [example_dynamic_scaling.py](example_dynamic_scaling.py) for complete working examples.
