"""
markov_engine.py — Markov Chain Machine State Modelling

Models machine degradation using Discrete-Time Markov Chains.
States: Running(0), Degraded(1), Broken(2), Maintenance(3)

Provides steady-state analysis, cascade breakdown rates,
mean first passage times, and health labels (EN/Tamil).
"""

import numpy as np
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════
# TRANSITION MATRICES
# ═══════════════════════════════════════════════════════════════════════

TRANSITION_MATRICES = {
    "good": np.array([
        [0.95, 0.04, 0.01, 0.00],   # Running
        [0.40, 0.55, 0.04, 0.01],   # Degraded
        [0.00, 0.00, 0.00, 1.00],   # Broken → always goes to Maintenance
        [0.90, 0.07, 0.03, 0.00],   # Maintenance
    ]),
    "average": np.array([
        [0.92, 0.06, 0.02, 0.00],
        [0.30, 0.60, 0.08, 0.02],
        [0.00, 0.00, 0.00, 1.00],
        [0.85, 0.10, 0.05, 0.00],
    ]),
    "poor": np.array([
        [0.85, 0.09, 0.06, 0.00],
        [0.20, 0.55, 0.18, 0.07],
        [0.00, 0.00, 0.00, 1.00],
        [0.75, 0.15, 0.10, 0.00],
    ]),
}

STATE_NAMES = ["Running", "Degraded", "Broken", "Maintenance"]


def build_transition_matrix(condition: str) -> np.ndarray:
    """Get the 4×4 transition matrix for given machine condition.

    States: Running(0), Degraded(1), Broken(2), Maintenance(3)

    Args:
        condition: Machine condition — 'good', 'average', or 'poor'.

    Returns:
        4×4 numpy array where P[i][j] = probability of going from state i to state j.

    Raises:
        ValueError: If condition is not recognized.

    Example:
        >>> P = build_transition_matrix("good")
        >>> P[0, 0]  # prob of staying Running
        0.95
    """
    if condition not in TRANSITION_MATRICES:
        raise ValueError(f"condition must be 'good', 'average', or 'poor', got '{condition}'")
    return TRANSITION_MATRICES[condition].copy()


def solve_steady_state(P: np.ndarray) -> np.ndarray:
    """Solve for the steady-state distribution π such that π·P = π, sum(π) = 1.

    Uses the standard approach: solve (P^T - I)·π = 0 with constraint sum(π) = 1.

    Args:
        P: n×n transition matrix (rows must sum to 1).

    Returns:
        Steady-state vector π of length n.

    Example:
        >>> P = build_transition_matrix("average")
        >>> pi = solve_steady_state(P)
        >>> print(f"Running: {pi[0]:.3f}, Degraded: {pi[1]:.3f}")
    """
    n = P.shape[0]

    # Build system: (P^T - I)·π = 0, with last equation replaced by sum(π) = 1
    A = P.T - np.eye(n)
    A[-1, :] = 1.0  # replace last row with sum constraint
    b = np.zeros(n)
    b[-1] = 1.0  # sum(π) = 1

    try:
        pi = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        # Fallback: use least squares
        pi, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    # Ensure non-negative and normalized
    pi = np.maximum(pi, 0.0)
    pi_sum = np.sum(pi)
    if pi_sum > 0:
        pi /= pi_sum

    return pi


def calc_cascade_breakdown_rate(base_lambda: float, utilization: float,
                                threshold: float = 0.75, k: float = 2.0) -> float:
    """Calculate breakdown rate considering cascade effects at high utilization.

    For ρ > threshold:
        λ_breakdown(ρ) = base_λ × exp(k × (ρ − threshold))

    For ρ ≤ threshold:
        λ_breakdown(ρ) = base_λ

    This models the reality that machines break down much faster
    when run at very high utilization.

    Args:
        base_lambda: Base breakdown rate (breakdowns per hour).
        utilization: Current utilization ρ ∈ [0, 1].
        threshold: Utilization threshold above which cascade kicks in (default 0.75).
        k: Exponential growth factor (default 2.0).

    Returns:
        Effective breakdown rate.

    Example:
        >>> calc_cascade_breakdown_rate(0.01, 0.9, threshold=0.75, k=2.0)
        0.01349...  # ~35% higher than base
    """
    if base_lambda < 0:
        raise ValueError(f"base_lambda must be non-negative, got {base_lambda}")
    utilization = max(0.0, min(utilization, 1.0))

    if utilization > threshold:
        import math
        return base_lambda * math.exp(k * (utilization - threshold))
    return base_lambda


def calc_mean_first_passage_time(P: np.ndarray, from_state: int,
                                 to_state: int) -> float:
    """Calculate expected steps to reach to_state starting from from_state.

    Uses the linear system approach: m_i = 1 + Σ_{j≠to} P[i,j] × m_j

    Args:
        P: n×n transition matrix.
        from_state: Starting state index.
        to_state: Target state index.

    Returns:
        Mean number of steps to reach to_state from from_state.

    Example:
        >>> P = build_transition_matrix("average")
        >>> mfpt = calc_mean_first_passage_time(P, from_state=0, to_state=2)
        >>> print(f"Expected steps to breakdown: {mfpt:.1f}")
    """
    n = P.shape[0]
    if from_state < 0 or from_state >= n:
        raise ValueError(f"from_state out of range: {from_state}")
    if to_state < 0 or to_state >= n:
        raise ValueError(f"to_state out of range: {to_state}")
    if from_state == to_state:
        return 0.0

    # Build system for transient states (excluding to_state)
    transient = [i for i in range(n) if i != to_state]
    idx_map = {state: i for i, state in enumerate(transient)}
    m = len(transient)

    A = np.zeros((m, m))
    b = np.ones(m)

    for i, si in enumerate(transient):
        A[i, i] = 1.0
        for j, sj in enumerate(transient):
            A[i, j] -= P[si, sj]

    try:
        result = np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        result, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    return float(result[idx_map[from_state]])


def get_machine_health_label(pi_running: float) -> dict:
    """Convert steady-state running probability to a health label.

    Args:
        pi_running: Steady-state probability of being in Running state.

    Returns:
        Dictionary with 'en' (English), 'ta' (Tamil), and 'color' keys.

    Example:
        >>> get_machine_health_label(0.92)
        {'en': 'Good', 'ta': 'நல்லது', 'color': 'green'}
    """
    if pi_running > 0.90:
        return {"en": "Good", "ta": "நல்லது", "color": "green"}
    elif pi_running > 0.75:
        return {"en": "Average", "ta": "சராசரி", "color": "amber"}
    else:
        return {"en": "Poor", "ta": "மோசம்", "color": "red"}


def get_full_machine_health(condition: str) -> dict:
    """Get complete machine health analysis for a given condition.

    Convenience function that builds the matrix, solves steady state,
    and returns all metrics.

    Args:
        condition: 'good', 'average', or 'poor'.

    Returns:
        Dict with steady_state, health_label, mfpt_to_breakdown, etc.
    """
    P = build_transition_matrix(condition)
    pi = solve_steady_state(P)
    health = get_machine_health_label(float(pi[0]))
    mfpt_breakdown = calc_mean_first_passage_time(P, from_state=0, to_state=2)

    return {
        "condition": condition,
        "steady_state": {
            STATE_NAMES[i]: round(float(pi[i]), 4) for i in range(4)
        },
        "availability": round(float(pi[0]), 4),
        "health_label": health,
        "mfpt_to_breakdown": round(mfpt_breakdown, 1),
        "mfpt_to_repair": round(
            calc_mean_first_passage_time(P, from_state=2, to_state=0), 1
        ),
    }
