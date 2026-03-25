"""
config_manager.py — Factory Configuration Management

Central configuration system for the Digital Twin. The factory_config.json
file drives the entire system: Android writes it, Python reads it, Unity reads it.

Supports:
- Dynamic machine count (1-70 maximum)
- Automatic floor sizing based on machine count
- Environment adaptation (3D scene dimensions)
- Grid-based machine layout
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
import math

try:
    from floor_layout_calculator import FloorLayoutCalculator, FloorDimensions
except ImportError:
    FloorLayoutCalculator = None
    FloorDimensions = None


# ═══════════════════════════════════════════════════════════════════════
# MACHINE CATALOGUE — complete list of all machines per factory type
# ═══════════════════════════════════════════════════════════════════════

MACHINE_CATALOGUE: dict[str, list[dict]] = {
    "lathe": [
        {"id": "lathe_machine",     "name": "Lathe Machine",       "name_ta": "கடைசல் இயந்திரம்",     "default_cycle_time_sec": 45, "num_machines_default": 2, "icon_name": "lathe_machine"},
        {"id": "cnc_mill",          "name": "CNC Mill",            "name_ta": "சிஎன்சி மில்",          "default_cycle_time_sec": 60, "num_machines_default": 1, "icon_name": "cnc_mill"},
        {"id": "drill_press",       "name": "Drill Press",         "name_ta": "துரப்பண இயந்திரம்",     "default_cycle_time_sec": 30, "num_machines_default": 2, "icon_name": "drill_press"},
        {"id": "surface_grinder",   "name": "Surface Grinder",     "name_ta": "மேற்பரப்பு சாணை",       "default_cycle_time_sec": 55, "num_machines_default": 1, "icon_name": "surface_grinder"},
        {"id": "welding_station",   "name": "Welding Station",     "name_ta": "வெல்டிங் நிலையம்",     "default_cycle_time_sec": 50, "num_machines_default": 1, "icon_name": "welding_station"},
        {"id": "heat_treatment",    "name": "Heat Treatment",      "name_ta": "வெப்ப சிகிச்சை",       "default_cycle_time_sec": 90, "num_machines_default": 1, "icon_name": "heat_treatment"},
        {"id": "qc_inspection",     "name": "QC Inspection",       "name_ta": "தர ஆய்வு",             "default_cycle_time_sec": 25, "num_machines_default": 1, "icon_name": "qc_inspection"},
        {"id": "deburring",         "name": "Deburring",           "name_ta": "கூர் நீக்கம்",          "default_cycle_time_sec": 20, "num_machines_default": 1, "icon_name": "deburring"},
    ],
    "textile": [
        {"id": "spinning",    "name": "Spinning",       "name_ta": "நூற்பு",           "default_cycle_time_sec": 40, "num_machines_default": 3, "icon_name": "spinning"},
        {"id": "warping",     "name": "Warping",        "name_ta": "பாவு கட்டுதல்",    "default_cycle_time_sec": 35, "num_machines_default": 1, "icon_name": "warping"},
        {"id": "loom",        "name": "Loom",           "name_ta": "நெசவு தறி",        "default_cycle_time_sec": 50, "num_machines_default": 4, "icon_name": "loom"},
        {"id": "dyeing_vat",  "name": "Dyeing Vat",     "name_ta": "சாயத் தொட்டி",     "default_cycle_time_sec": 120, "num_machines_default": 2, "icon_name": "dyeing_vat"},
        {"id": "drying",      "name": "Drying",         "name_ta": "உலர்த்துதல்",      "default_cycle_time_sec": 60, "num_machines_default": 1, "icon_name": "drying"},
        {"id": "cutting",     "name": "Cutting",        "name_ta": "வெட்டுதல்",        "default_cycle_time_sec": 30, "num_machines_default": 2, "icon_name": "cutting"},
        {"id": "stitching",   "name": "Stitching",      "name_ta": "தையல்",            "default_cycle_time_sec": 45, "num_machines_default": 3, "icon_name": "stitching"},
        {"id": "qc_fold",     "name": "QC & Folding",   "name_ta": "தர ஆய்வு & மடிப்பு","default_cycle_time_sec": 20, "num_machines_default": 2, "icon_name": "qc_fold"},
    ],
    "food": [
        {"id": "mixer",            "name": "Mixer",             "name_ta": "கலவை இயந்திரம்",    "default_cycle_time_sec": 60, "num_machines_default": 2, "icon_name": "mixer"},
        {"id": "oven",             "name": "Oven",              "name_ta": "அடுப்பு",            "default_cycle_time_sec": 120, "num_machines_default": 1, "icon_name": "oven"},
        {"id": "cooling_conveyor", "name": "Cooling Conveyor",  "name_ta": "குளிர்விப்பு",       "default_cycle_time_sec": 90, "num_machines_default": 1, "icon_name": "cooling_conveyor"},
        {"id": "filling_machine",  "name": "Filling Machine",   "name_ta": "நிரப்பு இயந்திரம்",  "default_cycle_time_sec": 30, "num_machines_default": 2, "icon_name": "filling_machine"},
        {"id": "labelling",        "name": "Labelling",         "name_ta": "லேபிள் ஒட்டுதல்",   "default_cycle_time_sec": 15, "num_machines_default": 1, "icon_name": "labelling"},
        {"id": "qc_food",          "name": "QC Food",           "name_ta": "உணவு தர ஆய்வு",     "default_cycle_time_sec": 20, "num_machines_default": 1, "icon_name": "qc_food"},
    ],
    "electronics": [
        {"id": "pcb_machine",      "name": "PCB Machine",       "name_ta": "பிசிபி இயந்திரம்",     "default_cycle_time_sec": 45, "num_machines_default": 1, "icon_name": "pcb_machine"},
        {"id": "smd_placement",    "name": "SMD Placement",     "name_ta": "எஸ்எம்டி பொருத்துதல்", "default_cycle_time_sec": 30, "num_machines_default": 2, "icon_name": "smd_placement"},
        {"id": "reflow_oven",      "name": "Reflow Oven",       "name_ta": "ரிஃப்ளோ அடுப்பு",     "default_cycle_time_sec": 90, "num_machines_default": 1, "icon_name": "reflow_oven"},
        {"id": "manual_soldering", "name": "Manual Soldering",  "name_ta": "கைமுறை சாலிடரிங்",    "default_cycle_time_sec": 60, "num_machines_default": 2, "icon_name": "manual_soldering"},
        {"id": "aoi_testing",      "name": "AOI Testing",       "name_ta": "ஏஓஐ சோதனை",          "default_cycle_time_sec": 25, "num_machines_default": 1, "icon_name": "aoi_testing"},
        {"id": "final_assembly",   "name": "Final Assembly",    "name_ta": "இறுதி அசெம்பிளி",     "default_cycle_time_sec": 40, "num_machines_default": 2, "icon_name": "final_assembly"},
        {"id": "burn_in_test",     "name": "Burn-In Test",      "name_ta": "பர்ன்-இன் சோதனை",     "default_cycle_time_sec": 180, "num_machines_default": 1, "icon_name": "burn_in_test"},
        {"id": "packing",          "name": "Packing",           "name_ta": "பேக்கிங்",             "default_cycle_time_sec": 20, "num_machines_default": 2, "icon_name": "packing"},
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class StationConfig:
    """Configuration for a single factory station/machine."""
    id: int
    name: str
    name_ta: str
    icon: str
    cycle_time_sec: float
    num_machines: int
    position_x: float
    position_z: float
    buffer_capacity: int = 50
    eta_weibull: float = 500.0
    beta_weibull: float = 1.8
    mttr_minutes: float = 30.0


@dataclass
class EnvironmentConfig:
    """Configuration for 3D environment and floor layout.
    
    Automatically calculated based on total machine count.
    Adapts floor dimensions, camera position, and lighting.
    """
    floor_width: float = 20.0
    floor_depth: float = 20.0
    floor_height: float = 4.0
    grid_spacing: float = 3.0
    grid_rows: int = 0
    grid_cols: int = 0
    camera_distance: float = 20.0
    camera_height: float = 10.0
    camera_fov: int = 60
    ambient_intensity: float = 0.8
    main_light_intensity: float = 1.2
    main_light_rotation: dict = field(default_factory=lambda: {"x": 45, "y": 45, "z": 0})
    max_render_distance: float = 200.0
    lod_quality: str = "high"  # "low", "medium", "high"


@dataclass
class FactoryConfig:
    """Complete factory configuration that drives the entire system.

    Android writes this, Python reads it for simulation,
    Unity reads it to build the 3D scene.
    
    Supports dynamic scaling up to 70 machines with automatic
    floor sizing and environment adaptation.
    """
    factory_type: str
    factory_name: str
    mode: str = "static"
    language: str = "en"
    demand: int = 200
    operators: int = 2
    shift_hours: float = 8.0
    machine_condition: str = "average"
    batch_size: int = 1
    unit_value_rupees: float = 100.0
    stations: list[StationConfig] = field(default_factory=list)
    environment: Optional[EnvironmentConfig] = field(default_factory=EnvironmentConfig)
    
    # Machine count limits
    MIN_MACHINES = 1
    MAX_MACHINES = 70


# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION MANAGER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def load_config(path: str) -> FactoryConfig:
    """Load factory configuration from a JSON file.

    Args:
        path: Path to the factory_config.json file.

    Returns:
        FactoryConfig object populated from the JSON.

    Raises:
        FileNotFoundError: If the config file doesn't exist.
        json.JSONDecodeError: If the JSON is malformed.

    Example:
        >>> config = load_config("configs/lathe_default.json")
        >>> print(config.factory_type)  # "lathe"
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    stations = []
    for s in data.get("stations", []):
        stations.append(StationConfig(
            id=s["id"],
            name=s["name"],
            name_ta=s.get("name_ta", s["name"]),
            icon=s["icon"],
            cycle_time_sec=float(s["cycle_time_sec"]),
            num_machines=int(s["num_machines"]),
            position_x=float(s.get("position_x", 0)),
            position_z=float(s.get("position_z", 0)),
            buffer_capacity=int(s.get("buffer_capacity", 50)),
            eta_weibull=float(s.get("eta_weibull", 500.0)),
            beta_weibull=float(s.get("beta_weibull", 1.8)),
            mttr_minutes=float(s.get("mttr_minutes", 30.0)),
        ))

    return FactoryConfig(
        factory_type=data["factory_type"],
        factory_name=data["factory_name"],
        mode=data.get("mode", "static"),
        language=data.get("language", "en"),
        demand=int(data.get("demand", 200)),
        operators=int(data.get("operators", 2)),
        shift_hours=float(data.get("shift_hours", 8.0)),
        machine_condition=data.get("machine_condition", "average"),
        batch_size=int(data.get("batch_size", 1)),
        unit_value_rupees=float(data.get("unit_value_rupees", 100.0)),
        stations=stations,
    )


