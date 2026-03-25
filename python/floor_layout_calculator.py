"""
floor_layout_calculator.py — Dynamic Factory Floor Layout & Environment Sizing

Handles:
- Dynamic floor sizing based on machine count (1-70 max)
- Automatic grid positioning of machines
- Environment scaling (Unity 3D scene dimensions)
- Spacing and layout optimization
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class FloorDimensions:
    """Physical dimensions of the factory floor."""
    width: float      # X-axis (meters)
    depth: float      # Z-axis (meters)
    height: float     # Y-axis (meters) - for ceiling
    grid_spacing: float  # Distance between machine positions


@dataclass
class MachinePosition:
    """Position of a machine in 3D space."""
    machine_id: int
    name: str
    position_x: float
    position_z: float
    grid_row: int
    grid_col: int


class FloorLayoutCalculator:
    """Dynamically calculates floor layout based on total machine count."""
    
    # Maximum allowed machines per side of a grid
    MAX_MACHINES_PER_SIDE = 10
    MAX_TOTAL_MACHINES = 70
    
    # Base dimensions (in Unity meters - adjust to your scale)
    BASE_MACHINE_SPACING = 3.0  # Distance between machine centers
    MIN_FLOOR_WIDTH = 10.0
    MIN_FLOOR_DEPTH = 10.0
    FLOOR_HEIGHT = 4.0
    
    # Spacing around grid edges
    EDGE_MARGIN = 2.0
    
    def __init__(self, total_machines: int):
        """
        Initialize layout calculator.
        
        Args:
            total_machines: Total count of machines (1-70)
        
        Raises:
            ValueError: If machine count exceeds 70 or is less than 1
        """
        if total_machines < 1 or total_machines > self.MAX_TOTAL_MACHINES:
            raise ValueError(
                f"Machine count must be 1-{self.MAX_TOTAL_MACHINES}, "
                f"got {total_machines}"
            )
        self.total_machines = total_machines
    
    def calculate_grid_dimensions(self) -> Tuple[int, int]:
        """
        Calculate optimal grid dimensions for machine placement.
        
        Returns most square-like grid (rows, cols) that fits all machines.
        
        Returns:
            Tuple of (rows, cols) where rows * cols >= total_machines
        """
        # Find most balanced grid
        sqrt_machines = math.ceil(math.sqrt(self.total_machines))
        
        # Ensure it doesn't exceed MAX_MACHINES_PER_SIDE
        rows = min(sqrt_machines, self.MAX_MACHINES_PER_SIDE)
        cols = math.ceil(self.total_machines / rows)
        
        # Make sure we don't exceed max per side
        while cols > self.MAX_MACHINES_PER_SIDE:
            rows += 1
            cols = math.ceil(self.total_machines / rows)
        
        return rows, cols
    
    def calculate_floor_dimensions(self) -> FloorDimensions:
        """
        Calculate floor dimensions based on machine count.
        
        Adapts floor size to accommodate all machines in a balanced grid.
        
        Returns:
            FloorDimensions with width, depth, height, and grid spacing
        """
        rows, cols = self.calculate_grid_dimensions()
        
        # Calculate dimensions needed for grid
        grid_width = cols * self.BASE_MACHINE_SPACING
        grid_depth = rows * self.BASE_MACHINE_SPACING
        
        # Add margins around grid
        floor_width = max(
            grid_width + (2 * self.EDGE_MARGIN),
            self.MIN_FLOOR_WIDTH
        )
        floor_depth = max(
            grid_depth + (2 * self.EDGE_MARGIN),
            self.MIN_FLOOR_DEPTH
        )
        
        return FloorDimensions(
            width=floor_width,
            depth=floor_depth,
            height=self.FLOOR_HEIGHT,
            grid_spacing=self.BASE_MACHINE_SPACING
        )
    
    def generate_machine_positions(
        self, 
        machines: List[dict]
    ) -> List[MachinePosition]:
        """
        Generate 3D positions for all machines in ordered grid layout.
        
        Places machines in a grid pattern starting from top-left,
        reading left-to-right, top-to-bottom.
        
        Args:
            machines: List of machine dicts, each containing 'id' and 'name'
        
        Returns:
            List of MachinePosition objects with X and Z coordinates
        
        Raises:
            ValueError: If number of machines doesn't match total_machines
        """
        if len(machines) != self.total_machines:
            raise ValueError(
                f"Expected {self.total_machines} machines, got {len(machines)}"
            )
        
        rows, cols = self.calculate_grid_dimensions()
        floor = self.calculate_floor_dimensions()
        
        # Calculate starting position (top-left corner of grid)
        start_x = self.EDGE_MARGIN
        start_z = self.EDGE_MARGIN
        
        positions = []
        
        for idx, machine in enumerate(machines):
            # Calculate grid position
            grid_row = idx // cols
            grid_col = idx % cols
            
            # Calculate 3D position
            position_x = start_x + (grid_col * floor.grid_spacing)
            position_z = start_z + (grid_row * floor.grid_spacing)
            
            positions.append(MachinePosition(
                machine_id=machine.get('id', idx + 1),
                name=machine.get('name', f'Machine_{idx + 1}'),
                position_x=position_x,
                position_z=position_z,
                grid_row=grid_row,
                grid_col=grid_col
            ))
        
        return positions
    
    def get_environment_config(self) -> dict:
        """
        Get complete environment configuration for Unity/3D rendering.
        
        Returns:
            Dict with floor dimensions and scaling info
        """
        floor = self.calculate_floor_dimensions()
        rows, cols = self.calculate_grid_dimensions()
        
        return {
            "machine_count": self.total_machines,
            "grid_rows": rows,
            "grid_cols": cols,
            "floor": {
                "width": floor.width,
                "depth": floor.depth,
                "height": floor.height,
                "spacing": floor.grid_spacing
            },
            "camera": {
                "distance": self._calculate_camera_distance(floor),
                "height": self._calculate_camera_height(floor),
                "fov": 60
            },
            "lighting": {
                "ambient_intensity": 0.8,
                "main_light_intensity": 1.2,
                "main_light_rotation": {"x": 45, "y": 45, "z": 0}
            }
        }
    
    def _calculate_camera_distance(self, floor: FloorDimensions) -> float:
        """Calculate optimal camera distance based on floor size."""
        diagonal = math.sqrt(floor.width**2 + floor.depth**2)
        return diagonal * 0.6
    
    def _calculate_camera_height(self, floor: FloorDimensions) -> float:
        """Calculate optimal camera height for isometric view."""
        max_dim = max(floor.width, floor.depth)
        return max_dim * 0.4
    
    def validate_configuration(self) -> dict:
        """
        Validate that configuration is valid and return summary.
        
        Returns:
            Dict with validation status and warnings
        """
        warnings = []
        
        if self.total_machines > 50:
            warnings.append(
                f"High machine count ({self.total_machines}). "
                "May require optimization for rendering performance."
            )
        
        rows, cols = self.calculate_grid_dimensions()
        occupancy = self.total_machines / (rows * cols)
        
        if occupancy < 0.6:
            warnings.append(
                f"Grid has low occupancy ({occupancy:.1%}). "
                "Consider redistributing machines."
            )
        
        floor = self.calculate_floor_dimensions()
        if floor.width > 50 or floor.depth > 50:
            warnings.append(
                f"Floor is very large ({floor.width}x{floor.depth}m). "
                "May need LOD (level of detail) optimization."
            )
        
        return {
            "valid": True,
            "total_machines": self.total_machines,
            "grid_layout": f"{rows}x{cols}",
            "occupancy": occupancy,
            "warnings": warnings
        }


def create_layout_for_config(config: dict) -> dict:
    """
    Utility function to create layout from a factory config dict.
    
    Modifies config in-place by adding layout information.
    
    Args:
        config: Factory configuration dict with 'stations' list
    
    Returns:
        Updated config dict with layout info
    """
    total_machines = sum(
        s.get('num_machines', 1) for s in config.get('stations', [])
    )
    
    calculator = FloorLayoutCalculator(total_machines)
    
    # Generate positions for all machines
    machines = []
    for station in config.get('stations', []):
        num = station.get('num_machines', 1)
        for i in range(num):
            machines.append({
                'id': station.get('id', 0) * 100 + i,
                'name': station.get('name', 'Machine')
            })
    
    positions = calculator.generate_machine_positions(machines)
    
    # Add environment config
    config['environment'] = calculator.get_environment_config()
    config['layout'] = {
        'total_machines': total_machines,
        'positions': [
            {
                'machine_id': p.machine_id,
                'name': p.name,
                'x': p.position_x,
                'z': p.position_z,
                'grid_row': p.grid_row,
                'grid_col': p.grid_col
            }
            for p in positions
        ]
    }
    
    # Add validation info
    config['validation'] = calculator.validate_configuration()
    
    return config
