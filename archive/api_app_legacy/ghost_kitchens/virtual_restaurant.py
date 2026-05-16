"""Virtual Restaurant Economics"""
from typing import Dict

class VirtualRestaurant:
    """Ghost kitchen and virtual brand economics"""
    
    def __init__(self, concept_type: str = "delivery_only"):
        self.concept = concept_type
    
    def kitchen_capex(self, size_sqft: float = 2000) -> Dict:
        equipment_per_sqft = 300
        buildout_per_sqft = 150
        tech_systems = 50000
        
        total = (size_sqft * (equipment_per_sqft + buildout_per_sqft)) + tech_systems
        
        return {
            "total_capex": total,
            "per_sqft": equipment_per_sqft + buildout_per_sqft,
            "size_sqft": size_sqft,
            "vs_traditional_restaurant": 0.30  # 30% of traditional cost
        }
    
    def unit_economics(self, orders_per_day: int = 200) -> Dict:
        avg_order_value = 25
        commission_rate = 0.30  # Delivery app
        food_cost_rate = 0.25
        labor_per_order = 4
        packaging = 1.50
        
        revenue_per_order = avg_order_value * (1 - commission_rate)
        cost_per_order = (avg_order_value * food_cost_rate) + labor_per_order + packaging
        contribution_margin = revenue_per_order - cost_per_order
        
        monthly_orders = orders_per_day * 30
        monthly_contribution = monthly_orders * contribution_margin
        
        # Fixed costs
        rent = 8000
        utilities = 2000
        insurance = 1000
        total_fixed = rent + utilities + insurance
        
        return {
            "contribution_margin_per_order": contribution_margin,
            "contribution_margin_pct": round(contribution_margin / revenue_per_order * 100, 1),
            "monthly_contribution": monthly_contribution,
            "monthly_fixed_costs": total_fixed,
            "monthly_profit": monthly_contribution - total_fixed,
            "break_even_orders_per_day": round((total_fixed / 30) / contribution_margin, 0)
        }
    
    def multi_brand_strategy(self, brand_count: int = 5) -> Dict:
        # Multiple virtual brands from one kitchen
        kitchen_cost = self.kitchen_capex()["total_capex"]
        
        per_brand_capex = kitchen_cost / brand_count
        
        return {
            "brands_per_kitchen": brand_count,
            "capex_per_brand": per_brand_capex,
            "advantage": "Diversified cuisine types, shared infrastructure",
            "examples": ["Chuck E. Cheese virtual brands", "Wendy's Reef Kitchens"]
        }
