"""Darkweb Intel - Dark web intelligence for security"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime

@dataclass
class ThreatIntel:
    threat_id: str
    threat_type: str
    severity: int  # 1-10
    target_sector: str
    discovered_date: datetime
    mitigation_cost: float

class DarkwebIntel:
    def __init__(self):
        self.threats: List[ThreatIntel] = []
    
    def add(self, t: ThreatIntel):
        self.threats.append(t)
    
    def get_by_sector(self, sector: str) -> List[ThreatIntel]:
        return [t for t in self.threats if t.target_sector == sector]
    
    def get_summary(self) -> Dict:
        if not self.threats:
            return {'status': 'NO_DATA'}
        by_sector = {}
        for t in self.threats:
            if t.target_sector not in by_sector:
                by_sector[t.target_sector] = {'count': 0, 'avg_severity': 0, 'total_mitigation': 0}
            by_sector[t.target_sector]['count'] += 1
            by_sector[t.target_sector]['avg_severity'] += t.severity
            by_sector[t.target_sector]['total_mitigation'] += t.mitigation_cost
        
        for sector in by_sector:
            if by_sector[sector]['count'] > 0:
                by_sector[sector]['avg_severity'] = round(by_sector[sector]['avg_severity'] / by_sector[sector]['count'], 1)
        
        return {
            'total_threats': len(self.threats),
            'avg_severity': round(sum(t.severity for t in self.threats) / len(self.threats), 1),
            'total_mitigation_cost': round(sum(t.mitigation_cost for t in self.threats), 2),
            'by_sector': by_sector
        }
