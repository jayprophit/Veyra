"""E-book Publishing - Self-publishing platforms and royalties"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class EbookPlatform:
    name: str
    royalty_rate: float
    delivery_fee: float
    min_price: float
    max_price: float

class EbookPublishing:
    """E-book publishing across platforms"""
    
    PLATFORMS = {
        "amazon_kdp": EbookPlatform("Amazon KDP", 0.70, 0.00, 0.99, 200.00),
        "apple_books": EbookPlatform("Apple Books", 0.70, 0.00, 0.99, 200.00),
        "google_play": EbookPlatform("Google Play Books", 0.70, 0.00, 0.99, 200.00),
        "kobo": EbookPlatform("Kobo Writing Life", 0.70, 0.00, 0.99, 200.00),
        "bn_nook": EbookPlatform("Barnes & Noble Nook", 0.65, 0.00, 0.99, 200.00),
        "smashwords": EbookPlatform("Smashwords", 0.60, 0.00, 0.99, 200.00),
        "draft2digital": EbookPlatform("Draft2Digital", 0.60, 0.00, 0.99, 200.00),
        "gumroad": EbookPlatform("Gumroad", 0.95, 0.00, 1.00, 1000.00),
        "payhip": EbookPlatform("Payhip", 0.95, 0.00, 1.00, 1000.00),
        "leanpub": EbookPlatform("Leanpub", 0.80, 0.00, 4.99, 500.00),
    }
    
    def calculate_royalty(self, platform: str, price: float, pages: int = 0) -> Dict:
        """Calculate royalty for a sale"""
        plat = self.PLATFORMS.get(platform.lower())
        if not plat:
            return {"error": "Platform not found"}
        
        # Amazon KDP delivery fee for certain markets
        delivery_fee = 0.15 if platform == "amazon_kdp" and pages > 0 else 0
        
        royalty = (price * plat.royalty_rate) - delivery_fee
        
        return {
            "platform": plat.name,
            "list_price": price,
            "royalty_rate": plat.royalty_rate * 100,
            "delivery_fee": delivery_fee,
            "net_royalty": round(royalty, 2),
            "effective_rate": round(royalty / price * 100, 1) if price > 0 else 0
        }
    
    def compare_platforms(self, price: float) -> Dict[str, float]:
        """Compare royalties across platforms"""
        results = {}
        for name, plat in self.PLATFORMS.items():
            royalty = price * plat.royalty_rate
            results[name] = round(royalty, 2)
        return results
    
    def multi_platform_revenue(self, monthly_sales: Dict[str, int], price: float) -> Dict:
        """Calculate revenue across all platforms"""
        total_revenue = 0
        breakdown = {}
        
        for platform, sales in monthly_sales.items():
            plat = self.PLATFORMS.get(platform.lower())
            if plat:
                revenue = sales * price * plat.royalty_rate
                breakdown[plat.name] = round(revenue, 2)
                total_revenue += revenue
        
        return {
            "total_monthly_revenue": round(total_revenue, 2),
            "platform_breakdown": breakdown,
            "annual_projection": round(total_revenue * 12, 2)
        }
    
    def pricing_optimization(self, word_count: int, genre: str) -> Dict:
        """Suggest optimal pricing"""
        # Genre-based pricing tiers
        genre_prices = {
            "fiction": {"short": 2.99, "novel": 4.99, "epic": 9.99},
            "non_fiction": {"short": 4.99, "standard": 9.99, "premium": 19.99},
            "technical": {"basic": 9.99, "advanced": 29.99, "expert": 49.99},
            "cookbook": {"standard": 9.99, "premium": 19.99},
            "children": {"picture": 4.99, "chapter": 6.99, "ya": 9.99}
        }
        
        suggested = genre_prices.get(genre.lower(), {"standard": 4.99})
        
        # Volume-based adjustment
        if word_count < 10000:
            tier = "short"
        elif word_count < 50000:
            tier = "standard"
        else:
            tier = "premium"
        
        price = suggested.get(tier, list(suggested.values())[0])
        
        return {
            "suggested_price": price,
            "price_range": f"${price * 0.8:.2f} - ${price * 1.2:.2f}",
            "word_count_tier": tier,
            "genre": genre
        }
