"""Orbital Space Hotel Economics"""
from typing import Dict

class OrbitalHospitality:
    """Analyze orbital space station and hotel investments"""
    
    def __init__(self, capacity: int = 4):
        self.capacity = capacity  # Guests at a time
    
    def station_capex(self) -> Dict:
        # ISS cost comparison: $150B for 7 people
        # Commercial station should be cheaper
        
        module_cost = 500e6  # $500M per module
        modules_needed = max(1, self.capacity / 4)
        
        life_support = 200e6
        power_systems = 150e6
        docking = 100e6
        communication = 50e6
        
        development = 300e6  # R&D
        launch_cost = modules_needed * 100e6  # $100M per launch
        
        total = ((module_cost * modules_needed) + life_support + power_systems +
                docking + communication + development + launch_cost)
        
        return {
            "total_capex_millions": round(total / 1e6, 0),
            "modules": round(modules_needed, 0),
            "module_cost_millions": module_cost / 1e6,
            "life_support_millions": life_support / 1e6,
            "launch_cost_millions": launch_cost / 1e6,
            "per_guest_capacity_cost_millions": round(total / self.capacity / 1e6, 1)
        }
    
    def hospitality_economics(self, stays_per_year: int = 12) -> Dict:
        # Pricing strategy
        duration_days = 7
        price_per_day = 500000  # $500K per night
        stay_price = duration_days * price_per_day
        
        # Annual capacity
        annual_guests = self.capacity * stays_per_year
        
        # Revenue
        annual_revenue = annual_guests * stay_price
        
        # Operating costs
        resupply_per_guest = 50e6  # Food, water, air
        crew_cost_per_guest = 20e6  # 2 crew per guest
        maintenance = 50e6  # Annual
        insurance = 30e6
        
        annual_opex = ((annual_guests * (resupply_per_guest + crew_cost_per_guest)) +
                      maintenance + insurance)
        
        ebitda = annual_revenue - annual_opex
        
        return {
            "guest_capacity": self.capacity,
            "stays_per_year": stays_per_year,
            "annual_guests": annual_guests,
            "price_per_7day_stay": stay_price,
            "annual_revenue_millions": round(annual_revenue / 1e6, 1),
            "annual_opex_millions": round(annual_opex / 1e6, 1),
            "ebitda_millions": round(ebitda / 1e6, 1),
            "margin_pct": round(ebitda / annual_revenue * 100, 1)
        }
    
    def investment_returns(self) -> Dict:
        capex = self.station_capex()["total_capex_millions"] * 1e6
        ops = self.hospitality_economics()
        
        ebitda = ops["ebitda_millions"] * 1e6
        
        # Simple DCF
        years = 15  # Station lifetime
        exit_multiple = 8
        
        # Assume some growth
        terminal_value = ebitda * exit_multiple * (1.1 ** years)
        
        # Simplified IRR
        if ebitda > 0 and capex > 0:
            simple_irr = ((ebitda * years + terminal_value) / capex) ** (1/years) - 1
            irr_pct = simple_irr * 100
        else:
            irr_pct = 0
        
        payback = capex / ebitda if ebitda > 0 else float('inf')
        
        return {
            "capex_millions": capex / 1e6,
            "annual_ebitda_millions": ops["ebitda_millions"],
            "terminal_value_millions": round(terminal_value / 1e6, 0),
            "estimated_irr_pct": round(irr_pct, 1),
            "payback_years": round(payback, 1),
            "investment_horizon": years
        }
    
    def market_competition(self) -> Dict:
        return {
            "axiom_space": {
                "modules": 4,
                "capacity": 8,
                "price_per_day": 350000,
                "timeline": "2025-2026"
            },
            "sierra_space": {
                "modules": 3,
                "capacity": 6,
                "price_per_day": 400000,
                "timeline": "2026-2027"
            },
            "orbital_reef": {
                "modules": 5,
                "capacity": 10,
                "price_per_day": 300000,
                "timeline": "2027-2028"
            },
            "total_market_capacity_2030": 30  # Guests per year
        }
