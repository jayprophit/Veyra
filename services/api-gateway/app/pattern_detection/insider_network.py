"""Insider Network Mapper - Map relationships between insiders"""
from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class Insider:
    insider_id: str
    name: str
    company: str
    role: str
    related_insiders: List[str]

@dataclass
class NetworkConnection:
    insider1: str
    insider2: str
    connection_type: str
    strength: int  # 1-10

class InsiderNetworkMapper:
    def __init__(self):
        self.insiders: Dict[str, Insider] = {}
        self.connections: List[NetworkConnection] = []
    
    def add_insider(self, i: Insider):
        self.insiders[i.insider_id] = i
    
    def add_connection(self, c: NetworkConnection):
        self.connections.append(c)
    
    def get_network_for_insider(self, insider_id: str) -> List[NetworkConnection]:
        return [c for c in self.connections if c.insider1 == insider_id or c.insider2 == insider_id]
    
    def get_summary(self) -> Dict:
        if not self.insiders:
            return {'status': 'NO_INSIDERS'}
        
        by_company = {}
        for i in self.insiders.values():
            c = i.company
            if c not in by_company:
                by_company[c] = {'insiders': 0, 'connections': 0}
            by_company[c]['insiders'] += 1
        
        for c in self.connections:
            i1 = self.insiders.get(c.insider1)
            i2 = self.insiders.get(c.insider2)
            if i1 and i2 and i1.company == i2.company:
                by_company[i1.company]['connections'] += 1
        
        return {
            'total_insiders': len(self.insiders),
            'total_connections': len(self.connections),
            'by_company': by_company
        }
