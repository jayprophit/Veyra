"""Virtual Item Trading - Skins, items, digital goods"""
from typing import Dict, List

class VirtualItemTrading:
    """Trade and value virtual items and skins"""
    
    def skin_valuation(self, rarity: str,
                      wear_rating: float,
                      sticker_value: float) -> Dict:
        """Value CS:GO/Valorant skin"""
        rarity_multipliers = {"consumer": 1, "industrial": 2, "milspec": 5, "restricted": 15, "classified": 50, "covert": 200, "contraband": 500}
        base = rarity_multipliers.get(rarity.lower(), 1)
        wear_discount = wear_rating  # 0-1 scale
        value = base * (1 - wear_discount * 0.5) + sticker_value
        return {"base_value": base, "wear_adjusted": base * (1 - wear_discount * 0.5), "total_value": value}
    
    def arbitrage_scanner(self, prices_by_platform: Dict[str, float]) -> Dict:
        """Find arbitrage opportunities across platforms"""
        min_price = min(prices_by_platform.values())
        max_price = max(prices_by_platform.values())
        spread = max_price - min_price
        spread_pct = (spread / min_price) * 100 if min_price > 0 else 0
        return {"min_platform": min(prices_by_platform.items(), key=lambda x: x[1])[0], "max_platform": max(prices_by_platform.items(), key=lambda x: x[1])[0], "spread": spread, "spread_percent": spread_pct, "profitable": spread_pct > 5}
    
    def item_float_analysis(self, float_values: List[float],
                          rarity_tier: str) -> Dict:
        """Analyze item float value distribution"""
        avg_float = sum(float_values) / len(float_values) if float_values else 0
        min_float = min(float_values) if float_values else 0
        max_float = max(float_values) if float_values else 0
        return {"average": avg_float, "range": max_float - min_float, "collectible_potential": min_float < 0.01}
