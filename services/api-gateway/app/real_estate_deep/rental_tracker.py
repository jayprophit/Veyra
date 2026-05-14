"""Real Estate Investment Tracker
Rental properties, Airbnb, REITs, and land investments"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Property:
    address: str
    purchase_price: float
    current_value: float
    monthly_rent: float
    property_type: str  # 'rental', 'airbnb', 'commercial'

class RealEstateTracker:
    """Track real estate investments"""
    
    def __init__(self):
        self.properties: List[Property] = []
        self.reit_holdings: Dict[str, float] = {}
    
    def add_property(self, prop: Property):
        """Add property to portfolio"""
        self.properties.append(prop)
    
    def calculate_portfolio_value(self) -> Dict:
        """Calculate total real estate portfolio value"""
        total_value = sum(p.current_value for p in self.properties)
        total_cost = sum(p.purchase_price for p in self.properties)
        monthly_income = sum(p.monthly_rent for p in self.properties)
        
        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'unrealized_gain': round(total_value - total_cost, 2),
            'monthly_rental_income': round(monthly_income, 2),
            'annual_yield_pct': round(monthly_income * 12 / total_value * 100, 2) if total_value > 0 else 0,
            'property_count': len(self.properties),
            'breakdown_by_type': self._breakdown_by_type()
        }
    
    def _breakdown_by_type(self) -> Dict:
        """Breakdown by property type"""
        by_type = {}
        for p in self.properties:
            if p.property_type not in by_type:
                by_type[p.property_type] = {'count': 0, 'value': 0}
            by_type[p.property_type]['count'] += 1
            by_type[p.property_type]['value'] += p.current_value
        return by_type
    
    def get_reit_allocation(self) -> Dict:
        """Get REIT allocation recommendations"""
        reit_sectors = {
            'residential': ['EQR', 'AVB', 'UDR'],
            'industrial': ['PLD', 'EXR'],
            'retail': ['SPG', 'O'],
            'healthcare': ['WELL', 'VTR'],
            'data_center': ['DLR', 'EQIX']
        }
        
        return {
            'current_holdings': self.reit_holdings,
            'recommended_allocation': {
                'residential': 0.25,
                'industrial': 0.25,
                'retail': 0.15,
                'healthcare': 0.20,
                'data_center': 0.15
            },
            'top_reits_by_sector': reit_sectors
        }

# Usage
def analyze_real_estate_portfolio(properties: List[Dict]) -> Dict:
    """Quick real estate portfolio analysis"""
    tracker = RealEstateTracker()
    
    for p in properties:
        tracker.add_property(Property(
            address=p['address'],
            purchase_price=p['purchase_price'],
            current_value=p.get('current_value', p['purchase_price']),
            monthly_rent=p.get('monthly_rent', 0),
            property_type=p.get('type', 'rental')
        ))
    
    return tracker.calculate_portfolio_value()
