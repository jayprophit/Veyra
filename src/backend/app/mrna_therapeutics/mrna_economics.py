"""mRNA Economics"""
from typing import Dict

class MRNAMain:
    """mRNA platform economics"""
    
    def market_overview(self) -> Dict:
        return {
            "market_size_2024": 50e9,
            "covid_vaccines_share": 0.80,
            "therapeutics_share": 0.20,
            "growth_rate": 0.15,
            "projected_2030": 120e9
        }
    
    def platform_comparison(self) -> Dict:
        return {
            "pfizer": {"partner": "BioNTech", "revenue_2023": 12e9, "focus": "Oncology"},
            "moderna": {"revenue_2023": 6e9, "pipeline": 48, "cash": 9e9},
            "curevac": {"status": "Restructuring", "lessons": "Delivery challenges"},
            "sanofi": {"approach": "Self-amplifying mRNA", "target": "Flu, COVID combo"}
        }
    
    def manufacturing_economics(self, batch_size: int = 10000) -> Dict:
        # Cost per dose
        raw_materials = 10
        processing = 5
        fill_finish = 3
        
        cost_per_dose = raw_materials + processing + fill_finish
        
        return {
            "cost_per_dose": cost_per_dose,
            "batch_cost": cost_per_dose * batch_size,
            "facility_capex": 200e6,
            "production_time_days": 60,
            "margin_at_20_price": (20 - cost_per_dose) / 20
        }