def save_config(config: FactoryConfig, path: str) -> None:
    """Save factory configuration to a JSON file.

    Args:
        config: The FactoryConfig object to save.
        path: Output file path (will be created/overwritten).

    Example:
        >>> save_config(config, "configs/my_factory.json")
    """
    data = {
        "factory_type": config.factory_type,
        "factory_name": config.factory_name,
        "mode": config.mode,
        "language": config.language,
        "demand": config.demand,
        "operators": config.operators,
        "shift_hours": config.shift_hours,
        "machine_condition": config.machine_condition,
        "batch_size": config.batch_size,
        "unit_value_rupees": config.unit_value_rupees,
        "stations": [asdict(s) for s in config.stations],
    }
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def validate_config(config: FactoryConfig) -> tuple[bool, list[str]]:
    """Validate that a factory configuration has all required fields and valid values.

    Args:
        config: The FactoryConfig to validate.

    Returns:
        Tuple of (is_valid, list_of_error_messages).

    Example:
        >>> valid, errors = validate_config(config)
        >>> if not valid: print(errors)
    """
    errors: list[str] = []

    # Check factory type
    valid_types = list(MACHINE_CATALOGUE.keys())
    if config.factory_type not in valid_types:
        errors.append(f"factory_type must be one of {valid_types}, got '{config.factory_type}'")

    # Check factory name
    if not config.factory_name or len(config.factory_name.strip()) == 0:
        errors.append("factory_name is required and cannot be empty")

    # Check mode
    if config.mode not in ("static", "realtime"):
        errors.append(f"mode must be 'static' or 'realtime', got '{config.mode}'")

    # Check language
    if config.language not in ("en", "ta"):
        errors.append(f"language must be 'en' or 'ta', got '{config.language}'")

    # Check numeric fields
    if config.demand <= 0:
        errors.append(f"demand must be positive, got {config.demand}")
    if config.operators <= 0:
        errors.append(f"operators must be positive, got {config.operators}")
    if config.shift_hours <= 0 or config.shift_hours > 24:
        errors.append(f"shift_hours must be between 0 and 24, got {config.shift_hours}")
    if config.machine_condition not in ("good", "average", "poor"):
        errors.append(f"machine_condition must be 'good', 'average', or 'poor', got '{config.machine_condition}'")

    # Check stations
    if len(config.stations) == 0:
        errors.append("stations list cannot be empty")

    station_ids = set()
    total_machines = 0
    for i, s in enumerate(config.stations):
        if s.id in station_ids:
            errors.append(f"Duplicate station id: {s.id}")
        station_ids.add(s.id)

        if s.cycle_time_sec <= 0:
            errors.append(f"Station {s.id}: cycle_time_sec must be positive, got {s.cycle_time_sec}")
        if s.num_machines <= 0:
            errors.append(f"Station {s.id}: num_machines must be positive, got {s.num_machines}")
        if not s.name:
            errors.append(f"Station {s.id}: name is required")
        if not s.icon:
            errors.append(f"Station {s.id}: icon is required")
        
        total_machines += s.num_machines
    
    # Check total machine count (1-70 limit)
    if total_machines < FactoryConfig.MIN_MACHINES:
        errors.append(f"Total machines ({total_machines}) must be >= {FactoryConfig.MIN_MACHINES}")
    if total_machines > FactoryConfig.MAX_MACHINES:
        errors.append(f"Total machines ({total_machines}) exceeds maximum of {FactoryConfig.MAX_MACHINES}")

    return (len(errors) == 0, errors)


