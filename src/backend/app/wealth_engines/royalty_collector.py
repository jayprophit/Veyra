"""Royalty Collector - IP and content royalty tracking"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class RoyaltyStream:
    stream_id: str
    asset_type: str  # 'music', 'patent', 'book', 'photo'
    asset_name: str
    monthly_royalty: float
    platform: str

class RoyaltyCollector:
    def __init__(self):
        self.streams: List[RoyaltyStream] = []
    
    def add(self, s: RoyaltyStream):
        self.streams.append(s)
    
    def get_by_type(self, asset_type: str) -> List[RoyaltyStream]:
        return [s for s in self.streams if s.asset_type == asset_type]
    
    def get_summary(self) -> Dict:
        if not self.streams:
            return {'status': 'NO_STREAMS'}
        
        by_type = {}
        for s in self.streams:
            t = s.asset_type
            if t not in by_type:
                by_type[t] = {'count': 0, 'monthly': 0}
            by_type[t]['count'] += 1
            by_type[t]['monthly'] += s.monthly_royalty
        
        total_monthly = sum(s.monthly_royalty for s in self.streams)
        
        return {
            'streams': len(self.streams),
            'monthly_total': round(total_monthly, 2),
            'annual_total': round(total_monthly * 12, 2),
            'by_asset_type': by_type
        }
