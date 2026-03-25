"""
example_dynamic_scaling.py — Example: Dynamic Machine Scaling with Adaptive Environment

Demonstrates:
1. Creating a factory configuration
2. Scaling machine count (1-70)
3. Automatic floor sizing
4. Environment adaptation for 3D rendering
5. Exporting configuration for Unity

Usage:
    python example_dynamic_scaling.py
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import (
    FactoryConfig, StationConfig, EnvironmentConfig,
    get_default_config, setup_environment_config,
    get_total_machine_count, validate_machine_count,
    validate_config, export_environment_for_unity,
)
from floor_layout_calculator import FloorLayoutCalculator


def example_1_basic_scaling():
    """Example 1: Basic machine count scaling."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Machine Count Scaling (1-70)")
    print("="*70)
    
    # Start with default config
    config = get_default_config("lathe")
    
    test_counts = [5, 10, 25, 50, 70]
    
    for target_count in test_counts:
        # Create a new config with adjusted machine count
        test_config = get_default_config("lathe")
        
        # Scale machines (distribute across stations)
        total_currently = get_total_machine_count(test_config)
        scale_factor = target_count / total_currently
        
        for station in test_config.stations:
            station.num_machines = max(1, int(station.num_machines * scale_factor))
        
        # Adjust last station to hit exact target
        current = get_total_machine_count(test_config)
        if current != target_count:
            diff = target_count - current
            test_config.stations[-1].num_machines += diff
        
        # Validate
        valid, error = validate_machine_count(test_config)
        
        print(f"\nTarget machines: {target_count}")
        print(f"  Valid: {valid}")
        if not valid:
            print(f"  Error: {error}")
        else:
            print(f"  ✓ Configuration valid for {target_count} machines")
            
            # Setup environment
            setup_environment_config(test_config)
            env = test_config.environment
            
            print(f"  Floor dimensions: {env.floor_width:.1f}m × {env.floor_depth:.1f}m")
            print(f"  Grid layout: {env.grid_rows} rows × {env.grid_cols} cols")
            print(f"  LOD quality: {env.lod_quality}")


def example_2_grid_layout():
    """Example 2: Understanding grid layout calculations."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Grid Layout Calculations")
    print("="*70)
    
    test_counts = [1, 4, 9, 16, 25, 36, 48, 64, 70]
    
    print("\nMachine Count → Grid Layout → Floor Size")
    print("-" * 70)
    
    for count in test_counts:
        calculator = FloorLayoutCalculator(count)
        rows, cols = calculator.calculate_grid_dimensions()
        floor = calculator.calculate_floor_dimensions()
        
        occupancy = count / (rows * cols)
        
        print(
            f"  {count:2d} machines → {rows}×{cols} grid → "
            f"{floor.width:.1f}m × {floor.depth:.1f}m floor "
            f"({occupancy:.0%} full)"
        )


def example_3_environment_adaptation():
    """Example 3: How environment adapts to machine count."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Environment Adaptation")
    print("="*70)
    
    configs_to_test = [
        ("Small factory", 10),
        ("Medium factory", 30),
        ("Large factory", 70),
    ]
    
    for factory_name, machine_count in configs_to_test:
        print(f"\n{factory_name} ({machine_count} machines):")
        
        # Create config
        config = get_default_config("textile")
        
        # Scale to target machine count
        total = get_total_machine_count(config)
        for station in config.stations:
            station.num_machines = max(1, int(station.num_machines * machine_count / total))
        
        # Fine-tune to exact count
        current = get_total_machine_count(config)
        if current != machine_count:
            config.stations[-1].num_machines += machine_count - current
        
        # Setup environment
        setup_environment_config(config)
        env = config.environment
        
        print(f"  Floor: {env.floor_width:.1f}m × {env.floor_depth:.1f}m × {env.floor_height:.1f}m")
        print(f"  Camera distance: {env.camera_distance:.1f}m")
        print(f"  Camera height: {env.camera_height:.1f}m")
        print(f"  Ambient light: {env.ambient_intensity}")
        print(f"  Main light: {env.main_light_intensity}")
        print(f"  LOD quality: {env.lod_quality}")
        print(f"  Use instancing: {env.grid_rows * env.grid_cols > 30}")


