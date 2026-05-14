"""Mine Economics - Mining project valuation"""
from typing import Dict

class MineEconomics:
    """Analyze mining project economics"""
    
    def all_in_sustaining_cost(self, production_oz: float,
                              operating_costs: float,
                              sustaining_capex: float,
                              g_and_a: float) -> Dict:
        """Calculate AISC for gold mining"""
        total_costs = operating_costs + sustaining_capex + g_and_a
        aisc_per_oz = total_costs / production_oz if production_oz > 0 else 0
        
        return {
            "production_oz": production_oz,
            "operating_costs": operating_costs,
            "sustaining_capex": sustaining_capex,
            "g_and_a": g_and_a,
            "aisc_per_oz": round(aisc_per_oz, 2),
            "margin_at_1800": round(1800 - aisc_per_oz, 2),
            "margin_at_2000": round(2000 - aisc_per_oz, 2),
            "tier": "low_cost" if aisc_per_oz < 1000 else "mid_cost" if aisc_per_oz < 1300 else "high_cost"
        }
    
    def npv_mining_project(self, annual_production: float,
                          commodity_price: float,
                          opex_per_unit: float,
                          initial_capex: float,
                          mine_life: int,
                          discount_rate: float = 0.08) -> Dict:
        """NPV valuation for mining project"""
        annual_revenue = annual_production * commodity_price
        annual_opex = annual_production * opex_per_unit
        annual_cashflow = annual_revenue - annual_opex
        
        # NPV calculation
        npv = -initial_capex
        for year in range(1, mine_life + 1):
            # Declining production curve
            production_factor = 1 - (year * 0.03)
            year_cashflow = annual_cashflow * max(0.5, production_factor)
            npv += year_cashflow / ((1 + discount_rate) ** year)
        
        return {
            "initial_capex": initial_capex,
            "annual_cashflow": round(annual_cashflow, 0),
            "npv": round(npv, 0),
            "irr_estimate": round((annual_cashflow / initial_capex) * 100, 1),
            "payback_years": round(initial_capex / annual_cashflow, 1) if annual_cashflow > 0 else 999,
            "viable": npv > 0
        }
    
    def grade_tonnage_curve(self, resource_tons: float,
                           grade_percent: float,
                           metal_price: float,
                           recovery_rate: float) -> Dict:
        """Calculate contained metal value"""
        contained_metal = resource_tons * (grade_percent / 100) * recovery_rate
        in_situ_value = contained_metal * metal_price
        
        return {
            "resource_tons": resource_tons,
            "grade_percent": grade_percent,
            "contained_metal_tons": round(contained_metal, 0),
            "in_situ_value": round(in_situ_value, 0),
            "value_per_ton": round(in_situ_value / resource_tons, 2) if resource_tons > 0 else 0
        }
