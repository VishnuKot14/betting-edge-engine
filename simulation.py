"""
simulation.py

Refactored Monte Carlo simulation module.

Design:
- simulate_single_path: low-level engine (one path, drawdown, ruin)
- run_strategy_simulation: Monte Carlo framework (many paths, distributions)
- simulate_kelly_paths: convenience wrapper for Kelly-based strategies
"""

from __future__ import annotations

from typing import Callable, Dict, Any, List, Optional
import numpy as np


# Strategy function type:
# bet_size_fn(current_bankroll, peak_bankroll, bet_index) -> stake (in dollars)
BetSizeFn = Callable[[float, float, int], float]


def simulate_single_path(
    prob_win: float,
    decimal_odds: float,
    initial_bankroll: float,
    n_bets: int,
    bet_size_fn: BetSizeFn,
    ruin_level: float,
    rng: np.random.Generator,
) -> Dict[str, Any]:
    """
    Simulate ONE bankroll trajectory.

    Args:
        prob_win: Win probability (0 to 1).
        decimal_odds: Decimal odds (> 1).
        initial_bankroll: Starting bankroll.
        n_bets: Number of bets to simulate.
        bet_size_fn: Strategy stake function.
        ruin_level: Absolute bankroll level that triggers ruin (e.g., 0.4 * initial_bankroll).
        rng: NumPy random generator for reproducibility.

    Returns:
        dict with:
            - path: list[float] bankroll after each bet (including start)
            - final_bankroll: float
            - max_drawdown: float in [0, 1]
            - ruined: bool
    """
    bankroll = float(initial_bankroll)
    peak = float(initial_bankroll)
    max_dd = 0.0
    ruined = False

    profit_mult = decimal_odds - 1.0
    path: List[float] = [bankroll]

    for t in range(n_bets):
        if bankroll <= 0.0:
            bankroll = 0.0
            ruined = True
            path.append(bankroll)
            break

        stake = float(bet_size_fn(bankroll, peak, t))

        # Safety clamps
        if stake < 0.0:
            stake = 0.0
        if stake > bankroll:
            stake = bankroll

        # No-bet case
        if stake == 0.0:
            path.append(bankroll)
            continue

        # Outcome
        if rng.random() < prob_win:
            bankroll += stake * profit_mult
        else:
            bankroll -= stake

        # Peak + drawdown tracking
        if bankroll > peak:
            peak = bankroll

        if peak > 0:
            dd = (peak - bankroll) / peak
            if dd > max_dd:
                max_dd = dd

        path.append(bankroll)

        # Ruin check (threshold-based)
        if bankroll <= ruin_level:
            ruined = True
            break

    return {
        "path": path,
        "final_bankroll": bankroll,
        "max_drawdown": max_dd,
        "ruined": ruined,
    }


def run_strategy_simulation(
    prob_win: float,
    decimal_odds: float,
    initial_bankroll: float,
    n_bets: int,
    n_sims: int,
    bet_size_fn: BetSizeFn,
    ruin_threshold: float = 0.4,
    n_paths_to_store: int = 25,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run MANY simulations for a single strategy and return distributions + sample paths.

    Args:
        prob_win: Win probability (0 to 1).
        decimal_odds: Decimal odds (> 1).
        initial_bankroll: Starting bankroll per simulation.
        n_bets: Bets per simulation.
        n_sims: Number of Monte Carlo runs.
        bet_size_fn: Strategy stake function.
        ruin_threshold: Ruin defined as bankroll <= ruin_threshold * initial_bankroll.
        n_paths_to_store: Store this many sample paths for plotting.
        seed: Optional RNG seed for reproducibility.

    Returns:
        dict with:
            - final_bankrolls: np.ndarray
            - max_drawdowns: np.ndarray
            - ruined_flags: np.ndarray
            - sample_paths: list of list[float]
            - summary: dict of key metrics
    """
    # Basic validation
    if not (0.0 <= prob_win <= 1.0):
        raise ValueError("prob_win must be between 0 and 1.")
    if decimal_odds <= 1.0:
        raise ValueError("decimal_odds must be > 1.0.")
    if initial_bankroll <= 0:
        raise ValueError("initial_bankroll must be > 0.")
    if n_bets <= 0 or n_sims <= 0:
        raise ValueError("n_bets and n_sims must be > 0.")
    if not (0.0 < ruin_threshold < 1.0):
        raise ValueError("ruin_threshold must be a fraction between 0 and 1.")
    if n_paths_to_store < 0:
        raise ValueError("n_paths_to_store must be >= 0.")

    rng = np.random.default_rng(seed)
    ruin_level = ruin_threshold * initial_bankroll

    final_bankrolls: List[float] = []
    max_drawdowns: List[float] = []
    ruined_flags: List[bool] = []
    sample_paths: List[List[float]] = []

    for _ in range(n_sims):
        result = simulate_single_path(
            prob_win=prob_win,
            decimal_odds=decimal_odds,
            initial_bankroll=initial_bankroll,
            n_bets=n_bets,
            bet_size_fn=bet_size_fn,
            ruin_level=ruin_level,
            rng=rng,
        )

        final_bankrolls.append(result["final_bankroll"])
        max_drawdowns.append(result["max_drawdown"])
        ruined_flags.append(result["ruined"])

        if len(sample_paths) < n_paths_to_store:
            sample_paths.append(result["path"])

    final_arr = np.array(final_bankrolls, dtype=float)
    dd_arr = np.array(max_drawdowns, dtype=float)
    ruined_arr = np.array(ruined_flags, dtype=bool)

    summary = {
        "mean_final_bankroll": float(np.mean(final_arr)),
        "median_final_bankroll": float(np.median(final_arr)),
        "probability_of_profit": float(np.mean(final_arr > initial_bankroll)),
        "probability_of_ruin": float(np.mean(ruined_arr)),
        "mean_max_drawdown": float(np.mean(dd_arr)),
        "median_max_drawdown": float(np.median(dd_arr)),
    }

    return {
        "final_bankrolls": final_arr,
        "max_drawdowns": dd_arr,
        "ruined_flags": ruined_arr,
        "sample_paths": sample_paths,
        "summary": summary,
    }


def simulate_kelly_paths(
    prob_win: float,
    decimal_odds: float,
    initial_bankroll: float,
    n_bets: int,
    n_sims: int,
    kelly_fraction: float,
    kelly_multiplier: float = 0.5,
    ruin_threshold: float = 0.4,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Convenience wrapper: simulate a Kelly-style strategy without needing strategies.py.

    This keeps your older API usable, while internally using the strategy-agnostic framework.

    Args:
        kelly_fraction: Base Kelly fraction (e.g., 0.04 means 4% bankroll).
        kelly_multiplier: Fractional Kelly (0.5 = half Kelly).
        ruin_threshold: Ruin threshold as a fraction of initial bankroll.

    Returns:
        Same output structure as run_strategy_simulation.
    """
    if kelly_fraction < 0:
        kelly_fraction = 0.0
    if not (0.0 <= kelly_multiplier <= 1.0):
        raise ValueError("kelly_multiplier must be between 0 and 1.")

    def kelly_bet_fn(bankroll: float, peak: float, t: int) -> float:
        frac = max(0.0, kelly_fraction) * kelly_multiplier
        return bankroll * frac

    return run_strategy_simulation(
        prob_win=prob_win,
        decimal_odds=decimal_odds,
        initial_bankroll=initial_bankroll,
        n_bets=n_bets,
        n_sims=n_sims,
        bet_size_fn=kelly_bet_fn,
        ruin_threshold=ruin_threshold,
        seed=seed,
    )