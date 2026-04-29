"""Gene Editing Valuation"""
from typing import Dict

class GeneEditingValuation:
    """Valuation models for gene editing companies"""
    
    def __init__(self, platform: str = "crispr"):
        self.platform = platform  # crispr, base_editing, prime_editing
        self.companies = {
            "crispr_tx": {"market_cap": 5.5e9, "pipeline_stage": "commercial"},
            "editas": {"market_cap": 0.8e9, "pipeline_stage": "phase_1_2"},
            "intellia": {"market_cap": 2.8e9, "pipeline_stage": "phase_3"},
            "beam": {"market_cap": 0.5e9, "pipeline_stage": "phase_1_2"}
        }
    
    def platform_value(self, patents: int = 50) -> Dict:
        value_per_patent = 50e6  # $50M per foundational patent
        platform_value = patents * value_per_patent
        
        return {
            "patent_count": patents,
            "value_per_patent_millions": 50,
            "platform_value_millions": round(platform_value / 1e6, 1),
            "platform": self.platform,
            "includes_ip": ["Guide RNA", "Delivery vectors", "Editing enzymes"]
        }
    
    def clinical_asset_valuation(self, phase: str = "phase_2") -> Dict:
        rnp = {
            "preclinical": {"pos": 0.05, "value": 50e6},
            "phase_1": {"pos": 0.08, "value": 150e6},
            "phase_2": {"pos": 0.15, "value": 400e6},
            "phase_3": {"pos": 0.50, "value": 1.2e9},
            "registered": {"pos": 0.85, "value": 2.5e9}
        }
        
        asset = rnp.get(phase, rnp["preclinical"])
        
        peak_sales = 1e9
        prob_success = asset["pos"]
        value = asset["value"]
        
        return {
            "development_phase": phase,
            "probability_of_success": prob_success,
            "asset_value_millions": round(value / 1e6, 1),
            "peak_sales_potential_millions": round(peak_sales / 1e6, 1),
            "time_to_market_years": self._time_to_market(phase)
        }
    
    def _time_to_market(self, phase: str) -> int:
        timeline = {
            "preclinical": 8,
            "phase_1": 6,
            "phase_2": 4,
            "phase_3": 2,
            "registered": 0
        }
        return timeline.get(phase, 5)
    
    def company_dcf(self, products: int = 3) -> Dict:
        # Simplified DCF for gene editing company
        wacc = 0.12
        terminal_growth = 0.03
        
        # Revenue projections (conservative)
        revenues = [50, 150, 400, 800, 1200]  # $M over 5 years
        
        # High margins post-commercialization
        ebitda_margins = [-2.0, -0.5, 0.1, 0.25, 0.35]
        
        fcf = []
        for i, (rev, margin) in enumerate(zip(revenues, ebitda_margins)):
            ebitda = rev * margin
            # Simplified: FCF = EBITDA - CapEx - Change in WC
            capex = rev * 0.10
            fcf_val = ebitda - capex
            # Discount
            pv = fcf_val / ((1 + wacc) ** (i + 1))
            fcf.append(pv)
        
        # Terminal value
        terminal_ebitda = revenues[-1] * ebitda_margins[-1]
        terminal_value = (terminal_ebitda * 10) / ((1 + wacc) ** 5)
        
        enterprise_value = sum(fcf) + terminal_value
        
        return {
            "enterprise_value_millions": round(enterprise_value, 1),
            "wacc_pct": round(wacc * 100, 1),
            "terminal_growth_pct": round(terminal_growth * 100, 1),
            "products_in_pipeline": products,
            "valuation_per_product": round(enterprise_value / products, 1)
        }
    
    def competitive_moat(self) -> Dict:
        moat_factors = {
            "crispr": {"patent_strength": "High", "delivery": "Lipid nanoparticles", "advantage": "Established"},
            "base_editing": {"patent_strength": "Medium", "delivery": "Lipid nanoparticles", "advantage": "Precision"},
            "prime_editing": {"patent_strength": "Medium", "delivery": "Viral vectors", "advantage": "Versatility"}
        }
        
        return {
            "platform": self.platform,
            "moat_rating": moat_factors.get(self.platform, {}),
            "switching_costs": "Very High - clinical validation takes years",
            "network_effects": "Moderate - manufacturing know-how accumulates",
            "regulatory_expertise": "Critical - few companies have gene therapy approvals"
        }
