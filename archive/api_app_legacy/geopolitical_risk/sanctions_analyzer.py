"""Sanctions Analyzer"""
from typing import Dict

class SanctionsAnalyzer:
    def sanction_impact(self, trade_volume_affected: float, alternative_cost: float) -> Dict:
        direct_cost = trade_volume_affected * 0.15
        indirect_cost = trade_volume_affected * 0.10
        return {"total_impact": direct_cost + indirect_cost + alternative_cost}
    
    def compliance_cost(self, entity_count: int, screening_per_entity: float) -> Dict:
        return {"annual_compliance": entity_count * screening_per_entity}
