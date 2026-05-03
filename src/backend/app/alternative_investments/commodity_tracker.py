"""Commodity Tracker - Alternative commodity investments"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class CommodityHolding:
    commodity: str
    units: float
    unit_price: float
    purchase_date: date

class CommodityTracker:
    """Track commodity investments"""
    
    def __init__(self):
        self.holdings: List[CommodityHolding] = []
    
    def add_holding(self, holding: CommodityHolding):
        self.holdings.append(holding)
    
    def get_summary(self) -> Dict:
        total_value = sum(h.units * h.unit_price for h in self.holdings)
        return {
            'holdings': len(self.holdings),
            'total_value': round(total_value, 2),
            'commodities': list(set(h.commodity for h in self.holdings))
        }
