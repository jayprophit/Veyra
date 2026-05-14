"""Crowdfunding Platform Economics"""
from typing import Dict

class PlatformEconomics:
    """Analyze crowdfunding platform business models"""
    
    def kickstarter_model(self) -> Dict:
        """Rewards-based crowdfunding economics"""
        return {
            "platform_fee": 0.05,
            "payment_processing": 0.03,
            "total_take_rate": 0.08,
            "all_or_nothing": True,
            "success_rate": 0.40,
            "avg_project_size": 25000,
            "annual_volume_billions": 0.5
        }
    
    def indiegogo_model(self) -> Dict:
        """Flexible funding model"""
        return {
            "platform_fee": 0.05,
            "flexible_funding_fee": 0.05,  # If you keep money when not funded
            "total_take_rate": 0.08,
            "success_rate": 0.25,
            "differentiation": "Keep what you raise option"
        }
    
    def equity_crowdfunding(self) -> Dict:
        """Equity crowdfunding (Reg CF, Reg A+)"""
        return {
            "platform_fee": 0.07,
            "success_fee": 0.02,
            "total_take_rate": 0.09,
            "avg_raise_reg_cf": 500000,
            "avg_raise_reg_a": 15e6,
            "investor_limits": "Based on income/net worth"
        }
    
    def revenue_forecast(self, annual_volume: float = 300e6) -> Dict:
        """Project platform revenue"""
        take_rate = 0.08
        gross_revenue = annual_volume * take_rate
        operating_margin = 0.30
        
        return {
            "gross_revenue_millions": gross_revenue / 1e6,
            "operating_profit_millions": (gross_revenue * operating_margin) / 1e6,
            "take_rate": take_rate,
            "operating_margin": operating_margin
        }
