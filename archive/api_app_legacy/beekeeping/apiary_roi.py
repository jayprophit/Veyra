"""Apiary ROI - Beekeeping business economics"""
from typing import Dict

class ApiaryROI:
    """Analyze beekeeping business returns"""
    
    def hive_economics(self, hive_count: int,
                      honey_per_hive: float,
                      honey_price_per_lb: float,
                      queen_replacement_cost: float) -> Dict:
        """Calculate per-hive economics"""
        total_honey = hive_count * honey_per_hive
        honey_revenue = total_honey * honey_price_per_lb
        
        # Annual costs
        queen_cost = hive_count * queen_replacement_cost * 0.3  # 30% replace annually
        feed_cost = hive_count * 50  # $50/hive feed
        equipment_depreciation = hive_count * 30
        
        total_costs = queen_cost + feed_cost + equipment_depreciation
        profit = honey_revenue - total_costs
        
        return {
            "hives": hive_count,
            "honey_production_lbs": round(total_honey, 0),
            "honey_revenue": round(honey_revenue, 0),
            "annual_costs": round(total_costs, 0),
            "profit": round(profit, 0),
            "profit_per_hive": round(profit / hive_count, 0),
            "roi_percent": round(profit / total_costs * 100, 1) if total_costs > 0 else 0
        }
    
    def pollination_contract_value(self, hives_contracted: int,
                                  price_per_hive: float,
                                  transport_cost: float,
                                  duration_weeks: int) -> Dict:
        """Value pollination service contracts"""
        revenue = hives_contracted * price_per_hive
        transport_total = transport_cost * 2  # Round trip
        opportunity_cost = hives_contracted * 40 * duration_weeks  # Lost honey production
        
        net_revenue = revenue - transport_total - opportunity_cost
        
        return {
            "hives": hives_contracted,
            "contract_revenue": round(revenue, 0),
            "transport_cost": round(transport_total, 0),
            "opportunity_cost": round(opportunity_cost, 0),
            "net_revenue": round(net_revenue, 0),
            "vs_honey_production": "better" if net_revenue > opportunity_cost * 1.5 else "comparable"
        }
