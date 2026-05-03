"""Party & Event Rentals Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class PartyRental:
    rental_id: str
    item_type: str
    quantity: int
    unit_price: float
    cleaning_cost: float
    date: date

class PartyRentalTracker:
    def __init__(self, name: str = "Party Rentals"):
        self.name = name
        self.rentals: List[PartyRental] = []
    
    def add(self, r: PartyRental):
        self.rentals.append(r)
    
    def get_metrics(self) -> Dict:
        if not self.rentals:
            return {'status': 'NO_DATA'}
        revenue = sum(r.quantity * r.unit_price for r in self.rentals)
        costs = sum(r.cleaning_cost for r in self.rentals)
        return {
            'company': self.name,
            'rentals': len(self.rentals),
            'revenue': round(revenue, 2),
            'cleaning_costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0
        }

def analyze_party_rentals(data: List[Dict]) -> Dict:
    t = PartyRentalTracker()
    for d in data:
        t.add(PartyRental(d['id'], d['item'], d.get('qty', 1), d['price'], d.get('cleaning', 0), d.get('date', date.today())))
    return t.get_metrics()
