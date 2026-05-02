"""Metal 3D Printing Economics"""
from typing import Dict

class MetalPrinting:
    """Additive manufacturing metals"""
    
    def technology_types(self) -> Dict:
        return {
            "laser_powder_bed": {
                "accuracy_mm": 0.05,
                "materials": ["Ti", "Al", "Ni", "CoCr"],
                "cost_per_kg": 500,
                "build_rate": "Moderate",
                "leader": "EOS, SLM Solutions"
            },
            "electron_beam": {
                "advantage": "No residual stress",
                "materials": ["Ti primarily"],
                "cost_per_kg": 400,
                "build_rate": "Fast",
                "leader": "Arcam (GE)"
            },
            "binder_jet": {
                "advantage": "Speed, lower cost",
                "post_process": "Sintering required",
                "cost_per_kg": 200,
                "growth": "Fastest"
            }
        }
    
    def applications(self) -> Dict:
        return {
            "aerospace": {"value_prop": "Weight reduction", "certification": "Challenging", "growth": 0.25},
            "medical_implants": {"value_prop": "Custom geometry", "margin": "High", "market": 2e9},
            "automotive": {"value_prop": "Consolidation", "volume": "Growing", "cost_target": 50}
        }
    
    def cost_trajectory(self) -> Dict:
        return {
            "current_premium_vs_subtractive": 10,
            "target_2030": 2,
            "drivers": ["Speed", "Powder cost reduction", "Automation"]
        }
