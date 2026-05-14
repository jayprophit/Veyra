"""Carbon Credits"""
from typing import Dict

class CarbonCredits:
    def value_credit(self, tonnes: int, vintage: int, standard: str) -> Dict:
        base_price = 50 if standard == "gold" else 30 if standard == "verra" else 20
        age_discount = max(0, (2026 - vintage) * 2)
        price = max(10, base_price - age_discount)
        return {"tonnes": tonnes, "price_per_tonne": price, "total_value": tonnes * price}
