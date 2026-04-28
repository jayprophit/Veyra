"""Carbon Removal Economics - DAC and carbon capture economics"""
from typing import Dict

class CarbonRemovalEconomics:
    """Economics of carbon dioxide removal technologies"""
    
    def direct_air_capture_cost(self, capex_per_ton: float,
                               opex_per_ton: float,
                              capacity_tons_per_year: int) -> Dict:
        """Calculate DAC facility economics"""
        total_capex = capex_per_ton * capacity_tons_per_year
        annual_opex = opex_per_ton * capacity_tons_per_year
        
        # At $100/ton carbon credit
        carbon_credit_revenue = 100 * capacity_tons_per_year
        
        # Simple payback
        net_annual = carbon_credit_revenue - annual_opex
        payback = total_capex / net_annual if net_annual > 0 else float('inf')
        
        return {
            "total_capex": round(total_capex, 0),
            "annual_opex": round(annual_opex, 0),
            "carbon_credit_revenue": carbon_credit_revenue,
            "simple_payback_years": round(payback, 1),
            "cost_per_ton": capex_per_ton + opex_per_ton,
            "profitable": net_annual > 0
        }
    
    def biochar_economics(self, feedstock_cost: float,
                         yield_per_ton: float,
                         carbon_price: float) -> Dict:
        """Calculate biochar production economics"""
        production_cost = feedstock_cost + 50  # Processing
        carbon_credits = yield_per_ton * carbon_price
        biochar_revenue = 200  # $200/ton biochar
        
        total_revenue = carbon_credits + biochar_revenue
        profit = total_revenue - production_cost
        
        return {
            "production_cost": production_cost,
            "carbon_credit_revenue": round(carbon_credits, 0),
            "biochar_revenue": biochar_revenue,
            "total_revenue": round(total_revenue, 0),
            "profit_per_ton": round(profit, 0),
            "margin": round(profit / total_revenue * 100, 1) if total_revenue > 0 else 0
        }
    
    def reforestation_npv(self, acres: int,
                       cost_per_acre: float,
                       carbon_absorption_per_acre: float,
                       carbon_price: float,
                       years: int) -> Dict:
        """Calculate NPV of reforestation project"""
        total_cost = acres * cost_per_acre
        annual_carbon = acres * carbon_absorption_per_acre
        annual_revenue = annual_carbon * carbon_price
        
        # NPV at 5% discount
        npv = sum(annual_revenue / (1.05 ** i) for i in range(1, years + 1)) - total_cost
        
        return {
            "total_cost": total_cost,
            "annual_carbon_tons": annual_carbon,
            "annual_revenue": round(annual_revenue, 0),
            "project_npv": round(npv, 0),
            "profitable": npv > 0,
            "years_to_break_even": int(total_cost / annual_revenue) if annual_revenue > 0 else float('inf')
        }
