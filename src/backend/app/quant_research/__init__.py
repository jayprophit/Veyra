"""Quant Research Platform - Backtesting framework and alpha research tools"""

from .backtest_framework import BacktestFramework
from .alpha_research import AlphaResearch
from .signal_generator import SignalGenerator

__all__ = [
    "BacktestFramework",
    "AlphaResearch",
    "SignalGenerator"
]
