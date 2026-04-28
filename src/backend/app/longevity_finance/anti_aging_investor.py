"""Anti-Aging Investor - Investment strategies for longevity"""
from typing import Dict, List

class AntiAgingInvestor:
    """Investment analysis for anti-aging sector"""
    
    def longevity_portfolio_allocation(self, net_worth: float,
                                      risk_tolerance: str) -> Dict:
        """Allocate to longevity investments"""
        allocations = {
            "conservative": {"public_biotech": 0.05, "longevity_etfs": 0.03, "private_vc": 0},
            "moderate": {"public_biotech": 0.08, "longevity_etfs": 0.05, "private_vc": 0.02},
            "aggressive": {"public_biotech": 0.12, "longevity_etfs": 0.08, "private_vc": 0.05}
        }
        
        alloc = allocations.get(risk_tolerance, allocations["moderate"])
        
        return {
            "total_allocation": net_worth * sum(alloc.values()),
            "public_biotech": net_worth * alloc["public_biotech"],
            "longevity_etfs": net_worth * alloc["longevity_etfs"],
            "private_vc": net_worth * alloc["private_vc"],
            "strategy": f"{risk_tolerance} longevity allocation"
        }
    
    def clinical_trial_valuation(self, phase: str,
                               patients_enrolled: int,
                               funding_raised: float) -> Dict:
        """Value company based on clinical trial progress"""
        phase_probabilities = {
            "preclinical": 0.06,
            "phase1": 0.52,
            "phase2": 0.28,
            "phase3": 0.58,
            "approved": 1.0
        }
        
        prob = phase_probabilities.get(phase.lower(), 0.1)
        value_per_patient = funding_raised / patients_enrolled if patients_enrolled > 0 else 0
        implied_valuation = funding_raised / prob if prob > 0 else 0
        
        return {
            "phase": phase,
            "success_probability": prob,
            "patients_enrolled": patients_enrolled,
            "value_per_patient": round(value_per_patient, 0),
            "implied_success_valuation": round(implied_valuation, 0),
            "risk_level": "extreme" if phase == "preclinical" else "high" if phase in ["phase1", "phase2"] else "moderate"
        }
    
    def biomarker_investment_score(self, biomarkers_validated: int,
                                  peer_reviewed_papers: int,
                                  patent_count: int) -> Dict:
        """Score longevity investment opportunity"""
        score = (biomarkers_validated * 10 + 
                peer_reviewed_papers * 2 + 
                patent_count * 5)
        
        return {
            "investment_score": score,
            "grade": "A" if score > 100 else "B" if score > 50 else "C" if score > 20 else "D",
            "recommendation": "strong_buy" if score > 100 else "buy" if score > 50 else "hold" if score > 20 else "avoid",
            "key_strengths": f"{biomarkers_validated} validated biomarkers, {patent_count} patents"
        }