def config_to_dict(config: FactoryConfig) -> dict:
    """Convert a FactoryConfig to a serializable dictionary.

    Args:
        config: The FactoryConfig to convert.

    Returns:
        Dictionary suitable for JSON serialization.
    """
    return {
        "factory_type": config.factory_type,
        "factory_name": config.factory_name,
        "mode": config.mode,
        "language": config.language,
        "demand": config.demand,
        "operators": config.operators,
        "shift_hours": config.shift_hours,
        "machine_condition": config.machine_condition,
        "batch_size": config.batch_size,
        "unit_value_rupees": config.unit_value_rupees,
        "stations": [asdict(s) for s in config.stations],
    }


def get_default_config(factory_type: str) -> FactoryConfig:
    """Get a default configuration for a given factory type.

    Args:
        factory_type: One of 'lathe', 'textile', 'food', 'electronics'.

    Returns:
        FactoryConfig with default machines for the factory type.

    Raises:
        ValueError: If factory_type is not recognized.
    """
    if factory_type not in MACHINE_CATALOGUE:
        raise ValueError(f"Unknown factory type: '{factory_type}'. Choose from {list(MACHINE_CATALOGUE.keys())}")

    machines = MACHINE_CATALOGUE[factory_type]
    stations = []
    for i, m in enumerate(machines[:5]):  # default: first 5 machines
        stations.append(StationConfig(
            id=i + 1,
            name=m["name"],
            name_ta=m["name_ta"],
            icon=m["icon_name"],
            cycle_time_sec=m["default_cycle_time_sec"],
            num_machines=m["num_machines_default"],
            position_x=float(i * 6),
            position_z=0.0,
        ))

    name_map = {
        "lathe": "Precision Lathe Factory",
        "textile": "Tamil Nadu Textile Mill",
        "food": "Fresh Foods Processing",
        "electronics": "PCB Assembly Plant",
    }

    return FactoryConfig(
        factory_type=factory_type,
        factory_name=name_map.get(factory_type, f"{factory_type.title()} Factory"),
        stations=stations,
    )


