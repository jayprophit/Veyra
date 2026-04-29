"""Warehouse Automation - Logistics robotics economics"""
from typing import Dict

class WarehouseAutomation:
    """Analyze warehouse automation ROI"""
    
    def amr_payback(self, robot_cost: float,
                   labor_hours_saved_daily: float,
                   labor_rate: float,
                   maintenance_pct: float) -> Dict:
        """Calculate AMR (Autonomous Mobile Robot) payback"""
        annual_hours_saved = labor_hours_saved_daily * 250  # work days
        annual_savings = annual_hours_saved * labor_rate
        maintenance_cost = robot_cost * (maintenance_pct / 100)
        net_savings = annual_savings - maintenance_cost
        
        payback = robot_cost / net_savings if net_savings > 0 else 999
        
        return {
            "robot_cost": robot_cost,
            "annual_savings": round(annual_savings, 0),
            "maintenance_annual": round(maintenance_cost, 0),
            "payback_years": round(payback, 1),
            "roi_5year": round((net_savings * 5 - robot_cost) / robot_cost * 100, 0),
            "automation_justified": payback < 3
        }
    
    def pick_and_place_roi(self, picks_per_hour_human: int,
                          picks_per_hour_robot: int,
                          robot_cost: float,
                          hourly_labor_cost: float) -> Dict:
        """Calculate pick-and-place robot ROI"""
        productivity_gain = picks_per_hour_robot - picks_per_hour_human
        efficiency_ratio = picks_per_hour_robot / picks_per_hour_human if picks_per_hour_human > 0 else 1
        
        # Value of increased throughput
        value_multiplier = efficiency_ratio * 0.7  # 70% of theoretical
        effective_labor_value = hourly_labor_cost * value_multiplier
        
        annual_value = effective_labor_value * 2000  # 2000 hours/year
        payback = robot_cost / annual_value if annual_value > 0 else 999
        
        return {
            "human_rate": picks_per_hour_human,
            "robot_rate": picks_per_hour_robot,
            "efficiency_ratio": round(efficiency_ratio, 1),
            "annual_value": round(annual_value, 0),
            "payback_years": round(payback, 1),
            "justified": efficiency_ratio > 2 and payback < 4
        }
