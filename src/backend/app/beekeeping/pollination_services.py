"""Pollination Services - Bee pollination contract analysis"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class PollinationContract:
    contract_id: str
    crop_type: str
    acres: float
    hives_needed: int
    price_per_hive: float
    duration_days: int

class PollinationServices:
    def __init__(self):
        self.contracts: List[PollinationContract] = []
    
    def add(self, c: PollinationContract):
        self.contracts.append(c)
    
    def calculate_contract_value(self, c: PollinationContract) -> Dict:
        total_value = c.hives_needed * c.price_per_hive
        daily_rate = total_value / c.duration_days if c.duration_days else 0
        
        return {
            'contract_id': c.contract_id,
            'crop_type': c.crop_type,
            'acres': c.acres,
            'hives': c.hives_needed,
            'total_value': round(total_value, 2),
            'daily_rate': round(daily_rate, 2),
            'hives_per_acre': round(c.hives_needed / c.acres, 1) if c.acres else 0
        }
    
    def get_summary(self) -> Dict:
        if not self.contracts:
            return {'status': 'NO_CONTRACTS'}
        
        details = [self.calculate_contract_value(c) for c in self.contracts]
        by_crop = {}
        for c in self.contracts:
            if c.crop_type not in by_crop:
                by_crop[c.crop_type] = {'contracts': 0, 'total_acres': 0, 'total_value': 0}
            by_crop[c.crop_type]['contracts'] += 1
            by_crop[c.crop_type]['total_acres'] += c.acres
            by_crop[c.crop_type]['total_value'] += c.hives_needed * c.price_per_hive
        
        return {
            'total_contracts': len(self.contracts),
            'total_acres': sum(c.acres for c in self.contracts),
            'total_hives': sum(c.hives_needed for c in self.contracts),
            'total_contract_value': round(sum(d['total_value'] for d in details), 2),
            'by_crop_type': by_crop
        }
