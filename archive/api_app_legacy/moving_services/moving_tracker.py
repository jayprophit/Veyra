"""Moving & Relocation Services Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class Move:
    move_id: str
    move_type: str  # 'local', 'long_distance', 'commercial'
    revenue: float
    truck_cost: float
    labor_cost: float
    miles: int
    date: date

class MovingTracker:
    def __init__(self, name: str = "Movers"):
        self.name = name
        self.moves: List[Move] = []
    
    def add(self, m: Move):
        self.moves.append(m)
    
    def get_metrics(self) -> Dict:
        if not self.moves:
            return {'status': 'NO_DATA'}
        revenue = sum(m.revenue for m in self.moves)
        costs = sum(m.truck_cost + m.labor_cost for m in self.moves)
        miles = sum(m.miles for m in self.moves)
        profit = revenue - costs
        return {
            'company': self.name,
            'moves': len(self.moves),
            'revenue': round(revenue, 2),
            'costs': round(costs, 2),
            'profit': round(profit, 2),
            'margin': round(profit / revenue * 100, 1) if revenue else 0,
            'total_miles': miles,
            'avg_per_move': round(revenue / len(self.moves), 2)
        }

def analyze_moving(data: List[Dict]) -> Dict:
    t = MovingTracker()
    for d in data:
        t.add(Move(d['id'], d['type'], d['revenue'], d.get('truck', 0), d.get('labor', 0), d.get('miles', 0), d.get('date', date.today())))
    return t.get_metrics()
