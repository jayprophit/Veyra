"""Personal eVTOL Market"""
from typing import Dict

class PersonalEVTOL:
    """Consumer-grade electric vertical takeoff"""
    
    def emerging_products(self) -> Dict:
        return {
            "jetson_one": {
                "type": "Ultralight octocopter",
                "price": 98000,
                "flight_time_min": 20,
                "max_speed_kmh": 102,
                "license": "None (ultralight)",
                "availability": "Limited production"
            },
            "ryse_recon": {
                "type": "Ultralight multicopter",
                "price": 150000,
                "flight_time_min": 25,
                "target": "Rural/Ag use",
                "license": "Part 107 drone"
            },
            "hover_survey": {
                "market_sentiment": "Early adopters",
                "safety_concerns": "High",
                "price_barrier": "Significant"
            }
        }
    
    def use_cases(self) -> Dict:
        return {
            "rural_access": {
                "value_prop": "Skip 2-hour drive",
                "flight_time": "15 minutes",
                "market": "Ranch owners, large properties"
            },
            "recreation": {
                "value_prop": "Aerial thrill",
                "comparison": "Expensive hobby vs helicopter",
                "market_size": 1e9
            },
            "emergency_access": {
                "value_prop": "Medical evacuation from remote",
                "market": "Search and rescue, medical"
            }
        }
    
    def technology_gaps(self) -> Dict:
        return {
            "battery_energy_density": {"current_wh_kg": 250, "needed": 400, "timeline": "2030"},
            "noise_levels": {"current_db": 85, "target": 65, "community_acceptance": "Critical"},
            "reliability": {"target_mtbf_hours": 1000, "current": "Unproven"}
        }
