"""Digital Audio - Music, sound effects, podcasts"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AudioProduct:
    name: str
    audio_type: str
    duration_minutes: float
    quality: str

class DigitalAudio:
    """Digital audio products and monetization"""
    
    AUDIO_TYPES = {
        "royalty_free_music": {"price_per_track": 15, "bundle_discount": 0.3},
        "sound_effects": {"price_per_pack": 10, "unit_price": 1},
        "podcast_episode": {"price_free": 0, "premium": 5},
        "audiobook": {"price_per_hour": 7, "chapter_price": 3},
        "meditation_track": {"price": 3, "subscription_ready": True},
        "sample_pack": {"price": 25, "producer_friendly": True},
        "loop_kit": {"price": 20, "royalty_split": 0.5},
        " vst_preset": {"price": 15, "bundle_friendly": True},
        "field_recording": {"price": 8, "rareness_premium": 2.0},
        "ringtone": {"price": 1, "volume_model": True},
    }
    
    PLATFORMS = {
        "audiojungle": {"revenue_share": 0.45, "type": "marketplace"},
        "epidemic_sound": {"revenue_share": 0.50, "type": "subscription"},
        "artlist": {"revenue_share": 0.50, "type": "subscription"},
        "pond5": {"revenue_share": 0.50, "type": "marketplace"},
        "bandcamp": {"revenue_share": 0.85, "type": "direct"},
        "soundstripe": {"revenue_share": 0.50, "type": "subscription"},
        "musicbed": {"revenue_share": 0.50, "type": "premium"},
        "spotify_for_podcasters": {"revenue_share": 0.00, "type": "ad_supported"},
        "audiobooks_com": {"revenue_share": 0.40, "type": "retail"},
        "audible": {"revenue_share": 0.25, "type": "exclusive"},
    }
    
    def price_track(self, audio_type: str, duration: float, 
                   quality: str = "standard") -> Dict:
        """Price an audio track/product"""
        type_data = self.AUDIO_TYPES.get(audio_type.lower())
        if not type_data:
            return {"error": "Audio type not found"}
        
        # Base pricing
        if "price_per_track" in type_data:
            base = type_data["price_per_track"]
        elif "price_per_hour" in type_data:
            base = duration / 60 * type_data["price_per_hour"]
        elif "price_per_pack" in type_data:
            base = type_data["price_per_pack"]
        else:
            base = type_data.get("price", 5)
        
        # Quality adjustment
        quality_multipliers = {"standard": 1.0, "high": 1.2, "lossless": 1.5, "studio": 2.0}
        price = base * quality_multipliers.get(quality, 1.0)
        
        # Duration premium for longer tracks
        if duration > 10 and audio_type == "royalty_free_music":
            price *= 1.3
        
        return {
            "audio_type": audio_type,
            "duration_minutes": duration,
            "quality_tier": quality,
            "suggested_price": round(price, 2),
            "bulk_discount_available": type_data.get("bundle_discount", 0) > 0
        }
    
    def streaming_revenue(self, platform: str, streams: int,
                         stream_type: str = "music") -> Dict:
        """Calculate streaming revenue"""
        # Industry average payouts per stream
        payouts = {
            "spotify": 0.003,
            "apple_music": 0.01,
            "youtube_music": 0.002,
            "amazon_music": 0.004,
            "tidal": 0.013,
            "deezer": 0.006,
            "pandora": 0.0013,
            "napster": 0.019
        }
        
        rate = payouts.get(platform.lower(), 0.003)
        revenue = streams * rate
        
        # Platform cut (typically 30% goes to platform/distributor)
        net_revenue = revenue * 0.70
        
        return {
            "platform": platform,
            "streams": streams,
            "per_stream_rate": rate,
            "gross_revenue": round(revenue, 2),
            "net_revenue": round(net_revenue, 2),
            "needed_for_1000": round(1000 / rate, 0) if rate > 0 else 0
        }
    
    def sample_pack_licensing(self, pack_price: float, 
                             sales_projected: int = 100) -> Dict:
        """Analyze sample pack economics"""
        gross = pack_price * sales_projected
        platform_fee = gross * 0.30  # Typical marketplace cut
        net = gross - platform_fee
        
        return {
            "pack_price": pack_price,
            "projected_sales": sales_projected,
            "gross_revenue": gross,
            "platform_fees": platform_fee,
            "net_revenue": net,
            "royalty_obligation": "50% of commercial releases using samples",
            "marketing_tips": [
                "Include demo tracks",
                "Offer stems for flexibility",
                "Bundle with tutorials"
            ]
        }
    
    def podcast_monetization(self, downloads_per_episode: int,
                            episodes_per_month: int = 4) -> Dict:
        """Calculate podcast revenue potential"""
        # CPM rates
        ad_cpm = 25  # $25 per 1000 downloads
        sponsor_cpm = 50
        
        monthly_downloads = downloads_per_episode * episodes_per_month
        
        ad_revenue = (monthly_downloads / 1000) * ad_cpm * 2  # 2 ads per episode
        sponsor_revenue = (monthly_downloads / 1000) * sponsor_cpm * 0.3  # 30% get sponsors
        
        patron_potential = downloads_per_episode * 0.05 * 5  # 5% become patrons at $5
        
        total_monthly = ad_revenue + sponsor_revenue + patron_potential
        
        return {
            "monthly_downloads": monthly_downloads,
            "ad_revenue": round(ad_revenue, 2),
            "sponsor_revenue": round(sponsor_revenue, 2),
            "patron_potential": round(patron_potential, 2),
            "total_monthly": round(total_monthly, 2),
            "annual_projection": round(total_monthly * 12, 2),
            "revenue_per_listener": round(total_monthly / monthly_downloads * 1000, 2) if monthly_downloads > 0 else 0
        }
    
    def compare_platforms(self, track_price: float) -> Dict:
        """Compare audio platform revenue"""
        results = {}
        
        for name, data in self.PLATFORMS.items():
            revenue = track_price * data["revenue_share"]
            results[name] = {
                "revenue_per_sale": round(revenue, 2),
                "take_home_pct": data["revenue_share"] * 100,
                "platform_type": data["type"],
                "recommendation": "direct" if data["revenue_share"] > 0.70 else "volume"
            }
        
        return results
