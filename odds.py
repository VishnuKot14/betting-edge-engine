"""Utility functions for working with betting odds.

This module provides functions to convert between different formats of betting odds,
including decimal, fractional, and American odds."""


def implied_probability(odds: int) -> float:
    """
    Calculate the implied probability from American odds.

    Args:
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        

    Returns: 
        float: The implied probability as a decimal between 0 and 1.    
    """
    
    if odds == 0:
        raise ValueError("Odds cannot be zero.")
    
    if odds > 0:
        probability = 100 / (odds + 100)
    else:
        probability = abs(odds) / (abs(odds) + 100)
    return probability


def american_to_decimal(american_odds: int) -> float:
    """
    Convert American odds to decimal odds.

    Args:
        american_odds (int): The American odds. Positive for underdogs, negative for favorites.

    Returns:
        float: The decimal odds.
    """
    
    if american_odds == 0:
        raise ValueError("Odds cannot be zero.")
    
    if american_odds > 0:
        decimal_odds = 1 + (american_odds / 100)
    else:
        decimal_odds = 1 + (100 / abs(american_odds))
    return decimal_odds


def payout_profit(odds: int, stake: float) -> float:
    """
    Calculate the profit from a bet given American odds and stake.

    Args:
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        stake (float): The amount of money wagered.

    Returns:
        float: The profit from the bet.     
    """
    
    if odds == 0:
        raise ValueError("Odds cannot be zero.")
    
    if odds > 0:
        profit = (odds / 100) * stake
    else:
        profit = (100 / abs(odds)) * stake
    return profit


def break_even_probability(odds: int) -> float:
    """
    Alias for implied probability.
    Represents the win probabiity needed to break even on a bet.

    Args:
        odds (int): The American odds. Positive for underdogs, negative for favorites.
        
    Returns:
        float: The break-even probability as a decimal between 0 and 1. 
    """
    
    return implied_probability(odds)
    
    
        