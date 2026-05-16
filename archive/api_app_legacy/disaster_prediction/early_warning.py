"""Early Warning System Economics"""
from typing import Dict

class EarlyWarning:
    """Disaster prediction and alert systems"""
    
    def system_types(self) -> Dict:
        return {
            "earthquake": {
                "method": "Seismic sensors + ML",
                "warning_time_sec": 60,
                "cost_per_station": 10000,
                "coverage_needed": "Dense networks",
                "systems": ["ShakeAlert", "Japan EEW"]
            },
            "tsunami": {
                "method": "Ocean buoys + seismic",
                "warning_time_min": 30,
                "cost_per_buoy": 250000,
                "global_coverage_pct": 60
            },
            "wildfire": {
                "method": "Satellites + cameras + AI",
                "detection_time": "Minutes",
                "cost_per_camera": 5000,
                "coverage_radius_km": 50
            },
            "flood": {
                "method": "River gauges + weather models",
                "warning_time_hours": 12,
                "existing_gauges": 10000,
                "improvement_needed": "Integration"
            }
        }
    
    def value_of_information(self) -> Dict:
        return {
            "life_saved_per_warning": 1000,  # Per major event
            "economic_value_per_warning_m": 500,
            "cost_benefit_ratio": 10,
            "insurance_discount_pct": 5
        }
    
    def market_structure(self) -> Dict:
        return {
            "government_funded": {"share": 0.70, "budgets_annual_b": 2},
            "private_services": {"share": 0.30, "growth": 0.20},
            "insurance_subsidized": {"emerging": True, "models": "Premium discounts"}
        }
