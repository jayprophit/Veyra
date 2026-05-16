"""Immersive Hardware Market"""
from typing import Dict

class ImmersiveHardware:
    """VR/AR headset market economics"""
    
    def market_overview(self) -> Dict:
        return {
            "vr_market_2024": 15e9,
            "ar_market_2024": 8e9,
            "combined_2030": 100e9,
            "units_shipped_2024": 15e6,
            "average_selling_price": 450
        }
    
    def vendor_comparison(self) -> Dict:
        return {
            "meta": {
                "market_share": 0.60,
                "products": ["Quest 2", "Quest 3", "Quest Pro"],
                "strategy": "Subsidized hardware",
                "loss_per_unit": 200
            },
            "apple": {
                "market_share": 0.05,
                "product": "Vision Pro",
                "strategy": "Premium margin",
                "margin": 1500
            },
            "pico": {
                "market_share": 0.15,
                "owner": "ByteDance",
                "focus": "China and enterprise"
            }
        }
    
    byod_policy = {
        "enterprise_adoption": 0.25,
        "training_use_cases": ["Safety", "Medical", "Technical"],
        "roi_metrics": ["Reduced accidents", "Faster onboarding", "Remote expertise"]
    }
