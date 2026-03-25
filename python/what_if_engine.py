"""
what_if_engine.py — Scenario Comparison Engine

The core feature workers use most. Runs baseline + scenario simulations
and produces plain-English/Tamil recommendations.

Pre-built scenarios:
  1. add_machine_at_bottleneck
  2. add_one_operator
  3. reduce_batch_size_half
  4. increase_demand_20pct
  5. reduce_cycle_time_10pct
  6. two_shift_operation
"""

import copy
from dataclasses import dataclass, field
from typing import Optional

from config_manager import FactoryConfig
from data_source import DataSource, SyntheticDataSource
from factory_simulation import (
    SimulationResult, ProductionLine, run_replications, aggregate_results
)


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Scenario:
    """Defines a what-if scenario to compare against baseline.

    Attributes:
        name: Short identifier (e.g., 'add_machine_at_bottleneck').
        description: Human-readable description.
        description_ta: Tamil description.
        parameter_changes: Dict of changes to apply to baseline config.

    Example:
        >>> s = Scenario(
        ...     name="add_machine",
        ...     description="Add one machine at Station 3",
        ...     parameter_changes={"station_3_num_machines": 2}
        ... )
    """
    name: str
    description: str
    description_ta: str = ""
    parameter_changes: dict = field(default_factory=dict)


@dataclass
class ScenarioResult:
    """Result of a single scenario comparison."""
    scenario: Scenario = None
    result: dict = field(default_factory=dict)
    throughput_delta: float = 0.0
    throughput_delta_pct: float = 0.0
    lead_time_delta: float = 0.0
    lead_time_delta_pct: float = 0.0
    recommendation: str = ""
    recommendation_ta: str = ""


@dataclass
class WhatIfResult:
    """Complete what-if comparison result."""
    baseline: dict = field(default_factory=dict)
    scenarios: list[ScenarioResult] = field(default_factory=list)
    best_scenario: Optional[str] = None
    recommendation_en: str = ""
    recommendation_ta: str = ""

    def to_summary_dict(self) -> dict:
        """Convert to dict for sending to Android as JSON."""
        scenario_list = []
        for sr in self.scenarios:
            scenario_list.append({
                "name": sr.scenario.name,
                "description": sr.scenario.description,
                "description_ta": sr.scenario.description_ta,
                "throughput_delta": sr.throughput_delta,
                "throughput_delta_pct": sr.throughput_delta_pct,
                "lead_time_delta": sr.lead_time_delta,
                "lead_time_delta_pct": sr.lead_time_delta_pct,
                "recommendation": sr.recommendation,
                "recommendation_ta": sr.recommendation_ta,
                "throughput_mean": sr.result.get("throughput_mean", 0),
                "throughput_ci_lower": sr.result.get("throughput_ci_lower", 0),
                "throughput_ci_upper": sr.result.get("throughput_ci_upper", 0),
                "lead_time_mean": sr.result.get("lead_time_mean", 0),
                "bottleneck_station_name": sr.result.get("bottleneck_station_name", ""),
            })

        return {
            "baseline": self.baseline,
            "scenarios": scenario_list,
            "best_scenario": self.best_scenario,
            "recommendation_en": self.recommendation_en,
            "recommendation_ta": self.recommendation_ta,
        }


# ═══════════════════════════════════════════════════════════════════════
# APPLY PARAMETER CHANGES TO CONFIG
# ═══════════════════════════════════════════════════════════════════════

