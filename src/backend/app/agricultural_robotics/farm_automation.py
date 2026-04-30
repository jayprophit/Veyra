"""Farm Automation Economics"""
from typing import Dict

class FarmAutomation:
    """Autonomous tractors and farming equipment"""
    
    def __init__(self, farm_size_acres: float = 1000):
        self.farm_size = farm_size_acres
    
    def equipment_costs(self) -> Dict:
        equipment = {
            "autonomous_tractor": {"cost": 500000, "labor_saved": 1, "fuel_efficiency": 1.15},
            "robotic_harvester": {"cost": 800000, "labor_saved": 2, "efficiency_gain": 1.20},
            "drone_sprayer": {"cost": 50000, "chemical_savings": 0.30, "coverage_acres_per_day": 200},
            "soil_robot": {"cost": 100000, "data_value": 50, "coverage_acres_per_day": 100}
        }
        
        # Calculate for farm size
        tractors_needed = max(1, self.farm_size / 500)
        drones_needed = max(1, self.farm_size / 400)
        
        total_cost = (equipment["autonomous_tractor"]["cost"] * tractors_needed +
                     equipment["drone_sprayer"]["cost"] * drones_needed +
                     equipment["soil_robot"]["cost"])
        
        return {
            "total_investment": total_cost,
            "equipment_breakdown": {
                "tractors": equipment["autonomous_tractor"]["cost"] * tractors_needed,
                "drones": equipment["drone_sprayer"]["cost"] * drones_needed,
                "soil_robots": equipment["soil_robot"]["cost"]
            },
            "per_acre_cost": total_cost / self.farm_size
        }
    
    def roi_calculation(self) -> Dict:
        investment = self.equipment_costs()["total_investment"]
        
        # Annual savings
        labor_savings = 75000  # 1.5 FTE at $50K each
        fuel_savings = 15000   # 15% efficiency gain
        chemical_savings = 20000  # Precision application
        yield_increase = 30000   # 3% yield improvement
        
        total_annual_benefit = labor_savings + fuel_savings + chemical_savings + yield_increase
        
        return {
            "total_investment": investment,
            "annual_savings": total_annual_benefit,
            "payback_years": round(investment / total_annual_benefit, 1),
            "five_year_roi": round((total_annual_benefit * 5 - investment) / investment * 100, 0)
        }
    
    def technology_providers(self) -> Dict:
        return {
            "john_deere": {"market_share": 0.35, "autonomy_level": "L3", "pricing_premium": 0.30},
            "case_ih": {"market_share": 0.25, "autonomy_level": "L2", "pricing_premium": 0.20},
            "agco": {"market_share": 0.20, "autonomy_level": "L2", "pricing_premium": 0.15},
            "startups": {
                "small_robot_company": {"focus": "Lightweight robots", "funding": 20e6},
                "root_ai": {"focus": "Harvesting", "acquired_by": "AppHarvest"},
                "farmwise": {"focus": "Weeding", "funding": 45e6}
            }
        }
