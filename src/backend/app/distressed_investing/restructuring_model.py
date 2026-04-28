"""Restructuring Model - Debt restructuring analysis"""
from typing import Dict

class RestructuringModel:
    """Model debt restructuring scenarios"""
    
    def exchange_offer(self, face_value: float, current_price: float,
                      new_terms: Dict) -> Dict:
        """Analyze debt exchange offer"""
        current_value = face_value * (current_price / 100)
        
        # New bond value with haircut and extended maturity
        haircut = new_terms.get("haircut", 0.20)
        new_face = face_value * (1 - haircut)
        coupon = new_terms.get("coupon", 0.05)
        maturity = new_terms.get("maturity", 5)
        
        # Simple NPV calculation
        new_value = sum(new_face * coupon / (1.08 ** t) for t in range(1, maturity + 1)) + \
                    new_face / (1.08 ** maturity)
        
        return {
            "current_recovery": current_value,
            "new_recovery": new_value,
            "improvement": round((new_value - current_value) / current_value * 100, 1) if current_value > 0 else 0,
            "acceptance_recommended": new_value > current_value * 1.1
        }
    
    def cramdown_analysis(self, impaired_classes: int, accepting_classes: int) -> Dict:
        """Analyze cramdown feasibility"""
        return {
            "total_classes": impaired_classes,
            "accepting_classes": accepting_classes,
            "acceptance_rate": round(accepting_classes / impaired_classes * 100, 1) if impaired_classes > 0 else 0,
            "cramdown_available": accepting_classes > impaired_classes / 2
        }
