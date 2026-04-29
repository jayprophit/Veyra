"""Defense Contracts - Military procurement analytics"""
from typing import Dict

class DefenseContracts:
    """Analyze defense contract economics"""
    
    def contract_margin_analysis(self, contract_value: float,
                                cost_plus_pct: float,
                                fixed_fee: float,
                                award_fee_potential: float) -> Dict:
        """Analyze cost-plus contract profitability"""
        cost_plus_revenue = contract_value * (1 + cost_plus_pct)
        award_fee = fixed_fee * award_fee_potential
        total_revenue = cost_plus_revenue + award_fee
        
        estimated_costs = contract_value * 0.85  # 85% cost ratio
        profit = total_revenue - estimated_costs
        margin = profit / total_revenue if total_revenue > 0 else 0
        
        return {
            "contract_value": contract_value,
            "cost_plus_revenue": round(cost_plus_revenue, 0),
            "award_fee": round(award_fee, 0),
            "total_revenue": round(total_revenue, 0),
            "estimated_profit": round(profit, 0),
            "margin_percent": round(margin * 100, 2),
            "contract_type": "cost_plus_award_fee"
        }
    
    def backlog_quality(self, total_backlog: float,
                      funded_backlog: float,
                      unfunded_backlog: float,
                      completion_timeline: int) -> Dict:
        """Score contract backlog quality"""
        funded_ratio = funded_backlog / total_backlog if total_backlog > 0 else 0
        
        # Quality score
        score = funded_ratio * 100
        score -= completion_timeline * 2  # Penalty for long timelines
        score += min(total_backlog / 1e9, 10)  # Bonus for scale
        
        return {
            "total_backlog": total_backlog,
            "funded_backlog": funded_backlog,
            "funded_ratio": round(funded_ratio * 100, 1),
            "backlog_score": round(score, 1),
            "quality_grade": "A" if score > 80 else "B" if score > 60 else "C",
            "revenue_visibility": f"{completion_timeline}+ years"
        }
    
    def geopolitical_risk_premium(self, contract_exposure: Dict[str, float],
                                 region_risk_scores: Dict[str, float]) -> Dict:
        """Calculate geopolitical risk premium for defense contracts"""
        weighted_risk = sum(
            contract_exposure.get(region, 0) * risk 
            for region, risk in region_risk_scores.items()
        ) / sum(contract_exposure.values()) if sum(contract_exposure.values()) > 0 else 0
        
        return {
            "weighted_risk_score": round(weighted_risk, 2),
            "risk_premium_pct": round(weighted_risk * 2, 2),
            "highest_risk_region": max(region_risk_scores, key=region_risk_scores.get),
            "diversification_score": round(100 - weighted_risk * 20, 1)
        }
