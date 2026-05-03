"""Franchise Automation - Franchise income and operations"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class FranchiseUnit:
    unit_id: str
    brand: str
    franchise_fee_annual: float
    royalty_pct: float
    monthly_gross_sales: float
    location: str

class FranchiseAutomation:
    def __init__(self):
        self.units: List[FranchiseUnit] = []
    
    def add(self, u: FranchiseUnit):
        self.units.append(u)
    
    def calculate_monthly_royalty(self, u: FranchiseUnit) -> float:
        return u.monthly_gross_sales * u.royalty_pct / 100
    
    def get_summary(self) -> Dict:
        if not self.units:
            return {'status': 'NO_UNITS'}
        
        monthly_royalties = sum(self.calculate_monthly_royalty(u) for u in self.units)
        annual_fees = sum(u.franchise_fee_annual for u in self.units)
        
        by_brand = {}
        for u in self.units:
            b = u.brand
            if b not in by_brand:
                by_brand[b] = {'units': 0, 'monthly_royalty': 0}
            by_brand[b]['units'] += 1
            by_brand[b]['monthly_royalty'] += self.calculate_monthly_royalty(u)
        
        return {
            'units': len(self.units),
            'monthly_royalty_income': round(monthly_royalties, 2),
            'annual_fee_income': round(annual_fees, 2),
            'total_annual_income': round(monthly_royalties * 12 + annual_fees, 2),
            'by_brand': by_brand
        }
