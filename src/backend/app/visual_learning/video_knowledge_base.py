"""Video Knowledge Base - Store video insights"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class VideoEntry:
    entry_id: str
    video_url: str
    insights: List[str]

class VideoKnowledgeBase:
    def __init__(self):
        self.entries: List[VideoEntry] = []
    
    def add(self, e: VideoEntry):
        self.entries.append(e)
    
    def get_summary(self) -> Dict:
        return {'entries': len(self.entries), 'total_insights': sum(len(e.insights) for e in self.entries)}
