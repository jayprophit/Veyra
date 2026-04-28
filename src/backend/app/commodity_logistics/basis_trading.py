"""Basis Trading"""
from typing import Dict

class BasisTrading:
    """Analyze basis trades"""
    
    def basis_calculation(self, spot_price: float, 
                         futures_price: float) -> Dict:
        """Calculate basis"""
        basis = spot_price - futures_price
        return {"basis": basis, "contango": basis < 0, "backwardation": basis > 0}
    
    def storage_arb(self, spot: float, future: float,
                   storage_cost: float, months: int) -> Dict:
        """Arbitrage storage play"""
        carry_return = future - spot - storage_cost
        annualized = (carry_return / spot) * (12 / months) * 100 if spot > 0 else 0
        
        return {
            "gross_carry": future - spot,
            "net_carry": carry_return,
            "annualized_return": annualized,
            "profitable": carry_return > 0
        }
