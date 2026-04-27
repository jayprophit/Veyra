"""Quantitative Strategies - Statistical arbitrage, pairs trading, mean reversion"""

from .pairs_trading import PairsTradingEngine
from .stat_arb import StatisticalArbitrage
from .mean_reversion import MeanReversionStrategy
from .momentum_quant import QuantitativeMomentum

__all__ = [
    "PairsTradingEngine",
    "StatisticalArbitrage",
    "MeanReversionStrategy",
    "QuantitativeMomentum"
]
