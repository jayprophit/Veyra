"""Rental Income Tracker - Real estate rental income"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class RentalProperty:
    property_id: str
    address: str
    monthly_rent: float
    expenses_monthly: float
    vacancy_rate_pct: float

class RentalIncomeTracker:
    def __init__(self):
        self.properties: List[RentalProperty] = []
    
    def add(self, p: RentalProperty):
        self.properties.append(p)
    
    def calculate_net_income(self, p: RentalProperty) -> float:
        effective_rent = p.monthly_rent * (1 - p.vacancy_rate_pct / 100)
        return effective_rent - p.expenses_monthly
    
    def get_summary(self) -> Dict:
        if not self.properties:
            return {'status': 'NO_PROPERTIES'}
        
        total_gross = sum(p.monthly_rent for p in self.properties)
        total_net = sum(self.calculate_net_income(p) for p in self.properties)
        
        return {
            'properties': len(self.properties),
            'monthly_gross': round(total_gross, 2),
            'monthly_net': round(total_net, 2),
            'annual_net': round(total_net * 12, 2),
            'avg_expense_ratio': round(sum(p.expenses_monthly / p.monthly_rent for p in self.properties) / len(self.properties) * 100, 1)
        }
