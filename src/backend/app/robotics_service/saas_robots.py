"""Robotics as a Service Economics"""
from typing import Dict

class SaaSRobots:
    """RaaS business model analysis"""
    
    def business_model(self) -> Dict:
        return {
            "subscription_types": {
                "basic": {"monthly": 2000, "hours_included": 160, "overage": 15},
                "professional": {"monthly": 5000, "hours_included": 400, "overage": 14},
                "enterprise": {"monthly": 15000, "hours_included": 1200, "overage": 13}
            },
            "value_prop": "No capex, maintenance included, upgrades"
        }
    
    def unit_economics(self) -> Dict:
        robot_cost = 100000
        lifespan_months = 48
        maintenance_monthly = 500
        utilization_target = 0.80
        
        monthly_depreciation = robot_cost / lifespan_months
        monthly_costs = monthly_depreciation + maintenance_monthly
        
        # At 80% utilization on professional plan
        revenue_monthly = 5000 * 0.80
        
        return {
            "monthly_costs": monthly_costs,
            "monthly_revenue": revenue_monthly,
            "gross_margin": revenue_monthly - monthly_costs,
            "gross_margin_pct": round((revenue_monthly - monthly_costs) / revenue_monthly * 100, 1),
            "payback_months": round(robot_cost / (revenue_monthly - monthly_costs), 0)
        }
    
    def market_opportunity(self) -> Dict:
        return {
            "raas_market_2024": 2.5e9,
            "raas_market_2030": 15e9,
            "penetration_rate_current": 0.15,
            "target_verticals": ["Logistics", "Manufacturing", "Healthcare", "Agriculture"]
        }
