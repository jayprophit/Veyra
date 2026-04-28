"""Bullion Analyzer - Physical precious metals analysis"""
from typing import Dict

class BullionAnalyzer:
    """Analyze physical bullion investments"""
    
    def gold_silver_ratio(self, gold_price: float, silver_price: float) -> Dict:
        """Calculate gold/silver ratio for trading"""
        ratio = gold_price / silver_price if silver_price > 0 else 0
        historical_mean = 65
        
        return {
            "ratio": round(ratio, 2),
            "historical_mean": historical_mean,
            "deviation": round(ratio - historical_mean, 2),
            "signal": "buy_silver" if ratio > 80 else "buy_gold" if ratio < 40 else "neutral",
            "percentile": "high" if ratio > 80 else "low" if ratio < 40 else "normal"
        }
    
    def bullion_premium(self, spot_price: float, dealer_price: float, metal_type: str) -> Dict:
        """Calculate bullion premium over spot"""
        premium = dealer_price - spot_price
        premium_pct = (premium / spot_price) * 100 if spot_price > 0 else 0
        
        typical_premiums = {"gold": 3.0, "silver": 15.0, "platinum": 5.0, "palladium": 4.0}
        typical = typical_premiums.get(metal_type, 5.0)
        
        return {
            "spot_price": spot_price,
            "dealer_price": dealer_price,
            "premium_amount": round(premium, 2),
            "premium_percent": round(premium_pct, 2),
            "typical_premium": typical,
            "expensive": premium_pct > typical * 1.5
        }
    
    def numismatic_valuation(self, metal_value: float, rarity_score: float, condition: str) -> Dict:
        """Value collectible coins"""
        multipliers = {"poor": 1.1, "fair": 1.3, "good": 1.6, "fine": 2.0, "uncirculated": 3.0, "proof": 5.0}
        condition_mult = multipliers.get(condition.lower(), 1.0)
        
        numismatic_value = metal_value * condition_mult * (1 + rarity_score / 100)
        
        return {
            "metal_value": metal_value,
            "numismatic_value": round(numismatic_value, 2),
            "premium_over_metal": round((numismatic_value / metal_value - 1) * 100, 1),
            "collectible_grade": condition,
            "investment_type": "numismatic" if rarity_score > 50 else "bullion"
        }
