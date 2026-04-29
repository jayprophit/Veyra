"""Debris Removal Economics - Space cleanup business models"""
from typing import Dict

class DebrisRemovalEconomics:
    """Analyze space debris removal economics"""
    
    def removal_mission_cost(self, debris_mass_kg: float,
                            orbital_altitude: float,
                            capture_method: str) -> Dict:
        """Calculate debris removal mission cost"""
        # Base costs
        launch_cost_per_kg = 5000  # Falcon 9 approx
        capture_costs = {
            "net": 50e6, "harpoons": 40e6, "laser": 100e6,
            "tether": 30e6, "dedicated_sat": 80e6
        }
        
        # Altitude factor (higher = harder)
        altitude_factor = 1 + (orbital_altitude - 400) / 1000
        
        launch_cost = debris_mass_kg * launch_cost_per_kg * altitude_factor
        capture_tech = capture_costs.get(capture_method, 50e6)
        
        total_cost = launch_cost + capture_tech
        
        return {
            "debris_mass_kg": debris_mass_kg,
            "launch_cost": round(launch_cost, 0),
            "capture_tech_cost": capture_tech,
            "total_mission_cost": round(total_cost, 0),
            "cost_per_kg": round(total_cost / debris_mass_kg, 0) if debris_mass_kg > 0 else 0
        }
    
    def insurance_premium_impact(self, debris_density_increase: float,
                               collision_probability_base: float,
                               satellite_value_insured: float) -> Dict:
        """Calculate debris impact on insurance premiums"""
        new_probability = collision_probability_base * (1 + debris_density_increase)
        premium_increase = (new_probability / collision_probability_base - 1) * 100
        
        additional_premium = satellite_value_insured * (premium_increase / 100) * 0.02
        
        return {
            "collision_probability": round(new_probability, 4),
            "premium_increase_pct": round(premium_increase, 1),
            "additional_annual_premium": round(additional_premium, 0),
            "debris_mitigation_value": round(additional_premium * 5, 0)  # 5-year NPV
        }
