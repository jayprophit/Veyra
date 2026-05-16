"""Fermentation Economics - Biomanufacturing costs"""
from typing import Dict

class FermentationEconomics:
    """Fermentation manufacturing economics"""
    
    def cost_per_kg(self, bioreactor_volume: float,
                   titer_g_per_l: float,
                   batch_days: float,
                   media_cost_per_l: float) -> Dict:
        """Calculate production cost per kg"""
        grams_per_batch = bioreactor_volume * titer_g_per_l
        kg_per_batch = grams_per_batch / 1000
        batches_per_year = 365 / batch_days
        
        media_cost = media_cost_per_l * bioreactor_volume * batches_per_year
        facility_annual = 500000  # Fixed cost assumption
        
        total_cost = media_cost + facility_annual
        annual_kg = kg_per_batch * batches_per_year
        
        cost_per_kg = total_cost / annual_kg if annual_kg > 0 else 0
        
        return {
            "annual_kg": round(annual_kg, 0),
            "cost_per_kg": round(cost_per_kg, 0),
            "competitive": cost_per_kg < 100
        }
    
    def scale_up_factor(self, lab_titer: float,
                       pilot_titer: float,
                       production_titer: float) -> Dict:
        """Analyze scale-up success"""
        pilot_factor = pilot_titer / lab_titer if lab_titer > 0 else 0
        production_factor = production_titer / pilot_titer if pilot_titer > 0 else 0
        
        return {
            "pilot_scale_factor": round(pilot_factor, 2),
            "production_scale_factor": round(production_factor, 2),
            "scale_up_success": production_factor > 0.7,
            "risk_level": "low" if production_factor > 0.8 else "medium" if production_factor > 0.5 else "high"
        }
