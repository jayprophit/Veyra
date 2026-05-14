"""Aging Therapeutics Economics"""
from typing import Dict

class AgingTherapeutics:
    """Analyze anti-aging drug development and market"""
    
    def __init__(self, therapy_type: str = "senolytic"):
        self.therapy_type = therapy_type  # senolytic, rapamycin, metformin, NAD+
    
    def market_sizing(self) -> Dict:
        # Global population aging
        population_65_plus = 800e6
        targetable_segment = 0.20  # 20% would consider anti-aging
        
        # Willingness to pay
        annual_willingness = 5000  # $5K per year
        
        tam = population_65_plus * targetable_segment * annual_willingness
        
        therapies = {
            "senolytic": {"penetration": 0.05, "premium": 2.0},
            "rapamycin": {"penetration": 0.10, "premium": 0.5},
            "metformin": {"penetration": 0.15, "premium": 0.2},
            "NAD_plus": {"penetration": 0.08, "premium": 1.0}
        }
        
        t = therapies.get(self.therapy_type, therapies["senolytic"])
        
        return {
            "global_tam_billions": tam / 1e9,
            "therapy_tam_billions": (tam * t["penetration"]) / 1e9,
            "target_population": population_65_plus * targetable_segment,
            "therapy_penetration": t["penetration"],
            "pricing_premium": t["premium"]
        }
    
    def clinical_development(self) -> Dict:
        # Longevity trials are unique - need long duration
        return {
            "trial_duration_years": 5,  # Minimum for aging endpoints
            "cost_per_patient": 50000,   # Higher than typical
            "patients_needed": 3000,     # For mortality endpoints
            "total_trial_cost": 150e6,
            "biomarker_substitutes": ["epigenetic clocks", "frailty indices"],
            "regulatory_pathway": "Aging as indication - still evolving"
        }
    
    def key_companies(self) -> Dict:
        return {
            "unity_biotechnology": {"stage": "Phase 2", "focus": "Senolytics", "market_cap": 100e6},
            "resTORbio": {"stage": "Acquired", "focus": "mTOR inhibitors", "price": 650e6},
            "calico": {"stage": "Private", "focus": "Basic research", "funding": 2.5e9},
            "altos_labs": {"stage": "Private", "focus": "Reprogramming", "funding": 3.0e9},
            "insilico_medicine": {"stage": "Clinical", "focus": "AI-driven", "valuation": 1.0e9}
        }
    
    def reimbursement_analysis(self) -> Dict:
        return {
            "current_status": "Not covered - lifestyle/wellness",
            "future_possibility": "If proven to prevent disease",
            "analog": "Statins for prevention - took decades",
            "value_proposition": "Years of healthy life added",
            "cost_effectiveness_threshold": "$50K per QALY"
        }