def _apply_changes(config: FactoryConfig, changes: dict) -> FactoryConfig:
    """Clone the config and apply parameter changes.

    Supported change keys:
    - 'demand': new demand value
    - 'operators': new operator count
    - 'shift_hours': new shift hours
    - 'station_X_num_machines': set num_machines for station X
    - 'station_X_cycle_time_sec': set cycle time for station X
    - 'all_cycle_time_pct': multiply all cycle times by this factor
    - 'batch_size': new batch size

    Args:
        config: Base FactoryConfig.
        changes: Dictionary of changes.

    Returns:
        New FactoryConfig with changes applied.
    """
    new_config = copy.deepcopy(config)

    for key, value in changes.items():
        if key == "demand":
            new_config.demand = int(value)
        elif key == "operators":
            new_config.operators = int(value)
        elif key == "shift_hours":
            new_config.shift_hours = float(value)
        elif key == "batch_size":
            new_config.batch_size = int(value)
        elif key.startswith("station_") and key.endswith("_num_machines"):
            station_id = int(key.split("_")[1])
            for s in new_config.stations:
                if s.id == station_id:
                    s.num_machines = int(value)
        elif key.startswith("station_") and key.endswith("_cycle_time_sec"):
            station_id = int(key.split("_")[1])
            for s in new_config.stations:
                if s.id == station_id:
                    s.cycle_time_sec = float(value)
        elif key == "all_cycle_time_pct":
            for s in new_config.stations:
                s.cycle_time_sec *= float(value)

    return new_config


# ═══════════════════════════════════════════════════════════════════════
# RUN WHAT-IF ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def run_what_if(baseline_config: FactoryConfig,
                scenarios: list[Scenario],
                data_source_class=SyntheticDataSource,
                n_reps: int = 30,
                condition: str = "average") -> WhatIfResult:
    """Run baseline and scenario simulations, then compare.

    1. Run baseline simulation (n_reps replications)
    2. For each scenario: clone config, apply changes, run n_reps
    3. Compare each scenario to baseline
    4. Return WhatIfResult

    Args:
        baseline_config: The current factory configuration.
        scenarios: List of Scenario objects to compare.
        data_source_class: DataSource class to use (default SyntheticDataSource).
        n_reps: Number of replications per scenario.
        condition: Machine condition string.

    Returns:
        WhatIfResult with baseline and all scenario comparisons.
    """
    # Run baseline
    print("Running baseline simulation...")
    baseline_results = run_replications(
        baseline_config,
        lambda seed: data_source_class(baseline_config.stations, condition, seed),
        n_reps=n_reps,
        shift_hours=baseline_config.shift_hours,
        demand=baseline_config.demand,
        condition=condition,
        verbose=False,
    )
    baseline_agg = aggregate_results(baseline_results)

    # Run each scenario
    scenario_results: list[ScenarioResult] = []

    for i, scenario in enumerate(scenarios):
        print(f"Running scenario {i + 1}/{len(scenarios)}: {scenario.name}...")

        # Apply changes to config
        scenario_config = _apply_changes(baseline_config, scenario.parameter_changes)

        # Run simulation
        results = run_replications(
            scenario_config,
            lambda seed: data_source_class(scenario_config.stations, condition, seed),
            n_reps=n_reps,
            shift_hours=scenario_config.shift_hours,
            demand=scenario_config.demand,
            condition=condition,
            verbose=False,
        )
        scenario_agg = aggregate_results(results)

        # Calculate deltas
        tp_delta = scenario_agg["throughput_mean"] - baseline_agg["throughput_mean"]
        tp_delta_pct = (tp_delta / baseline_agg["throughput_mean"] * 100) if baseline_agg["throughput_mean"] > 0 else 0
        lt_delta = scenario_agg["lead_time_mean"] - baseline_agg["lead_time_mean"]
        lt_delta_pct = (lt_delta / baseline_agg["lead_time_mean"] * 100) if baseline_agg["lead_time_mean"] > 0 else 0

        # Generate recommendation
        rec_en = _generate_recommendation(scenario, tp_delta, tp_delta_pct, "en")
        rec_ta = _generate_recommendation(scenario, tp_delta, tp_delta_pct, "ta")

        scenario_results.append(ScenarioResult(
            scenario=scenario,
            result=scenario_agg,
            throughput_delta=round(tp_delta, 1),
            throughput_delta_pct=round(tp_delta_pct, 1),
            lead_time_delta=round(lt_delta, 2),
            lead_time_delta_pct=round(lt_delta_pct, 1),
            recommendation=rec_en,
            recommendation_ta=rec_ta,
        ))

    # Find best scenario
    best = max(scenario_results, key=lambda s: s.throughput_delta) if scenario_results else None

    overall_rec_en = ""
    overall_rec_ta = ""
    best_name = None
    if best and best.throughput_delta > 0:
        best_name = best.scenario.name
        overall_rec_en = best.recommendation
        overall_rec_ta = best.recommendation_ta

    return WhatIfResult(
        baseline=baseline_agg,
        scenarios=scenario_results,
        best_scenario=best_name,
        recommendation_en=overall_rec_en,
        recommendation_ta=overall_rec_ta,
    )


