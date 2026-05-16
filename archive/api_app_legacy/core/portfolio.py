"""Core Portfolio - Portfolio management base module"""
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Holding:
    symbol: str
    shares: float
    avg_cost: float
    current_price: float

class Portfolio:
    """Core portfolio management"""
    
    def __init__(self, name: str = "Portfolio"):
        self.name = name
        self.holdings: List[Holding] = []
    
    def add_holding(self, holding: Holding):
        self.holdings.append(holding)
    
    def get_value(self) -> float:
        return sum(h.shares * h.current_price for h in self.holdings)
    
    def get_summary(self) -> Dict:
        value = self.get_value()
        cost = sum(h.shares * h.avg_cost for h in self.holdings)
        return {
            'name': self.name,
            'holdings': len(self.holdings),
            'total_value': round(value, 2),
            'total_cost': round(cost, 2),
            'unrealized_pnl': round(value - cost, 2)
        }
