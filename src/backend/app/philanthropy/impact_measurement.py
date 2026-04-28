"""Impact Measurement"""
from typing import Dict

class ImpactMeasurement:
    def sroi_calculation(self, social_outcomes: float, investment: float) -> Dict:
        sroi = social_outcomes / investment if investment > 0 else 0
        return {"social_return": social_outcomes, "investment": investment, "sroi": round(sroi, 2)}
    
    def lives_touched(self, program_budget: float, cost_per_beneficiary: float) -> Dict:
        beneficiaries = program_budget / cost_per_beneficiary if cost_per_beneficiary > 0 else 0
        return {"budget": program_budget, "cost_per": cost_per_beneficiary, "beneficiaries": int(beneficiaries)}
    
    def esg_alignment(self, charity_mission: str, donor_priorities: list) -> Dict:
        matches = sum(1 for p in donor_priorities if p.lower() in charity_mission.lower())
        alignment = matches / len(donor_priorities) if donor_priorities else 0
        return {"alignment_score": round(alignment * 100, 1), "matches": matches}
