"""Helium-3 Mining Economics"""
from typing import Dict

class Helium3Mining:
    """Fusion fuel from the Moon"""
    
    def helium3_properties(self) -> Dict:
        return {
            "concentration_ppb": 10,  # Parts per billion in regolith
            "extraction_energy": "Heat regolith to 600C",
            "fusion_value": "Aneutronic, clean",
            "energy_density_vs_coal": 1000000
        }
    
    def economics(self) -> Dict:
        return {
            "regolith_to_process_tons_per_kg_he3": 100000,
            "mining_rate_tons_per_year": 1000000,
            "he3_produced_kg_per_year": 10,
            "value_per_kg_he3_m": 200,  # At current energy prices
            "production_cost_per_kg_m": 500,  # Currently uneconomical
            "breakeven_energy_price_factor": 25  # Energy must cost 25x more
        }
    
    def fusion_context(self) -> Dict:
        return {
            "terrestrial_fusion_timeline": "2030-2040 commercial",
            "d_t_fuel_preferred": True,  # Deuterium-tritium easier
            "d_he3_advantages": ["No neutrons", "Direct conversion", "Clean"],
            "he3_supply_constraint": "D-T fusion doesn't need it",
            "market_timeline": "If ever, 2050+"
        }
    
    def mining_challenges(self) -> Dict:
        return {
            "scale": {"regolith_volume": "Enormous", "equipment_mass_from_earth": "Limited"},
            "energy": {"solar_available": "14 days on, 14 days off", "nuclear_backup": "Required"},
            "transport": {"he3_to_earth_cost_per_kg": "High", "insitu_use_preferred": True}
        }
