"""Inheritance Tax"""
from typing import Dict

class InheritanceTax:
    US_ESTATE_EXEMPTION = 13610000  # 2024
    
    def us_estate_tax(self, gross_estate: float) -> Dict:
        taxable = max(0, gross_estate - self.US_ESTATE_EXEMPTION)
        tax = taxable * 0.40
        return {"gross_estate": gross_estate, "taxable": taxable, "estate_tax": tax, "effective_rate": tax / gross_estate if gross_estate > 0 else 0}
    
    def generation_skipping(self, transfer: float) -> Dict:
        gst_rate = 0.40
        tax = transfer * gst_rate
        return {"transfer": transfer, "gst_tax": tax, "total_cost": transfer + tax}
    
    def step_up_basis(self, appreciated_assets: float, gain: float) -> Dict:
        tax_saved = gain * 0.20  # LTCG avoided
        return {"stepped_up_basis": appreciated_assets, "capital_gains_wiped": gain, "tax_saved": tax_saved}
