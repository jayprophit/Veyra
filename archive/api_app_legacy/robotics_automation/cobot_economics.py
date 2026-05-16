"""Cobot Economics - Collaborative robot ROI"""
from typing import Dict

class CobotEconomics:
    """Analyze collaborative robot investments"""
    
    def payback_analysis(self, cobot_cost: float,
                        labor_replaced: float,
                        labor_cost_hourly: float,
                        hours_per_day: int,
                        utilization: float) -> Dict:
        """Calculate cobot payback period"""
        annual_hours = hours_per_day * 250 * utilization  # 250 working days
        annual_savings = labor_replaced * labor_cost_hourly * annual_hours
        
        # Maintenance and programming costs
        annual_costs = cobot_cost * 0.05  # 5% maintenance
        net_savings = annual_savings - annual_costs
        
        payback_years = cobot_cost / net_savings if net_savings > 0 else 999
        
        return {
            "cobot_cost": cobot_cost,
            "annual_labor_savings": round(annual_savings, 0),
            "annual_operating_costs": round(annual_costs, 0),
            "net_annual_savings": round(net_savings, 0),
            "payback_years": round(payback_years, 1),
            "roi_5year": round((net_savings * 5 - cobot_cost) / cobot_cost * 100, 1),
            "viable": payback_years < 2
        }
    
    def task_automation_score(self, repetitiveness: float,  # 0-10
                             precision_required: float,  # 0-10
                             hazard_level: float,  # 0-10
                             batch_size: int) -> Dict:
        """Score task suitability for cobot automation"""
        score = (repetitiveness * 0.3 + 
                precision_required * 0.2 + 
                hazard_level * 0.3 +
                min(batch_size / 100, 10) * 0.2)
        
        return {
            "automation_score": round(score, 1),
            "suitability": "excellent" if score > 8 else "good" if score > 6 else "fair" if score > 4 else "poor",
            "priority": "high" if score > 7 else "medium" if score > 5 else "low",
            "recommended_cobot_payload": "5-10kg" if precision_required > 7 else "10-20kg"
        }
