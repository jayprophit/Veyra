"""Precision Fermentation Economics"""
from typing import Dict

class PrecisionFermentation:
    """Analyze microbial production of proteins, fats, and chemicals"""
    
    def __init__(self, product_type: str = "protein"):
        self.product = product_type  # protein, fat, chemical
    
    def facility_cost(self, capacity_kg_per_year: float = 1000000) -> Dict:
        # Cost per kg of annual capacity
        cost_per_kg_capacity = {
            "protein": 200,  # $/kg/year
            "fat": 150,
            "chemical": 300
        }
        
        cost_per_kg = cost_per_kg_capacity.get(self.product, 200)
        capex = capacity_kg_per_year * cost_per_kg
        
        return {
            "total_capex": round(capex, 0),
            "cost_per_kg_capacity": cost_per_kg,
            "annual_capacity_kg": capacity_kg_per_year,
            "fermenter_volume_liters": round(capacity_kg_per_year / 100),  # 100 batches/year, 1kg/L
            "includes": ["Fermenters", "DSP equipment", "Utilities", "QC lab"]
        }
    
    def unit_economics(self, titer_g_per_l: float = 10) -> Dict:
        # Production cost breakdown per kg
        substrate = 15  # Sugar feedstock
        utilities = 8  # Steam, electricity, cooling
        labor = 12
        consumables = 10
        maintenance = 5
        depreciation = 20  # CAPEX recovery
        
        total_cost = substrate + utilities + labor + consumables + maintenance + depreciation
        
        # Pricing
        if self.product == "protein":
            market_price = 50
        elif self.product == "fat":
            market_price = 30
        else:
            market_price = 80
        
        margin = market_price - total_cost
        
        return {
            "production_cost_per_kg": round(total_cost, 2),
            "market_price_per_kg": market_price,
            "gross_margin_per_kg": round(margin, 2),
            "gross_margin_pct": round(margin / market_price * 100, 1),
            "titer_g_per_l": titer_g_per_l,
            "cost_drivers": ["substrate", "utilities", "labor", "depreciation"]
        }
    
    def production_economics(self, capacity_kg: float = 1000000) -> Dict:
        facility = self.facility_cost(capacity_kg)
        unit = self.unit_economics()
        
        annual_revenue = capacity_kg * unit["market_price_per_kg"]
        annual_cogs = capacity_kg * unit["production_cost_per_kg"]
        
        # 8000 hours/year operation
        ebitda = annual_revenue - annual_cogs
        
        return {
            "annual_revenue_millions": round(annual_revenue / 1e6, 1),
            "annual_cogs_millions": round(annual_cogs / 1e6, 1),
            "gross_profit_millions": round(ebitda / 1e6, 1),
            "ebitda_margin_pct": round(ebitda / annual_revenue * 100, 1),
            "payback_years": round(facility["total_capex"] / ebitda, 1) if ebitda > 0 else float('inf')
        }
    
    def vs_conventional(self, conventional_cost_per_kg: float = 3) -> Dict:
        pf_cost = self.unit_economics()["production_cost_per_kg"]
        
        premium = pf_cost - conventional_cost_per_kg
        
        return {
            "precision_fermentation_cost": pf_cost,
            "conventional_cost": conventional_cost_per_kg,
            "premium_per_kg": round(premium, 2),
            "premium_pct": round((pf_cost / conventional_cost_per_kg - 1) * 100, 0),
            "justification": "Functional equivalence, sustainability, supply security",
            "timeline_to_cost_parity": "5-7 years with scale"
        }
