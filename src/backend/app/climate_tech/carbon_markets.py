"""Carbon Markets Economics"""
from typing import Dict

class CarbonMarkets:
    """Voluntary and compliance carbon trading"""
    
    def market_overview(self) -> Dict:
        return {
            "compliance_market_2024": 300e9,
            "voluntary_market_2024": 2e9,
            "voluntary_2030": 50e9,
            "major_exchanges": ["EU ETS", "California", "RGGI", "UK ETS"],
            "price_range_per_ton": (5, 100)
        }
    
    def credit_types(self) -> Dict:
        return {
            "avoidance": {
                "examples": ["Renewable energy", "Efficiency"],
                "price_per_ton": 5,
                "controversy": "Additionality concerns"
            },
            "removal": {
                "examples": ["DAC", "Reforestation", "Soil carbon"],
                "price_per_ton": 100,
                "quality": "Higher permanence"
            },
            "nature_based": {
                "examples": ["Mangroves", "Forests"],
                "price_per_ton": 15,
                "risk": "Reversal risk"
            }
        }
    
    def trading_volume(self) -> Dict:
        return {
            "eu_ets_annual": 15e9,  # EU allowance units
            "futures_volume_daily": 500e6,
            "speculator_participation": 0.30,
            "corporate_hedging": 0.70
        }
