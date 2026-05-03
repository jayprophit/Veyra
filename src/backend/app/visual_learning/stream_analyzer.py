"""Stream Analyzer - Real-time stream analysis"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class StreamData:
    stream_id: str
    source: str
    data_points: int

class StreamAnalyzer:
    def __init__(self):
        self.streams: List[StreamData] = []
    
    def add(self, s: StreamData):
        self.streams.append(s)
    
    def get_summary(self) -> Dict:
        return {'streams': len(self.streams), 'total_points': sum(s.data_points for s in self.streams)}
