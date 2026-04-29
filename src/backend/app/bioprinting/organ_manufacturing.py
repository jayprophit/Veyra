"""Organ Manufacturing Economics"""
from typing import Dict

class OrganManufacturing:
    """Analyze 3D bioprinting of transplantable organs"""
    
    def __init__(self, organ_type: str = "kidney"):
        self.organ = organ_type  # kidney, liver, heart, skin
    
    def market_opportunity(self) -> Dict:
        organs = {
            "kidney": {"waitlist_us": 90000, "annual_transplants": 25000, "market_value_billions": 25},
            "liver": {"waitlist_us": 11000, "annual_transplants": 9000, "market_value_billions": 10},
            "heart": {"waitlist_us": 3500, "annual_transplants": 3500, "market_value_billions": 8},
            "skin": {"burn_patients_us": 40000, "procedures": 50000, "market_value_billions": 5}
        }
        
        data = organs.get(self.organ, organs["kidney"])
        
        # Price willing to pay (vs dialysis for kidney)
        if self.organ == "kidney":
            annual_dialysis_cost = 90000
            graft_survival_years = 15
            value_of_kidney = annual_dialysis_cost * graft_survival_years
        else:
            value_of_organ = 500000  # General transplant value
        
        return {
            "organ": self.organ,
            "current_waitlist": data["waitlist_us"],
            "annual_transplants": data.get("annual_transplants", data.get("procedures")),
            "market_value_billions": data["market_value_billions"],
            "economic_value_per_organ": value_of_kidney if self.organ == "kidney" else 500000,
            "supply_gap": "Critical shortage - 20% of waitlist dies annually"
        }
    
    def manufacturing_cost(self, scale: str = "pilot") -> Dict:
        # Bioprinting costs (current estimates)
        costs = {
            "research": {"scaffold": 50000, "cells": 30000, "bioreactor": 20000, "labor": 50000},
            "pilot": {"scaffold": 10000, "cells": 5000, "bioreactor": 5000, "labor": 10000},
            "commercial": {"scaffold": 2000, "cells": 1000, "bioreactor": 1000, "labor": 2000}
        }
        
        cost_data = costs.get(scale, costs["pilot"])
        total = sum(cost_data.values())
        
        return {
            "scale": scale,
            "cost_components": cost_data,
            "total_cost": total,
            "vs_transplant_cost": 200000,  # Current transplant
            "premium": "TBD - currently more expensive"
        }
    
    def technology_timeline(self) -> Dict:
        return {
            "current_2024": {
                "capability": "Simple tissues (skin, cartilage)",
                "status": "Clinical trials",
                "complexity": "Limited vascularization"
            },
            "2028_2030": {
                "capability": "Thin organs (cornea, trachea)",
                "status": "First approvals expected",
                "complexity": "Basic vascular networks"
            },
            "2035_2040": {
                "capability": "Solid organs (kidney, liver)",
                "status": "Clinical adoption begins",
                "complexity": "Full vascularization"
            },
            "2045_plus": {
                "capability": "Complex organs (heart, lung)",
                "status": "Standard of care",
                "complexity": "Autonomous function"
            }
        }
    
    def key_players(self) -> Dict:
        return {
            "prellis": {"focus": "Vascularization", "stage": "Series B", "funding": 30e6},
            "collplant": {"focus": "Skin/tissue", "stage": "Public", "valuation": 50e6},
            "united_therapeutics": {"focus": "Lung", "stage": "Clinical", "investment": 100e6},
            "organovo": {"focus": "Liver tissue", "stage": "Public", "valuation": 30e6},
            "academic": {
                "wake_forest": "Bladder, muscle tissue",
                "mgh": "Liver tissue models",
                "eth_zurich": "Heart tissue"
            }
        }
