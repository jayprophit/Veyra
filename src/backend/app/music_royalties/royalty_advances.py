"""Royalty Advances"""
from typing import Dict

class RoyaltyAdvances:
    """Structure royalty advances"""
    
    def advance_structure(self, annual_royalties: float, 
                         advance_multiple: float = 1.5,
                         recoup_rate: float = 0.5) -> Dict:
        """Structure advance deal"""
        advance_amount = annual_royalties * advance_multiple
        years_to_recoup = advance_multiple / recoup_rate
        
        return {
            "advance_amount": advance_amount,
            "annual_royalties": annual_royalties,
            "years_to_recoup": years_to_recoup,
            "recoup_rate": recoup_rate
        }
    
    def buyout_vs_advance(self, catalog_value: float, 
                         advance_amount: float) -> Dict:
        """Compare buyout vs advance"""
        buyout_premium = catalog_value * 0.15
        return {
            "advance_value": advance_amount,
            "buyout_value": catalog_value + buyout_premium,
            "difference": catalog_value + buyout_premium - advance_amount
        }
