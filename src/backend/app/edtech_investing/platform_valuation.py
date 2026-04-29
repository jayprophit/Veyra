"""Platform Valuation - EdTech platform metrics"""
from typing import Dict

class PlatformValuation:
    """Value EdTech platforms"""
    
    def saas_metrics(self, arr: float,
                    growth_rate: float,
                    churn_rate: float,
                    cac: float,
                    ltv: float) -> Dict:
        """SaaS metrics for EdTech platforms"""
        ltv_cac_ratio = ltv / cac if cac > 0 else 0
        net_retention = 1 + growth_rate - churn_rate
        
        # ARR multiple based on metrics
        base_multiple = 5
        growth_premium = min(growth_rate * 20, 5)
        retention_premium = min(net_retention * 2, 3)
        
        final_multiple = base_multiple + growth_premium + retention_premium
        valuation = arr * final_multiple
        
        return {
            "arr": arr,
            "ltv_cac_ratio": round(ltv_cac_ratio, 2),
            "net_retention": round(net_retention, 2),
            "revenue_multiple": round(final_multiple, 1),
            "valuation": round(valuation, 0),
            "health_grade": "A" if ltv_cac_ratio > 3 and net_retention > 1.1 else "B"
        }
    
    def student_lifetime_value(self, monthly_fee: float,
                              avg_tenure_months: float,
                              upsell_rate: float) -> Dict:
        """Calculate student/customer LTV"""
        base_ltv = monthly_fee * avg_tenure_months
        upsell_ltv = base_ltv * upsell_rate
        total_ltv = base_ltv + upsell_ltv
        
        return {
            "monthly_fee": monthly_fee,
            "avg_tenure_months": avg_tenure_months,
            "base_ltv": round(base_ltv, 0),
            "upsell_ltv": round(upsell_ltv, 0),
            "total_ltv": round(total_ltv, 0),
            "payback_threshold": round(total_ltv * 0.3, 0)  # 30% for CAC
        }
    
    def market_penetration(self, total_students: int,
                          current_users: int,
                          addressable_population: int) -> Dict:
        """Calculate EdTech market penetration"""
        market_share = current_users / total_students if total_students > 0 else 0
        tam_penetration = current_users / addressable_population if addressable_population > 0 else 0
        
        return {
            "total_addressable_market": total_students,
            "current_users": current_users,
            "market_share_pct": round(market_share * 100, 2),
            "tam_penetration_pct": round(tam_penetration * 100, 2),
            "growth_room": round((1 - market_share) * 100, 1)
        }
