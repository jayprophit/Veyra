"""Foot Traffic - Retail location analytics"""
from typing import Dict

class FootTraffic:
    """Analyze foot traffic for retail investment decisions"""
    
    def traffic_trend(self, monthly_visits: list, 
                     store_sqft: float) -> Dict:
        """Calculate traffic trends and density"""
        avg_monthly = sum(monthly_visits) / len(monthly_visits) if monthly_visits else 0
        trend = (monthly_visits[-1] - monthly_visits[0]) / monthly_visits[0] * 100 if monthly_visits and monthly_visits[0] > 0 else 0
        
        return {
            "avg_monthly_visits": avg_monthly,
            "traffic_trend_percent": round(trend, 1),
            "visits_per_sqft": round(avg_monthly / store_sqft, 2) if store_sqft > 0 else 0,
            "direction": "growing" if trend > 5 else "declining" if trend < -5 else "stable"
        }
    
    def sales_estimate(self, visits: int, 
                      conversion_rate: float,
                      avg_ticket: float) -> Dict:
        """Estimate sales from traffic data"""
        customers = visits * conversion_rate
        sales = customers * avg_ticket
        
        return {
            "estimated_customers": int(customers),
            "estimated_sales": round(sales, 0),
            "conversion_rate": conversion_rate,
            "revenue_per_visit": round(sales / visits, 2) if visits > 0 else 0
        }
    
    def competitive_analysis(self, our_traffic: int,
                           competitor_traffic: list) -> Dict:
        """Compare traffic to competitors"""
        comp_avg = sum(competitor_traffic) / len(competitor_traffic) if competitor_traffic else 0
        market_share = our_traffic / (our_traffic + comp_avg) if (our_traffic + comp_avg) > 0 else 0
        
        return {
            "our_traffic": our_traffic,
            "competitor_avg": comp_avg,
            "market_share_estimate": round(market_share * 100, 1),
            "position": "leader" if market_share > 0.5 else "challenger" if market_share > 0.3 else "follower"
        }
