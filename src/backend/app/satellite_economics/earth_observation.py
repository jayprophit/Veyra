"""Earth Observation Economics"""
from typing import Dict

class EarthObservation:
    """Satellite imagery and data analytics"""
    
    def __init__(self, resolution: str = "high"):
        self.resolution = resolution  # low, medium, high, very_high
    
    def market_segments(self) -> Dict:
        return {
            "agriculture": {"size_billions": 1.5, "use_case": "Crop monitoring", "growth": 0.20},
            "defense": {"size_billions": 8.0, "use_case": "Intelligence", "growth": 0.08},
            "environment": {"size_billions": 0.5, "use_case": "Climate monitoring", "growth": 0.25},
            "urban_planning": {"size_billions": 0.8, "use_case": "Development tracking", "growth": 0.15},
            "finance": {"size_billions": 0.3, "use_case": "Economic indicators", "growth": 0.30},
            "insurance": {"size_billions": 0.4, "use_case": "Risk assessment", "growth": 0.22}
        }
    
    def satellite_economics(self, constellation_size: int = 100) -> Dict:
        # Small sat costs
        satellite_cost = 2e6  # $2M per satellite
        launch_cost = 0.5e6   # $500K per satellite (rideshare)
        
        constellation_capex = constellation_size * (satellite_cost + launch_cost)
        
        # Revenue potential
        images_per_day_per_sat = 100
        price_per_image = 500
        annual_revenue_per_sat = images_per_day_per_sat * 365 * price_per_image
        
        total_annual_revenue = annual_revenue_per_sat * constellation_size
        
        return {
            "constellation_capex_millions": constellation_capex / 1e6,
            "annual_revenue_potential_millions": total_annual_revenue / 1e6,
            "revenue_per_satellite_millions": annual_revenue_per_sat / 1e6,
            "payback_years": round(constellation_capex / total_annual_revenue, 1),
            "constellation_lifetime_years": 5
        }
    
    def key_players(self) -> Dict:
        return {
            "planet_labs": {"constellation": 200, "revenue_millions": 100, "focus": "Daily coverage"},
            "maxar": {"constellation": 4, "revenue_millions": 1800, "focus": "High resolution"},
            "spice": {"constellation": 100, "revenue_millions": 50, "focus": "Thermal imaging"},
            "blacksky": {"constellation": 60, "revenue_millions": 40, "focus": "Rapid revisit"},
            "capella": {"constellation": 36, "revenue_millions": 30, "focus": "SAR radar"}
        }
