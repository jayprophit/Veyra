"""Art Valuation"""
from typing import Dict

class ArtValuation:
    def value_artwork(self, artist: str, year: int, medium: str, size_sqft: float) -> Dict:
        base_values = {"picasso": 10e6, "basquiat": 15e6, "warhol": 8e6, "unknown": 50000}
        base = base_values.get(artist.lower(), 100000)
        age_premium = max(0, (2026 - year) * 0.02 * base)
        size_adj = size_sqft * 10000
        return {"estimated_value": base + age_premium + size_adj, "confidence": "medium"}
