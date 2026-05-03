"""
Beauty & Salon Business Tracker
================================
Track salon, spa, and beauty business income
"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class ServiceTicket:
    ticket_id: str
    service_type: str
    price: float
    product_cost: float
    staff_member: str
    date: date


class SalonBusinessTracker:
    """Track salon and spa business operations"""
    
    def __init__(self, salon_name: str = "Salon"):
        self.salon_name = salon_name
        self.tickets: List[ServiceTicket] = []
    
    def add_ticket(self, ticket: ServiceTicket):
        self.tickets.append(ticket)
    
    def get_salon_health_report(self) -> Dict:
        cutoff = date.today() - timedelta(days=30)
        recent = [t for t in self.tickets if t.date >= cutoff]
        
        if not recent:
            return {'status': 'NO_DATA'}
        
        total = sum(t.price for t in recent)
        days = len(set(t.date for t in recent))
        daily_avg = total / max(days, 1)
        
        by_service = {}
        for t in recent:
            s = t.service_type
            if s not in by_service:
                by_service[s] = {'count': 0, 'revenue': 0}
            by_service[s]['count'] += 1
            by_service[s]['revenue'] += t.price
        
        return {
            'salon_name': self.salon_name,
            'status': 'HEALTHY' if daily_avg > 1000 else 'BUILDING',
            'monthly_projection': round(daily_avg * 30, 2),
            'avg_ticket': round(total / len(recent), 2),
            'service_mix': by_service
        }


# Usage
def analyze_salon(tickets: List[Dict]) -> Dict:
    tracker = SalonBusinessTracker()
    for t in tickets:
        tracker.add_ticket(ServiceTicket(
            ticket_id=t['id'],
            service_type=t['service'],
            price=t['price'],
            product_cost=t.get('cost', 0),
            staff_member=t.get('staff', 'Staff'),
            date=t.get('date', date.today())
        ))
    return tracker.get_salon_health_report()
