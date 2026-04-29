"""Port Economics - Container port analytics"""
from typing import Dict

class PortEconomics:
    """Analyze container port economics"""
    
    def throughput_value(self, teu_annual: int,
                        revenue_per_teu: float,
                        utilization_pct: float) -> Dict:
        """Calculate port throughput value"""
        annual_revenue = teu_annual * revenue_per_teu
        capacity_constrained = utilization_pct > 85
        
        return {
            "annual_teu": teu_annual,
            "annual_revenue": round(annual_revenue, 0),
            "utilization": utilization_pct,
            "capacity_constrained": capacity_constrained,
            "expansion_needed": utilization_pct > 90,
            "revenue_per_teu": revenue_per_teu
        }
    
    def concession_value(self, annual_guarantee: float,
                        revenue_share_pct: float,
                        port_revenue: float,
                        years_remaining: int) -> Dict:
        """Value port concession agreement"""
        revenue_share = port_revenue * (revenue_share_pct / 100)
        annual_total = annual_guarantee + revenue_share
        concession_npv = annual_total * min(years_remaining, 20)  # Simplified
        
        return {
            "annual_guarantee": annual_guarantee,
            "revenue_share": round(revenue_share, 0),
            "annual_total": round(annual_total, 0),
            "concession_npv": round(concession_npv, 0),
            "years_remaining": years_remaining
        }
