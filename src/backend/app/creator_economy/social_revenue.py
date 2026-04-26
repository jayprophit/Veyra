"""Social Revenue Tracker - Multi-platform social media income tracking"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class Platform(Enum):
    TWITTER = "twitter"; TIKTOK = "tiktok"; INSTAGRAM = "instagram"
    YOUTUBE = "youtube"; TWITCH = "twitch"; FACEBOOK = "facebook"
    LINKEDIN = "linkedin"; PINTEREST = "pinterest"; SNAPCHAT = "snapchat"
    REDDIT = "reddit"; DISCORD = "discord"; TELEGRAM = "telegram"
    MASTODON = "mastodon"; BLUESKY = "bluesky"; THREADS = "threads"
    LENS = "lens"; FARCASTER = "farcaster"; DESO = "deso"

@dataclass
class RevenueStream:
    platform: Platform; revenue_type: str
    amount: Decimal; date: date
    source_details: Dict

class SocialRevenueTracker:
    """Track revenue from all social media platforms"""
    
    def __init__(self):
        self.revenue_history: List[RevenueStream] = []
        self.platform_configs = self._init_platforms()
        
    def _init_platforms(self):
        return {
            Platform.TWITTER: {
                "monetization": ["ads_revenue", "subscriptions", "tips", "spaces_tickets"],
                "min_followers": 500, "payout_threshold": 50,
                "rpm_range": (2.00, 12.00),  # Revenue per 1000 impressions
                "supported_regions": ["US", "UK", "CA", "AU", "JP"]
            },
            Platform.TIKTOK: {
                "monetization": ["creator_fund", "live_gifts", "series", "shop_commission"],
                "min_followers": 10000, "payout_threshold": 100,
                "rpm_range": (0.50, 4.00),
                "supported_regions": ["US", "UK", "DE", "FR", "IT", "ES"]
            },
            Platform.INSTAGRAM: {
                "monetization": ["subscriptions", "badges", "bonuses", "reels_ads"],
                "min_followers": 10000, "payout_threshold": 100,
                "rpm_range": (1.00, 8.00),
                "supported_regions": ["Global"]
            },
            Platform.YOUTUBE: {
                "monetization": ["adsense", "memberships", "super_chat", "shopping", "sponsorships"],
                "min_followers": 1000, "payout_threshold": 100,
                "rpm_range": (3.00, 25.00),
                "supported_regions": ["Global"]
            },
            Platform.TWITCH: {
                "monetization": ["subscriptions", "bits", "ads", "sponsorships"],
                "min_followers": 50, "payout_threshold": 100,
                "rpm_range": (5.00, 15.00),
                "supported_regions": ["Global"]
            },
            Platform.LINKEDIN: {
                "monetization": ["creator_mode", "newsletters", "courses", "services"],
                "min_followers": 150, "payout_threshold": 0,
                "rpm_range": (10.00, 50.00),
                "supported_regions": ["Global"]
            }
        }
    
    def calculate_potential_revenue(self, platform: Platform, 
                                    followers: int, 
                                    monthly_views: int,
                                    engagement_rate: float = 0.03) -> Dict:
        """Calculate potential monthly revenue for a platform"""
        if platform not in self.platform_configs:
            return {"error": "Platform not configured"}
        
        config = self.platform_configs[platform]
        rpm_low, rpm_high = config["rpm_range"]
        rpm_avg = (rpm_low + rpm_high) / 2
        
        # Base ad revenue calculation
        ad_revenue = Decimal(str(monthly_views / 1000 * rpm_avg * engagement_rate / 0.03))
        
        # Platform-specific calculations
        revenue_breakdown = {"ads": float(ad_revenue)}
        
        if platform == Platform.TWITTER:
            # Twitter Blue/Verified subscriptions (creator keeps 50% of first year)
            subscription_revenue = min(followers * 0.001, 1000) * 4 * 0.50  # $4/month
            revenue_breakdown["subscriptions"] = subscription_revenue
            revenue_breakdown["tips"] = followers * 0.0001 * 5  # 0.01% tip $5 avg
            
        elif platform == Platform.TIKTOK:
            # Creator fund (very low RPM)
            creator_fund = monthly_views / 1000 * 0.50 * 0.02
            revenue_breakdown["creator_fund"] = creator_fund
            # Live gifts (typically higher engagement)
            live_revenue = followers * 0.005 * 2  # 0.5% attend, $2 avg
            revenue_breakdown["live_gifts"] = live_revenue
            
        elif platform == Platform.INSTAGRAM:
            # Subscriptions
            sub_revenue = followers * 0.002 * 5  # 0.2% subscribe at $5
            revenue_breakdown["subscriptions"] = sub_revenue
            # Bonuses
            revenue_breakdown["bonuses"] = 500 if monthly_views > 1000000 else 100
            
        elif platform == Platform.YOUTUBE:
            # Channel memberships
            membership_revenue = followers * 0.005 * 5  # 0.5% at $5
            revenue_breakdown["memberships"] = membership_revenue
            # Super Chat (live streams)
            revenue_breakdown["super_chat"] = followers * 0.001 * 10
            
        elif platform == Platform.TWITCH:
            # Tier 1 subs ($4.99, streamer gets ~$2.50)
            sub_revenue = followers * 0.15 * 2.50  # 15% sub rate
            revenue_breakdown["subscriptions"] = sub_revenue
            # Bits (average 1 bit per viewer per stream)
            revenue_breakdown["bits"] = followers * 0.05 * 0.01  # 5% viewers, 1 bit
        
        total_monthly = sum(revenue_breakdown.values())
        
        return {
            "platform": platform.value,
            "followers": followers,
            "monthly_views": monthly_views,
            "engagement_rate": engagement_rate,
            "estimated_monthly_usd": round(total_monthly, 2),
            "estimated_yearly_usd": round(total_monthly * 12, 2),
            "breakdown": {k: round(v, 2) for k, v in revenue_breakdown.items()},
            "rpm_average": rpm_avg,
            "requirements_met": followers >= config["min_followers"],
            "monetization_eligible": followers >= config["min_followers"]
        }
    
    def add_revenue(self, platform: Platform, revenue_type: str,
                   amount: Decimal, source_details: Dict) -> Dict:
        """Record revenue from a platform"""
        stream = RevenueStream(
            platform=platform,
            revenue_type=revenue_type,
            amount=amount,
            date=date.today(),
            source_details=source_details
        )
        self.revenue_history.append(stream)
        
        return {
            "success": True,
            "platform": platform.value,
            "type": revenue_type,
            "amount": float(amount),
            "date": stream.date.isoformat()
        }
    
    def get_revenue_summary(self, start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> Dict:
        """Get revenue summary across all platforms"""
        streams = self.revenue_history
        
        if start_date:
            streams = [s for s in streams if s.date >= start_date]
        if end_date:
            streams = [s for s in streams if s.date <= end_date]
        
        by_platform = {}
        by_type = {}
        total = Decimal("0")
        
        for stream in streams:
            total += stream.amount
            
            platform = stream.platform.value
            by_platform[platform] = by_platform.get(platform, Decimal("0")) + stream.amount
            
            rev_type = stream.revenue_type
            by_type[rev_type] = by_type.get(rev_type, Decimal("0")) + stream.amount
        
        return {
            "total_revenue": float(total),
            "by_platform": {k: float(v) for k, v in by_platform.items()},
            "by_type": {k: float(v) for k, v in by_type.items()},
            "transaction_count": len(streams),
            "average_transaction": float(total / len(streams)) if streams else 0,
            "top_platform": max(by_platform.items(), key=lambda x: x[1])[0] if by_platform else None
        }
    
    def optimize_strategy(self, platforms_data: List[Dict]) -> Dict:
        """Get optimization recommendations for multiple platforms"""
        recommendations = []
        
        # Sort by revenue per follower (efficiency)
        sorted_by_efficiency = sorted(
            platforms_data,
            key=lambda x: x.get("monthly_revenue", 0) / max(x.get("followers", 1), 1),
            reverse=True
        )
        
        top_performer = sorted_by_efficiency[0] if sorted_by_efficiency else None
        
        if top_performer:
            recommendations.append({
                "type": "double_down",
                "message": f"Focus on {top_performer['platform']} - highest revenue per follower",
                "action": "Increase posting frequency by 50%",
                "expected_lift": "20-30%"
            })
        
        # Cross-platform strategy
        recommendations.append({
            "type": "cross_post",
            "message": "Repurpose TikTok/Reels for YouTube Shorts",
            "action": "Upload Shorts daily",
            "expected_lift": "15-25% additional revenue"
        })
        
        # Engagement optimization
        recommendations.append({
            "type": "engagement",
            "message": "Post when audience is most active",
            "action": "Use analytics to find peak times",
            "expected_lift": "10-20% views"
        })
        
        # Platform-specific optimizations
        recommendations.append({
            "type": "diversification",
            "message": "Don't rely on single platform algorithm",
            "action": "Build email list and newsletter",
            "expected_lift": "Revenue stability +10%"
        })
        
        return {
            "top_performing_platform": top_performer["platform"] if top_performer else None,
            "platform_efficiency_ranking": [p["platform"] for p in sorted_by_efficiency],
            "recommendations": recommendations,
            "total_monthly_estimate": sum(p.get("monthly_revenue", 0) for p in platforms_data),
            "growth_opportunities": len(recommendations)
        }
    
    def get_decentralized_platforms(self) -> List[Dict]:
        """Get decentralized social media earning opportunities"""
        return [
            {
                "platform": "Lens Protocol",
                "token": "LENS",
                "monetization": "NFT posts, collect fees, tipping",
                "avg_earnings_monthly": 200,
                "entry_cost": "Free (need handle)",
                "pros": ["Own your content", "Direct fan monetization", "No algorithm suppression"],
                "cons": ["Smaller audience", "Crypto complexity", "Gas fees"]
            },
            {
                "platform": "Farcaster",
                "token": "DEGEN",
                "monetization": "Frames, tips, NFT mints",
                "avg_earnings_monthly": 500,
                "entry_cost": "$5/year",
                "pros": ["High engagement", "Crypto native", "Frame economy"],
                "cons": ["Niche audience", "Technical barrier", "Early stage"]
            },
            {
                "platform": "DeSo (Diamond)",
                "token": "DESO",
                "monetization": "Diamond tips, NFTs, creator coins",
                "avg_earnings_monthly": 150,
                "entry_cost": "Free",
                "pros": ["Integrated wallet", "Creator coins", "Cross-posting"],
                "cons": ["Low liquidity", "Complex UX", "Small userbase"]
            },
            {
                "platform": "Mirror.xyz",
                "token": "ETH",
                "monetization": "NFT essays, crowdfund, splits",
                "avg_earnings_monthly": 800,
                "entry_cost": "Free (need $WRITE token)",
                "pros": ["Web3 publishing", "Permanent storage", "Token gated"],
                "cons": ["Writer focused", "Gas costs", "Technical"]
            }
        ]
