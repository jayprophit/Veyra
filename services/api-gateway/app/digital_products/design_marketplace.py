"""Design Marketplace - Templates, graphics, and digital assets"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DesignAsset:
    name: str
    asset_type: str
    base_price: float
    complexity: str

class DesignMarketplace:
    """Digital design assets marketplace"""
    
    ASSET_TYPES = {
        "logo_template": {"price_range": (5, 50), "popularity": "high"},
        "ui_kit": {"price_range": (20, 200), "popularity": "high"},
        "icon_set": {"price_range": (5, 30), "popularity": "medium"},
        "presentation_template": {"price_range": (10, 100), "popularity": "high"},
        "resume_template": {"price_range": (5, 25), "popularity": "medium"},
        "social_media_pack": {"price_range": (10, 50), "popularity": "high"},
        "business_card": {"price_range": (5, 20), "popularity": "medium"},
        "infographic": {"price_range": (10, 75), "popularity": "medium"},
        "3d_model": {"price_range": (10, 500), "popularity": "low"},
        "font": {"price_range": (15, 100), "popularity": "medium"},
        "mockup": {"price_range": (10, 50), "popularity": "high"},
        "pattern": {"price_range": (5, 25), "popularity": "low"},
    }
    
    PLATFORMS = {
        "creative_market": {"fee": 0.30, "traffic": "high"},
        "envato_elements": {"fee": 0.50, "traffic": "high", "subscription": True},
        "creative_fabrica": {"fee": 0.25, "traffic": "medium"},
        "design_bundles": {"fee": 0.30, "traffic": "medium"},
        "gumroad": {"fee": 0.05, "traffic": "low"},
        "etsy": {"fee": 0.065, "traffic": "medium"},
        "designcuts": {"fee": 0.30, "traffic": "medium"},
        "adobe_stock": {"fee": 0.35, "traffic": "high"},
        "shutterstock": {"fee": 0.30, "traffic": "high"},
    }
    
    def price_asset(self, asset_type: str, complexity: str, 
                   exclusivity: bool = False) -> Dict:
        """Price a design asset"""
        type_data = self.ASSET_TYPES.get(asset_type.lower())
        if not type_data:
            return {"error": "Asset type not found"}
        
        base = sum(type_data["price_range"]) / 2
        
        # Complexity adjustment
        complexity_multipliers = {"simple": 0.7, "standard": 1.0, "complex": 1.5, "premium": 2.0}
        price = base * complexity_multipliers.get(complexity, 1.0)
        
        # Exclusivity premium
        if exclusivity:
            price *= 3
        
        return {
            "asset_type": asset_type,
            "suggested_price": round(price, 0),
            "price_range": type_data["price_range"],
            "complexity": complexity,
            "exclusivity": exclusivity,
            "popularity": type_data["popularity"]
        }
    
    def marketplace_comparison(self, asset_price: float, 
                              monthly_sales: int = 10) -> Dict:
        """Compare marketplace fees and net revenue"""
        results = {}
        
        for name, data in self.PLATFORMS.items():
            gross = asset_price * monthly_sales
            fee = gross * data["fee"]
            net = gross - fee
            
            results[name] = {
                "monthly_gross": round(gross, 2),
                "platform_fees": round(fee, 2),
                "net_revenue": round(net, 2),
                "take_home_pct": round((1 - data["fee"]) * 100, 1),
                "traffic_level": data["traffic"],
                "subscription_based": data.get("subscription", False)
            }
        
        # Best options
        best_net = max(results.items(), key=lambda x: x[1]["net_revenue"])
        best_traffic = [n for n, d in results.items() if d["traffic_level"] == "high"]
        
        return {
            "platforms": results,
            "best_for_revenue": best_net[0],
            "best_for_traffic": best_traffic,
            "recommended_strategy": "List on high-traffic, then migrate to low-fee"
        }
    
    def bundle_pricing(self, items: List[str]) -> Dict:
        """Calculate bundle pricing strategy"""
        individual_total = 0
        for item in items:
            type_data = self.ASSET_TYPES.get(item.lower())
            if type_data:
                individual_total += sum(type_data["price_range"]) / 2
        
        # Bundle discount typically 20-30%
        bundle_price = individual_total * 0.75
        
        return {
            "items_in_bundle": len(items),
            "individual_total": round(individual_total, 2),
            "bundle_price": round(bundle_price, 2),
            "customer_savings_pct": 25,
            "creator_revenue": round(bundle_price * 0.70, 2)  # After platform fee
        }
    
    def license_tiers(self) -> Dict:
        """Define standard license tiers"""
        return {
            "personal": {
                "price_multiplier": 1.0,
                "usage": "Personal projects only",
                "redistribution": False
            },
            "commercial": {
                "price_multiplier": 2.5,
                "usage": "Commercial projects",
                "redistribution": False
            },
            "extended": {
                "price_multiplier": 5.0,
                "usage": "Unlimited commercial",
                "redistribution": True
            },
            "exclusive": {
                "price_multiplier": 10.0,
                "usage": "Full rights transfer",
                "redistribution": True,
                "asset_removed": True
            }
        }
