"""Tutoring & Education Services Tracker"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import date

@dataclass
class TutoringSession:
    session_id: str
    subject: str
    hours: float
    hourly_rate: float
    date: date

class TutoringTracker:
    def __init__(self, name: str = "Tutoring"):
        self.name = name
        self.sessions: List[TutoringSession] = []
    
    def add(self, s: TutoringSession):
        self.sessions.append(s)
    
    def get_metrics(self) -> Dict:
        if not self.sessions:
            return {'status': 'NO_DATA'}
        hours = sum(s.hours for s in self.sessions)
        rev = sum(s.hours * s.hourly_rate for s in self.sessions)
        by_subject = {}
        for s in self.sessions:
            sub = s.subject
            if sub not in by_subject:
                by_subject[sub] = {'hours': 0, 'revenue': 0}
            by_subject[sub]['hours'] += s.hours
            by_subject[sub]['revenue'] += s.hours * s.hourly_rate
        return {
            'business': self.name,
            'sessions': len(self.sessions),
            'total_hours': round(hours, 1),
            'revenue': round(rev, 2),
            'by_subject': by_subject,
            'avg_hourly': round(rev / hours, 2) if hours else 0
        }

def analyze_tutoring(data: List[Dict]) -> Dict:
    t = TutoringTracker()
    for d in data:
        t.add(TutoringSession(d['id'], d['subject'], d['hours'], d['rate'], d.get('date', date.today())))
    return t.get_metrics()
