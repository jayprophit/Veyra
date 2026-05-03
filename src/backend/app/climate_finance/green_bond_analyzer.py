"""Green Bond Analyzer - Green bond investment analysis"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class GreenBond:
    bond_id: str
    issuer: str
    principal: float
    coupon_rate: float
    green_use_of_proceeds: str
    carbon_impact_tonnes: float

class GreenBondAnalyzer:
    def __init__(self):
        self.bonds: List[GreenBond] = []
    
    def add(self, b: GreenBond):
        self.bonds.append(b)
    
    def get_summary(self) -> Dict:
        if not self.bonds:
            return {'status': 'NO_BONDS'}
        return {
            'bonds': len(self.bonds),
            'total_principal': round(sum(b.principal for b in self.bonds), 2),
            'avg_coupon': round(sum(b.coupon_rate for b in self.bonds) / len(self.bonds), 2),
            'total_carbon_impact': round(sum(b.carbon_impact_tonnes for b in self.bonds), 0)
        }
