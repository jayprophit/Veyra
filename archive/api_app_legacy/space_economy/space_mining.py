"""Space Mining - Asteroid and lunar mining economics"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Asteroid:
    name: str
    type: str
    distance_au: float
    estimated_mass_tons: float
    platinum_pct: float
    water_pct: float
    iron_pct: float

class SpaceMining:
    """Analyze space mining economics"""
    
    COMMODITY_PRICES = {
        "platinum": 30000,  # per kg
        "water": 500,       # per kg (in space)
        "iron": 100,        # per kg (in space)
        "gold": 60000       # per kg
    }
    
    def __init__(self):
        self.asteroids: List[Asteroid] = []
    
    def add_asteroid(self, asteroid: Asteroid):
        self.asteroids.append(asteroid)
    
    def valuation(self, asteroid: Asteroid) -> Dict:
        """Value an asteroid's resources"""
        mass_kg = asteroid.estimated_mass_tons * 1000
        
        platinum_value = mass_kg * (asteroid.platinum_pct / 100) * self.COMMODITY_PRICES["platinum"]
        water_value = mass_kg * (asteroid.water_pct / 100) * self.COMMODITY_PRICES["water"]
        iron_value = mass_kg * (asteroid.iron_pct / 100) * self.COMMODITY_PRICES["iron"]
        
        total_value = platinum_value + water_value + iron_value
        
        # Mission cost estimate
        mission_cost = asteroid.distance_au * 500e6 + 2e9
        
        return {
            "asteroid": asteroid.name,
            "total_value": total_value,
            "breakdown": {
                "platinum": platinum_value,
                "water": water_value,
                "iron": iron_value
            },
            "mission_cost_estimate": mission_cost,
            "roi": round((total_value - mission_cost) / mission_cost * 100, 1),
            "viable": total_value > mission_cost * 2
        }
    
    def lunar_mining_economics(self, annual_tons: int) -> Dict:
        """Lunar mining economics"""
        # Helium-3 and water ice
        transport_cost_per_kg = 50000  # From Moon to LEO
        helium3_price_per_kg = 3e6     # Nuclear fusion fuel
        
        annual_revenue = annual_tons * 1000 * 0.01 * helium3_price_per_kg
        capex = 10e9
        opex = annual_tons * 1000 * transport_cost_per_kg * 0.5
        
        return {
            "annual_revenue": annual_revenue,
            "capex": capex,
            "annual_opex": opex,
            "payback_years": round(capex / (annual_revenue - opex), 1),
            "primary_product": "Helium-3"
        }
