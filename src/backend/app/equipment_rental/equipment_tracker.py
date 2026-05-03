"""Equipment Rental Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class Rental:
    rental_id: str
    equipment_type: str
    daily_rate: float
    days_rented: int
    maintenance: float
    date: date

class EquipmentRentalTracker:
    def __init__(self, name: str = "Equipment Rental"):
        self.name = name
        self.rentals: List[Rental] = []
    
    def add(self, r: Rental):
        self.rentals.append(r)
    
    def get_metrics(self) -> Dict:
        if not self.rentals:
            return {'status': 'NO_DATA'}
        revenue = sum(r.daily_rate * r.days_rented for r in self.rentals)
        costs = sum(r.maintenance for r in self.rentals)
        return {
            'company': self.name,
            'rentals': len(self.rentals),
            'revenue': round(revenue, 2),
            'maintenance': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0
        }

def analyze_equipment_rental(data: List[Dict]) -> Dict:
    t = EquipmentRentalTracker()
    for d in data:
        t.add(Rental(d['id'], d['type'], d['rate'], d['days'], d.get('maint', 0), d.get('date', date.today())))
    return t.get_metrics()
