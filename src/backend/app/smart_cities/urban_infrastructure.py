"""Urban Infrastructure Economics"""
from typing import Dict

class UrbanInfrastructure:
    """Analyze smart city infrastructure investments"""
    
    def __init__(self, city_size: str = "medium"):
        self.city_size = city_size  # small, medium, large, mega
    
    def smart_infrastructure_costs(self) -> Dict:
        populations = {"small": 100000, "medium": 500000, "large": 2000000, "mega": 10000000}
        pop = populations.get(self.city_size, 500000)
        
        # Per capita smart city investment
        per_capita = 1000  # $1000 per resident
        
        components = {
            "iot_sensors": {"per_capita": 100, "coverage": "Street lights, parking, air quality"},
            "smart_grid": {"per_capita": 200, "coverage": "Electricity distribution"},
            "digital_twins": {"per_capita": 150, "coverage": "3D city modeling"},
            "data_centers": {"per_capita": 300, "coverage": "Edge computing infrastructure"},
            "connectivity": {"per_capita": 250, "coverage": "5G, fiber, LoRaWAN"}
        }
        
        total_cost = sum(c["per_capita"] for c in components.values()) * pop
        
        return {
            "total_investment_millions": total_cost / 1e6,
            "per_capita_cost": sum(c["per_capita"] for c in components.values()),
            "population": pop,
            "components": {k: {"cost_millions": v["per_capita"] * pop / 1e6, "coverage": v["coverage"]} for k, v in components.items()}
        }
    
    def roi_calculation(self) -> Dict:
        # Annual benefits
        energy_savings = 20e6  # Smart grid optimization
        traffic_efficiency = 15e6  # Reduced congestion
        maintenance_savings = 10e6  # Predictive maintenance
        service_efficiency = 8e6  # Digital services
        
        total_annual_benefits = energy_savings + traffic_efficiency + maintenance_savings + service_efficiency
        
        investment = self.smart_infrastructure_costs()["total_investment_millions"] * 1e6
        
        return {
            "annual_benefits_millions": total_annual_benefits / 1e6,
            "payback_years": round(investment / total_annual_benefits, 1),
            "twenty_year_npv": round((total_annual_benefits * 20 - investment) / 1e6, 0),
            "benefit_sources": {
                "energy_savings": energy_savings / 1e6,
                "traffic_efficiency": traffic_efficiency / 1e6,
                "maintenance": maintenance_savings / 1e6,
                "service_efficiency": service_efficiency / 1e6
            }
        }
    
    def vendors(self) -> Dict:
        return {
            "cisco": {"focus": "Connectivity", "contracts": "Multiple cities"},
            "siemens": {"focus": "Smart grid", "scale": "Large"},
            "ibm": {"focus": "Data analytics", "approach": "AI-driven"},
            "accenture": {"focus": "Consulting + Implementation", "market": "Premium"},
            "chinese_vendors": {
                "huawei": "Connectivity (restricted in West)",
                "dahua": "Surveillance systems",
                "hikvision": "Security infrastructure"
            }
        }
