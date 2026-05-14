"""Satellite Imaging Economics"""
from typing import Dict

class ImagingEconomics:
    """Commercial satellite imagery market"""
    
    def resolution_tiers(self) -> Dict:
        return {
            "very_high": {"resolution_m": 0.3, "price_per_km2": 200, "applications": ["Defense", "Intelligence"]},
            "high": {"resolution_m": 1, "price_per_km2": 50, "applications": ["Urban planning", "Agriculture"]},
            "medium": {"resolution_m": 5, "price_per_km2": 10, "applications": ["Climate", "Forestry"]},
            "low": {"resolution_m": 30, "price_per_km2": 1, "applications": ["Weather", "Broad monitoring"]}
        }
    
    def market_segments(self) -> Dict:
        return {
            "defense_intelligence": {"share": 0.40, "growth": 0.08, "classified_premium": 5},
            "agriculture": {"share": 0.15, "growth": 0.20, "key_metric": "Crop health"},
            "finance_insurance": {"share": 0.10, "growth": 0.25, "use_case": "Alternative data"},
            "environmental": {"share": 0.15, "growth": 0.15, "drivers": ["ESG", "Compliance"]},
            "urban": {"share": 0.20, "growth": 0.12, "applications": ["Construction", "Real estate"]}
        }
    
    def data_pricing_models(self) -> Dict:
        return {
            "tasking": {"price": "Premium", "control": "Direct acquisition", "latency_hours": 24},
            "archive": {"price": "Standard", "control": "Historical only", "latency": "Immediate"},
            "subscription": {"price": "Volume discount", "control": "API access", "commitment": "Annual"},
            "platform": {"price": "Analytics included", "control": "Dashboard", "target": "Non-experts"}
        }
