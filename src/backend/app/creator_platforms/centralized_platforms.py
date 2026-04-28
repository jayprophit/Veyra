"""Centralized Platforms - Content creator monetization"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CreatorPlatform:
    name: str
    revenue_models: List[str]
    fee_pct: float
    min_payout: float
    frequency: str

class CentralizedPlatformManager:
    """Manage centralized creator platforms"""
    
    PLATFORMS = {
        "youtube": CreatorPlatform("YouTube", ["adsense", "memberships", "super_chat"], 45.0, 100.0, "monthly"),
        "tiktok": CreatorPlatform("TikTok", ["creator_fund", "gifts", "shop"], 50.0, 50.0, "monthly"),
        "instagram": CreatorPlatform("Instagram", ["badges", "subscriptions"], 0.0, 25.0, "monthly"),
        "x_twitter": CreatorPlatform("X", ["ad_revenue", "subscriptions"], 0.0, 10.0, "monthly"),
        "twitch": CreatorPlatform("Twitch", ["subs", "bits", "ads"], 50.0, 100.0, "monthly"),
        "kick": CreatorPlatform("Kick", ["subs", "donations"], 5.0, 0.0, "weekly"),
        "patreon": CreatorPlatform("Patreon", ["memberships"], 8.0, 0.0, "monthly"),
        "substack": CreatorPlatform("Substack", ["subscriptions"], 10.0, 0.0, "monthly"),
        "gumroad": CreatorPlatform("Gumroad", ["product_sales"], 10.0, 0.0, "weekly"),
        "udemy": CreatorPlatform("Udemy", ["course_sales"], 63.0, 0.0, "monthly"),
    }
    
    def get_platform(self, name: str) -> CreatorPlatform:
        return self.PLATFORMS.get(name.lower())
    
    def list_platforms(self) -> List[str]:
        return list(self.PLATFORMS.keys())
    
    def compare_fees(self) -> Dict:
        return {name: p.fee_pct for name, p in self.PLATFORMS.items()}
