"""Digital Courses - Online course creation and monetization"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CoursePlatform:
    name: str
    revenue_share: float
    transaction_fee: float
    subscription_model: bool

class DigitalCourses:
    """Online course business analytics"""
    
    PLATFORMS = {
        "udemy": CoursePlatform("Udemy", 0.37, 0.03, False),
        "coursera": CoursePlatform("Coursera", 0.40, 0.00, True),
        "skillshare": CoursePlatform("Skillshare", 0.50, 0.00, True),
        "teachable": CoursePlatform("Teachable", 0.95, 0.059, False),
        "thinkific": CoursePlatform("Thinkific", 1.00, 0.00, False),
        "kajabi": CoursePlatform("Kajabi", 1.00, 0.00, False),
        "podia": CoursePlatform("Podia", 0.95, 0.00, False),
        "linkedin_learning": CoursePlatform("LinkedIn Learning", 0.40, 0.00, True),
        "pluralsight": CoursePlatform("Pluralsight", 0.30, 0.00, True),
        "masterclass": CoursePlatform("MasterClass", 0.20, 0.00, True),
    }
    
    def calculate_revenue(self, platform: str, students: int, price: float) -> Dict:
        """Calculate course revenue"""
        plat = self.PLATFORMS.get(platform.lower())
        if not plat:
            return {"error": "Platform not found"}
        
        gross_revenue = students * price
        platform_fee = gross_revenue * (1 - plat.revenue_share)
        transaction_costs = gross_revenue * plat.transaction_fee
        net_revenue = gross_revenue - platform_fee - transaction_costs
        
        return {
            "platform": plat.name,
            "students": students,
            "course_price": price,
            "gross_revenue": gross_revenue,
            "platform_fee": round(platform_fee, 2),
            "transaction_fees": round(transaction_costs, 2),
            "net_revenue": round(net_revenue, 2),
            "effective_take_home": round(net_revenue / gross_revenue * 100, 1) if gross_revenue > 0 else 0
        }
    
    def pricing_strategy(self, course_hours: float, market: str) -> Dict:
        """Recommend course pricing"""
        # Hour-based pricing
        base_price = course_hours * 15  # $15 per hour
        
        # Market adjustment
        market_multipliers = {
            "beginner": 0.7,
            "professional": 1.2,
            "enterprise": 1.5,
            "niche": 1.0
        }
        
        multiplier = market_multipliers.get(market.lower(), 1.0)
        suggested = base_price * multiplier
        
        # Tier options
        tiers = {
            "basic": round(suggested * 0.6, 0),
            "standard": round(suggested, 0),
            "premium": round(suggested * 1.5, 0)
        }
        
        return {
            "suggested_tiers": tiers,
            "price_per_hour": 15 * multiplier,
            "market": market,
            "strategy": "value_based"
        }
    
    def lifetime_value(self, completion_rate: float, upsell_rate: float,
                      avg_upsell_value: float) -> Dict:
        """Calculate student lifetime value"""
        base_ltv = 1  # Base course price normalized
        completion_bonus = completion_rate * 0.5
        upsell_value = upsell_rate * avg_upsell_value
        
        total_ltv = base_ltv + completion_bonus + upsell_value
        
        return {
            "student_ltv": round(total_ltv, 2),
            "completion_impact": round(completion_bonus, 2),
            "upsell_impact": round(upsell_value, 2),
            "recommendations": [
                "Increase completion rates for higher LTV",
                "Add upsell courses or coaching",
                "Create course bundles"
            ]
        }
    
    def platform_comparison(self, monthly_students: int, price: float) -> Dict:
        """Compare revenue across all platforms"""
        results = {}
        
        for name, plat in self.PLATFORMS.items():
            gross = monthly_students * price
            fees = gross * (1 - plat.revenue_share + plat.transaction_fee)
            net = gross - fees
            
            results[name] = {
                "net_revenue": round(net, 2),
                "platform_fees": round(fees, 2),
                "take_home_pct": round(net / gross * 100, 1) if gross > 0 else 0,
                "model": "subscription" if plat.subscription_model else "one_time"
            }
        
        # Sort by net revenue
        best = max(results.items(), key=lambda x: x[1]["net_revenue"])
        
        return {
            "platforms": results,
            "best_for_revenue": best[0],
            "best_take_home": best[1]["take_home_pct"]
        }
