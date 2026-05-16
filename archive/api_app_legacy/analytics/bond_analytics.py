"""UK Bond Analytics - Gilts and Corporate Bonds"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal

@dataclass
class Bond:
    isin: str
    name: str
    issuer: str
    coupon: Decimal
    maturity: date
    price: Decimal
    yield_pct: Decimal
    rating: str  # AAA, AA, A, BBB, etc.
    type: str  # Gilt, Corporate, Index-Linked

class BondAnalytics:
    """UK Bond Market Analytics"""
    
    def __init__(self):
        self.bonds: Dict[str, Bond] = {}
        self._load_sample_gilts()
    
    def _load_sample_gilts(self):
        """Load sample UK gilts"""
        sample_bonds = [
            Bond("GB00B3KJDH25", "Treasury 4.5% 2029", "UK Government", 
                 Decimal("4.5"), date(2029, 3, 7), Decimal("98.5"), 
                 Decimal("4.8"), "AAA", "Gilt"),
            Bond("GB00B52WS153", "Treasury 0.125% 2030", "UK Government",
                 Decimal("0.125"), date(2030, 1, 31), Decimal("78.2"),
                 Decimal("4.6"), "AAA", "Gilt"),
            Bond("GB00B54QLM75", "Treasury 1.75% 2037", "UK Government",
                 Decimal("1.75"), date(2037, 9, 7), Decimal("82.4"),
                 Decimal("4.5"), "AAA", "Gilt"),
        ]
        for bond in sample_bonds:
            self.bonds[bond.isin] = bond
    
    def get_gilt_yields(self) -> Dict[str, float]:
        """Get current gilt yields by maturity"""
        return {
            "2Y": 4.45,
            "5Y": 4.25,
            "10Y": 4.15,
            "30Y": 4.35
        }
    
    def calculate_bond_ladder(self, investment: float, years: int = 5) -> List[Dict]:
        """Calculate a bond ladder strategy"""
        yearly = investment / years
        ladder = []
        for i in range(1, years + 1):
            ladder.append({
                "year": i,
                "maturity": date(datetime.now().year + i, 1, 1),
                "investment": yearly,
                "estimated_yield": 4.2,
                "annual_income": yearly * 0.042
            })
        return ladder
    
    def get_summary(self) -> Dict:
        """Get bond market summary"""
        gilts = [b for b in self.bonds.values() if b.type == "Gilt"]
        avg_yield = sum(b.yield_pct for b in gilts) / len(gilts) if gilts else 0
        
        return {
            "total_bonds": len(self.bonds),
            "gilts": len(gilts),
            "corporates": len([b for b in self.bonds.values() if b.type == "Corporate"]),
            "average_gilt_yield": float(avg_yield),
            "gilt_yields": self.get_gilt_yields(),
            "last_updated": datetime.now().isoformat()
        }

class BondLadderBuilder:
    """Build bond ladders for steady income"""
    
    def __init__(self):
        self.analytics = BondAnalytics()
    
    def build_ladder(self, amount: float, rungs: int = 5) -> Dict:
        """Build a bond ladder portfolio"""
        per_rung = amount / rungs
        
        ladder = {
            "total_investment": amount,
            "num_rungs": rungs,
            "per_rung": per_rung,
            "estimated_annual_yield": 4.2,
            "estimated_annual_income": amount * 0.042,
            "rungs": []
        }
        
        for i in range(1, rungs + 1):
            maturity_year = datetime.now().year + i
            ladder["rungs"].append({
                "rung": i,
                "maturity_year": maturity_year,
                "investment": per_rung,
                "bond_type": "UK Gilt" if i <= 3 else "Corporate Bond",
                "estimated_coupon": per_rung * 0.04
            })
        
        return ladder
