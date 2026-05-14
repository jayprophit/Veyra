"""Art Securitization"""
from typing import Dict

class ArtSecuritization:
    def structure_fund(self, portfolio_value: float, num_works: int) -> Dict:
        ltv = 0.40
        advance = portfolio_value * ltv
        return {"advance_amount": advance, "ltv": ltv, "interest_rate": 0.08}
