"""Event-Driven Strategies - Merger arb, activism, special situations"""

from .merger_arbitrage import MergerArbitrage
from .activism_tracker import ActivismTracker
from .special_situations import SpecialSituations

__all__ = [
    "MergerArbitrage",
    "ActivismTracker",
    "SpecialSituations"
]
