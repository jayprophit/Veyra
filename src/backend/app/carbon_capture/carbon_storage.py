"""Carbon Storage - Long-term CO2 storage analysis"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class StorageType(Enum):
    GEOLOGICAL = "geological"
    MINERALIZATION = "mineralization"
    OCEAN = "ocean"
    BIOMASS = "biomass"

@dataclass
class StorageSite:
    site_id: str
    storage_type: StorageType
    capacity_million_tonnes: float
    injection_rate_per_year: float
    monitoring_cost_per_year: float
    permanence_years: int

class CarbonStorage:
    def __init__(self):
        self.sites: List[StorageSite] = []
    
    def add(self, s: StorageSite):
        self.sites.append(s)
    
    def get_by_type(self, storage_type: StorageType) -> List[StorageSite]:
        return [s for s in self.sites if s.storage_type == storage_type]
    
    def get_summary(self) -> Dict:
        if not self.sites:
            return {'status': 'NO_SITES'}
        
        by_type = {}
        for s in self.sites:
            t = s.storage_type.value
            if t not in by_type:
                by_type[t] = {'count': 0, 'capacity': 0, 'annual_cost': 0}
            by_type[t]['count'] += 1
            by_type[t]['capacity'] += s.capacity_million_tonnes
            by_type[t]['annual_cost'] += s.monitoring_cost_per_year
        
        return {
            'total_sites': len(self.sites),
            'total_capacity_million_tonnes': sum(s.capacity_million_tonnes for s in self.sites),
            'total_annual_monitoring': round(sum(s.monitoring_cost_per_year for s in self.sites), 2),
            'avg_permanence_years': round(sum(s.permanence_years for s in self.sites) / len(self.sites), 0),
            'by_storage_type': by_type
        }
