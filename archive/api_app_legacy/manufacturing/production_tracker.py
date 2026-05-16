"""Manufacturing & Production Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date

@dataclass
class ProductionRun:
    run_id: str
    units_produced: int
    material_cost: float
    labor_cost: float
    overhead: float
    date: date

class ManufacturingTracker:
    def __init__(self, name: str = "Factory"):
        self.name = name
        self.runs: List[ProductionRun] = []
    
    def add_run(self, r: ProductionRun):
        self.runs.append(r)
    
    def get_metrics(self) -> Dict:
        if not self.runs:
            return {'status': 'NO_DATA'}
        units = sum(r.units_produced for r in self.runs)
        materials = sum(r.material_cost for r in self.runs)
        labor = sum(r.labor_cost for r in self.runs)
        overhead = sum(r.overhead for r in self.runs)
        total_cost = materials + labor + overhead
        return {
            'factory': self.name,
            'units_produced': units,
            'material_cost': round(materials, 2),
            'labor_cost': round(labor, 2),
            'overhead': round(overhead, 2),
            'total_cost': round(total_cost, 2),
            'cost_per_unit': round(total_cost / units, 2) if units else 0,
            'production_runs': len(self.runs)
        }

def analyze_manufacturing(runs: List[Dict]) -> Dict:
    t = ManufacturingTracker()
    for r in runs:
        t.add_run(ProductionRun(r['id'], r['units'], r.get('materials', 0), r.get('labor', 0), r.get('overhead', 0), r.get('date', date.today())))
    return t.get_metrics()
