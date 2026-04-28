"""Brand Valuation - Celebrity brand worth and IP licensing"""
from typing import Dict

class BrandValuation:
    """Calculate celebrity brand value and licensing potential"""
    
    def celebrity_brand_value(self, followers: int, engagement: float, 
                             niche: str, years_active: int) -> Dict:
        """Calculate total brand value"""
        # Base value per follower with engagement multiplier
        base_per_follower = 0.05
        engagement_multiplier = 1 + (engagement * 10)
        
        # Niche multipliers
        niche_multipliers = {
            "beauty": 3.0, "fashion": 2.5, "fitness": 2.0, 
            "tech": 1.8, "finance": 2.2, "gaming": 1.5,
            "lifestyle": 2.0, "food": 1.6, "travel": 1.7
        }
        niche_mult = niche_multipliers.get(niche.lower(), 1.5)
        
        # Longevity bonus
        longevity_bonus = 1 + (years_active * 0.02)
        
        brand_value = followers * base_per_follower * engagement_multiplier * niche_mult * longevity_bonus
        
        return {
            "brand_value": round(brand_value, 0),
            "per_follower": round(base_per_follower * engagement_multiplier * niche_mult, 3),
            "engagement_premium": round((engagement_multiplier - 1) * 100, 1),
            "niche_multiplier": niche_mult,
            "annual_licensing_potential": round(brand_value * 0.15, 0)
        }
    
    def ip_licensing_deal(self, brand_value: float, license_type: str,
                         duration_years: int, territory: str) -> Dict:
        """Structure IP licensing deal"""
        # Licensing rates by type
        rates = {
            "merchandise": 0.08, "endorsement": 0.15, 
            "collaboration": 0.12, "franchise": 0.20,
            "content": 0.10, "product_line": 0.18
        }
        
        base_rate = rates.get(license_type.lower(), 0.10)
        
        # Territory multiplier
        territory_mult = {"global": 1.0, "regional": 0.6, "national": 0.4, "local": 0.2}
        terr_mult = territory_mult.get(territory.lower(), 0.5)
        
        annual_fee = brand_value * base_rate * terr_mult
        total_deal = annual_fee * duration_years
        
        return {
            "annual_licensing_fee": round(annual_fee, 0),
            "total_deal_value": round(total_deal, 0),
            "royalty_rate": base_rate * 100,
            "territory_scope": territory,
            "minimum_guarantee": round(annual_fee * 0.5, 0)
        }
    
    def endorsement_pricing(self, followers: int, platform: str,
                           content_type: str) -> Dict:
        """Price endorsement deal"""
        # Base CPM by platform
        platform_cpm = {
            "instagram": 10, "tiktok": 8, "youtube": 12,
            "twitter": 6, "twitch": 15, "linkedin": 20
        }
        
        # Content type multipliers
        content_mult = {
            "post": 1.0, "story": 0.3, "reel": 0.8, "video": 1.5,
            "live": 2.0, "series": 3.0, "campaign": 5.0
        }
        
        cpm = platform_cpm.get(platform.lower(), 10)
        mult = content_mult.get(content_type.lower(), 1.0)
        
        # Estimated reach (typically 10-30% of followers)
        estimated_reach = followers * 0.15
        
        price = (estimated_reach / 1000) * cpm * mult
        
        return {
            "suggested_price": round(price, 0),
            "estimated_reach": round(estimated_reach, 0),
            "cpm": cpm,
            "content_multiplier": mult,
            "price_range": f"${round(price * 0.8, 0)} - ${round(price * 1.2, 0)}"
        }
