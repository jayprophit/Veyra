"""Digital Valuation - Virtual property appraisal"""
from typing import Dict

class DigitalValuation:
    """Appraise digital properties"""
    
    def appraise(self, property_type: str, metrics: dict) -> Dict:
        """Appraise digital property"""
        if property_type == "website":
            value = metrics.get("monthly_revenue", 0) * 36  # 3x annual
        elif property_type == "domain":
            value = len(metrics.get("name", "")) * 100
        else:
            value = 0
        
        return {
            "property_type": property_type,
            "estimated_value": value,
            "method": "income_approach" if property_type == "website" else "comparable"
        }
