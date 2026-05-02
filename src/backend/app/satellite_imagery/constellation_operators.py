"""Satellite Constellation Operators"""
from typing import Dict

class ConstellationOperators:
    """Major commercial imagery providers"""
    
    def maxar(self) -> Dict:
        return {
            "constellation": "WorldView + Legion",
            "resolution_m": 0.3,
            "revisit_days": 1,
            "revenue_annual": 1.8e9,
            "market_share": 0.30,
            "focus": "Defense + Government"
        }
    
    def planet_labs(self) -> Dict:
        return {
            "constellation": "Dove + SkySat",
            "resolution_m": 3,
            "revisit": "Daily global",
            "satellites": 200,
            "revenue_annual": 200e6,
            "market_position": "Daily coverage leader"
        }
    
    def blacksky(self) -> Dict:
        return {
            "constellation": "Gen-3 satellites",
            "resolution_m": 1,
            "unique_value": "Rapid revisit",
            "latency_minutes": 90,
            "pricing": "Competitive"
        }
    
    def emerging_players(self) -> Dict:
        return {
            "spire": {"focus": "AIS + weather", "sats": 100, "data_fusion": True},
            "iceye": {"focus": "SAR radar", "advantage": "All-weather imaging", "resolution_m": 1},
            "capella": {"focus": "SAR", "resolution_m": 0.5, "market": "Defense + Commercial"}
        }
