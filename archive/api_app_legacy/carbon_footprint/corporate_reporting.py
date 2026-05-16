"""Corporate Carbon Reporting"""
from typing import Dict

class CorporateReporting:
    """Scope 1, 2, 3 emissions tracking"""
    
    def scope_definitions(self) -> Dict:
        return {
            "scope_1": {
                "definition": "Direct emissions",
                "sources": ["Fleet", "Facilities", "Manufacturing"],
                "measurement": "Metered/fuel records",
                "cost_to_measure": "Low"
            },
            "scope_2": {
                "definition": "Purchased energy",
                "sources": ["Electricity", "Steam", "Heating"],
                "measurement": "Utility bills + emission factors",
                "cost_to_measure": "Low"
            },
            "scope_3": {
                "definition": "Value chain",
                "sources": ["Suppliers", "Transport", "Product use", "End of life"],
                "measurement": "Estimates, supplier data",
                "cost_to_measure": "High",
                "share_of_total": 0.70
            }
        }
    
    def reporting_frameworks(self) -> Dict:
        return {
            "ghg_protocol": {"adoption": "Universal", "complexity": "Medium", "free": True},
            "gri": {"focus": "Sustainability broadly", "complexity": "High", "cost": "Membership"},
            "sasb": {"focus": "Financial materiality", "sector_specific": True, "cost": "Free"},
            "tcfd": {"focus": "Climate risk", "audience": "Investors", "mandatory_in": ["UK", "EU", "Japan"]}
        }
    
    def software_market(self) -> Dict:
        return {
            "market_size_2024": 1e9,
            "growth_rate": 0.30,
            "major_vendors": ["Persefoni", "Watershed", "Salesforce Net Zero"],
            "average_spend_fortune500_k": 500
        }
    
    def regulatory_mandatory(self) -> Dict:
        return {
            "sec_us": {"scope": "Large public", "phase_in": "2024-2026", "requires": "Scope 1,2 + material 3"},
            "csrd_eu": {"scope": "Large EU companies", "start": 2024, "requires": "Full scope 1,2,3"},
            "california": {"scope": "Revenue > $1B", "start": 2026}
        }
