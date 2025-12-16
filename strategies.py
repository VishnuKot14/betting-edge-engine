"""
strategies.py

Bet sizing strategies for bankroll simulations.

Each strategy returns a function (closure) with signature:
    bet_size_fn(current_bankroll, peak_bankroll, bet_index) -> stake_amount(float)

This keeps simulation logic (outcoes/risk metrics) separate from sizing logic,
so you can easily compare strategies under identical conditions.
"""

from __future__ import annotations

from typing import Callable

BetSizeFn = Callable[[float, float, int], float]  # current_bankroll, peak_bankroll, bet_index -> stake

def flat_bet(stake: float) -> BetSizeFn:
    """
    Flat betting strategy: wager a constant dollar amount each bet.

    Args:
        stake: Fixed stake in dollars (e.g., 10.0 for $10 bets).
    
    Returns:
        A bet_size_fn that always returns 'stake'.
        (simulation.py should clamp stake to <= bankroll)
    """

    if stake < 0:
        raise ValueError("Stake must be >= 0")
    
    def fn(bankroll: float, peak: float, t: int) -> float:
        return stake
    
    return fn

def fixed_fraction(fraction: float) -> BetSizeFn:
    """
    Fixed fraction betting strategy: wager a constant fraction of current bankroll.

    Args:
        fraction: Fraction of bankroll to wager (between 0 and 1).
    
    Returns:
        A bet_size_fn that returns 'fraction' * current_bankroll.
    """

    if not (0 <= fraction <= 1):
        raise ValueError("Fraction must be between 0 and 1.")
    
    def fn(bankroll: float, peak: float, t: int) -> float:
        return bankroll * fraction
    
    return fn


def kelly_fraction_strategy(
    prob_win: float,
    odds: int,
    kelly_multiplier: float = 1.0
) -> BetSizeFn:
    """
    Kelly Criterion betting strategy.

    Args:
        prob_win: Estimated probability of winning the bet (between 0 and 1).
        odds: American odds (positive for underdogs, negative for favorites).
        kelly_multiplier: Fraction of Kelly fraction to use (between 0 and 1).

    Returns:
        A bet_size_fn that computes stake based on Kelly Criterion.
    """

    from kelly import kelly_fraction  # Import here to avoid circular dependency

    if not (0 <= prob_win <= 1):
        raise ValueError("Probability must be between 0 and 1.")
    
    if not (0 <= kelly_multiplier <= 1):
        raise ValueError("Kelly multiplier must be between 0 and 1.")
    
    kelly_frac = kelly_fraction(prob_win, odds) * kelly_multiplier

    def fn(bankroll: float, peak: float, t: int) -> float:
        return bankroll * kelly_frac
    
    return fn


def min_bet_wrapper(base_strategy: BetSizeFn, min_bet: float) -> BetSizeFn:
    """
    Wrapper to enforce a minimum bet size on any base strategy.

    Realism: sportsbooks often have minimu bets; this increases variance and can meaningfully affect ruin probability.

    Args:
        base_strategy: The underlying bet sizing strategy.
        min_bet: Minimum bet size in dollars.

    Returns:
        A bet_size_fn that enforces the minimum bet size.
    """

    if min_bet < 0:
        raise ValueError("Minimum bet must be >= 0.")
    
    def fn(bankroll: float, peak: float, t: int) -> float:
        base_bet = base_strategy(bankroll, peak, t)
        return max(base_bet, min_bet)
    
    return fn


def capped_bet_wrapper(base_strategy: BetSizeFn, max_bet: float) -> BetSizeFn:
    """
    Wrapper to enforce a maximum bet size on any base strategy.

    Args:
        base_strategy: The underlying bet sizing strategy.
        max_bet: Maximum bet size in dollars.

    Returns:
        A bet_size_fn that enforces the maximum bet size.
    """

    if max_bet < 0:
        raise ValueError("Maximum bet must be >= 0.")
    
    def fn(bankroll: float, peak: float, t: int) -> float:
        base_bet = base_strategy(bankroll, peak, t)
        return min(base_bet, max_bet)
    
    return fn


def risk_adjusted_kelly_strategy(
    prob_win: float,
    decimal_odds: float,
    prob_std: float = 0.02,
    kelly_multiplier: float = 0.5,
    edge_threshold: float = 0.01,
    max_drawdown: float = 0.3,
) -> BetSizeFn:
    """
    Risk-adjusted Kelly Strategy using existing kelly.py functions:

    1) edge_adjusted_kelly(prob_win, decimal_odds, edge_threshold)
    2) uncertainty_adjusted_kelly(prob_win, decimal_odds, prob_std)
    3) drawdown_adjusted_kelly(kelly_fraction, current_bankroll, peak_bankroll, max_drawdown)
    4) apply kelly_multiplier (fractional kelly)

    Args:
        prob_win: Estimated probability of winning the bet (between 0 and 1).
        decimal_odds: Decimal odds for the bet.
        prob_std: Standard deviation of the probability estimate.
        kelly_multiplier: Fraction of Kelly fraction to use (between 0 and 1).
        edge_threshold: Minimum edge required to place a bet.
        max_drawdown: Maximum acceptable drawdown as a fraction of peak bankroll.
    
    Returns:
        A bet_size_fn that computes stake based on risk-adjusted Kelly Criterion.
    """
    if not (0 <= prob_win <= 1):
        raise ValueError("Probability must be between 0 and 1.")
    if decimal_odds <= 1.0:
        raise ValueError("Decimal odds must be greater than 1.0.")
    if prob_std < 0:
        raise ValueError("Probability standard deviation must be >= 0.")
    if not (0 <= kelly_multiplier <= 1):
        raise ValueError("Kelly multiplier must be between 0 and 1.")
    if not (0 <= edge_threshold <= 1):
        raise ValueError("Edge threshold must be between 0 and 1.")
    if not (0 <= max_drawdown <= 1):
        raise ValueError("Max drawdown must be between 0 and 1.")
    

    from kelly import (
        edge_adjusted_kelly,
        uncertainty_adjusted_kelly,
        drawdown_adjusted_kelly,
    )

    def fn(bankroll: float, peak: float, t: int) -> float:
        k_edge = edge_adjusted_kelly(prob_win, decimal_odds, edge_threshold)
        k_unc = uncertainty_adjusted_kelly(prob_win, decimal_odds, prob_std)
        k = max(0.0, min(k_edge, k_unc))

        k = drawdown_adjusted_kelly(k, bankroll, peak, max_drawdown)

        k *= kelly_multiplier


        return bankroll * k
    
    return fn

