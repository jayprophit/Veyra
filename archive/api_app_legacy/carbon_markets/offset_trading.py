"""Offset Trading"""
from typing import Dict

class OffsetTrading:
    def arb_opportunity(self, market_a_price: float, market_b_price: float, tonnes: int) -> Dict:
        spread = abs(market_a_price - market_b_price)
        return {"spread_per_tonne": spread, "total_profit": spread * tonnes, "viable": spread > 5}
