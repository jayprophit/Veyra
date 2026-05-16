"""Dumpster Rental Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class DumpsterRental:
    rental_id: str
    size: str  # '10yd', '20yd', '30yd'
    flat_rate: float
    disposal_fees: float
    days_rented: int
    date: date

class DumpsterTracker:
    def __init__(self, name: str = "Dumpster Rental"):
        self.name = name
        self.rentals: List[DumpsterRental] = []
    
    def add(self, r: DumpsterRental):
        self.rentals.append(r)
    
    def get_metrics(self) -> Dict:
        if not self.rentals:
            return {'status': 'NO_DATA'}
        revenue = sum(r.flat_rate for r in self.rentals)
        costs = sum(r.disposal_fees for r in self.rentals)
        return {
            'company': self.name,
            'rentals': len(self.rentals),
            'revenue': round(revenue, 2),
            'disposal_costs': round(costs, 2),
            'profit': round(revenue - costs, 2),
            'margin': round((revenue - costs) / revenue * 100, 1) if revenue else 0
        }

def analyze_dumpster_rental(data: List[Dict]) -> Dict:
    t = DumpsterTracker()
    for d in data:
        t.add(DumpsterRental(d['id'], d['size'], d['rate'], d.get('disposal', 100), d.get('days', 7), d.get('date', date.today())))
    return t.get_metrics()
