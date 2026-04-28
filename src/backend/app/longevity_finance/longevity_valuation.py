"""Longevity Valuation - Valuing life extension companies"""
from typing import Dict

class LongevityValuation:
    """Value longevity and life extension companies"""
    
    def longevity_company_dcf(self, annual_revenue: float,
                             growth_rate: float,
                             market_size: float,
                             success_prob: float) -> Dict:
        """DCF valuation for longevity biotech"""
        # High risk-adjusted discount rate
        discount_rate = 0.15
        
        # 10-year projection
        projected_revenue = annual_revenue * ((1 + growth_rate) ** 10) * success_prob
        
        # Terminal value with market penetration
        terminal_value = market_size * 0.05 * success_prob
        
        # DCF calculation (simplified)
        dcf_value = projected_revenue * 5 + terminal_value * 0.3
        
        return {
            "current_revenue": annual_revenue,
            "projected_revenue": round(projected_revenue, 0),
            "terminal_value": round(terminal_value, 0),
            "dcf_valuation": round(dcf_value, 0),
            "risk_adjusted": True,
            "success_probability": success_prob
        }
    
    def healthspan_roi(self, treatment_cost: float,
                      years_gained: float,
                      quality_adjustment: float,
                      annual_income: float) -> Dict:
        """Calculate ROI on longevity treatments"""
        # Value of additional healthy years
        value_per_year = annual_income * quality_adjustment
        total_value = value_per_year * years_gained
        roi = (total_value - treatment_cost) / treatment_cost if treatment_cost > 0 else 0
        
        return {
            "treatment_cost": treatment_cost,
            "years_gained": years_gained,
            "total_value": round(total_value, 0),
            "roi_percent": round(roi * 100, 1),
            "payback_years": treatment_cost / value_per_year if value_per_year > 0 else float('inf')
        }
    
    def senolytic_market_model(self, target_population: int,
                              penetration_rate: float,
                              annual_price: float) -> Dict:
        """Model senolytic (aging cell removal) market"""
        addressable = target_population * 0.4  # 40% over 50
        target = addressable * penetration_rate
        market_size = target * annual_price
        
        return {
            "total_population": target_population,
            "addressable_market": int(addressable),
            "target_customers": int(target),
            "annual_market_size": round(market_size, 0),
            "tam_category": "multi_billion" if market_size > 1e9 else "billion" if market_size > 1e8 else "sub_billion"
        }
