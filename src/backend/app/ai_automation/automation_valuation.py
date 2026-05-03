"""Automation Valuation - Value of automation systems"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AutomationSystem:
    name: str
    implementation_cost: float
    annual_savings: float
    risk_reduction_value: float

class AutomationValuation:
    def __init__(self):
        self.systems: List[AutomationSystem] = []
    
    def add(self, s: AutomationSystem):
        self.systems.append(s)
    
    def calculate_npv(self, s: AutomationSystem, years: int = 5, rate: float = 0.08) -> float:
        total_value = s.annual_savings + s.risk_reduction_value
        npv = -s.implementation_cost
        for year in range(1, years + 1):
            npv += total_value / ((1 + rate) ** year)
        return npv
    
    def get_summary(self) -> Dict:
        if not self.systems:
            return {'status': 'NO_DATA'}
        return {
            'systems': len(self.systems),
            'total_investment': round(sum(s.implementation_cost for s in self.systems), 2),
            'total_annual_value': round(sum(s.annual_savings + s.risk_reduction_value for s in self.systems), 2)
        }
