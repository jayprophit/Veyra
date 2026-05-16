"""Warehouse Robotics Economics"""
from typing import Dict

class WarehouseRobots:
    """Analyze warehouse automation investments"""
    
    def __init__(self, robot_type: str = "amr"):
        self.robot_type = robot_type  # amr, agv, picking_arm
    
    def robot_costs(self, units: int = 10) -> Dict:
        costs = {
            "amr": {"unit_cost": 40000, "software_annual": 5000, "maintenance_annual": 3000},
            "agv": {"unit_cost": 60000, "software_annual": 8000, "maintenance_annual": 5000},
            "picking_arm": {"unit_cost": 80000, "software_annual": 10000, "maintenance_annual": 6000}
        }
        
        c = costs.get(self.robot_type, costs["amr"])
        hardware = units * c["unit_cost"]
        annual = units * (c["software_annual"] + c["maintenance_annual"])
        
        return {
            "hardware_cost": hardware,
            "annual_operating": annual,
            "unit_cost": c["unit_cost"],
            "units": units,
            "total_first_year": hardware + annual
        }
    
    def labor_savings(self, workers_replaced: int = 5) -> Dict:
        annual_wage = 45000
        benefits = 0.30
        total_cost_per_worker = annual_wage * (1 + benefits)
        
        savings = workers_replaced * total_cost_per_worker
        
        return {
            "workers_replaced": workers_replaced,
            "annual_savings": savings,
            "payback_months": "See robot_costs calculation"
        }
    
    def productivity_gains(self) -> Dict:
        return {
            "picks_per_hour_human": 100,
            "picks_per_hour_robot": 300,
            "accuracy_human": 0.97,
            "accuracy_robot": 0.999,
            "uptime_human_hours": 8,
            "uptime_robot_hours": 22,
            "productivity_multiple": 8  # Robot is 8x more productive
        }