# ═══════════════════════════════════════════════════════════════════════
# ENVIRONMENT CONFIGURATION & MACHINE SCALING
# ═══════════════════════════════════════════════════════════════════════

def get_total_machine_count(config: FactoryConfig) -> int:
    """
    Calculate total machine count from all stations.
    
    Args:
        config: Factory configuration
    
    Returns:
        Total count of machines across all stations
    """
    return sum(s.num_machines for s in config.stations)


def validate_machine_count(config: FactoryConfig) -> tuple[bool, Optional[str]]:
    """
    Validate that machine count is within allowed limits (1-70).
    
    Args:
        config: Factory configuration to validate
    
    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    total = get_total_machine_count(config)
    
    if total < FactoryConfig.MIN_MACHINES:
        return False, f"Total machines ({total}) must be >= {FactoryConfig.MIN_MACHINES}"
    
    if total > FactoryConfig.MAX_MACHINES:
        return False, f"Total machines ({total}) exceeds maximum of {FactoryConfig.MAX_MACHINES}"
    
    return True, None


def setup_environment_config(config: FactoryConfig) -> FactoryConfig:
    """
    Automatically set up environment configuration based on machine count.
    
    Uses FloorLayoutCalculator to:
    - Calculate optimal floor dimensions
    - Generate grid layout
    - Adjust camera and lighting
    - Set LOD quality based on machine count
    
    Modifies config in-place.
    
    Args:
        config: Factory configuration to update
    
    Returns:
        Updated configuration with environment settings
    
    Raises:
        ValueError: If machine count exceeds limits
        ImportError: If FloorLayoutCalculator not available
    """
    # Validate machine count first
    valid, error = validate_machine_count(config)
    if not valid:
        raise ValueError(error)
    
    total_machines = get_total_machine_count(config)
    
    # If FloorLayoutCalculator is not available, use fallback
    if FloorLayoutCalculator is None:
        config.environment = _setup_environment_fallback(total_machines)
    else:
        try:
            calculator = FloorLayoutCalculator(total_machines)
            
            # Get environment config
            env_dict = calculator.get_environment_config()
            floor = calculator.calculate_floor_dimensions()
            
            # Create EnvironmentConfig
            config.environment = EnvironmentConfig(
                floor_width=floor.width,
                floor_depth=floor.depth,
                floor_height=floor.height,
                grid_spacing=floor.grid_spacing,
                grid_rows=env_dict['grid_rows'],
                grid_cols=env_dict['grid_cols'],
                camera_distance=env_dict['camera']['distance'],
                camera_height=env_dict['camera']['height'],
                camera_fov=env_dict['camera']['fov'],
                ambient_intensity=env_dict['lighting']['ambient_intensity'],
                main_light_intensity=env_dict['lighting']['main_light_intensity'],
                main_light_rotation=env_dict['lighting']['main_light_rotation'],
                lod_quality=_calculate_lod_quality(total_machines),
            )
            
            # Update machine positions based on layout
            positions = calculator.generate_machine_positions([
                {'id': s.id, 'name': s.name}
                for s in config.stations
                for _ in range(s.num_machines)
            ])
            
            # Update station positions (spread across grid)
            pos_idx = 0
            for station in config.stations:
                if pos_idx < len(positions):
                    pos = positions[pos_idx]
                    station.position_x = pos.position_x
                    station.position_z = pos.position_z
                    pos_idx += station.num_machines
        
        except Exception as e:
            print(f"Warning: Could not set up environment from calculator: {e}")
            config.environment = _setup_environment_fallback(total_machines)
    
    return config


def _setup_environment_fallback(total_machines: int) -> EnvironmentConfig:
    """
    Fallback environment setup if FloorLayoutCalculator unavailable.
    
    Args:
        total_machines: Total machine count
    
    Returns:
        EnvironmentConfig with calculated dimensions
    """
    # Calculate grid dimensions
    grid_cols = math.ceil(math.sqrt(total_machines))
    grid_rows = math.ceil(total_machines / grid_cols)
    
    # Scale based on machine count
    base_spacing = 3.0
    floor_width = max(20.0, grid_cols * base_spacing + 4.0)
    floor_depth = max(20.0, grid_rows * base_spacing + 4.0)
    
    camera_dist = max(20.0, floor_width * 0.6)
    camera_height = max(10.0, floor_depth * 0.4)
    
    return EnvironmentConfig(
        floor_width=floor_width,
        floor_depth=floor_depth,
        floor_height=4.0,
        grid_spacing=base_spacing,
        grid_rows=grid_rows,
        grid_cols=grid_cols,
        camera_distance=camera_dist,
        camera_height=camera_height,
        camera_fov=60,
        lod_quality=_calculate_lod_quality(total_machines),
    )


def _calculate_lod_quality(machine_count: int) -> str:
    """
    Calculate LOD (Level of Detail) quality based on machine count.
    
    Args:
        machine_count: Total number of machines
    
    Returns:
        Quality level: "high" (1-20), "medium" (21-50), "low" (51-70)
    """
    if machine_count <= 20:
        return "high"
    elif machine_count <= 50:
        return "medium"
    else:
        return "low"


def export_environment_for_unity(config: FactoryConfig, output_path: str) -> None:
    """
    Export environment configuration in a format suitable for Unity.
    
    Creates a JSON file that Unity can read to set up the 3D scene.
    
    Args:
        config: Factory configuration with environment settings
        output_path: Where to save the exported configuration
    """
    if config.environment is None:
        raise ValueError("Environment not configured. Call setup_environment_config() first.")
    
    env = config.environment
    
    unity_config = {
        "factory_name": config.factory_name,
        "factory_type": config.factory_type,
        "machine_count": get_total_machine_count(config),
        "environment": {
            "floor": {
                "width": env.floor_width,
                "depth": env.floor_depth,
                "height": env.floor_height,
                "material": "concrete"
            },
            "grid": {
                "rows": env.grid_rows,
                "cols": env.grid_cols,
                "spacing": env.grid_spacing
            },
            "camera": {
                "distance": env.camera_distance,
                "height": env.camera_height,
                "fov": env.camera_fov,
                "type": "isometric"
            },
            "lighting": {
                "ambient_intensity": env.ambient_intensity,
                "main_light_intensity": env.main_light_intensity,
                "main_light_rotation": env.main_light_rotation,
                "shadows": True
            },
            "rendering": {
                "lod_quality": env.lod_quality,
                "max_render_distance": env.max_render_distance,
                "use_instancing": env.grid_rows * env.grid_cols > 30
            }
        },
        "stations": [
            {
                "id": s.id,
                "name": s.name,
                "name_ta": s.name_ta,
                "icon": s.icon,
                "num_machines": s.num_machines,
                "position_x": s.position_x,
                "position_z": s.position_z,
                "cycle_time_sec": s.cycle_time_sec,
            }
            for s in config.stations
        ]
    }
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unity_config, f, indent=2, ensure_ascii=False)
