"""DNA Sequencing Economics"""
from typing import Dict

class SequencingEconomics:
    """Analyze genome sequencing costs and markets"""
    
    def __init__(self, sequencing_type: str = "ngs"):
        self.seq_type = sequencing_type  # ngs, long_read, single_cell
    
    def cost_per_genome(self) -> Dict:
        costs = {
            "ngs": {"cost": 200, "time": "24 hours", "accuracy": 0.9999},
            "long_read": {"cost": 1000, "time": "48 hours", "accuracy": 0.9995},
            "single_cell": {"cost": 5000, "time": "72 hours", "accuracy": 0.999}
        }
        return costs.get(self.seq_type, costs["ngs"])
    
    def market_size(self) -> Dict:
        return {
            "clinical_sequencing": 15e9,  # $15B
            "research": 8e9,
            "consumer": 2e9,
            "agricultural": 3e9,
            "total_2024": 28e9,
            "cagr": 0.18,
            "projected_2030": 75e9
        }
    
    def illumina_dominance(self) -> Dict:
        return {
            "market_share": 0.80,
            "instrument_cost": 1000000,  # $1M per sequencer
            "reagent_revenue_annual": 3e9,
            "gross_margin": 0.70,
            "competition": "PacBio, Oxford Nanopore gaining share"
        }
