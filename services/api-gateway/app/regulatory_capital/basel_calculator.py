"""Basel Calculator - Capital adequacy calculations"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class RiskWeightedAsset:
    asset_class: str
    exposure: float
    risk_weight: float

class BaselCalculator:
    """Calculate Basel III/IV capital requirements"""
    
    CET1_MIN = 0.045
    TIER1_MIN = 0.06
    TOTAL_MIN = 0.08
    BUFFER = 0.025
    
    def __init__(self):
        self.rwa_list: List[RiskWeightedAsset] = []
        self.cet1 = self.at1 = self.tier2 = 0.0
    
    def add_rwa(self, rwa: RiskWeightedAsset):
        self.rwa_list.append(rwa)
    
    def set_capital(self, cet1: float, at1: float, tier2: float):
        self.cet1, self.at1, self.tier2 = cet1, at1, tier2
    
    def calculate_total_rwa(self) -> float:
        return sum(r.exposure * r.risk_weight for r in self.rwa_list)
    
    def calculate_ratios(self) -> Dict:
        total_rwa = self.calculate_total_rwa()
        if total_rwa == 0:
            return {"error": "No RWA"}
        tier1 = self.cet1 + self.at1
        total = tier1 + self.tier2
        return {
            "rwa": total_rwa,
            "cet1_ratio": round(self.cet1 / total_rwa * 100, 2),
            "tier1_ratio": round(tier1 / total_rwa * 100, 2),
            "total_ratio": round(total / total_rwa * 100, 2),
            "compliant": (self.cet1 / total_rwa >= self.CET1_MIN + self.BUFFER)
        }
