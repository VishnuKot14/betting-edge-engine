import matplotlib.pyplot as plt

from odds import american_to_decimal
from simulation import run_strategy_simulation
from strategies import (
    flat_bet,
    fixed_fraction,
    min_bet_wrapper,
    risk_adjusted_kelly_strategy,
)


def print_summary(name: str, summary: dict) -> None:
    """Pretty-print summary metrics for one strategy."""
    print(f"\n=== {name} ===")
    print(f"Mean Final Bankroll:   ${summary['mean_final_bankroll']:.2f}")
    print(f"Median Final Bankroll: ${summary['median_final_bankroll']:.2f}")
    print(f"Prob. Profit:          {summary['probability_of_profit']:.3f}")
    print(f"Prob. Ruin:            {summary['probability_of_ruin']:.3f}")
    print(f"Mean Max Drawdown:     {summary['mean_max_drawdown']:.3f}")
    print(f"Median Max Drawdown:   {summary['median_max_drawdown']:.3f}")


def plot_paths(sample_paths, title: str) -> None:
    """Plot multiple bankroll paths to visualize volatility and drawdowns."""
    plt.figure()
    for path in sample_paths:
        plt.plot(path)
    plt.title(title)
    plt.xlabel("Bet #")
    plt.ylabel("Bankroll")


def plot_hist(values, title: str, xlabel: str) -> None:
    """Plot a histogram for a distribution (final bankrolls, drawdowns, etc.)."""
    plt.figure()
    plt.hist(values, bins=40)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("Frequency")


def main():
    # ------------------------------
    # Global simulation settings
    # ------------------------------
    odds = -110
    prob_win = 0.545          # realistic small edge
    prob_std = 0.02           # uncertainty in your estimate
    initial_bankroll = 1000
    n_bets = 300
    n_sims = 5000
    ruin_threshold = 0.4      # "ruin" = bankroll <= 40% of initial
    seed = 42                 # reproducibility

    decimal_odds = american_to_decimal(odds)

    print("=== SETUP ===")
    print(f"Odds (American): {odds}")
    print(f"Odds (Decimal):  {decimal_odds:.3f}")
    print(f"Prob(win):       {prob_win:.3f}")
    print(f"Bankroll:        ${initial_bankroll}")
    print(f"Bets/Sims:       {n_bets} bets, {n_sims} simulations")
    print(f"Ruin Threshold:  {ruin_threshold:.0%} of initial bankroll")

    # ------------------------------
    # Define strategies to compare
    # ------------------------------
    strategies = {
        "Flat $10": flat_bet(10),
        "2% Fraction": fixed_fraction(0.02),
        "2% Fraction (Min $10)": min_bet_wrapper(fixed_fraction(0.02), min_bet=10),
        "Risk-Adjusted Kelly (Half Kelly)": risk_adjusted_kelly_strategy(
            prob_win=prob_win,
            decimal_odds=decimal_odds,
            prob_std=prob_std,
            kelly_multiplier=0.5,
            edge_threshold=0.01,
            max_drawdown=0.3
        ),
    }

    # ------------------------------
    # Run simulations and plot
    # ------------------------------
    # We'll plot for ONE strategy (most useful: risk-adjusted Kelly),
    # but we will print summaries for all strategies.
    results_by_strategy = {}

    for name, bet_fn in strategies.items():
        results = run_strategy_simulation(
            prob_win=prob_win,
            decimal_odds=decimal_odds,
            initial_bankroll=initial_bankroll,
            n_bets=n_bets,
            n_sims=n_sims,
            bet_size_fn=bet_fn,
            ruin_threshold=ruin_threshold,
            n_paths_to_store=30,  # store some paths for plotting
            seed=seed
        )
        results_by_strategy[name] = results
        print_summary(name, results["summary"])

    # ------------------------------
    # Matplotlib showcase (pick one strategy to visualize deeply)
    # ------------------------------
    showcase_name = "Risk-Adjusted Kelly (Half Kelly)"
    showcase = results_by_strategy[showcase_name]

    plot_paths(showcase["sample_paths"], f"{showcase_name} — Sample Bankroll Paths")
    plot_hist(showcase["final_bankrolls"], f"{showcase_name} — Final Bankroll Distribution", "Final Bankroll")
    plot_hist(showcase["max_drawdowns"], f"{showcase_name} — Max Drawdown Distribution", "Max Drawdown (fraction)")

    plt.show()


if __name__ == "__main__":
    main()

