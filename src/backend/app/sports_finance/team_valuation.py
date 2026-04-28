"""Team Valuation - Sports franchise valuation"""
from typing import Dict

class TeamValuation:
    """Value sports franchises"""
    
    MULTIPLES = {
        "nfl": 8.0, "nba": 7.0, "mlb": 6.0, 
        "nhl": 5.0, "premier_league": 6.5, "mls": 4.0
    }
    
    def value_by_revenue(self, league: str, revenue: float, 
                        market_size: str = "medium") -> Dict:
        """Value team based on revenue"""
        base_multiple = self.MULTIPLES.get(league.lower(), 5.0)
        
        # Market size adjustment
        market_adj = {"small": 0.8, "medium": 1.0, "large": 1.3}
        adj = market_adj.get(market_size, 1.0)
        
        enterprise_value = revenue * base_multiple * adj
        
        return {
            "enterprise_value": enterprise_value,
            "revenue_multiple": base_multiple * adj,
            "league": league,
            "market_size": market_size
        }
    
    def value_by_enterprise(self, ebitda: float, growth_rate: float) -> Dict:
        """DCF valuation for sports teams"""
        # Sports teams typically 10-12x EBITDA
        multiple = 11.0 * (1 + growth_rate)
        return {"dcf_value": ebitda * multiple, "ebitda_multiple": multiple}
