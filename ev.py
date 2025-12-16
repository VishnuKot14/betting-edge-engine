"""
Expected Value (EV) calculations and bet quality evlauation.
Uses probability and odds to determine long-term profitability of bets.
"""

from odds import implied_probability

def payout_from_american_odds(odds: int, stake: float) -> float:
    """Calculate the total payout from a bet given American odds and stake.

    Args:
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        stake (float): The amount of money wagered.
    
    Returns:
        float: The total payout from the bet.
    """
    
    if odds == 0:
        raise ValueError("Odds cannot be zero.")
    if odds > 0:
        return stake * (odds / 100)
    else:
        return stake * (100 / abs(odds))
    

def expected_value(prob_win: float, odds: int, stake: float) -> float:
    """Calculate the expected value (EV) of a bet.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        stake (float): The amount of money wagered.
    
    Returns:
        float: The expected value of the bet.
        """
    
    if not (0 <= prob_win <= 1):
        raise ValueError("Probability must be between 0 and 1.")
    
    profit = payout_from_american_odds(odds, stake)
    ev = (prob_win * profit) - ((1 - prob_win) * stake)
    return ev


def bet_quality(prob_win: float, odds: int) -> str:
    """
    Determine qualitative bet rating based on edge.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        odds (int): The American odds. Positive for underdogs, negative for favorites.
    
    Returns:
        str: Qualitative rating of the bet.
    """

    implied_prob = implied_probability(odds)
    edge = prob_win - implied_prob

    if edge > 0.05:
        return "STRONG POSITIVE EDGE"
    elif edge > 0:
        return "SMALL POSITIVE EDGE"
    elif abs(edge) < 0.01:
        return "BREAKEVEN"
    else:
        return "NEGATIVE EDGE"


def evaluate_bet(prob_win: float, odds: int, stake: float) -> dict:
    """
    Evaluate a bet and provide expected value and qualitative rating.

    Args:
        prob_win (float): The estimated probability of winning the bet (between 0 and 1).
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        stake (float): The amount of money wagered.
    
    Returns:
        dict: A dictionary containing expected value and bet quality rating.
    """
    implied_prob = implied_probability(odds)
    edge = prob_win - implied_prob
    ev = expected_value(prob_win, odds, stake)

    verdict = "GOOD BET" if ev > 0 else "BAD BET"

    return {
        "implied_probability": round(implied_prob, 4),
        "estimated_probability": round(prob_win, 4),
        "edge": round(edge, 4),
        "expected_value": round(ev, 2),
        "verdict": verdict,
        "bet_quality": bet_quality(prob_win, odds)
    }