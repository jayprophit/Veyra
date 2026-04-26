"""Fan Platform Revenue - OnlyFans, Patreon, Fanvue, Fansly, and other creator platforms"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class FanPlatform(Enum):
    ONLYFANS = "onlyfans"; PATREON = "patreon"; FANSLY = "fansly"
    FANVUE = "fanvue"; JUSTFORFANS = "justforfans"; AVN = "avn"
    MANYVIDS = "manyvids"; FRISK = "frisk"; UNLOCKD = "unlockd"
    SUBSCRIBESTAR = "subscribestar"; KO_FI = "ko_fi"; BUY_ME_COFFEE = "buy_me_coffee"

@dataclass
class FanRevenue:
    platform: FanPlatform; amount: Decimal
    source: str; date: date
    subscriber_count: int; churn_rate: float

class FanPlatformRevenue:
    """Track revenue from all fan/creator platforms including OnlyFans, Patreon, etc."""
    
    def __init__(self):
        self.revenue_history: List[FanRevenue] = []
        self.platform_fees = {
            FanPlatform.ONLYFANS: Decimal("0.20"),      # 20% platform fee
            FanPlatform.PATREON: Decimal("0.05"),       # 5-12% depending on tier
            FanPlatform.FANSLY: Decimal("0.20"),          # 20% fee
            FanPlatform.FANVUE: Decimal("0.15"),        # 15% fee
            FanPlatform.JUSTFORFANS: Decimal("0.20"),
            FanPlatform.AVN: Decimal("0.20"),
            FanPlatform.MANYVIDS: Decimal("0.30"),      # 30% for videos
            FanPlatform.FRISK: Decimal("0.20"),
            FanPlatform.UNLOCKD: Decimal("0.15"),
            FanPlatform.SUBSCRIBESTAR: Decimal("0.05"),
            FanPlatform.KO_FI: Decimal("0.00"),         # 0% fee (donations)
            FanPlatform.BUY_ME_COFFEE: Decimal("0.05")  # 5% fee
        }
        
    def calculate_platform_revenue(self, platform: FanPlatform,
                                   subscribers: int,
                                   subscription_price: Decimal,
                                   content_sales_monthly: Decimal = Decimal("0"),
                                   tips_monthly: Decimal = Decimal("0"),
                                   pay_per_view: Decimal = Decimal("0")) -> Dict:
        """Calculate revenue for a fan platform"""
        if platform not in self.platform_fees:
            return {"error": "Platform not configured"}
        
        platform_fee = self.platform_fees[platform]
        
        # Calculate gross revenue
        monthly_subscription_revenue = Decimal(subscribers) * subscription_price
        gross_revenue = (monthly_subscription_revenue + content_sales_monthly + 
                        tips_monthly + pay_per_view)
        
        # Calculate net after platform fee
        platform_cut = gross_revenue * platform_fee
        net_revenue = gross_revenue - platform_cut
        
        # Payment processor fees (typically 2-3%)
        processing_fee = net_revenue * Decimal("0.029") + Decimal("0.30") * (subscribers // 10)
        final_revenue = net_revenue - processing_fee
        
        # Estimate churn and lifetime value
        avg_churn_monthly = 0.10  # 10% monthly churn
        avg_subscriber_lifetime_months = 1 / avg_churn_monthly if avg_churn_monthly > 0 else 12
        ltv = subscription_price * Decimal(str(avg_subscriber_lifetime_months))
        
        return {
            "platform": platform.value,
            "subscribers": subscribers,
            "subscription_price": float(subscription_price),
            "gross_monthly_revenue": float(gross_revenue),
            "platform_fee_pct": float(platform_fee * 100),
            "platform_cut": float(platform_cut),
            "payment_processing": float(processing_fee),
            "net_monthly_revenue": float(final_revenue),
            "net_yearly_revenue": float(final_revenue * 12),
            "revenue_breakdown": {
                "subscriptions": float(monthly_subscription_revenue),
                "content_sales": float(content_sales_monthly),
                "tips": float(tips_monthly),
                "pay_per_view": float(pay_per_view)
            },
            "subscriber_ltv": float(ltv),
            "estimated_monthly_churn": avg_churn_monthly,
            "take_home_pct": float(final_revenue / gross_revenue * 100) if gross_revenue > 0 else 0
        }
    
    def compare_platforms(self, subscribers: int = 1000,
                         subscription_price: Decimal = Decimal("9.99")) -> List[Dict]:
        """Compare all fan platforms side by side"""
        comparisons = []
        
        # Additional revenue assumptions
        content_sales = Decimal(str(subscribers * 2))  # $2 per subscriber in content sales
        tips = Decimal(str(subscribers * 1.5))  # $1.50 per subscriber in tips
        ppv = Decimal(str(subscribers * 0.5))  # $0.50 per subscriber in PPV
        
        for platform in FanPlatform:
            result = self.calculate_platform_revenue(
                platform, subscribers, subscription_price,
                content_sales, tips, ppv
            )
            comparisons.append(result)
        
        # Sort by net revenue
        return sorted(comparisons, key=lambda x: x["net_monthly_revenue"], reverse=True)
    
    def optimize_pricing(self, platform: FanPlatform,
                        current_subscribers: int,
                        current_price: Decimal,
                        price_elasticity: float = -1.5) -> Dict:
        """Recommend optimal pricing strategy"""
        # Test different price points
        test_prices = [Decimal("4.99"), Decimal("9.99"), Decimal("14.99"),
                      Decimal("19.99"), Decimal("29.99"), Decimal("49.99")]
        
        results = []
        for price in test_prices:
            # Estimate subscriber change based on price elasticity
            price_ratio = float(price / current_price)
            subscriber_ratio = price_ratio ** price_elasticity
            estimated_subscribers = int(current_subscribers * subscriber_ratio)
            
            revenue_data = self.calculate_platform_revenue(
                platform, estimated_subscribers, price
            )
            results.append({
                "price": float(price),
                "estimated_subscribers": estimated_subscribers,
                "monthly_net_revenue": revenue_data["net_monthly_revenue"],
                "vs_current": revenue_data["net_monthly_revenue"] - 
                             self.calculate_platform_revenue(platform, current_subscribers, 
                                                            current_price)["net_monthly_revenue"]
            })
        
        best = max(results, key=lambda x: x["monthly_net_revenue"])
        
        return {
            "current_price": float(current_price),
            "current_subscribers": current_subscribers,
            "optimal_price": best["price"],
            "projected_revenue_at_optimal": best["monthly_net_revenue"],
            "revenue_lift_pct": (best["monthly_net_revenue"] / 
                                max([r["monthly_net_revenue"] for r in results if r["price"] == float(current_price)], 1) - 1) * 100,
            "all_scenarios": results
        }
    
    def content_strategy_roi(self, platform: FanPlatform) -> List[Dict]:
        """Get content strategy ROI recommendations"""
        strategies = [
            {
                "content_type": "exclusive_photos",
                "frequency": "daily",
                "production_cost": 50,
                "expected_revenue_boost": 200,
                "roi": 300,
                "difficulty": "low"
            },
            {
                "content_type": "premium_videos",
                "frequency": "3x weekly",
                "production_cost": 200,
                "expected_revenue_boost": 800,
                "roi": 300,
                "difficulty": "medium"
            },
            {
                "content_type": "live_streams",
                "frequency": "weekly",
                "production_cost": 100,
                "expected_revenue_boost": 500,
                "roi": 400,
                "difficulty": "medium"
            },
            {
                "content_type": "custom_content",
                "frequency": "on_demand",
                "production_cost": 150,
                "expected_revenue_boost": 600,
                "roi": 300,
                "difficulty": "high"
            },
            {
                "content_type": "behind_scenes",
                "frequency": "weekly",
                "production_cost": 30,
                "expected_revenue_boost": 150,
                "roi": 400,
                "difficulty": "low"
            }
        ]
        
        return sorted(strategies, key=lambda x: x["roi"], reverse=True)
    
    def diversification_strategy(self, current_platform: FanPlatform,
                                monthly_revenue: Decimal) -> Dict:
        """Recommend multi-platform diversification"""
        platform_types = {
            "subscription": [FanPlatform.ONLYFANS, FanPlatform.FANSLY, FanPlatform.FANVUE],
            "membership": [FanPlatform.PATREON, FanPlatform.SUBSCRIBESTAR],
            "tipping": [FanPlatform.KO_FI, FanPlatform.BUY_ME_COFFEE],
            "video": [FanPlatform.MANYVIDS]
        }
        
        current_type = None
        for ptype, platforms in platform_types.items():
            if current_platform in platforms:
                current_type = ptype
                break
        
        recommendations = []
        for ptype, platforms in platform_types.items():
            if ptype != current_type:
                for platform in platforms[:1]:  # Recommend first of each type
                    fee = self.platform_fees[platform]
                    estimated_capture = monthly_revenue * Decimal("0.30")  # 30% of audience
                    net_from_new = estimated_capture * (Decimal("1") - fee)
                    
                    recommendations.append({
                        "platform": platform.value,
                        "type": ptype,
                        "estimated_monthly": float(net_from_new),
                        "audience_overlap_pct": 30,
                        "setup_difficulty": "medium",
                        "why": f"Different monetization model reduces platform risk"
                    })
        
        return {
            "current_platform": current_platform.value,
            "current_type": current_type,
            "monthly_revenue": float(monthly_revenue),
            "recommended_diversification": recommendations,
            "total_additional_revenue_potential": sum(r["estimated_monthly"] for r in recommendations),
            "risk_reduction": "High - not dependent on single platform"
        }
    
    def tax_compliance_notes(self, jurisdiction: str = "US") -> Dict:
        """Get tax compliance information for creator income"""
        notes = {
            "US": {
                "tax_form": "1099-NEC or 1099-K",
                "self_employment_tax": True,
                "quarterly_estimated": True,
                "deductible_expenses": [
                    "Camera equipment", "Lighting", "Props/costumes",
                    "Home office space", "Internet", "Phone",
                    "Editing software", "Platform fees"
                ],
                "record_keeping": "Track all income and expenses monthly"
            },
            "UK": {
                "tax_form": "Self Assessment",
                "self_employment_tax": True,
                "quarterly_estimated": False,
                "deductible_expenses": [
                    "Equipment", "Travel for content", "Professional services"
                ],
                "record_keeping": "Keep records for 5 years"
            }
        }
        
        return notes.get(jurisdiction, notes["US"])
