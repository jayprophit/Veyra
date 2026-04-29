"""Platform Licensing - Synbio platform economics"""
from typing import Dict

class PlatformLicensing:
    """Synthetic biology platform licensing"""
    
    def milestone_value(self, upfront: float,
                       milestones: Dict[str, float],
                       royalty_pct: float,
                       peak_sales_estimate: float) -> Dict:
        """Value platform licensing deal"""
        milestone_sum = sum(milestones.values())
        royalty_value = peak_sales_estimate * (royalty_pct / 100) * 5  # 5x multiple
        
        total_value = upfront + milestone_sum + royalty_value
        
        return {
            "upfront": upfront,
            "milestones": milestone_sum,
            "royalty_value": round(royalty_value, 0),
            "total_deal_value": round(total_value, 0),
            "structure": "back_loaded" if milestone_sum > upfront * 2 else "balanced"
        }
    
    def exclusivity_premium(self, territory: str,
                         field: str,
                         base_rate: float) -> Dict:
        """Calculate exclusivity premium"""
        territory_mult = {"global": 3.0, "major": 2.0, "regional": 1.5, "single": 1.0}
        field_mult = {"broad": 2.5, "therapeutic": 1.5, "research": 1.0}
        
        premium = territory_mult.get(territory, 1) * field_mult.get(field, 1)
        adjusted_rate = base_rate * premium
        
        return {
            "exclusivity_premium": round(premium, 1),
            "adjusted_rate": round(adjusted_rate, 3),
            "annual_min": round(adjusted_rate * 1e6, 0)  # Assume $1M base
        }
