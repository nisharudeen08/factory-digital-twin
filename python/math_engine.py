import numpy as np
import scipy.stats as stats
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional, Union

@dataclass
class StationMetric:
    id: int
    name: str
    name_ta: str
    utilization: float
    queue_length: int
    wait_time_mean: float
    is_bottleneck: bool
    status: str

@dataclass
class ShiftResult:
    throughput: int
    stations: List[StationMetric]
    bottleneck_id: int
    bottleneck_name: str
    lead_time_mean: float
    shift_completion_pct: float


# ═══════════════════════════════════════════════════════════════════════
# CORE QUEUEING THEORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def calc_utilization(arrival_rate: float, service_rate: float, num_machines: int = 1) -> float:
    """Calculate utilization (rho) of a station."""
    if service_rate == 0 or num_machines == 0:
        return 1.0
    return min(1.0, arrival_rate / (service_rate * num_machines))


def calc_queue_length_mm1(rho: float) -> float:
    """Calculate expected queue length for an M/M/1 queue (Lq).

    Uses the formula: Lq = rho^2 / (1 - rho)

    Args:
        rho: Server utilization (0 < rho < 1).

    Returns:
        Expected number of customers waiting in the queue.
    """
    if rho >= 1.0 or rho < 0:
        return 0.0
    return (rho ** 2) / (1.0 - rho)


def calc_wait_time(Lq: float, arrival_rate: float) -> float:
    """Calculate expected wait time in queue (Wq) using Little's Law.

    Wq = Lq / lambda

    Args:
        Lq: Expected queue length.
        arrival_rate: Average arrival rate (lambda).

    Returns:
        Expected waiting time in the queue.
    """
    if arrival_rate <= 0:
        return 0.0
    return Lq / arrival_rate


def calc_kingman_wq(arrival_rate: float, service_rate: float,
                    ca_sq: float, cs_sq: float, num_machines: int = 1) -> float:
    """Kingman's formula (VUT equation) for G/G/1 expected wait time.

    Wq ≈ (rho / (1 - rho)) * ((ca² + cs²) / 2) * (1 / service_rate)

    Args:
        arrival_rate: Average arrival rate.
        service_rate: Average service rate.
        ca_sq: Squared coefficient of variation of inter-arrival times.
        cs_sq: Squared coefficient of variation of service times.
        num_machines: Number of parallel servers.

    Returns:
        Approximate expected waiting time in queue.
    """
    rho = calc_utilization(arrival_rate, service_rate, num_machines)
    if rho >= 1.0 or service_rate <= 0:
        return 0.0
    return (rho / (1.0 - rho)) * ((ca_sq + cs_sq) / 2.0) * (1.0 / service_rate)


# ═══════════════════════════════════════════════════════════════════════
# BOTTLENECK IDENTIFICATION
# ═══════════════════════════════════════════════════════════════════════

def calc_bottleneck_index(utilization: float, Lq: float, cv_squared: float,
                          Lq_max: float = 10.0, cv_max_sq: float = 1.0) -> float:
    """Calculate Bottleneck Index (BNI) for a station.

    BNI = 0.5 * utilization + 0.3 * (Lq / Lq_max) + 0.2 * (cv² / cv_max²)

    Args:
        utilization: Station utilization (0-1).
        Lq: Queue length for this station.
        cv_squared: Coefficient of variation squared for cycle times.
        Lq_max: Maximum Lq across all stations (for normalization).
        cv_max_sq: Maximum cv² across all stations (for normalization).

    Returns:
        BNI score (higher = more likely bottleneck).
    """
    lq_factor = Lq / max(Lq_max, 0.001)
    cv_factor = cv_squared / max(cv_max_sq, 0.001)
    bni = 0.5 * utilization + 0.3 * lq_factor + 0.2 * cv_factor
    return float(bni)


def identify_bottleneck(station_metrics: Union[List[dict], List[StationMetric]]) -> Optional[Union[dict, StationMetric]]:
    """Identify the bottleneck station based on highest BNI.

    Accepts either a list of dicts (from factory_simulation) or
    a list of StationMetric dataclasses.

    Args:
        station_metrics: List of station metrics (dicts or StationMetric).

    Returns:
        The station with the highest BNI, or None if empty.
    """
    if not station_metrics:
        return None

    # Handle list of dicts (from factory_simulation.py)
    if isinstance(station_metrics[0], dict):
        best = max(station_metrics, key=lambda m: m.get("bni", 0.0))
        return best

    # Handle list of StationMetric dataclasses
    max_q = max([m.queue_length for m in station_metrics] + [1])
    return max(station_metrics, key=lambda m: calc_bottleneck_index(
        m.utilization, m.queue_length, 0.0, max_q, 1.0
    ))


# ═══════════════════════════════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════════════════════════════

def calc_confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
    """Calculate confidence interval for a list of values.

    Args:
        values: Sample values.
        confidence: Confidence level (default 0.95).

    Returns:
        Tuple of (mean, lower_bound, upper_bound).
    """
    if len(values) < 2:
        val = values[0] if values else 0.0
        return (val, val, val)
    mean = float(np.mean(values))
    sem = stats.sem(values)
    ci = stats.t.interval(confidence, len(values) - 1, loc=mean, scale=sem)
    return (mean, float(ci[0]), float(ci[1]))


def run_monte_carlo(throughput_samples: List[int]) -> Dict[str, float]:
    """Calculate statistics for throughput samples."""
    arr = np.array(throughput_samples)
    return {
        "p10": float(np.percentile(arr, 10)),
        "p50": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr))
    }


# ═══════════════════════════════════════════════════════════════════════
# RELIABILITY / AVAILABILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def calc_weibull_mtbf(eta: float, beta: float) -> float:
    """Calculate Mean Time Between Failures from Weibull parameters.

    MTBF = eta * Gamma(1 + 1/beta)

    Args:
        eta: Scale parameter (characteristic life) in hours.
        beta: Shape parameter.

    Returns:
        MTBF in hours.
    """
    from scipy.special import gamma
    if eta <= 0 or beta <= 0:
        return 1.0
    return eta * gamma(1.0 + 1.0 / beta)


def calc_availability(mtbf: float, mttr: float) -> float:
    """Calculate steady-state availability.

    Availability = MTBF / (MTBF + MTTR)

    Args:
        mtbf: Mean Time Between Failures (hours).
        mttr: Mean Time To Repair (minutes — converted internally).

    Returns:
        Availability fraction (0-1).
    """
    mttr_hours = mttr / 60.0  # convert minutes to hours
    if mtbf + mttr_hours <= 0:
        return 0.0
    return mtbf / (mtbf + mttr_hours)

