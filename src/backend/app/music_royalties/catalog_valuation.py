"""Catalog Valuation"""
from typing import Dict

class CatalogValuation:
    """Value music catalogs"""
    
    def multiple_approach(self, annual_royalties: float, 
                         growth_rate: float) -> Dict:
        """Value based on multiples"""
        # Catalogs trade 10-15x NPS depending on vintage
        base_multiple = 12.0
        growth_adj = growth_rate * 20
        multiple = base_multiple + growth_adj
        
        return {"annual_royalties": annual_royalties, "multiple": multiple, "value": annual_royalties * multiple}
    
    def dcf_approach(self, year1_royalties: float, growth: float,
                    decline: float, years: int) -> Dict:
        """DCF valuation for catalog"""
        cash_flows = []
        for y in range(1, years + 1):
            growth_phase = 1 + growth if y <= 3 else 1 - decline
            cf = year1_royalties * (growth_phase ** y)
            cash_flows.append(cf / (1.1 ** y))
        
        return {"dcf_value": sum(cash_flows), "terminal_years": years}
