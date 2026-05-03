"""
Real Estate & Property Management Tracker
==========================================
Track rental income, property expenses, vacancy rates
Multi-family, single-family, commercial properties
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date


@dataclass
class Property:
    property_id: str
    address: str
    property_type: str  # 'single_family', 'multi_family', 'commercial'
    monthly_rent: float
    vacancy_rate: float
    operating_expenses: float
    mortgage_payment: float


class PropertyManagerTracker:
    """Track real estate portfolio"""
    
    def __init__(self, portfolio_name: str = "Portfolio"):
        self.portfolio_name = portfolio_name
        self.properties: List[Property] = []
    
    def add_property(self, prop: Property):
        self.properties.append(prop)
    
    def get_portfolio_summary(self) -> Dict:
        if not self.properties:
            return {'status': 'NO_PROPERTIES'}
        
        total_units = len(self.properties)
        potential_rent = sum(p.monthly_rent for p in self.properties)
        actual_rent = sum(p.monthly_rent * (1 - p.vacancy_rate) for p in self.properties)
        total_expenses = sum(p.operating_expenses + p.mortgage_payment for p in self.properties)
        
        cash_flow = actual_rent - total_expenses
        
        return {
            'portfolio': self.portfolio_name,
            'total_properties': total_units,
            'potential_monthly_rent': round(potential_rent, 2),
            'actual_monthly_rent': round(actual_rent, 2),
            'vacancy_loss': round(potential_rent - actual_rent, 2),
            'operating_expenses': round(sum(p.operating_expenses for p in self.properties), 2),
            'mortgage_payments': round(sum(p.mortgage_payment for p in self.properties), 2),
            'monthly_cash_flow': round(cash_flow, 2),
            'annual_cash_flow': round(cash_flow * 12, 2),
            'cash_on_cash_return': round(cash_flow * 12 / sum(p.monthly_rent * 12 for p in self.properties) * 100, 1)
        }


# Usage
def analyze_property_portfolio(properties: List[Dict]) -> Dict:
    tracker = PropertyManagerTracker()
    for p in properties:
        tracker.add_property(Property(
            property_id=p['id'],
            address=p['address'],
            property_type=p.get('type', 'single_family'),
            monthly_rent=p['rent'],
            vacancy_rate=p.get('vacancy', 0.05),
            operating_expenses=p.get('expenses', p['rent'] * 0.30),
            mortgage_payment=p.get('mortgage', 0)
        ))
    return tracker.get_portfolio_summary()
