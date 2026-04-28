"""Streaming Analytics"""
from typing import Dict

class StreamingAnalytics:
    """Analyze music streaming economics"""
    
    PAYOUTS = {"spotify": 0.003, "apple_music": 0.01, "youtube": 0.002, "amazon": 0.004}
    
    def revenue_estimate(self, streams: int, platform: str) -> Dict:
        """Estimate streaming revenue"""
        rate = self.PAYOUTS.get(platform.lower(), 0.003)
        return {"streams": streams, "rate": rate, "revenue": streams * rate}
    
    def multi_platform(self, streams_by_platform: Dict[str, int]) -> Dict:
        """Aggregate across platforms"""
        total = sum(streams * self.PAYOUTS.get(p, 0.003) for p, streams in streams_by_platform.items())
        return {"total_revenue": total, "breakdown": streams_by_platform}
