"""Exploration Valuation - Junior mining project analysis"""
from typing import Dict

class ExplorationValuation:
    """Value exploration-stage mining projects"""
    
    def discovery_valuation(self, acres: int,
                          anomalies: int,
                          commodity: str,
                          jurisdiction: str) -> Dict:
        """Value exploration prospect pre-resource"""
        # Value per acre by jurisdiction and commodity
        base_value_per_acre = 50
        
        commodity_multipliers = {
            "gold": 2.0, "copper": 1.5, "silver": 1.8, "lithium": 3.0, "rare_earth": 2.5
        }
        
        jurisdiction_risk = {
            "canada": 1.0, "australia": 1.0, "nevada": 0.9, "chile": 0.8,
            "drc": 0.4, "russia": 0.5, "china": 0.6
        }
        
        mult = commodity_multipliers.get(commodity, 1.0)
        risk_adj = jurisdiction_risk.get(jurisdiction, 0.7)
        
        value_per_acre = base_value_per_acre * mult * risk_adj
        total_value = acres * value_per_acre * (1 + anomalies * 0.1)
        
        return {
            "acres": acres,
            "anomalies": anomalies,
            "value_per_acre": round(value_per_acre, 0),
            "total_value": round(total_value, 0),
            "discovery_potential": "high" if anomalies > 5 else "medium" if anomalies > 2 else "speculative"
        }
    
    def drill_program_roi(self, meters_planned: int,
                         cost_per_meter: float,
                         discovery_value: float,
                         success_probability: float) -> Dict:
        """Calculate exploration drilling ROI"""
        total_cost = meters_planned * cost_per_meter
        expected_value = discovery_value * success_probability
        roi = ((expected_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        
        return {
            "drill_meters": meters_planned,
            "total_cost": total_cost,
            "expected_value": round(expected_value, 0),
            "roi": round(roi, 1),
            "risk_adjusted_return": "attractive" if roi > 300 else "moderate" if roi > 100 else "speculative"
        }
