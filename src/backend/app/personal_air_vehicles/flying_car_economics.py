"""Flying Car Economics"""
from typing import Dict

class FlyingCarEconomics:
    """Personal aerial vehicle market"""
    
    def vehicle_categories(self) -> Dict:
        return {
            "light_sport": {
                "price_range": (150000, 400000),
                "examples": ["ICON A5", "Terrafugia Transition"],
                "license_required": "Sport pilot",
                "market_size_annual": 500e6
            },
            "flying_car_concepts": {
                "klein_vision": {"status": "Certified", "price": 500000, "drive_fly": True},
                "aska": {"status": "Prototype", "price": 789000, "vtol": True},
                "pal_v": {"status": "Pre-order", "price": 599000, "gyrocopter": True}
            },
            "premium_evtol": {
                "lilium_jet": {"price_estimate": 7000000, "passengers": 6, "range_km": 250},
                "advantage": "Door-to-door travel"
            }
        }
    
    def operating_costs(self) -> Dict:
        return {
            "fuel_per_hour": 50,
            "maintenance_per_hour": 100,
            "insurance_annual": 20000,
            "storage_hangar_monthly": 500,
            "total_per_hour": 200
        }
    
    def regulatory_barriers(self) -> Dict:
        return {
            "certification": {"faa_timeline": "Years", "cost": "10M+"},
            "airspace_integration": {"uts_future": "2028", "autonomous_approval": "TBD"},
            "infrastructure": {"vertiports_needed": True, "cost_per_location": 5e6}
        }
    
    def market_outlook(self) -> Dict:
        return {
            "recreational_pilots_us": 200000,
            "flying_car_tam_2040": 50e9,
            "barriers": ["Cost", "Regulation", "Safety", "Training"],
            "drivers": ["Time savings", "Lifestyle", "Technology maturation"]
        }
