"""Family Governance"""
from typing import Dict

class FamilyGovernance:
    def family_constitution(self, family_members: int, assets: float) -> Dict:
        return {"members": family_members, "assets": assets, "governance_required": family_members > 5}
    
    def next_gen_education(self, heirs: int, education_budget: float) -> Dict:
        per_heir = education_budget / heirs if heirs > 0 else 0
        return {"heirs": heirs, "budget": education_budget, "per_heir": per_heir}
    
    def family_council(self, voting_members: int, decision_threshold: float) -> Dict:
        votes_needed = int(voting_members * decision_threshold)
        return {"members": voting_members, "threshold": decision_threshold, "votes_needed": votes_needed}