def _generate_recommendation(scenario: Scenario, tp_delta: float,
                              tp_delta_pct: float, language: str) -> str:
    """Generate a plain-language recommendation."""
    direction = "increases" if tp_delta > 0 else "decreases"
    abs_delta = abs(tp_delta)
    abs_pct = abs(tp_delta_pct)

    if language == "ta":
        direction_ta = "அதிகரிக்கும்" if tp_delta > 0 else "குறையும்"
        return f"{scenario.description_ta} — தினசரி உற்பத்தி {abs_delta:.0f} அலகுகள் ({abs_pct:.0f}%) {direction_ta}"
    else:
        return f"{scenario.description} {direction} daily output by {abs_delta:.0f} units ({abs_pct:.0f}%)"


# ═══════════════════════════════════════════════════════════════════════
# PRE-BUILT SCENARIOS
# ═══════════════════════════════════════════════════════════════════════

def get_prebuilt_scenarios(config: FactoryConfig) -> list[Scenario]:
    """Create the 6 pre-built scenarios based on current config.

    Args:
        config: Current factory configuration (used to find bottleneck station).

    Returns:
        List of 6 ready-to-use Scenario objects.
    """
    # Find the station with highest cycle time (likely bottleneck)
    bottleneck = max(config.stations, key=lambda s: s.cycle_time_sec) if config.stations else None
    bn_id = bottleneck.id if bottleneck else 1
    bn_name = bottleneck.name if bottleneck else "Station"
    bn_machines = bottleneck.num_machines if bottleneck else 1

    return [
        Scenario(
            name="add_machine_at_bottleneck",
            description=f"Add one machine at {bn_name}",
            description_ta=f"{bn_name} இல் ஒரு இயந்திரம் சேர்",
            parameter_changes={f"station_{bn_id}_num_machines": bn_machines + 1},
        ),
        Scenario(
            name="add_one_operator",
            description="Add one operator to the shift",
            description_ta="ஷிப்டில் ஒரு ஆபரேட்டர் சேர்",
            parameter_changes={"operators": config.operators + 1},
        ),
        Scenario(
            name="reduce_batch_size_half",
            description="Reduce batch size by half",
            description_ta="தொகுப்பு அளவை பாதியாக குறை",
            parameter_changes={"batch_size": max(config.batch_size // 2, 1)},
        ),
        Scenario(
            name="increase_demand_20pct",
            description="Increase demand by 20%",
            description_ta="தேவையை 20% அதிகரி",
            parameter_changes={"demand": int(config.demand * 1.2)},
        ),
        Scenario(
            name="reduce_cycle_time_10pct",
            description="Reduce all cycle times by 10% (process improvement)",
            description_ta="அனைத்து சுழற்சி நேரங்களையும் 10% குறை",
            parameter_changes={"all_cycle_time_pct": 0.9},
        ),
        Scenario(
            name="two_shift_operation",
            description="Run two shifts (double shift hours)",
            description_ta="இரண்டு ஷிப்ட் இயக்கம்",
            parameter_changes={"shift_hours": config.shift_hours * 2},
        ),
    ]
