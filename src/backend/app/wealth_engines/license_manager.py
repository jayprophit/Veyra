"""License Manager - Software and IP license revenue"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class License:
    license_id: str
    license_type: str  # 'software', 'patent', 'trademark'
    licensee: str
    annual_fee: float
    royalty_rate_pct: float
    min_guarantee: float

class LicenseManager:
    def __init__(self):
        self.licenses: List[License] = []
    
    def add(self, l: License):
        self.licenses.append(l)
    
    def calculate_revenue(self, l: License, licensee_revenue: float = 0) -> float:
        royalty = licensee_revenue * l.royalty_rate_pct / 100
        return max(l.annual_fee, royalty) if royalty > 0 else l.annual_fee
    
    def get_summary(self) -> Dict:
        if not self.licenses:
            return {'status': 'NO_LICENSES'}
        
        base_revenue = sum(l.annual_fee for l in self.licenses)
        
        by_type = {}
        for l in self.licenses:
            t = l.license_type
            if t not in by_type:
                by_type[t] = {'count': 0, 'revenue': 0}
            by_type[t]['count'] += 1
            by_type[t]['revenue'] += l.annual_fee
        
        return {
            'licenses': len(self.licenses),
            'base_annual_revenue': round(base_revenue, 2),
            'by_license_type': by_type
        }
