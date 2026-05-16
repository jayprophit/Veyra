"""Water Harvesting Applications"""
from typing import Dict

class WaterHarvesting:
    """Atmospheric water use cases"""
    
    def use_cases(self) -> Dict:
        return {
            "residential_off_grid": {
                "target_market": "Rural homes, islands",
                "household_need_liters": 200,
                "system_cost": 5000,
                "alternative": "Trucked water @ $100/month"
            },
            "disaster_relief": {
                "deployment_time_hours": 2,
                "daily_output_liters": 5000,
                "persons_served": 1000,
                "ngo_interest": "High"
            },
            "military_field": {
                "value_prop": "Eliminate water logistics",
                "current_cost_per_liter_delivered": 15,
                "awg_cost_per_liter": 0.50,
                "payback_missions": 3
            },
            "agriculture_greenhouse": {
                "application": "Humidity control + water",
                "integration": "HVAC synergy",
                "roi_percent": 25
            }
        }
    
    def efficiency_factors(self) -> Dict:
        return {
            "humidity": {"optimal_pct": 80, "minimum_pct": 30, "impact": "Linear"},
            "temperature": {"optimal_c": 30, "cooler_better": True},
            "energy_source": {"grid": "$0.10/kWh", "solar": "Variable", "waste_heat": "Ideal"}
        }
    
    def water_quality(self) -> Dict:
        return {
            "purity": {"comparable_to": "Distilled", "mineralization_needed": True},
            "contamination_risk": {"air_pollutants": "Filtered", "bacteria": "UV treated"},
            "standards": {"potable": True, "bottled_water_comparable": True}
        }
