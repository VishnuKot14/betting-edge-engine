# Betting Edge & Risk Evaluation Engine

OVERVIEW
This project is a risk-aware betting analytics engine that evaluates whether a wager is favorable by combining expected value anyalsis, odds normalization, Kelly-optimal sizing, and Monte Carlo risk simulation.

Rather than focusing on predicting winners, bets are treated as financial investments under uncertainty, epmhasizing capital allocation, variance, and downside risk.

MOTIVATION
I created this project from a personal interest in sports betting and a curiosity about why most bettors lose even when they believe they have an edge. Through experience, it became clear that outcomes are often dominated not by picking winners, but by poor sizing, overconfidence, and blind-betting.

I wanted to appraoch betting as a financial decision-making problem, similar to how capital is allocated in trading or investing. This project reflects my shift in perspective of focusing less on prediction accuracy and more on expected value, uncertianty, and making a long-term profit.


# System Components

ODDS & PRICING(odds.py)
- Converts American odds to decimal odds
- Computes implied market probabilities
- Normalizes sportsbook pricing for EV analysis

EXPECTED VALUE(ev.py)
- Calculates expected value using true probability estimates
- Quantifies edge over the market
- Separates long-term profitability from short-term variance

RISK-ADJUSTED KELLY ALLOCATION(kelly.py)
- Edge-aware scaling (shrinks small edges)
- Uncertainty-aware penalties (models estimation error)
- Drawdown-based exposure limits
- Risk regime classification (No/Low/Moderate/High conviction)

MONTE CARLO SIMULATION(simulation.py)
- Simulates thousands of betting paths
- Tracks bankroll evolution over time
- Computes drawdown-based probability of ruin
- Demonstrates variance even with positive EV strategies

DEMONSTRATION(main.py)
- Standard sportsbook odds (-110)
- Small informational edge (~54-55%)
- Fractional Kelly sizing
- Bankroll and drawdown constraints


# Purpose, Limitations & Future Work

PURPOSE
The purpose of this project is to analyze how small statistical edges trasnlate into long-term outcomes when risk, uncertainty, and bankroll constraints are properly managed. Rather than focusin on prediction accuracy, the system ephasizes capital allocation, variance, and survivability, modeling bets as financial investments under uncertainty. By using expected value analysis, risk-adjusted Kelly sizing, and Monte Carlo simulation, the project demonstrates how disciplined sizing and risk control are often more important than simply picking winners.

LIMITATIONS
- Probability estimates are user-supplied (no predictive model yet)
- Assumes independent bets
- Simplified market efficiency assumptions

FUTURE EXTENSIONS
- Machine learning probability estimation
- Live odds ingestion
- Multi-bet portfolio optimization


