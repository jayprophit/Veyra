"""CAR-T Cell Therapy Economics"""
from typing import Dict

class CARTEconomics:
    """Analyze CAR-T therapy costs, pricing, and market dynamics"""
    
    def __init__(self, indication: str = "large_b_cell_lymphoma"):
        self.indication = indication
        self.approved_therapies = {
            "kymriah": {"price": 475000, "indications": ["ALL", "DLBCL"]},
            "yescarta": {"price": 373000, "indications": ["DLBCL", "PMBCL"]},
            "breyanzi": {"price": 410000, "indications": ["DLBCL"]},
            "tecartus": {"price": 373000, "indications": ["MCL", "ALL"]}
        }
    
    def treatment_cost(self) -> Dict:
        drug_price = 400000  # Average
        hospitalization = 25000
        monitoring = 15000
        adverse_event_mgmt = 35000
        
        total = drug_price + hospitalization + monitoring + adverse_event_mgmt
        
        return {
            "drug_acquisition": drug_price,
            "hospitalization": hospitalization,
            "monitoring": monitoring,
            "ae_management": adverse_event_mgmt,
            "total_cost": total,
            "one_time_treatment": True
        }
    
    def manufacturer_economics(self, patients_treated_annual: int = 1000) -> Dict:
        cost_components = {
            "vector_production": 50000,
            "cell_processing": 25000,
            "qc_testing": 15000,
            "logistics": 10000,
            "overhead_allocation": 20000
        }
        
        cogs_per_patient = sum(cost_components.values())
        price = 400000
        gross_margin = price - cogs_per_patient
        
        annual_revenue = patients_treated_annual * price
        annual_cogs = patients_treated_annual * cogs_per_patient
        
        # R&D and SG&A
        rd_pct = 0.35
        sga_pct = 0.25
        
        rd = annual_revenue * rd_pct
        sga = annual_revenue * sga_pct
        
        ebitda = annual_revenue - annual_cogs - rd - sga
        ebitda_margin = ebitda / annual_revenue if annual_revenue > 0 else 0
        
        return {
            "cogs_per_patient": cogs_per_patient,
            "gross_margin_per_patient": gross_margin,
            "gross_margin_pct": round(gross_margin / price * 100, 1),
            "annual_revenue_millions": round(annual_revenue / 1e6, 1),
            "ebitda_millions": round(ebitda / 1e6, 1),
            "ebitda_margin_pct": round(ebitda_margin * 100, 1),
            "patients_for_breakeven": 5000  # R&D recovery
        }
    
    def market_sizing(self, addressable_population: int = 10000) -> Dict:
        eligible_pct = 0.70  # Eligible for CAR-T
        treatment_rate = 0.40  # Actually get treated
        
        eligible = addressable_population * eligible_pct
        treated = eligible * treatment_rate
        
        price = 400000
        market_value = treated * price
        
        return {
            "addressable_population": addressable_population,
            "eligible_patients": int(eligible),
            "treated_patients": int(treated),
            "market_value_millions": round(market_value / 1e6, 1),
            "penetration_rate_pct": round(treatment_rate * 100, 1),
            "market_growth_rate": "15-20% annually"
        }
    
    def cost_effectiveness(self, qaly_gained: float = 3.5) -> Dict:
        total_cost = self.treatment_cost()["total_cost"]
        
        icer = total_cost / qaly_gained  # Incremental cost-effectiveness ratio
        
        # WTP thresholds
        wtp_us = 150000
        wtp_uk = 50000  # NICE threshold
        
        cost_effective_us = icer < wtp_us
        cost_effective_uk = icer < wtp_uk
        
        return {
            "total_treatment_cost": total_cost,
            "qalys_gained": qaly_gained,
            "icer": round(icer, 0),
            "cost_effective_us": cost_effective_us,
            "cost_effective_uk": cost_effective_uk,
            "vs_chemo_survival_months": 24
        }
