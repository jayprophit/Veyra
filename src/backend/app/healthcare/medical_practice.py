"""Healthcare Practice Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date

@dataclass
class Visit:
    visit_id: str
    billed: float
    collected: float
    date: date

class MedicalPracticeTracker:
    def __init__(self, name: str = "Practice"):
        self.name = name
        self.visits: List[Visit] = []
    
    def add_visit(self, v: Visit):
        self.visits.append(v)
    
    def get_metrics(self) -> Dict:
        if not self.visits:
            return {'status': 'NO_DATA'}
        billed = sum(v.billed for v in self.visits)
        collected = sum(v.collected for v in self.visits)
        return {
            'practice': self.name,
            'total_billed': round(billed, 2),
            'total_collected': round(collected, 2),
            'collection_rate': round(collected / billed * 100, 1),
            'patient_visits': len(self.visits),
            'avg_per_visit': round(billed / len(self.visits), 2)
        }

def analyze_medical_practice(visits: List[Dict]) -> Dict:
    t = MedicalPracticeTracker()
    for v in visits:
        t.add_visit(Visit(v['id'], v['billed'], v.get('collected', v['billed']), v.get('date', date.today())))
    return t.get_metrics()
