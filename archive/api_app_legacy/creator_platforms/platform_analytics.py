"""Platform Analytics - Earnings optimization"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class PlatformMetrics:
    platform: str
    followers: int
    engagement_rate: float
    revenue_per_follower: float
    monthly_revenue: float
    growth_rate: float

class PlatformAnalytics:
    """Analyze and optimize creator earnings"""
    
    def __init__(self):
        self.metrics: Dict[str, PlatformMetrics] = {}
    
    def add_metrics(self, metrics: PlatformMetrics):
        self.metrics[metrics.platform] = metrics
    
    def best_performing(self) -> str:
        if not self.metrics:
            return "No data"
        return max(self.metrics.items(), key=lambda x: x[1].monthly_revenue)[0]
    
    def highest_engagement(self) -> str:
        if not self.metrics:
            return "No data"
        return max(self.metrics.items(), key=lambda x: x[1].engagement_rate)[0]
    
    def revenue_optimization(self) -> Dict:
        if not self.metrics:
            return {}
        
        best_rpf = max(self.metrics.values(), key=lambda x: x.revenue_per_follower)
        total_revenue = sum(m.monthly_revenue for m in self.metrics.values())
        
        return {
            "best_revenue_per_follower": best_rpf.platform,
            "highest_revenue_per_follower": round(best_rpf.revenue_per_follower, 4),
            "total_monthly_revenue": round(total_revenue, 2),
            "platform_count": len(self.metrics),
            "avg_revenue_per_platform": round(total_revenue / len(self.metrics), 2),
            "recommendations": [
                f"Focus on {best_rpf.platform} for highest monetization efficiency",
                "Cross-promote content to best performing platform",
                "Analyze content type that drives highest RPF"
            ]
        }
    
    def compare_platforms(self) -> Dict[str, Dict]:
        return {
            name: {
                "rpm": round(m.revenue_per_follower * 1000, 2),
                "engagement": round(m.engagement_rate * 100, 2),
                "monthly_revenue": round(m.monthly_revenue, 2),
                "growth": round(m.growth_rate * 100, 2)
            }
            for name, m in self.metrics.items()
        }
