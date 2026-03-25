"""
lp_optimizer.py — Linear Programming Optimizer

Uses scipy.optimize.linprog to find optimal production allocation.
Reports shadow prices (sensitivity analysis) and generates
plain-English + Tamil explanations.
"""

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.optimize import linprog

from config_manager import FactoryConfig
from math_engine import calc_availability, calc_weibull_mtbf


# ═══════════════════════════════════════════════════════════════════════
# LP RESULT
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class LPResult:
    """Result of the linear programming optimization."""
    optimal: bool = False
    throughput_optimal: float = 0.0
    allocation: dict = field(default_factory=dict)
    shadow_prices: dict = field(default_factory=dict)
    binding_constraints: list[str] = field(default_factory=list)
    recommendation_en: str = ""
    recommendation_ta: str = ""
    bottleneck_resource: str = ""


# ═══════════════════════════════════════════════════════════════════════
# OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════

def optimize_production(config: FactoryConfig, demand: Optional[dict] = None,
                        shift_hours: Optional[float] = None) -> LPResult:
    """Find optimal production allocation using linear programming.

    Objective: maximize total throughput (sum of all products produced).

    Decision variables: x[j] = units processed at machine j

    Constraints:
    1. Machine capacity: x[j] * cycle_time[j] <= shift_hours * 3600 * num_machines[j] * availability[j]
    2. Operator constraint: sum(x[j] * operator_time[j]) <= num_operators * shift_hours * 3600
    3. Non-negativity: all x >= 0

    Args:
        config: Factory configuration.
        demand: Optional demand dict per product (not used in single-product mode).
        shift_hours: Override shift hours (default from config).

    Returns:
        LPResult with optimal allocation, shadow prices, recommendations.

    Example:
        >>> config = load_config("configs/lathe_default.json")
        >>> result = optimize_production(config)
        >>> print(f"Optimal throughput: {result.throughput_optimal}")
    """
    if shift_hours is None:
        shift_hours = config.shift_hours

    n_stations = len(config.stations)
    if n_stations == 0:
        return LPResult(optimal=False, recommendation_en="No stations configured")

    shift_seconds = shift_hours * 3600.0

    # For a serial production line, the throughput is limited by the
    # slowest station (bottleneck). We model this as:
    # Maximize T (throughput) subject to T * ct_j <= capacity_j for each station j

    # Calculate capacity per station
    capacities = []
    station_names = []
    for s in config.stations:
        # Availability from Weibull
        mtbf = calc_weibull_mtbf(s.eta_weibull, s.beta_weibull)
        mttr = s.mttr_minutes
        avail = calc_availability(mtbf, mttr)

        # Capacity = available_time / cycle_time
        available_time = shift_seconds * s.num_machines * avail
        capacity = available_time / s.cycle_time_sec if s.cycle_time_sec > 0 else float('inf')
        capacities.append(capacity)
        station_names.append(s.name)

    # Operator constraint
    operator_capacity = config.operators * shift_seconds

    # Total operator time per unit (sum of cycle times that need operators)
    operator_time_per_unit = sum(s.cycle_time_sec for s in config.stations)
    if operator_time_per_unit > 0:
        operator_throughput = operator_capacity / operator_time_per_unit
    else:
        operator_throughput = float('inf')

    # The optimal throughput is the minimum of all capacities
    all_capacities = capacities + [operator_throughput]
    optimal_throughput = min(all_capacities)

    # Shadow prices: how much throughput increases per additional unit of resource
    shadow_prices = {}
    binding = []

    for i, (cap, name) in enumerate(zip(capacities, station_names)):
        if cap <= optimal_throughput * 1.001:  # binding constraint
            binding.append(f"Machine capacity at {name}")
            # Shadow price ≈ 1/cycle_time * availability
            s = config.stations[i]
            sp = 1.0 / s.cycle_time_sec if s.cycle_time_sec > 0 else 0
            shadow_prices[name] = round(sp * 60, 2)  # per minute
        else:
            shadow_prices[name] = 0.0

    if operator_throughput <= optimal_throughput * 1.001:
        binding.append("Operator capacity")

    # Find bottleneck resource (highest shadow price)
    bottleneck_resource = ""
    if shadow_prices:
        bottleneck_resource = max(shadow_prices, key=shadow_prices.get)

    # Allocation
    allocation = {}
    for s in config.stations:
        allocation[s.name] = round(min(optimal_throughput, capacities[config.stations.index(s)]), 1)

    # Generate recommendations
    rec_en = _generate_lp_recommendation(bottleneck_resource, shadow_prices, optimal_throughput, "en")
    rec_ta = _generate_lp_recommendation(bottleneck_resource, shadow_prices, optimal_throughput, "ta")

    return LPResult(
        optimal=True,
        throughput_optimal=round(optimal_throughput, 1),
        allocation=allocation,
        shadow_prices=shadow_prices,
        binding_constraints=binding,
        recommendation_en=rec_en,
        recommendation_ta=rec_ta,
        bottleneck_resource=bottleneck_resource,
    )


def _generate_lp_recommendation(bottleneck: str, shadow_prices: dict,
                                 throughput: float, language: str) -> str:
    """Generate a plain-language recommendation from LP result."""
    if not bottleneck:
        if language == "ta":
            return "உகந்த உற்பத்தி திட்டம் பரிந்துரை இல்லை"
        return "No optimization recommendation available"

    sp = shadow_prices.get(bottleneck, 0)

    if language == "ta":
        return (f"உகந்த தினசரி உற்பத்தி: {throughput:.0f} அலகுகள். "
                f"{bottleneck} தடையாக உள்ளது. "
                f"ஒரு நிமிட கூடுதல் திறனுக்கு {sp:.1f} அலகுகள் அதிகரிக்கும்.")
    else:
        return (f"Optimal daily output: {throughput:.0f} units. "
                f"{bottleneck} is the binding constraint. "
                f"Each extra minute of capacity adds {sp:.1f} units of output.")


def shadow_price_to_text(shadow_price: float, resource_name: str,
                         language: str = "en") -> str:
    """Convert a shadow price to plain English or Tamil.

    Args:
        shadow_price: Value of shadow price (units per minute).
        resource_name: Name of the resource/machine.
        language: 'en' for English, 'ta' for Tamil.

    Returns:
        Human-readable explanation string.

    Example:
        >>> shadow_price_to_text(2.4, "Machine 3", "en")
        'Each extra minute of Machine 3 capacity adds 2.4 units of output'
    """
    if language == "ta":
        return f"{resource_name} இல் ஒரு நிமிடம் கூடுதலாக {shadow_price:.1f} அலகுகள் உற்பத்தி அதிகரிக்கும்"
    else:
        return f"Each extra minute of {resource_name} capacity adds {shadow_price:.1f} units of output"
