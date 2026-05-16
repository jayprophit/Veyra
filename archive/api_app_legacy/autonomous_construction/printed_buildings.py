"""3D Printed Building Economics"""
from typing import Dict

class PrintedBuildings:
    """Additive manufacturing of structures"""
    
    def technology_types(self) -> Dict:
        return {
            "gantry_based": {
                "scale": "Large",
                "material": "Concrete",
                "speed_m3_hour": 10,
                "building_size": "Unlimited",
                "examples": ["COBOD", "ICON", "PERI"]
            },
            "robotic_arm": {
                "scale": "Medium",
                "material": "Concrete/clay",
                "speed_m3_hour": 2,
                "building_size": "Limited reach",
                "examples": ["WASP", "SQ4D"]
            },
            "swarm_printing": {
                "scale": "Distributed",
                "material": "Various",
                "status": "Research",
                "advantage": "Complex geometries"
            }
        }
    
    def cost_analysis(self, building_m2: int = 100) -> Dict:
        return {
            "materials_per_m2": 200,
            "labor_per_m2": 50,  # Reduced from 150
            "equipment_depreciation_per_m2": 30,
            "total_cost_per_m2": 280,
            "vs_traditional_per_m2": 350,
            "savings_pct": 20,
            "speed_days": 30,  # vs 120 traditional
            "waste_reduction_pct": 60
        }
    
    def completed_projects(self) -> Dict:
        return {
            "icon_community": {"location": "Texas", "units": 100, "cost_reduction": 0.30},
            "dubai_office": {"floors": 2, "printed_pct": 0.80, "certification": "Obtained"},
            "low_income_housing": {"countries": ["Mexico", "Kenya"], "cost_per_unit": 4000}
        }
    
    def barriers_to_scale(self) -> Dict:
        return {
            "codes_standards": {"status": "Evolving", "approval_timeline": "2+ years per region"},
            "material_certification": {"concrete": "Available", "novel_materials": "Limited"},
            "financing": {"mortgage_eligibility": "Challenging", "insurance": "Developing"}
        }
