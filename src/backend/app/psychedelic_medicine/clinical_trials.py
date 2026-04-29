"""Psychedelic Clinical Trials Analysis"""
from typing import Dict

class PsychedelicTrials:
    """Analyze psychedelic medicine companies and trials"""
    
    def __init__(self, compound: str = "psilocybin", indication: str = "depression"):
        self.compound = compound  # psilocybin, MDMA, ketamine, LSD, DMT
        self.indication = indication
    
    def market_opportunity(self) -> Dict:
        # TAM for mental health conditions
        markets = {
            "depression": {"patients_us": 17e6, "annual_cost": 10000, "market_size": 170e9},
            "ptsd": {"patients_us": 9e6, "annual_cost": 12000, "market_size": 108e9},
            "anxiety": {"patients_us": 40e6, "annual_cost": 8000, "market_size": 320e9},
            "addiction": {"patients_us": 20e6, "annual_cost": 15000, "market_size": 300e9}
        }
        
        market = markets.get(self.indication, markets["depression"])
        
        # Addressable with psychedelics (treatment-resistant portion)
        addressable_pct = 30 if self.indication == "depression" else 40
        
        return {
            "total_patients_us": round(market["patients_us"] / 1e6, 1),
            "treatment_resistant_pct": addressable_pct,
            "addressable_patients": round(market["patients_us"] * addressable_pct / 100 / 1e6, 1),
            "tam_billions": round(market["market_size"] / 1e9, 1),
            "serviceable_tam": round(market["market_size"] * addressable_pct / 100 / 1e9, 1)
        }
    
    def development_costs(self, phase: str = "phase2") -> Dict:
        costs = {
            "phase1": 5e6,
            "phase2": 25e6,
            "phase3": 100e6,
            "approval": 10e6
        }
        
        durations = {
            "phase1": 1,
            "phase2": 2,
            "phase3": 3,
            "approval": 1
        }
        
        return {
            "cost": costs.get(phase, 25e6),
            "duration_years": durations.get(phase, 2),
            "total_to_approval": 140e6,
            "timeline_to_approval": 7
        }
    
    def competitive_landscape(self) -> Dict:
        companies = {
            "psilocybin": ["COMPASS Pathways", "Usona Institute", "Johns Hopkins"],
            "MDMA": ["MAPS", "MindMed"],
            "ketamine": ["Johnson & Johnson", "MindMed", "Field Trip"],
            "DMT": ["Small Pharma", "Entheon"]
        }
        
        return {
            "leaders": companies.get(self.compound, ["Various"]),
            "total_companies": 50,
            "total_funding_raised": 3.5e9,
            "regulatory_status": "FDA Breakthrough Therapy (MDMA 2024, Psilocybin TBD)"
        }
    
    def therapy_economics(self, sessions: int = 3, price_per_session: float = 1500) -> Dict:
        # Psychedelic-assisted therapy model
        drug_cost = 500
        therapy_cost = sessions * price_per_session
        monitoring_cost = 500
        
        total_treatment = drug_cost + therapy_cost + monitoring_cost
        
        # Compare to standard of care
        standard_annual = 12000  # SSRIs + therapy
        
        return {
            "total_treatment_cost": total_treatment,
            "sessions_required": sessions,
            "cost_per_session": price_per_session,
            "vs_standard_of_care": round(total_treatment - standard_annual, 0),
            "savings_if_durable": round(standard_annual * 2 - total_treatment, 0)  # If lasts 2 years
        }
