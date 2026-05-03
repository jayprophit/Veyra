"""Point Source Capture - Carbon capture at industrial sites"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CaptureFacility:
    facility_id: str
    industry_type: str
    capture_capacity_tonnes: float
    operating_cost_per_tonne: float
    capture_rate_pct: float

class PointSourceCapture:
    def __init__(self):
        self.facilities: List[CaptureFacility] = []
    
    def add(self, f: CaptureFacility):
        self.facilities.append(f)
    
    def calculate_annual_cost(self, f: CaptureFacility) -> float:
        return f.capture_capacity_tonnes * f.operating_cost_per_tonne
    
    def get_summary(self) -> Dict:
        if not self.facilities:
            return {'status': 'NO_FACILITIES'}
        
        by_industry = {}
        for f in self.facilities:
            if f.industry_type not in by_industry:
                by_industry[f.industry_type] = {'count': 0, 'capacity': 0, 'cost': 0}
            by_industry[f.industry_type]['count'] += 1
            by_industry[f.industry_type]['capacity'] += f.capture_capacity_tonnes
            by_industry[f.industry_type]['cost'] += self.calculate_annual_cost(f)
        
        return {
            'total_facilities': len(self.facilities),
            'total_capacity_tonnes': sum(f.capture_capacity_tonnes for f in self.facilities),
            'total_annual_cost': round(sum(self.calculate_annual_cost(f) for f in self.facilities), 2),
            'avg_capture_rate': round(sum(f.capture_rate_pct for f in self.facilities) / len(self.facilities), 1),
            'by_industry': by_industry
        }
