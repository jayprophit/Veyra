"""Cyber Insurance - Insurance coverage analysis"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CyberPolicy:
    policy_id: str
    company: str
    premium: float
    coverage_limit: float
    deductible: float
    industry: str

class CyberInsurance:
    def __init__(self):
        self.policies: List[CyberPolicy] = []
    
    def add(self, p: CyberPolicy):
        self.policies.append(p)
    
    def calculate_crad(self, p: CyberPolicy) -> float:
        """Coverage to premium ratio"""
        return p.coverage_limit / p.premium if p.premium else 0
    
    def get_summary(self) -> Dict:
        if not self.policies:
            return {'status': 'NO_DATA'}
        by_industry = {}
        for p in self.policies:
            if p.industry not in by_industry:
                by_industry[p.industry] = {'count': 0, 'total_premium': 0, 'total_coverage': 0}
            by_industry[p.industry]['count'] += 1
            by_industry[p.industry]['total_premium'] += p.premium
            by_industry[p.industry]['total_coverage'] += p.coverage_limit
        
        return {
            'policies': len(self.policies),
            'total_premiums': round(sum(p.premium for p in self.policies), 2),
            'total_coverage': round(sum(p.coverage_limit for p in self.policies), 2),
            'by_industry': by_industry
        }