def example_4_create_custom_config():
    """Example 4: Creating a custom factory configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Custom Factory Configuration")
    print("="*70)
    
    # Create custom stations
    stations = [
        StationConfig(
            id=1,
            name="Input Queue",
            name_ta="உள்ளீட்டு வரிசை",
            icon="input",
            cycle_time_sec=0,
            num_machines=3,  # 3 input buffers
            position_x=0,
            position_z=0,
        ),
        StationConfig(
            id=2,
            name="Processing Unit",
            name_ta="செயல்பாட்டு அலகு",
            icon="processor",
            cycle_time_sec=60,
            num_machines=20,  # 20 machines in processing
            position_x=10,
            position_z=0,
        ),
        StationConfig(
            id=3,
            name="Quality Check",
            name_ta="தர சரிபார்ப்பு",
            icon="qc",
            cycle_time_sec=30,
            num_machines=10,  # 10 QC stations
            position_x=20,
            position_z=0,
        ),
        StationConfig(
            id=4,
            name="Packaging",
            name_ta="பொதிதல்",
            icon="pack",
            cycle_time_sec=20,
            num_machines=7,  # 7 packaging lines
            position_x=30,
            position_z=0,
        ),
    ]
    
    # Create factory config
    config = FactoryConfig(
        factory_type="electronics",
        factory_name="Advanced Assembly Line",
        mode="realtime",
        language="ta",
        demand=500,
        operators=15,
        shift_hours=8.0,
        machine_condition="good",
        batch_size=10,
        unit_value_rupees=500.0,
        stations=stations,
    )
    
    total = get_total_machine_count(config)
    print(f"\nFactory: {config.factory_name}")
    print(f"Type: {config.factory_type}")
    print(f"Total machines: {total}")
    print(f"Demand: {config.demand} units/shift")
    print(f"Operators: {config.operators}")
    
    # Validate
    valid, errors = validate_config(config)
    if valid:
        print("\n✓ Configuration is VALID")
    else:
        print("\n✗ Validation errors:")
        for err in errors:
            print(f"  - {err}")
        return
    
    # Setup environment
    setup_environment_config(config)
    env = config.environment
    
    print(f"\nEnvironment Configuration:")
    print(f"  Floor: {env.floor_width:.1f}m × {env.floor_depth:.1f}m")
    print(f"  Grid: {env.grid_rows}×{env.grid_cols}")
    print(f"  Camera distance: {env.camera_distance:.1f}m")
    print(f"  LOD: {env.lod_quality}")


def example_5_export_for_unity():
    """Example 5: Export configuration for Unity."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Configuration for Unity")
    print("="*70)
    
    # Create a medium-sized factory
    config = get_default_config("electronics")
    
    # Scale to 35 machines
    for station in config.stations:
        station.num_machines = 7
    
    # Setup environment
    setup_environment_config(config)
    
    # Export
    output_path = "configs/unity_environment.json"
    export_environment_for_unity(config, output_path)
    
    print(f"\n✓ Exported to: {output_path}")
    
    # Show a sample of the output
    with open(output_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\nExported configuration structure:")
    print(json.dumps({
        "factory_name": data["factory_name"],
        "machine_count": data["machine_count"],
        "environment": {
            "floor": data["environment"]["floor"],
            "grid": data["environment"]["grid"],
            "camera": data["environment"]["camera"],
            "rendering": data["environment"]["rendering"],
        }
    }, indent=2))


def main():
    """Run all examples."""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█  DYNAMIC FACTORY SCALING - COMPREHENSIVE EXAMPLES".ljust(69) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    try:
        example_1_basic_scaling()
        example_2_grid_layout()
        example_3_environment_adaptation()
        example_4_create_custom_config()
        example_5_export_for_unity()
        
        print("\n" + "█" * 70)
        print("█  ALL EXAMPLES COMPLETED SUCCESSFULLY".ljust(69) + "█")
        print("█" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
