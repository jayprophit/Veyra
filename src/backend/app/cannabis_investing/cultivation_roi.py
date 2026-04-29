"""Cultivation ROI - Cannabis growing economics"""
from typing import Dict

class CultivationROI:
    """Analyze cannabis cultivation returns"""
    
    def indoor_cultivation_economics(self, square_feet: int,
                                   yield_per_sqft: float,
                                   wholesale_price_per_lb: float,
                                   cost_per_sqft: float) -> Dict:
        """Calculate indoor grow economics"""
        annual_yield = square_feet * yield_per_sqft
        revenue = annual_yield * wholesale_price_per_lb
        costs = square_feet * cost_per_sqft
        
        profit = revenue - costs
        margin = (profit / revenue) * 100 if revenue > 0 else 0
        
        return {
            "facility_sqft": square_feet,
            "annual_yield_lbs": round(annual_yield, 0),
            "revenue": round(revenue, 0),
            "costs": round(costs, 0),
            "profit": round(profit, 0),
            "margin_pct": round(margin, 1),
            "revenue_per_sqft": round(revenue / square_feet, 0)
        }
    
    def outdoor_vs_indoor(self, outdoor_yield: float,
                         outdoor_cost: float,
                         indoor_yield: float,
                         indoor_cost: float,
                         price_premium_indoor: float) -> Dict:
        """Compare outdoor vs indoor cultivation"""
        outdoor_profit = outdoor_yield - outdoor_cost
        indoor_profit = indoor_yield * price_premium_indoor - indoor_cost
        
        return {
            "outdoor_profit_per_plant": round(outdoor_profit, 0),
            "indoor_profit_per_plant": round(indoor_profit, 0),
            "superior_method": "indoor" if indoor_profit > outdoor_profit else "outdoor",
            "profit_differential": round(abs(indoor_profit - outdoor_profit), 0),
            "scale_consideration": "outdoor_for_volume" if outdoor_yield > indoor_yield * 2 else "indoor_for_quality"
        }
