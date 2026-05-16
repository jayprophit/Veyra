"""Cultured Meat Market Analysis"""
from typing import Dict

class MarketOutlook:
    """Market sizing and adoption"""
    
    def market_size(self) -> Dict:
        return {
            "global_meat_market": 1.4e12,  # $1.4T
            "addressable_millions": 50,
            "2030_projection": 25e9,
            "2050_projection": 500e9,
            "penetration_rate_2030": 0.02
        }
    
    def consumer_adoption(self) -> Dict:
        return {
            "willing_to_try": 0.45,
            "regular_buyers": 0.15,
            "price_premium_acceptable": 0.20,
            "main_concerns": ["Price", "Taste", "Naturalness"],
            "early_adopters": ["Flexitarians", "Environmentally conscious"]
        }
    
    def regulatory_status(self) -> Dict:
        return {
            "singapore": {"status": "Approved", "products": ["Chicken"]},
            "usa": {"status": "FDA cleared, USDA pending", "timeline": "2024-2025"},
            "eu": {"status": "Novel food approval", "timeline": "2025+"},
            "israel": {"status": "Approved", "products": ["Beef"]}
        }
