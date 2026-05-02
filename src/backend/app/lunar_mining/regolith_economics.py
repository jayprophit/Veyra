"""Lunar Regolith Economics"""
from typing import Dict

class RegolithEconomics:
    """Mining lunar soil and rock"""
    
    def resource_composition(self) -> Dict:
        return {
            "oxygen": {"percent": 45, "value": "Life support + propellant", "extraction_method": "Reduction"},
            "silicon": {"percent": 21, "value": "Solar panels, electronics", "extraction": "Melt processing"},
            "aluminum": {"percent": 13, "value": "Construction, spacecraft", "extraction": "Electrolysis"},
            "iron": {"percent": 5, "value": "Construction, radiation shield", "extraction": "Magnetic"},
            "titanium": {"percent": 3, "value": "High-performance alloys", "extraction": "Chemical"},
            "water_ice": {"location": "Permanently shadowed regions", "percent": 5, "value": "Life support, propellant"}
        }
    
    def mining_economics(self, mass_tons: int = 1000) -> Dict:
        transport_cost_per_kg = 10000  # From Earth
        lunar_extraction_cost_per_kg = 500
        value_on_moon_per_kg = 8000
        
        return {
            "extraction_cost_m": (mass_tons * 1000 * lunar_extraction_cost_per_kg) / 1e6,
            "earth_transport_equivalent_m": (mass_tons * 1000 * transport_cost_per_kg) / 1e6,
            "value_delivered_m": (mass_tons * 1000 * value_on_moon_per_kg) / 1e6,
            "savings_vs_earth": mass_tons * 1000 * (transport_cost_per_kg - lunar_extraction_cost_per_kg) / 1e6,
            "economic_breakeven_tons": 100  # When lunar ISRU beats Earth launch
        }
    
    def applications(self) -> Dict:
        return {
            "in_situ_construction": {"use": "Landing pads, habitats, roads", "value": "Infrastructure"},
            "propellant_production": {"method": "Water electrolysis", "value_per_ton_lox_lh2_m": 5},
            "radiation_shielding": {"use": "Buried habitats", "mass_needed_tons": 1000},
            "solar_panel_fabrication": {"use": "Silicon extraction", "capacity_kw_per_ton_si": 50}
        }
    
    def mission_architecture(self) -> Dict:
        return {
            "nasa_artemis": {"timeline": "2028-2030", "focus": "Demonstration", "budget_b": 3},
            "china_clep": {"timeline": "2030", "focus": "Research station", "autonomy": "High"},
            "commercial_missions": {"players": ["ispace", "intuitive_machines"], "model": "NASA contracts + data"}
        }
