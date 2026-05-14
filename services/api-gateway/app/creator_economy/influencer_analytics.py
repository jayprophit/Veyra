"""Influencer Analytics - Brand deals, sponsorships, rate calculations"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

class Tier(Enum):
    NANO = "nano"; MICRO = "micro"; MID = "mid"; MACRO = "macro"; MEGA = "mega"

class ContentVertical(Enum):
    FASHION = "fashion"; BEAUTY = "beauty"; TECH = "tech"; FINANCE = "finance"
    FITNESS = "fitness"; FOOD = "food"; TRAVEL = "travel"; GAMING = "gaming"
    LIFESTYLE = "lifestyle"; BUSINESS = "business"

@dataclass
class BrandDeal:
    brand: str; amount: Decimal; platforms: List[str]; date: date

class InfluencerAnalytics:
    """Analytics for influencer brand deals and sponsorships"""
    
    def __init__(self):
        self.rate_card = {
            Tier.NANO: {"followers": (1000, 10000), "post": (50, 250), "story": (20, 100)},
            Tier.MICRO: {"followers": (10000, 100000), "post": (250, 1000), "story": (100, 400)},
            Tier.MID: {"followers": (100000, 500000), "post": (1000, 5000), "story": (400, 1500)},
            Tier.MACRO: {"followers": (500000, 1000000), "post": (5000, 15000), "story": (1500, 5000)},
            Tier.MEGA: {"followers": (1000000, 10000000), "post": (15000, 100000), "story": (5000, 25000)}
        }
    
    def get_tier(self, followers: int) -> Tier:
        for tier, data in self.rate_card.items():
            if data["followers"][0] <= followers < data["followers"][1]:
                return tier
        return Tier.MEGA
    
    def calculate_post_value(self, followers: int, engagement: float = 0.03,
                          vertical: ContentVertical = ContentVertical.LIFESTYLE) -> Dict:
        tier = self.get_tier(followers)
        data = self.rate_card[tier]
        base = Decimal(str((data["post"][0] + data["post"][1]) / 2))
        
        mult = Decimal(str(engagement / 0.03))
        premiums = {ContentVertical.FINANCE: Decimal("1.5"), ContentVertical.TECH: Decimal("1.4"),
                   ContentVertical.BUSINESS: Decimal("1.3"), ContentVertical.FASHION: Decimal("1.2")}
        prem = premiums.get(vertical, Decimal("1.0"))
        
        post_val = base * mult * prem
        
        return {
            "tier": tier.value, "followers": followers,
            "post_value": float(post_val), "story_value": float(post_val * Decimal("0.4")),
            "reel_value": float(post_val * Decimal("1.5")),
            "cpm": float((post_val / Decimal(followers)) * 1000),
            "vertical": vertical.value
        }
    
    def sponsorship_package(self, followers: int, pkg: str = "basic") -> Dict:
        rates = self.calculate_post_value(followers)
        post = rates["post_value"]
        
        packages = {
            "nano": {"1_post": 100, "3_posts": 250, "bundle": 350},
            "basic": {"1_post": post, "3_posts": post * 2.5, "reel": rates["reel_value"], "retainer": post * 4},
            "premium": {"campaign": post * 3, "stories_10": rates["story_value"] * 10, "usage": "6 months"},
            "ambassador": {"6_month": post * 20, "min_monthly": "4 posts + 8 stories", "exclusivity": "category"}
        }
        
        return {"tier": rates["tier"], "followers": followers, "package": pkg, "pricing": packages.get(pkg, packages["basic"])}
    
    def media_kit_stats(self, platforms: List[Dict]) -> Dict:
        total = sum(p.get("followers", 0) for p in platforms)
        avg_eng = sum(p.get("engagement", 0) for p in platforms) / len(platforms) if platforms else 0
        
        return {
            "total_followers": total, "platforms": len(platforms),
            "avg_engagement": round(avg_eng * 100, 2),
            "age_18_34": 0.60, "female": 0.60, "us_uk_ca": 0.65,
            "quality_score": min(100, int(avg_eng * 100 * 3))
        }
    
    def deal_flow_pipeline(self, stage: str = "all") -> Dict:
        pipeline = {
            "outreach": 20, "negotiation": 8, "contract": 5, "delivered": 3, "paid": 12
        }
        conversion_rates = {
            "outreach_to_negotiation": 0.40, "negotiation_to_contract": 0.625,
            "contract_to_delivered": 0.60, "delivered_to_paid": 1.0
        }
        
        if stage == "all":
            return {"pipeline": pipeline, "conversions": conversion_rates, "total_active": sum(pipeline.values())}
        return pipeline.get(stage, 0)
