"""Carbon Credits - Carbon credit trading and valuation"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class CreditType(Enum):
    COMPLIANCE = "compliance"
    VOLUNTARY = "voluntary"
    NATURE_BASED = "nature_based"
    TECHNOLOGY_BASED = "technology_based"

@dataclass
class CarbonCredit:
    credit_id: str
    credit_type: CreditType
    tonnes_co2: float
    price_per_tonne: float
    vintage_year: int
    verification_standard: str

class CarbonCredits:
    def __init__(self):
        self.credits: List[CarbonCredit] = []
    
    def add(self, c: CarbonCredit):
        self.credits.append(c)
    
    def get_by_type(self, credit_type: CreditType) -> List[CarbonCredit]:
        return [c for c in self.credits if c.credit_type == credit_type]
    
    def get_summary(self) -> Dict:
        if not self.credits:
            return {'status': 'NO_CREDITS'}
        
        by_type = {}
        for c in self.credits:
            t = c.credit_type.value
            if t not in by_type:
                by_type[t] = {'count': 0, 'tonnes': 0, 'value': 0}
            by_type[t]['count'] += 1
            by_type[t]['tonnes'] += c.tonnes_co2
            by_type[t]['value'] += c.tonnes_co2 * c.price_per_tonne
        
        return {
            'total_credits': len(self.credits),
            'total_tonnes': round(sum(c.tonnes_co2 for c in self.credits), 0),
            'total_value': round(sum(c.tonnes_co2 * c.price_per_tonne for c in self.credits), 2),
            'by_type': by_type
        }
