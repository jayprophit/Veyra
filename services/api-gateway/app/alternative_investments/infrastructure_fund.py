"""Infrastructure Fund Analyzer"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class InfrastructureAsset:
    asset_id: str
    asset_type: str  # 'road', 'bridge', 'utility', 'renewable'
    value: float
    yield_pct: float

class InfrastructureFundAnalyzer:
    """Analyze infrastructure fund investments"""
    
    def __init__(self):
        self.assets: List[InfrastructureAsset] = []
    
    def add_asset(self, asset: InfrastructureAsset):
        self.assets.append(asset)
    
    def get_summary(self) -> Dict:
        total_value = sum(a.value for a in self.assets)
        avg_yield = sum(a.yield_pct for a in self.assets) / len(self.assets) if self.assets else 0
        return {
            'assets': len(self.assets),
            'total_value': round(total_value, 2),
            'avg_yield_pct': round(avg_yield, 2)
        }
