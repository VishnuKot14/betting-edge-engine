"""
simulation.py

Monte Carlo simulations for bankroll evolution.
Demonstrates variance, risk of ruin, and long-term outcomes.
"""

import random
import numpy as np

from odds import american_to_decimal

def simulate_single_path(
    prob_win: float,
    odds: int,
    bankroll: float,
    stake: float,
    num_bets: int
) -> list:
    """
    Simulate a single betting path over a number of bets.

    Args:
        prob_win (float): The estimated probability of winning each bet (between 0 and 1).
        odds (int): The American odds for each bet.
        bankroll (float): The initial bankroll.
        stake (float): The fixed stake for each bet.
        num_bets (int): The number of bets to simulate.
    
    Returns:
        list: The bankroll evolution over the number of bets.
    """

    path = [bankroll]

    for _ in range(num_bets):
        if bankroll <= 0:
            path.append(0)
            continue
    
        win = random.random() < prob_win

        if odds > 0:
            profit = stake * (odds / 100)
        else:
            profit = stake * (100 / abs(odds))
    
        bankroll += profit if win else -stake
        bankroll = max(bankroll, 0)
        path.append(bankroll)
    
    return path



def simulate_kelly_paths(
    prob_win,
    odds,
    bankroll,
    num_bets,
    num_simulations,
    kelly_multiplier=1.0
):
    initial_bankroll = bankroll
    ruin_threshold = 0.1 * initial_bankroll

    final_bankrolls = []
    ruin_count = 0

    decimal_odds = american_to_decimal(odds)

    for _ in range(num_simulations):
        bankroll = initial_bankroll
        ruined = False

        for _ in range(num_bets):
            kelly_fraction = (
                (prob_win * (decimal_odds - 1) - (1 - prob_win))
                / (decimal_odds - 1)
            )

            bet_fraction = max(kelly_fraction * kelly_multiplier, 0)
            bet_size = bankroll * bet_fraction

            if np.random.rand() < prob_win:
                bankroll += bet_size * (decimal_odds - 1)
            else:
                bankroll -= bet_size

            # ---- RUIN CHECK 
            if bankroll <= ruin_threshold:
                ruined = True
                break

        final_bankrolls.append(bankroll)

        if ruined:
            ruin_count += 1

    return {
        "mean_final_bankroll": round(np.mean(final_bankrolls), 2),
        "median_final_bankroll": round(np.median(final_bankrolls), 2),
        "probability_of_profit": round(
            np.mean(np.array(final_bankrolls) > initial_bankroll), 3
        ),
        "probability_of_ruin": round(ruin_count / num_simulations, 3)
    }
