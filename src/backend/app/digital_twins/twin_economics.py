"""Digital Twin Economics"""
from typing import Dict

class TwinEconomics:
    """Digital twin market and ROI"""
    
    def market_size(self) -> Dict:
        return {
            "market_2024": 10e9,
            "market_2030": 75e9,
            "cagr": 0.40,
            "by_industry": {
                "manufacturing": 0.35,
                "energy": 0.25,
                "healthcare": 0.15,
                "automotive": 0.15,
                "others": 0.10
            }
        }
    
    def roi_analysis(self, implementation_cost: float = 1e6) -> Dict:
        savings = {
            "downtime_reduction": 500000,
            "maintenance_optimization": 300000,
            "energy_efficiency": 200000,
            "quality_improvement": 150000
        }
        
        total_annual_savings = sum(savings.values())
        
        return {
            "implementation_cost": implementation_cost,
            "annual_savings": total_annual_savings,
            "roi_percent": round((total_annual_savings / implementation_cost) * 100, 0),
            "payback_months": round((implementation_cost / total_annual_savings) * 12, 0),
            "breakdown": savings
        }
    
    def technology_stack(self) -> Dict:
        return {
            "platforms": ["Siemens Xcelerator", "GE Digital", "Azure Digital Twins", "AWS IoT TwinMaker"],
            "enabling_tech": ["IoT sensors", "AI/ML", "Cloud computing", "5G connectivity"],
            "integration_cost": "30-50% of total project"
        }
