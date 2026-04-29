"""Patent Landscape - CRISPR and gene editing IP"""
from typing import Dict, List

class PatentLandscape:
    """Analyze gene editing patent landscape"""
    
    def freedom_to_operate(self, patents_blocking: int,
                          licensing_options: List[str],
                          geography: str) -> Dict:
        """Assess freedom to operate risk"""
        risk_score = patents_blocking * 10
        risk_score -= len(licensing_options) * 5
        
        # Geography factor
        geo_mult = {"us": 1.0, "eu": 0.9, "china": 1.2, "row": 0.7}
        risk_score *= geo_mult.get(geography, 1.0)
        
        return {
            "blocking_patents": patents_blocking,
            "licensing_options": len(licensing_options),
            "risk_score": round(risk_score, 0),
            "fto_status": "clear" if risk_score < 20 else "moderate" if risk_score < 50 else "high_risk",
            "strategy": "license" if risk_score > 30 else "design_around" if risk_score > 15 else "proceed"
        }
    
    def patent_thicket_nav(self, broad_patents: int,
                          narrow_patents: int,
                          patent_age_avg: float) -> Dict:
        """Navigate dense patent thickets"""
        # Older patents approaching expiry = opportunity
        expiry_window = 20 - patent_age_avg
        opportunity_score = max(0, expiry_window * 5)
        
        density = broad_patents + narrow_patents * 0.3
        
        return {
            "patent_density": round(density, 1),
            "expiry_opportunity": round(opportunity_score, 1),
            "avg_patent_age": patent_age_avg,
            "strategy": "wait_for_expiry" if opportunity_score > 30 else "license_or_design"
        }
