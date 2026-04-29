"""Dispensary Economics - Cannabis retail analytics"""
from typing import Dict

class DispensaryEconomics:
    """Analyze cannabis dispensary economics"""
    
    def unit_economics(self, avg_transaction: float,
                      daily_transactions: int,
                      cogs_pct: float,
                      rent_monthly: float,
                      employees: int) -> Dict:
        """Calculate per-store unit economics"""
        daily_revenue = avg_transaction * daily_transactions
        monthly_revenue = daily_revenue * 30
        monthly_cogs = monthly_revenue * (cogs_pct / 100)
        labor_cost = employees * 3500  # $3500/month avg
        
        monthly_profit = monthly_revenue - monthly_cogs - rent_monthly - labor_cost
        margin = monthly_profit / monthly_revenue if monthly_revenue > 0 else 0
        
        return {
            "monthly_revenue": round(monthly_revenue, 0),
            "monthly_cogs": round(monthly_cogs, 0),
            "monthly_profit": round(monthly_profit, 0),
            "profit_margin": round(margin * 100, 1),
            "revenue_per_sqft": "industry_avg_1500",
            "breakeven_daily_transactions": round((rent_monthly + labor_cost) / (avg_transaction * (1 - cogs_pct/100)), 0)
        }
    
    def license_valuation(self, license_type: str,
                         jurisdiction_population: int,
                         competing_licenses: int,
                         revenue_potential: float) -> Dict:
        """Value cannabis licenses as intangible assets"""
        scarcity = 1 / max(1, competing_licenses)
        population_multiplier = min(jurisdiction_population / 100000, 5)
        
        base_value = revenue_potential * 0.5  # 0.5x revenue
        adjusted_value = base_value * (1 + scarcity) * population_multiplier
        
        license_tiers = {
            "recreational": 1.5, "medical": 1.0, "cultivation": 0.8,
            "processing": 0.6, "distribution": 0.7
        }
        tier_mult = license_tiers.get(license_type, 1.0)
        
        return {
            "license_type": license_type,
            "base_value": round(base_value, 0),
            "adjusted_value": round(adjusted_value * tier_mult, 0),
            "scarcity_premium": round(scarcity * 100, 1),
            "jurisdiction_value": jurisdiction_population
        }
