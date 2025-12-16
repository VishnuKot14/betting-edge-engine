"""
main.py

Demo script for the Bet Risk Engine.
Shows evaluation, Kelly sizing, and Monte Carlo simulation.
"""

from ev import evaluate_bet
from kelly import kelly_bet_size, risk_level
from simulation import simulate_kelly_paths

def main():
    # ------------------------------
    # 1. Define example bet
    # ------------------------------
    odds = -110             # American odds
    prob_win = 0.545         # User's estimated probability
    stake = 100             # Amount for single bet
    bankroll = 1000         # Total bankroll for simulations
    fractional_kelly = 0.5  # Use half Kelly for safety

    print("=== Bet Risk Engine Demo ===\n")

    # ------------------------------
    # 2. Evaluate single bet
    # ------------------------------
    print(">>> Single Bet Evaluation:")
    evaluation = evaluate_bet(prob_win, odds, stake)
    for key, value in evaluation.items():
        print(f"{key}: {value}")
    
    # ------------------------------
    # 3. Calculate Kelly bet size
    # ------------------------------
    print("\n>>> Kelly Criterion Bet Sizing:")
    recommended_bet = kelly_bet_size(prob_win, odds, bankroll, fractional_kelly)
    risk = risk_level(recommended_bet / bankroll)
    print(f"Recommended bet: ${recommended_bet}")
    print(f"Risk level: {risk}")

    # ------------------------------
    # 4. Run Monte Carlo simulation
    # ------------------------------
    print("\n>>> Monte Carlo Simulation (Bankroll Evolution):")
    simulation_results = simulate_kelly_paths(
        prob_win=prob_win,
        odds=odds,
        bankroll=bankroll,
        num_bets=200,
        num_simulations=5000,
        kelly_multiplier=fractional_kelly
    )
    for key, value in simulation_results.items():
        print(f"{key}: {value}")

    print("\n=== Demo Complete ===")

if __name__ == "__main__":
    main()
