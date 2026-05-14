"""Grid Trading Bot - Phase 11 Extension"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class GridStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

@dataclass
class GridLevel:
    price: float
    buy_filled: bool = False
    sell_filled: bool = False
    quantity: float = 0.0

@dataclass
class GridConfig:
    symbol: str
    lower: float
    upper: float
    grids: int = 10
    investment: float = 100.0
    paper: bool = True

class GridBot:
    """Grid trading for sideways markets. Buys low, sells high."""
    
    def __init__(self, config: GridConfig):
        self.config = config
        self.status = GridStatus.STOPPED
        self.levels: List[GridLevel] = []
        self.profit = 0.0
        self.trades = 0
        self.spacing = (config.upper - config.lower) / config.grids
        self.qty_per_grid = config.investment / config.grids
        self._init_grids()
    
    def _init_grids(self):
        for i in range(self.config.grids + 1):
            price = self.config.lower + (i * self.spacing)
            self.levels.append(GridLevel(price=price))
    
    def start(self):
        self.status = GridStatus.ACTIVE
        logger.info(f"Grid bot started: {self.config.symbol}")
    
    def get_status(self) -> Dict:
        return {
            "symbol": self.config.symbol,
            "status": self.status.value,
            "range": f"{self.config.lower}-{self.config.upper}",
            "grids": self.config.grids,
            "profit": self.profit,
            "trades": self.trades
        }

class PionexGridBot(GridBot):
    """Pionex-optimized grid bot with 0.05% fees"""
    
    def __init__(self, symbol: str, lower: float, upper: float, 
                 grids: int = 10, investment: float = 100.0):
        config = GridConfig(
            symbol=symbol, lower=lower, upper=upper,
            grids=grids, investment=investment, paper=True
        )
        super().__init__(config)
        self.fee = 0.0005  # 0.05%
    
    def calculate_net_profit(self, grid_num: int) -> float:
        gross = self.spacing * self.qty_per_grid
        fees = self.qty_per_grid * (self.config.lower + self.spacing) * self.fee * 2
        return gross - fees
