"""Vertiport Infrastructure Economics"""
from typing import Dict

class VertiportInfrastructure:
    """Analyze urban air mobility vertiport investments"""
    
    def __init__(self, location_type: str = "urban", pad_count: int = 2):
        self.location = location_type  # urban, suburban, airport
        self.pads = pad_count
    
    def capex_analysis(self) -> Dict:
        costs = {
            "urban": {"base": 5.0e6, "per_pad": 1.5e6},
            "suburban": {"base": 3.0e6, "per_pad": 1.0e6},
            "airport": {"base": 2.0e6, "per_pad": 0.8e6}
        }
        
        c = costs.get(self.location, costs["urban"])
        total = c["base"] + (c["per_pad"] * self.pads)
        
        return {
            "total_capex": round(total, 0),
            "base_cost": c["base"],
            "pad_costs": c["per_pad"] * self.pads,
            "per_pad": c["per_pad"],
            "includes": ["Landing pads", "Passenger terminal", "Charging", "Maintenance"]
        }
    
    def revenue_model(self, daily_landings_per_pad: int = 30) -> Dict:
        landing_fee = 50
        annual_ops = daily_landings_per_pad * self.pads * 365
        
        gross_revenue = annual_ops * landing_fee
        
        # Operating costs
        staff = 200000
        maintenance = 100000 * self.pads
        utilities = 50000
        total_opex = staff + maintenance + utilities
        
        net_operating_income = gross_revenue - total_opex
        
        return {
            "annual_landings": annual_ops,
            "gross_revenue": round(gross_revenue, 0),
            "operating_costs": round(total_opex, 0),
            "noi": round(net_operating_income, 0),
            "landing_fee": landing_fee
        }
    
    def investment_return(self, daily_landings: int = 30) -> Dict:
        capex = self.capex_analysis()["total_capex"]
        rev = self.revenue_model(daily_landings)
        
        cap_rate = 0.08
        terminal_value = rev["noi"] / cap_rate if rev["noi"] > 0 else 0
        
        simple_yield = rev["noi"] / capex * 100
        
        return {
            "capex": capex,
            "annual_noi": rev["noi"],
            "simple_yield_pct": round(simple_yield, 2),
            "terminal_value": round(terminal_value, 0),
            "payback_years": round(capex / rev["noi"], 1) if rev["noi"] > 0 else float('inf')
        }
    
    def network_planning(self, city_population_millions: float = 5) -> Dict:
        # Vertiports needed based on population density
        vertiports_needed = int(city_population_millions * 3)  # 3 per million
        
        # Mix: 60% urban, 30% suburban, 10% airport
        mix = {
            "urban": int(vertiports_needed * 0.6),
            "suburban": int(vertiports_needed * 0.3),
            "airport": int(vertiports_needed * 0.1)
        }
        
        # Average cost per vertiport
        avg_capex = (5.0e6 + 3.0e6 + 2.0e6) / 3
        total_network_cost = vertiports_needed * avg_capex
        
        return {
            "city_population_millions": city_population_millions,
            "vertiports_needed": vertiports_needed,
            "mix": mix,
            "total_network_cost_millions": round(total_network_cost / 1e6, 1),
            "timeline_years": 5,
            "annual_capex_required": round(total_network_cost / 5 / 1e6, 1)
        }
