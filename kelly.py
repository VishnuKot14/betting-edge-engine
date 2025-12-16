"""
kelly.py

Kelly Criterion bet sizing for risk_managed wagering.
Used to determine optimal fraction of bankroll to wager.
"""

from odds import implied_probability

def kelly_fraction(prob_win: float, odds: int) -> float:
    """
    Calculate the Kelly Criterion fraction of bankroll to wager.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        odds (int): The American odds. Positive for underdogs, negative for favorites.

    Returns:
        float: The optimal fraction of bankroll to wager (between 0 and 1).
    """
    
    if not (0 <= prob_win <= 1):
        raise ValueError("Probability must be between 0 and 1.")
    
    
    if odds > 0:
        b = odds / 100
    else:
        b = 100 / abs(odds)
    
    kelly_frac = (b * prob_win - (1 - prob_win)) / b
    
    return max(0.0, kelly_frac)  #Kelly never recommends betting if edge is negative


def kelly_bet_size(
        prob_win: float,
        odds: int,
        bankroll: float,
        kelly_multiplier: float = 1.0
) -> float:
    """
    Calculate the optimal bet size using the Kelly Criterion.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        bankroll (float): The total bankroll available for betting.
        kelly_multiplier (float): A fraction of the Kelly fraction to use (between 0 and 1).

    Returns:
        float: The optimal bet size.
    """
    
    if bankroll <= 0:
        raise ValueError("Bankroll must be greater than zero.")
    
    fraction = kelly_fraction(prob_win, odds) * kelly_multiplier
    return round(bankroll * fraction, 2)


def risk_level(fraction: float) -> str:
    """
    Determine qualitative risk level based on Kelly fraction.

    Args:
        fraction (float): The Kelly fraction of bankroll to wager (between 0 and 1).

    Returns:
        str: Qualitative risk level.
    """

    if fraction == 0:
        return "NO BET"
    elif fraction < 0.1:
        return "LOW RISK"
    elif fraction < 0.25:
        return "MODERATE RISK"
    elif fraction < 0.5:
        return "HIGH RISK"
    else:
        return "VERY HIGH RISK"


def edge_adjusted_kelly(prob_win, decimal_odds, edge_threshold=0.01):
    """
    Calculate an edge-adjusted Kelly fraction.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        decimal_odds (float): The decimal odds for the bet.
        edge_threshold (float): Minimum edge required to place a bet.
    
    """
    edge = prob_win * (decimal_odds - 1) - (1 - prob_win)

    if edge <= edge_threshold:
        return 0.0
    
    raw_kelly = (edge) / (decimal_odds - 1)

    scaling_factor = min(edge / 0.05, 1.0)
    return raw_kelly * scaling_factor


def uncertainty_adjusted_kelly(
    prob_win,
    decimal_odds,
    prob_std
):
    """
    Calculate an uncertainty-adjusted Kelly fraction.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        decimal_odds (float): The decimal odds for the bet.
        prob_std (float): Standard deviation of the probability estimate.
    """
    edge = prob_win * (decimal_odds - 1) - (1 - prob_win)
    variance_penalty = prob_std * (decimal_odds - 1)

    adjusted_edge = max(edge - variance_penalty, 0)
    return adjusted_edge / (decimal_odds - 1)


def drawdown_adjusted_kelly(
    kelly_fraction,
    current_bankroll,
    peak_bankroll,
    max_drawdown=0.3
):
    """
    Calculate a drawdown-adjusted Kelly fraction.

    Args:
        kelly_fraction (float): The raw Kelly fraction.
        current_bankroll (float): The current bankroll.
        peak_bankroll (float): The peak bankroll achieved.
        max_drawdown (float): Maximum acceptable drawdown as a fraction of peak bankroll.
    """
    if peak_bankroll <= 0:
        return kelly_fraction
    
    drawdown = (peak_bankroll - current_bankroll) / peak_bankroll
    if drawdown >= max_drawdown:
        return 0.0
    
    drawdown_factor = 1 - (drawdown / max_drawdown)
    return kelly_fraction * drawdown_factor


def kelly_regime(kelly_fraction):
    """
    Determine betting regime based on Kelly fraction.

    Args:
        kelly_fraction (float): The Kelly fraction of bankroll to wager (between 0 and 1).

    Returns:
        str: Betting regime.
    """

    if kelly_fraction == 0:
        return "NO BET"
    elif kelly_fraction < 0.2:
        return "CONSERVATIVE"
    elif kelly_fraction < 0.5:
        return "AGGRESSIVE"
    else:
        return "SPECULATIVE"