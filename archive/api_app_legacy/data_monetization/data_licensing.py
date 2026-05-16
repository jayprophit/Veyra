"""Data Licensing"""
from typing import Dict

class DataLicensing:
    """Data licensing and valuation"""
    
    def license_value(self, records: int, uniqueness: float, refresh_freq: str) -> Dict:
        """Calculate data license value"""
        base_per_record = 0.01
        refresh_multiplier = {"realtime": 5, "daily": 2, "weekly": 1, "monthly": 0.5}
        
        value = records * base_per_record * uniqueness * refresh_multiplier.get(refresh_freq, 1)
        return {"annual_value": value, "per_record": base_per_record * uniqueness}
    
    def tiered_pricing(self, usage_tiers: Dict[str, int]) -> Dict:
        """Create tiered pricing structure"""
        tiers = {}
        for tier, calls in usage_tiers.items():
            price_per_call = max(0.001, 1000 / calls) if calls > 0 else 0.01
            tiers[tier] = {"calls": calls, "price_per_call": round(price_per_call, 4)}
        return tiers
