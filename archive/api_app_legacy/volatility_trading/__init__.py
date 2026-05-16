"""Volatility Trading - VIX strategies, volatility arbitrage, variance swaps"""

from .vix_strategy import VIXStrategy
from .volatility_arbitrage import VolatilityArbitrage
from .term_structure_analyzer import TermStructureAnalyzer

__all__ = [
    "VIXStrategy",
    "VolatilityArbitrage",
    "TermStructureAnalyzer"
]
