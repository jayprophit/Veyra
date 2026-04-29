"""Asteroid Valuation - Near-Earth object resource assessment"""
from typing import Dict

class AsteroidValuation:
    """Valuate asteroids for mining potential"""
    
    def __init__(self, asteroid_type: str, diameter_m: float, distance_au: float):
        self.type = asteroid_type  # C-type, S-type, M-type
        self.diameter = diameter_m
        self.distance = distance_au  # Astronomical units from Earth
    
    def resource_estimates(self) -> Dict:
        densities = {
            "C-type": 1.5,  # g/cm3
            "S-type": 2.7,
            "M-type": 5.0
        }
        density = densities.get(self.type, 2.0)
        
        volume = (4/3) * 3.14159 * ((self.diameter/2) ** 3)  # m3
        mass_kg = volume * density * 1000
        
        # Composition estimates
        if self.type == "M-type":
            iron_pct = 90
            nickel_pct = 8
            platinum_ppm = 50
            water_pct = 0
        elif self.type == "S-type":
            iron_pct = 20
            nickel_pct = 2
            platinum_ppm = 5
            water_pct = 5
        else:  # C-type
            iron_pct = 10
            nickel_pct = 1
            platinum_ppm = 1
            water_pct = 20
        
        return {
            "total_mass_tons": round(mass_kg / 1000, 0),
            "iron_tons": round(mass_kg / 1000 * iron_pct / 100, 0),
            "nickel_tons": round(mass_kg / 1000 * nickel_ppm / 100, 0),
            "platinum_kg": round(mass_kg * platinum_ppm / 1e6, 0),
            "water_tons": round(mass_kg / 1000 * water_pct / 100, 0)
        }
    
    def value_assessment(self, resources: Dict, launch_cost_per_kg: float = 2000) -> Dict:
        # Terrestrial prices
        iron_price = 100  # $/ton
        nickel_price = 20000  # $/ton
        platinum_price = 50000  # $/kg
        water_price_space = launch_cost_per_kg * 1000  # $/ton in space
        
        iron_value = resources["iron_tons"] * iron_price
        nickel_value = resources["nickel_tons"] * nickel_price
        platinum_value = resources["platinum_kg"] * platinum_price
        water_value = resources["water_tons"] * water_price_space
        
        total_value = iron_value + nickel_value + platinum_value + water_value
        
        # Accessible portion (assuming 10% extraction efficiency)
        accessible_value = total_value * 0.10
        
        return {
            "iron_value": round(iron_value, 0),
            "nickel_value": round(nickel_value, 0),
            "platinum_value": round(platinum_value, 0),
            "water_value_space": round(water_value, 0),
            "total_insitu_value": round(total_value, 0),
            "accessible_value_10pct": round(accessible_value, 0),
            "most_valuable": max([("platinum", platinum_value), ("water", water_value), ("nickel", nickel_value)], key=lambda x: x[1])[0]
        }
    
    def mission_economics(self, mission_cost_billions: float = 2.5) -> Dict:
        resources = self.resource_estimates()
        values = self.value_assessment(resources)
        
        roi = (values["accessible_value_10pct"] / (mission_cost_billions * 1e9) - 1) * 100
        payback_tons_platinum = (mission_cost_billions * 1e9) / 50000 / 1000  # kg platinum needed
        
        return {
            "mission_cost": mission_cost_billions * 1e9,
            "potential_return": values["accessible_value_10pct"],
            "theoretical_roi_pct": round(roi, 1),
            "platinum_for_payback_kg": round(payback_tons_platinum, 0),
            "mission_viable": roi > 0
        }
