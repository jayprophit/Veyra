"""Funeral Economics - Funeral home business analysis"""
from typing import Dict

class FuneralEconomics:
    """Analyze funeral home economics"""
    
    def case_volume_value(self, annual_cases: int,
                         avg_atneed_revenue: float,
                         avg_prenneed_revenue: float,
                         preneed_pct: float) -> Dict:
        """Calculate revenue from case volume"""
        atneed_cases = annual_cases * (1 - preneed_pct / 100)
        preneed_cases = annual_cases * (preneed_pct / 100)
        
        atneed_revenue = atneed_cases * avg_atneed_revenue
        preneed_revenue = preneed_cases * avg_prenneed_revenue
        
        total_revenue = atneed_revenue + preneed_revenue
        
        return {
            "total_cases": annual_cases,
            "atneed_revenue": round(atneed_revenue, 0),
            "preneed_revenue": round(preneed_revenue, 0),
            "total_revenue": round(total_revenue, 0),
            "revenue_per_case": round(total_revenue / annual_cases, 0),
            "preneed_mix": preneed_pct
        }
    
    def cemetery_furniture_ratio(self, funeral_revenue: float,
                                cemetery_revenue: float,
                                target_ratio: float) -> Dict:
        """Analyze funeral home vs cemetery revenue balance"""
        current_ratio = cemetery_revenue / funeral_revenue if funeral_revenue > 0 else 0
        
        return {
            "funeral_revenue": funeral_revenue,
            "cemetery_revenue": cemetery_revenue,
            "current_ratio": round(current_ratio, 2),
            "target_ratio": target_ratio,
            "gap_to_target": round((target_ratio - current_ratio) * funeral_revenue, 0)
        }
