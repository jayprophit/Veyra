"""Digital Content Analytics"""
from typing import Dict, List

class DigitalContentAnalytics:
    def revenue_dashboard(self, products: Dict[str, Dict]) -> Dict:
        total = sum(data.get("revenue", 0) for data in products.values())
        return {"total_monthly": round(total, 2), "total_annual": round(total * 12, 2)}
    
    def conversion_funnel(self, impressions: int, clicks: int, purchases: int) -> Dict:
        return {
            "ctr": round(clicks / impressions * 100, 1) if impressions > 0 else 0,
            "conversion": round(purchases / clicks * 100, 1) if clicks > 0 else 0
        }
    
    def content_roi(self, cost: float, monthly_rev: float, months: int) -> Dict:
        profit = monthly_rev * months - cost
        return {"profit": round(profit, 2), "roi": round(profit / cost * 100, 1) if cost > 0 else 0}
