"""Royalty Streaming - Precious metals royalty companies"""
from typing import Dict

class RoyaltyStreaming:
    """Analyze royalty and streaming companies"""
    
    def nsr_valuation(self, nsr_pct: float,  # Net Smelter Return %
                     mine_production: float,
                     commodity_price: float,
                     mine_life: int) -> Dict:
        """Value net smelter return royalty"""
        annual_royalty = mine_production * commodity_price * (nsr_pct / 100)
        
        # NPV at 5% discount
        npv = sum(annual_royalty / (1.05 ** year) for year in range(1, mine_life + 1))
        
        return {
            "nsr_percentage": nsr_pct,
            "annual_royalty": round(annual_royalty, 0),
            "royalty_npv": round(npv, 0),
            "multiple_attached": round(npv / annual_royalty, 1) if annual_royalty > 0 else 0,
            "risk_profile": "low_operational_no_capex"
        }
    
    def streaming_premium(self, upfront_payment: float,
                         ongoing_per_oz: float,
                         production_oz: float,
                         spot_price: float) -> Dict:
        """Calculate streaming agreement economics"""
        # Streaming company buys at ongoing_per_oz, sells at spot
        margin_per_oz = spot_price - ongoing_per_oz
        total_margin = margin_per_oz * production_oz
        
        # ROI on upfront
        years_to_payback = upfront_payment / total_margin if total_margin > 0 else 999
        
        return {
            "upfront_payment": upfront_payment,
            "purchase_price_per_oz": ongoing_per_oz,
            "spot_price": spot_price,
            "margin_per_oz": round(margin_per_oz, 0),
            "total_margin": round(total_margin, 0),
            "years_to_payback": round(years_to_payback, 1),
            "streaming_premium": round((spot_price - ongoing_per_oz) / spot_price * 100, 1)
        }
