"""API Pricing"""
from typing import Dict

class APIPricing:
    """API pricing models"""
    
    def pay_per_call(self, calls_per_month: int, rate_per_1000: float) -> Dict:
        """Pay-per-call pricing"""
        cost = (calls_per_month / 1000) * rate_per_1000
        return {"monthly_cost": cost, "effective_rate": rate_per_1000 / 1000}
    
    def subscription_tiers(self, tier: str) -> Dict:
        """Subscription tier pricing"""
        tiers = {
            "free": {"calls": 1000, "price": 0, "features": "basic"},
            "starter": {"calls": 10000, "price": 49, "features": "standard"},
            "pro": {"calls": 100000, "price": 199, "features": "advanced"},
            "enterprise": {"calls": 1000000, "price": 999, "features": "full"}
        }
        return tiers.get(tier.lower(), tiers["free"])
    
    def freemium_conversion(self, free_users: int, conversion_rate: float) -> Dict:
        """Freemium conversion revenue"""
        paying_users = free_users * conversion_rate
        arpu = 50  # Average revenue per user
        return {"paying_users": paying_users, "monthly_revenue": paying_users * arpu}
