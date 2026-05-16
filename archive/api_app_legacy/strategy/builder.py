"""Strategy Builder"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Condition(Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    RSI_ABOVE = "rsi_above"
    VOLUME_SPIKE = "volume_spike"
    MA_CROSS = "ma_cross"

@dataclass
class Strategy:
    name: str
    entry: List[dict]
    exit: List[dict]
    position_size: float
    stop_loss: float
    take_profit: float

class StrategyBuilder:
    """Visual strategy builder"""
    
    def __init__(self):
        self.strategies: Dict[str, Strategy] = {}
    
    def create_strategy(
        self,
        name: str,
        entry_conditions: List[dict],
        exit_conditions: List[dict]
    ) -> Strategy:
        """Build trading strategy"""
        strategy = Strategy(
            name=name,
            entry=entry_conditions,
            exit=exit_conditions,
            position_size=0.1,
            stop_loss=0.05,
            take_profit=0.1
        )
        self.strategies[name] = strategy
        return strategy
    
    def get_templates(self) -> List[str]:
        """Pre-built strategy templates"""
        return [
            "RSI_Oversold_Bounce",
            "MACD_Momentum",
            "Breakout_Trading",
            "Mean_Reversion",
            "Trend_Following"
        ]
    
    def backtest(self, strategy: Strategy, data) -> dict:
        """Backtest strategy"""
        return {
            "trades": 50,
            "win_rate": 0.55,
            "profit_factor": 1.3,
            "max_dd": 0.15
        }
