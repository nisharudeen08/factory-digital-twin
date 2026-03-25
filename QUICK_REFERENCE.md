# Dynamic Factory Scaling - Quick Reference

## ⚡ One-Line Activation

```python
from config_manager import setup_environment_config
setup_environment_config(config)  # That's it!
```

---

## 📊 Machine Count Ranges

```
1-20 machines:   ✓ high quality, no special handling
21-50 machines:  ✓ medium quality, GPU instancing enabled
51-70 machines:  ✓ low quality, optimized for speed
```

---

## 🎯 Key Functions

### Setup Environment
```python
setup_environment_config(config)
# → Auto-sizes floor, grid, camera, LOD
# → Modifies config.environment in-place
```

### Validate Machine Count
```python
valid, error = validate_machine_count(config)
if not valid:
    print(f"Error: {error}")
```

### Get Total Machines
```python
total = get_total_machine_count(config)
# → Sums all num_machines across stations
```

### Export for Unity
```python
export_environment_for_unity(config, "path/to/config.json")
# → Creates JSON ready for Unity to read
```

---

## 📐 Grid Calculations

| Machines | Grid | Floor | Camera |
|----------|------|-------|--------|
| 1-5 | 2×3 | 11m | 6.6m |
| 6-10 | 3×4 | 14m | 8.4m |
| 11-20 | 4×5 to 5×4 | 16-17m | 9.6-10.2m |
| 21-35 | 5×7 to 7×5 | 19-22m | 11.4-13.2m |
| 36-50 | 7×7 to 8×7 | 22-25m | 13.2-15m |
| 51-70 | 8×8 to 9×8 | 25-28m | 15-16.8m |

---

## 🔧 Integration Steps

### 1. Android UI
```kotlin
// Add slider for machine count
val machineCount: Int = slider.progress  // 1-70
sendConfig(machineCount)
```

### 2. Python API
```python
@app.post("/api/config")
async def receive_config(data: dict):
    config = create_config_from_data(data)
    setup_environment_config(config)  # ← Magic happens here
    export_environment_for_unity(config, "output.json")
    return {"status": "ready"}
```

### 3. Unity
```csharp
var config = LoadEnvironmentConfig("path/to/config.json");
ResizeFloor(config.environment.floor);
PositionCamera(config.environment.camera);
SetLODQuality(config.environment.lod_quality);
```

---

## ✅ Validation Checklist

```python
from config_manager import validate_config

valid, errors = validate_config(config)
# Checks:
# ✓ Factory type valid
# ✓ Machine count 1-70
# ✓ All fields present
# ✓ Numeric ranges valid
# ✓ No duplicate IDs
```

---

## 🎮 LOD Quality

```python
# Automatic based on machine count
count <= 20:     "high"     # Full details, shadows, reflections
count <= 50:     "medium"   # Reduced textures, soft shadows
count <= 70:     "low"      # Simple geometry, basic lighting
```

---

## 📝 Environment Config Structure

```json
{
  "floor": {
    "width": 28.0,
    "depth": 26.0,
    "height": 4.0,
    "grid_spacing": 3.0
  },
  "grid": {
    "rows": 7,
    "cols": 8
  },
  "camera": {
    "distance": 16.8,
    "height": 10.4,
    "fov": 60
  },
  "rendering": {
    "lod_quality": "medium",
    "use_instancing": true
  }
}
```

---

## 🚀 Common Workflows

### Workflow 1: Create Factory with N Machines
```python
config = get_default_config("textile")
# Adjust to N machines
total = get_total_machine_count(config)
for s in config.stations:
    s.num_machines = max(1, int(s.num_machines * N / total))
# Auto-setup
setup_environment_config(config)
```

### Workflow 2: Validate & Export
```python
valid, errors = validate_config(config)
if valid:
    export_environment_for_unity(config, "output.json")
else:
    for err in errors:
        print(f"Error: {err}")
```

### Workflow 3: Load & Update
```python
config = load_config("factory_config.json")
setup_environment_config(config)
print(f"Floor: {config.environment.floor_width}m")
```

---

## 🐛 Debugging Commands

```python
from floor_layout_calculator import FloorLayoutCalculator

calc = FloorLayoutCalculator(50)

# See grid
rows, cols = calc.calculate_grid_dimensions()
print(f"Grid: {rows}×{cols}")

# See floor
floor = calc.calculate_floor_dimensions()
print(f"Floor: {floor.width}×{floor.depth}m")

# See positions
positions = calc.generate_machine_positions(machines)
for p in positions:
    print(f"{p.name}: ({p.position_x}, {p.position_z})")

# See full config
config = calc.get_environment_config()
print(json.dumps(config, indent=2))
```

---

## ⚠️ Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| "exceeds maximum of 70" | Too many machines | Reduce count |
| "must be >= 1" | No machines | Add machines |
| "Duplicate station id" | Multiple stations with same ID | Rename station |
| "module not found" | Missing import | Check file path |

---

## 📂 File Locations

```
python/
├── floor_layout_calculator.py   ← Grid engine
├── config_manager.py            ← Config management
├── example_dynamic_scaling.py   ← Examples
├── test_scaling.py              ← Test script
└── configs/
    ├── factory_config.json      ← Input
    └── unity_environment.json   ← Output
```

---

## 🧪 Run Tests

```bash
# Quick validation
python python/test_scaling.py

# Comprehensive examples
python python/example_dynamic_scaling.py
```

---

## 💡 Pro Tips

1. **Always call `setup_environment_config()`** after changing machine count
2. **Export to Unity** after each configuration change
3. **Validate first** before exporting: `validate_config(config)`
4. **Check LOD** for 50+ machines to ensure performance
5. **Use `get_total_machine_count()`** to verify actual count

---

## 🔗 Cross-References

- **Full Details:** See [DYNAMIC_SCALING_README.md](DYNAMIC_SCALING_README.md)
- **Integration Steps:** See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Implementation Details:** See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Working Examples:** Run `example_dynamic_scaling.py`

---

## Support

**Issue?** Check [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md#troubleshooting)

**Need example?** See `example_dynamic_scaling.py` (5+ examples)

**Want full API?** Read [DYNAMIC_SCALING_README.md](DYNAMIC_SCALING_README.md)
