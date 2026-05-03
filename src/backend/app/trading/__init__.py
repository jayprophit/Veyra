"""
Advanced Trading Strategies Module
Automated trading with arbitrage, grid, momentum, and HODL strategies
"""

from .strategies import ArbitrageStrategy, GridTradingStrategy, MomentumStrategy, HODLStrategy
from .indicators import PatternRecognition, VolumeAnalysis, OrderFlow
from .kyc import KYCManager
from .external_data import WeatherTrading, SeasonalTrading
from .smart_contracts import TradingToken, SubscriptionManager

__all__ = [
    'ArbitrageStrategy',
    'GridTradingStrategy', 
    'MomentumStrategy',
    'HODLStrategy',
    'PatternRecognition',
    'VolumeAnalysis',
    'OrderFlow',
    'KYCManager',
    'WeatherTrading',
    'SeasonalTrading',
    'TradingToken',
    'SubscriptionManager'
]
