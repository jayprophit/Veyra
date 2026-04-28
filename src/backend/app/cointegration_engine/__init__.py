"""Cointegration Engine - Statistical arbitrage via cointegration analysis"""

from .pair_analyzer import PairAnalyzer
from .spread_trader import SpreadTrader
from .mean_reversion_detector import MeanReversionDetector

__all__ = [
    "PairAnalyzer",
    "SpreadTrader",
    "MeanReversionDetector"
]
