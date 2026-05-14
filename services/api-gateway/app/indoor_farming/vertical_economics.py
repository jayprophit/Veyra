"""Vertical Farm Economics"""
from typing import Dict

class VerticalEconomics:
    """Large-scale vertical farming"""
    
    def facility_capex(self, size_sqft: float = 10000) -> Dict:
        # Cost per sq ft for vertical farm buildout
        infrastructure = 150  # Racking, lighting, irrigation
        climate_control = 100  # HVAC, dehumidification
        lighting = 80  # LED grow lights
        automation = 50  # Sensors, controls
        
        cost_per_sqft = infrastructure + climate_control + lighting + automation
        total_capex = cost_per_sqft * size_sqft
        
        return {
            "cost_per_sqft": cost_per_sqft,
            "total_capex": total_capex,
            "size_sqft": size_sqft,
            "breakdown": {
                "infrastructure": infrastructure * size_sqft,
                "climate_control": climate_control * size_sqft,
                "lighting": lighting * size_sqft,
                "automation": automation * size_sqft
            }
        }
    
    def operating_costs(self, annual_production_lbs: float = 500000) -> Dict:
        # Cost per pound of leafy greens
        electricity = 0.50
        labor = 0.30
        nutrients = 0.15
        seeds = 0.10
        packaging = 0.20
        
        cost_per_lb = electricity + labor + nutrients + seeds + packaging
        
        wholesale_price = 3.00
        retail_price = 5.00
        
        return {
            "cost_per_lb": cost_per_lb,
            "wholesale_price": wholesale_price,
            "retail_price": retail_price,
            "wholesale_margin": wholesale_price - cost_per_lb,
            "retail_margin": retail_price - cost_per_lb,
            "annual_production_cost": cost_per_lb * annual_production_lbs,
            "annual_revenue_wholesale": wholesale_price * annual_production_lbs,
            "annual_revenue_retail": retail_price * annual_production_lbs
        }
    
    def vs_traditional(self) -> Dict:
        return {
            "water_use_reduction": 0.95,  # 95% less water
            "land_use_reduction": 0.99,   # 99% less land
            "pesticide_use": 0.00,          # Zero pesticides
            "yield_per_acre_multiplier": 100,  # 100x more per acre
            "energy_cost_premium": 3.0,     # 3x more energy
            "challenges": ["High energy costs", "Limited crop variety", "High capex"]
        }
    
    def major_players(self) -> Dict:
        return {
            "plenty": {"funding": 940e6, "focus": "Leafy greens", "locations": ["CA", "WA"]},
            "bowery_farming": {"funding": 647e6, "focus": "AI-driven", "retail_partners": ["Whole Foods", "Walmart"]},
            "aerofarms": {"funding": 200e6, "status": "Bankruptcy 2023", "lesson": "Unit economics matter"},
            "appharvest": {"funding": 500e6, "status": "Bankruptcy 2023", "lesson": "Greenhouses vs vertical"},
            "infarm": {"funding": 600e6, "focus": "In-store farms", "restructuring": 2023}
        }
