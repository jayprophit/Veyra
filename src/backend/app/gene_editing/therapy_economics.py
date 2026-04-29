"""Therapy Economics - Gene therapy pricing and access"""
from typing import Dict

class TherapyEconomics:
    """Analyze gene therapy economics"""
    
    def one_time_therapy_value(self, cure_probability: float,
                              lifetime_cost_of_care_avoided: float,
                              quality_of_life_improvement: float,
                              therapy_cost: float) -> Dict:
        """Value curative vs chronic therapy"""
        value_created = lifetime_cost_of_care_avoided * cure_probability
        value_created += quality_of_life_improvement * 50000  # QALY value
        
        cost_effectiveness = value_created / therapy_cost if therapy_cost > 0 else 0
        
        return {
            "therapy_cost": therapy_cost,
            "value_created": round(value_created, 0),
            "cost_effectiveness_ratio": round(cost_effectiveness, 2),
            "value_based_price": round(value_created * 0.3, 0),  # 30% capture
            "payer_acceptable": cost_effectiveness > 1.0
        }
    
    def manufacturing_at_scale(self, batch_cost: float,
                              doses_per_batch: int,
                              target_patients: int) -> Dict:
        """Calculate manufacturing scale economics"""
        cost_per_dose = batch_cost / doses_per_batch
        batches_needed = target_patients / doses_per_batch
        total_cost = batches_needed * batch_cost
        
        return {
            "cost_per_dose": round(cost_per_dose, 0),
            "batches_needed": round(batches_needed, 0),
            "total_manufacturing_cost": round(total_cost, 0),
            "economies_of_scale": "achieved" if doses_per_batch > 100 else "developing"
        }
