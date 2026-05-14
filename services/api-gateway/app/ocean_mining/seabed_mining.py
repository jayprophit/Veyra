"""Seabed Mining Economics"""
from typing import Dict

class SeabedMining:
    """Analyze deep sea mining operations"""
    
    def __init__(self, deposit_type: str = "nodules"):
        self.deposit_type = deposit_type  # nodules, sulfides, crusts
    
    def resource_assessment(self) -> Dict:
        deposits = {
            "nodules": {
                "location": "Clarion-Clipperton Zone",
                "depth_m": 4500,
                "abundance_kg_m2": 15,
                "metals": ["Mn", "Ni", "Cu", "Co"],
                "area_km2": 4000000
            },
            "sulfides": {
                "location": "Mid-ocean ridges",
                "depth_m": 2000,
                "grade_copper": 0.10,
                "grade_zinc": 0.05,
                "grade_gold_gt": 3
            },
            "crusts": {
                "location": "Seamounts",
                "depth_m": 800,
                "thickness_cm": 20,
                "cobalt_grade": 0.005
            }
        }
        return deposits.get(self.deposit_type, deposits["nodules"])
    
    def capex_analysis(self) -> Dict:
        # Mining vessel and equipment
        vessel_cost = 500e6
        mining_equipment = 200e6
        processing_plant = 150e6
        environmental_systems = 50e6
        
        total_capex = vessel_cost + mining_equipment + processing_plant + environmental_systems
        
        return {
            "total_capex_millions": total_capex / 1e6,
            "breakdown": {
                "vessel": vessel_cost / 1e6,
                "mining_equipment": mining_equipment / 1e6,
                "processing": processing_plant / 1e6,
                "environmental": environmental_systems / 1e6
            }
        }
    
    def operating_costs(self, annual_throughput_tons: float = 3000000) -> Dict:
        # $/ton of ore processed
        mining_cost_per_ton = 80
        processing_cost_per_ton = 40
        transport_cost_per_ton = 30
        environmental_monitoring = 20
        
        total_cost_per_ton = mining_cost_per_ton + processing_cost_per_ton + transport_cost_per_ton + environmental_monitoring
        
        annual_opex = annual_throughput_tons * total_cost_per_ton
        
        return {
            "cost_per_ton": total_cost_per_ton,
            "annual_throughput_tons": annual_throughput_tons,
            "annual_opex_millions": annual_opex / 1e6,
            "breakdown_per_ton": {
                "mining": mining_cost_per_ton,
                "processing": processing_cost_per_ton,
                "transport": transport_cost_per_ton,
                "environmental": environmental_monitoring
            }
        }
    
    def metal_revenue(self, nodules_mined_tons: float = 3000000) -> Dict:
        # Nodule composition and prices
        metal_content = {
            "manganese": {"grade": 0.27, "price_per_ton": 2000},
            "nickel": {"grade": 0.013, "price_per_ton": 20000},
            "copper": {"grade": 0.011, "price_per_ton": 9000},
            "cobalt": {"grade": 0.002, "price_per_ton": 50000}
        }
        
        revenues = {}
        total_revenue = 0
        
        for metal, data in metal_content.items():
            recovered_tons = nodules_mined_tons * data["grade"]
            revenue = recovered_tons * data["price_per_ton"]
            revenues[metal] = {
                "recovered_tons": recovered_tons,
                "revenue_millions": revenue / 1e6
            }
            total_revenue += revenue
        
        return {
            "metal_revenues": revenues,
            "total_revenue_millions": total_revenue / 1e6,
            "note": "Based on dry nodule weight and current metal prices"
        }
    
    def environmental_considerations(self) -> Dict:
        return {
            "impacts": [
                "Sediment plume dispersion",
                "Benthic ecosystem disruption",
                "Noise pollution",
                "Light pollution in deep ocean"
            ],
            "mitigation_costs": "5-10% of OPEX",
            "regulatory_status": "ISA developing framework",
            "moratoria": ["Some Pacific nations", "Environmental groups pushing for ban"],
            "monitoring_requirements": "Continuous seabed and water column monitoring"
        }
    
    def key_companies(self) -> Dict:
        return {
            "the_metals_company": {"stage": "Exploration", "contractor": "Nauru", "valuation": 500e6},
            "deepgreen": {"merged_with": "The Metals Company", "focus": "Nodules"},
            "norwegian_ministry": {"stage": "Planning", "focus": "Sulfides", "country": "Norway"},
            "demand": {"stage": "Exploration", "contractor": "Belgium", "focus": "Nodules"},
            "environmental_opposition": "Greenpeace, WWF, some Pacific nations"
        }
