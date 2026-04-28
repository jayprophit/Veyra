"""Trust Structures"""
from typing import Dict

class TrustStructures:
    def revocable_trust(self, assets: float, beneficiaries: int) -> Dict:
        return {"type": "revocable", "assets": assets, "probate_avoided": True, "beneficiaries": beneficiaries}
    
    def irrevocable_trust(self, assets: float, tax_savings: float) -> Dict:
        return {"type": "irrevocable", "assets": assets, "estate_tax_savings": tax_savings, "asset_protection": True}
    
    def charitable_trust(self, donation: float, years: int) -> Dict:
        tax_benefit = donation * 0.40
        annual_payout = donation / years
        return {"donation": donation, "tax_benefit": tax_benefit, "annual_payout": annual_payout}
