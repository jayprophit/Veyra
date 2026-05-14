"""Catalog Valuation - Music royalty catalog analysis"""
from typing import Dict

class CatalogValuation:
    """Value music royalty catalogs"""
    
    def dcf_valuation(self, annual_royalties: float,
                      growth_rate: float,
                      decay_rate: float,
                      discount_rate: float = 0.10) -> Dict:
        """DCF valuation for music catalog"""
        # Music catalogs decay over time but can have long tails
        cash_flows = []
        for year in range(1, 21):  # 20 years
            decay_factor = (1 - decay_rate) ** year
            growth_factor = (1 + growth_rate) ** year
            annual = annual_royalties * decay_factor * growth_factor
            cash_flows.append(annual)
        
        npv = sum(cf / ((1 + discount_rate) ** (i+1)) for i, cf in enumerate(cash_flows))
        
        return {
            "annual_royalties": annual_royalties,
            "catalog_value": round(npv, 0),
            "multiple": round(npv / annual_royalties, 1),
            "yield_on_cost": round(annual_royalties / npv * 100, 2),
            "decay_adjusted": True
        }
    
    def streaming_multiple(self, streams_last_12m: int,
                         avg_stream_rate: float,
                          catalog_age_years: int) -> Dict:
        """Value based on streaming data"""
        annual_royalties = streams_last_12m * avg_stream_rate
        
        # Age adjustment - newer catalogs worth more
        age_discount = max(0.5, 1 - (catalog_age_years * 0.02))
        adjusted_royalties = annual_royalties * age_discount
        
        # Multiple based on catalog type
        catalog_multiple = 12 if catalog_age_years < 5 else 8 if catalog_age_years < 15 else 5
        
        return {
            "annual_streams": streams_last_12m,
            "annual_royalties": round(annual_royalties, 0),
            "adjusted_royalties": round(adjusted_royalties, 0),
            "catalog_value": round(adjusted_royalties * catalog_multiple, 0),
            "multiple": catalog_multiple,
            "per_stream_value": round(adjusted_royalties * catalog_multiple / streams_last_12m, 4)
        }
    
    def hit_song_premium(self, base_value: float,
                        billboard_weeks: int,
                        grammy_nominations: int,
                        sync_licenses: int) -> Dict:
        """Calculate premium for hit songs"""
        billboard_premium = min(billboard_weeks * 0.02, 0.5)  # Max 50%
        grammy_premium = grammy_nominations * 0.15
        sync_premium = min(sync_licenses * 0.03, 0.3)
        
        total_premium = billboard_premium + grammy_premium + sync_premium
        adjusted_value = base_value * (1 + total_premium)
        
        return {
            "base_value": base_value,
            "premium_percent": round(total_premium * 100, 1),
            "adjusted_value": round(adjusted_value, 0),
            "premiums": {
                "billboard": round(billboard_premium * 100, 1),
                "grammy": round(grammy_premium * 100, 1),
                "sync": round(sync_premium * 100, 1)
            }
        }
