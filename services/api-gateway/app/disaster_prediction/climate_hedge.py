"""Climate Hedge Optimizer"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ClimateRisk:
    region: str
    risk_type: str
    probability: float
    projected_impact_usd: float

class ClimateHedgeOptimizer:
    """Optimize hedges for climate risk"""
    
    def __init__(self):
        self.hedge_instruments = {
            "agriculture": ["DBA", "CORN", "SOYB", "WEAT"],
            "water": ["CGW", "FIW", "PHO"],
            "renewable": ["ICLN", "TAN", "FAN"],
            "carbon": ["KRBN", "GRN", "NETZ"],
            "insurance": ["KIE", "IAK", "XLI"]
        }
    
    def optimize_hedge(self, portfolio: Dict[str, float], risks: List[ClimateRisk]) -> Dict:
        """Generate optimal climate hedge"""
        total_value = sum(portfolio.values())
        
        # Identify exposure
        exposed_sectors = {}
        for risk in risks:
            if risk.probability > 0.3:
                exposed_sectors[risk.risk_type] = exposed_sectors.get(risk.risk_type, 0) + risk.projected_impact_usd
        
        # Calculate hedge allocation
        hedge_allocation = []
        for risk_type, exposure in exposed_sectors.items():
            instruments = self.hedge_instruments.get(risk_type, [])
            allocation = min(exposure / total_value * 0.5, 0.1)  # Cap at 10%
            
            hedge_allocation.append({
                "risk_type": risk_type,
                "exposure_pct": round((exposure / total_value) * 100, 2),
                "recommended_hedge": instruments[:3],
                "allocation_pct": round(allocation * 100, 2)
            })
        
        return {
            "portfolio_value": total_value,
            "climate_risk_exposure": exposed_sectors,
            "hedge_allocation": hedge_allocation,
            "total_hedge_cost_pct": round(sum(h["allocation_pct"] for h in hedge_allocation), 2)
        }
    
    def get_climate_alpha(self, scenario: str) -> Dict:
        """Get climate alpha opportunities"""
        scenarios = {
            "warming_2c": {
                "winners": ["TAN", "ICLN", "ENPH", "SEDG"],
                "losers": ["XLE", "OIL", "KOL"],
                "strategy": "Long renewables, short fossil fuels"
            },
            "drought_severe": {
                "winners": ["CGW", "XYL", "AWK"],
                "losers": ["DBA", "ADM", "BG"],
                "strategy": "Long water infrastructure, short agriculture"
            },
            "hurricane_intense": {
                "winners": ["LOW", "HD", "CAT"],
                "losers": ["KIE", "PGR", "TRV"],
                "strategy": "Long rebuild plays, short insurance"
            }
        }
        
        return scenarios.get(scenario, {"strategy": "No data available"})
