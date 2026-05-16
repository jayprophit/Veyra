"""Merger Arbitrage - Merger arbitrage opportunity tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class MergerDeal:
    deal_id: str
    acquirer: str
    target: str
    offer_price: float
    current_price: float
    expected_close: date
    status: str  # 'pending', 'approved', 'completed', 'cancelled'

class MergerArbitrage:
    """Track merger arbitrage opportunities"""
    
    def __init__(self):
        self.deals: List[MergerDeal] = []
    
    def add_deal(self, deal: MergerDeal):
        self.deals.append(deal)
    
    def calculate_spread(self, deal: MergerDeal) -> float:
        return (deal.offer_price - deal.current_price) / deal.current_price * 100
    
    def get_summary(self) -> Dict:
        active = [d for d in self.deals if d.status == 'pending']
        return {
            'deals_tracked': len(self.deals),
            'active_deals': len(active),
            'avg_spread_pct': sum(self.calculate_spread(d) for d in active) / len(active) if active else 0
        }
