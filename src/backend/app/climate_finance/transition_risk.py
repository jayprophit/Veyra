"""Transition Risk - Climate transition risk assessment"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TransitionRiskProfile:
    company_id: str
    sector: str
    carbon_intensity: float
    regulatory_exposure: int  # 1-10
    technology_risk: int  # 1-10
    market_risk: int  # 1-10

class TransitionRisk:
    def __init__(self):
        self.profiles: List[TransitionRiskProfile] = []
    
    def add(self, p: TransitionRiskProfile):
        self.profiles.append(p)
    
    def calculate_risk_score(self, p: TransitionRiskProfile) -> int:
        return p.regulatory_exposure + p.technology_risk + p.market_risk
    
    def get_summary(self) -> Dict:
        if not self.profiles:
            return {'status': 'NO_DATA'}
        return {
            'profiles': len(self.profiles),
            'avg_risk_score': round(sum(self.calculate_risk_score(p) for p in self.profiles) / len(self.profiles), 1),
            'high_risk_count': sum(1 for p in self.profiles if self.calculate_risk_score(p) > 20)
        }
