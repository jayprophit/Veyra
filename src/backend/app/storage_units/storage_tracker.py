"""Storage Unit Facility Tracker"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class StorageUnit:
    unit_id: str
    size: str  # '5x5', '10x10', '10x20'
    monthly_rate: float
    occupied: bool

class StorageTracker:
    def __init__(self, name: str = "Storage"):
        self.name = name
        self.units: List[StorageUnit] = []
    
    def add(self, u: StorageUnit):
        self.units.append(u)
    
    def get_metrics(self) -> Dict:
        if not self.units:
            return {'status': 'NO_DATA'}
        occupied = [u for u in self.units if u.occupied]
        revenue = sum(u.monthly_rate for u in occupied)
        by_size = {}
        for u in self.units:
            if u.size not in by_size:
                by_size[u.size] = {'total': 0, 'occupied': 0, 'revenue': 0}
            by_size[u.size]['total'] += 1
            if u.occupied:
                by_size[u.size]['occupied'] += 1
                by_size[u.size]['revenue'] += u.monthly_rate
        return {
            'facility': self.name,
            'total_units': len(self.units),
            'occupied': len(occupied),
            'vacant': len(self.units) - len(occupied),
            'occupancy_pct': round(len(occupied) / len(self.units) * 100, 1),
            'monthly_revenue': round(revenue, 2),
            'annual_revenue': round(revenue * 12, 2),
            'by_size': by_size
        }

def analyze_storage(data: List[Dict]) -> Dict:
    t = StorageTracker()
    for d in data:
        t.add(StorageUnit(d['id'], d['size'], d['rate'], d.get('occupied', True)))
    return t.get_metrics()
