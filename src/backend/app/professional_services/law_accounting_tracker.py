"""Professional Services Tracker"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date

@dataclass
class BillableHour:
    entry_id: str
    client: str
    hours: float
    rate: float
    date: date

class ProfessionalServicesTracker:
    def __init__(self, firm: str = "Firm"):
        self.firm = firm
        self.hours: List[BillableHour] = []
    
    def add_entry(self, e: BillableHour):
        self.hours.append(e)
    
    def get_metrics(self) -> Dict:
        if not self.hours:
            return {'status': 'NO_DATA'}
        revenue = sum(h.hours * h.rate for h in self.hours)
        total_hours = sum(h.hours for h in self.hours)
        return {
            'firm': self.firm,
            'total_hours': round(total_hours, 1),
            'revenue': round(revenue, 2),
            'effective_rate': round(revenue / total_hours, 2) if total_hours else 0,
            'entries': len(self.hours)
        }

def analyze_professional_firm(entries: List[Dict]) -> Dict:
    t = ProfessionalServicesTracker()
    for e in entries:
        t.add_entry(BillableHour(e['id'], e['client'], e['hours'], e['rate'], e.get('date', date.today())))
    return t.get_metrics()
