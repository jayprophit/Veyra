"""Wealth Transfer"""
from typing import Dict

class WealthTransfer:
    ANNUAL_GIFT_LIMIT = 18000  # 2024
    LIFETIME_GIFT_LIMIT = 13610000
    
    def annual_gifting(self, recipients: int, years: int) -> Dict:
        annual = recipients * self.ANNUAL_GIFT_LIMIT
        total = annual * years
        estate_tax_saved = total * 0.40
        return {"annual_transfers": annual, "total_transferred": total, "estate_tax_saved": estate_tax_saved}
    
    def five_twenty_nine_contribution(self, beneficiaries: int, lump_sum: bool) -> Dict:
        if lump_sum:
            contribution = 5 * self.ANNUAL_GIFT_LIMIT
        else:
            contribution = self.ANNUAL_GIFT_LIMIT
        return {"contribution": contribution, "beneficiaries": beneficiaries, "education_funding": contribution * beneficiaries}
    
    def family_limited_partnership(self, asset_value: float, discount: float) -> Dict:
        discounted_value = asset_value * (1 - discount)
        estate_tax_saved = (asset_value - discounted_value) * 0.40
        return {"asset_value": asset_value, "discounted_value": discounted_value, "estate_tax_saved": estate_tax_saved}
