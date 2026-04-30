"""Genetic Testing Economics"""
from typing import Dict

class GeneticTesting:
    """Direct-to-consumer and clinical genetic testing"""
    
    def dtc_market(self) -> Dict:
        return {
            "market_size": 1.5e9,  # $1.5B
            "test_price": 199,
            "cost_to_company": 50,
            "gross_margin": 0.75,
            "market_leaders": ["23andMe", "Ancestry", "MyHeritage"],
            "growth_rate": 0.15,
            "challenges": "Privacy concerns, regulatory scrutiny"
        }
    
    def clinical_testing(self, test_type: str = "cancer_panel") -> Dict:
        tests = {
            "cancer_panel": {"cost": 3000, "reimbursement": 2500, "turnaround": "14 days"},
            "rare_disease": {"cost": 5000, "reimbursement": 4000, "turnaround": "30 days"},
            "pharmacogenomics": {"cost": 500, "reimbursement": 400, "turnaround": "7 days"},
            "prenatal": {"cost": 1000, "reimbursement": 800, "turnaround": "10 days"}
        }
        return tests.get(test_type, tests["cancer_panel"])
    
    def value_chain(self) -> Dict:
        return {
            "sample_collection": {"margin": 0.20, "players": "Clinics, DTC kits"},
            "sequencing": {"margin": 0.40, "players": "Illumina, PacBio"},
            "analysis": {"margin": 0.30, "players": "Bioinformatics companies"},
            "interpretation": {"margin": 0.50, "players": "Invitae, Myriad"},
            "counseling": {"margin": 0.60, "players": "Genetic counselors"}
        }
