"""Stage Gate - VC stage progression"""
from typing import Dict

class StageGate:
    """VC stage-gate progression analysis"""
    
    def series_valuation(self, revenue: float, growth_rate: float, stage: str) -> Dict:
        """Calculate series-stage valuation"""
        multiples = {"seed": 3, "series_a": 8, "series_b": 12, "series_c": 15, "pre_ipo": 20}
        base = multiples.get(stage.lower(), 10)
        premium = min(growth_rate * 10, 5)
        final = base + premium
        
        return {
            "stage": stage,
            "valuation": round(revenue * final, 0),
            "multiple": round(final, 1),
            "check_size": round(revenue * final * 0.25, 0)
        }
    
    def dilution_path(self, current_ownership: float, stages_remaining: int) -> Dict:
        """Project ownership dilution"""
        final = current_ownership * (0.8 ** stages_remaining)
        return {
            "current": round(current_ownership * 100, 2),
            "final": round(final * 100, 2),
            "dilution": round((current_ownership - final) * 100, 2)
        }
