"""BCI Market Analysis"""
from typing import Dict

class BCIMarket:
    """Brain-computer interface market sizing"""
    
    def market_size(self) -> Dict:
        return {
            "2024": 2.5e9,
            "2028": 7.5e9,
            "2034": 25e9,
            "cagr_10yr": 0.25
        }
    
    def segment_breakdown(self) -> Dict:
        return {
            "medical": {"share": 0.60, "growth": 0.22, "drivers": ["Paralysis", "Epilepsy", "Depression"]},
            "consumer": {"share": 0.25, "growth": 0.35, "drivers": ["Gaming", "Focus enhancement"]},
            "military": {"share": 0.10, "growth": 0.15, "drivers": ["Pilot training", "Drone control"]},
            "research": {"share": 0.05, "growth": 0.12, "drivers": ["Neuroscience", "AI development"]}
        }
    
    def investment_landscape(self) -> Dict:
        return {
            "2023_funding": 800e6,  # $800M
            "2024_funding": 1.2e9,  # $1.2B
            "deal_count": 45,
            "median_round": 25e6,
            "notable_investors": ["Khosla Ventures", "Peter Thiel", "Andreessen Horowitz"]
        }
