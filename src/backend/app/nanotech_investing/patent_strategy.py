"""Patent Strategy - Nanotech IP navigation"""
from typing import Dict

class PatentStrategy:
    """Patent strategy for nanotech"""
    
    def blocking_patent_analysis(self, competitor_patents: int,
                                 white_space_pct: float,
                                 cross_licensing_options: int) -> Dict:
        """Analyze patent blocking landscape"""
        blocking_risk = competitor_patents * 2
        white_space_value = white_space_pct * 10
        
        freedom_score = white_space_value - blocking_risk + (cross_licensing_options * 5)
        
        return {
            "blocking_risk": blocking_risk,
            "white_space_value": white_space_value,
            "freedom_score": round(freedom_score, 0),
            "strategy": "aggressive_r_and_d" if freedom_score > 50 else "cautious" if freedom_score > 0 else "license_first"
        }
    
    def patent_clustering_value(self, core_patents: int,
                               improvement_patents: int,
                               application_patents: int) -> Dict:
        """Value patent portfolio clustering"""
        # Defensive depth
        total_patents = core_patents + improvement_patents + application_patents
        defensive_depth = improvement_patents / max(core_patents, 1)
        
        # Portfolio value
        base_value = core_patents * 10  # $10M each
        improvement_value = improvement_patents * 2
        application_value = application_patents * 3
        
        return {
            "total_patents": total_patents,
            "defensive_depth": round(defensive_depth, 1),
            "portfolio_value": round(base_value + improvement_value + application_value, 0),
            "strength": "strong" if defensive_depth > 2 else "moderate" if defensive_depth > 1 else "weak"
        }
