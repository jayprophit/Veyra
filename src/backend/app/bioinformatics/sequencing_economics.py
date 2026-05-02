"""Sequencing Technology Economics"""
from typing import Dict

class SequencingEconomics:
    """DNA sequencing costs and market"""
    
    def technology_generations(self) -> Dict:
        return {
            "sanger": {
                "cost_per_mb": 1000,
                "read_length": 500,
                "use": "Validation only",
                "era": "Legacy"
            },
            "illumina_ngs": {
                "cost_per_gb": 100,
                "read_length": 150,
                "accuracy": 0.9999,
                "market_share": 0.70,
                "dominance": "Research + clinical"
            },
            "pacbio": {
                "cost_per_gb": 1000,
                "read_length": 10000,
                "advantage": "Long reads",
                "use": "Assembly"
            },
            "ont_nanopore": {
                "cost_per_gb": 200,
                "read_length": "Unlimited",
                "portable": True,
                "accuracy": 0.99
            }
        }
    
    def cost_trajectory(self) -> Dict:
        return {
            "first_human_genome_2001": 3e9,
            "human_genome_2010": 10000,
            "human_genome_2024": 200,
            "target_2030": 100,
            "super_exceeds_moores_law": True,
            "applications_unlocked": "Population genomics"
        }
    
    def market_segments(self) -> Dict:
        return {
            "clinical_diagnostics": {
                "market_2024_b": 15,
                "tests": ["Oncology", "Rare disease", "Prenatal"],
                "reimbursement": "Evolving"
            },
            "research": {
                "market_2024_b": 8,
                "drivers": ["Functional genomics", "Single cell"]
            },
            "direct_to_consumer": {
                "market_2024_b": 1,
                "ancestry": "Mature",
                "health": "Growing but regulated"
            }
        }
    
    def sequencer_vendors(self) -> Dict:
        return {
            "illumina": {"share": 0.70, "focus": "Short read accuracy", "challenges": "Antitrust"},
            "pacbio": {"share": 0.05, "focus": "Long read", "merger": "Completed"},
            "oxford_nanopore": {"share": 0.10, "focus": "Portability", "ip": "Nanopore patents"},
            "mgi": {"share": 0.10, "focus": "Price competition", "origin": "China"}
        }
