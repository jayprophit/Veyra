"""Startup Valuator - Early-stage company valuation methods"""
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class Startup:
    name: str
    stage: str  # Pre-seed, Seed, Series A, B, C, D+
    revenue: float  # ARR
    revenue_growth: float  # YoY growth rate
    industry: str
    market_size_tam: float
    team_score: float  # 1-10
    traction_score: float  # 1-10
    last_valuation: float = 0

class StartupValuator:
    """Value startups using multiple methods"""
    
    # Industry-specific ARR multiples by stage
    ARR_MULTIPLES = {
        "SaaS": {"Seed": 10, "Series A": 15, "Series B": 20, "Series C": 25, "D+": 30},
        "Fintech": {"Seed": 8, "Series A": 12, "Series B": 18, "Series C": 22, "D+": 28},
        "HealthTech": {"Seed": 6, "Series A": 10, "Series B": 15, "Series C": 20, "D+": 25},
        "AI/ML": {"Seed": 12, "Series A": 20, "Series B": 30, "Series C": 40, "D+": 50},
        "E-commerce": {"Seed": 4, "Series A": 6, "Series B": 10, "Series C": 15, "D+": 20},
        "Marketplace": {"Seed": 6, "Series A": 10, "Series B": 15, "Series C": 20, "D+": 25},
        "Consumer": {"Seed": 5, "Series A": 8, "Series B": 12, "Series C": 18, "D+": 25},
        "Enterprise": {"Seed": 8, "Series A": 12, "Series B": 18, "Series C": 25, "D+": 35}
    }
    
    # Pre-seed/seed valuations based on team and traction
    SEED_VALUATION_RANGES = {
        "Pre-seed": {"low": 2e6, "base": 5e6, "high": 10e6},
        "Seed": {"low": 5e6, "base": 12e6, "high": 25e6}
    }
    
    def __init__(self):
        self.startups: List[Startup] = []
    
    def add_startup(self, startup: Startup):
        """Add startup to watchlist"""
        self.startups.append(startup)
    
    def arr_multiple_valuation(self, startup: Startup) -> Dict:
        """Valuation based on ARR multiples"""
        if startup.revenue <= 0:
            return {"error": "No revenue for ARR multiple method"}
        
        # Get industry multiple
        industry_multiples = self.ARR_MULTIPLES.get(startup.industry, self.ARR_MULTIPLES["SaaS"])
        base_multiple = industry_multiples.get(startup.stage, 10)
        
        # Adjust for growth
        if startup.revenue_growth > 3.0:  # >300% growth
            growth_adjustment = 1.5
        elif startup.revenue_growth > 2.0:
            growth_adjustment = 1.3
        elif startup.revenue_growth > 1.0:
            growth_adjustment = 1.1
        elif startup.revenue_growth > 0.5:
            growth_adjustment = 1.0
        else:
            growth_adjustment = 0.8
        
        # Adjust for team quality
        team_adjustment = startup.team_score / 5.0  # 1.0 at score 5, 2.0 at score 10
        
        # Calculate adjusted multiple
        adjusted_multiple = base_multiple * growth_adjustment * team_adjustment
        
        valuation = startup.revenue * adjusted_multiple
        
        # Market cap adjustment
        market_adjustment = min(1.5, startup.market_size_tam / 10e9) if startup.market_size_tam > 0 else 1.0
        adjusted_valuation = valuation * market_adjustment
        
        return {
            "method": "ARR Multiple",
            "arr": startup.revenue,
            "base_multiple": base_multiple,
            "growth_adjustment": round(growth_adjustment, 2),
            "team_adjustment": round(team_adjustment, 2),
            "adjusted_multiple": round(adjusted_multiple, 1),
            "market_adjustment": round(market_adjustment, 2),
            "valuation": round(adjusted_valuation, 0),
            "valuation_range": {
                "low": round(adjusted_valuation * 0.7, 0),
                "base": round(adjusted_valuation, 0),
                "high": round(adjusted_valuation * 1.3, 0)
            }
        }
    
    def venture_capital_method(self, startup: Startup,
                               target_return: float = 10.0,
                               exit_timeline: int = 5,
                               exit_multiple: float = 3.0) -> Dict:
        """VC method: work backwards from expected exit"""
        # Estimate exit value
        projected_revenue = startup.revenue * ((1 + startup.revenue_growth) ** exit_timeline)
        exit_revenue = projected_revenue if startup.revenue > 0 else 10e6  # Assume $10M if pre-revenue
        
        exit_valuation = exit_revenue * exit_multiple
        
        # Required ownership to achieve target return
        # Target return = exit_value * ownership_pct / investment
        # Assume investment of $2M for this round
        investment = self._estimate_round_size(startup.stage)
        
        # Required ownership = target_return * investment / exit_valuation
        required_ownership = (target_return * investment) / exit_valuation if exit_valuation > 0 else 0.20
        required_ownership = min(required_ownership, 0.50)  # Cap at 50%
        
        # Post-money valuation
        post_money = investment / required_ownership if required_ownership > 0 else investment
        pre_money = post_money - investment
        
        return {
            "method": "Venture Capital",
            "exit_timeline_years": exit_timeline,
            "projected_exit_revenue": round(exit_revenue, 0),
            "exit_valuation": round(exit_valuation, 0),
            "assumed_investment": investment,
            "required_ownership_pct": round(required_ownership * 100, 1),
            "target_return_multiple": target_return,
            "post_money_valuation": round(post_money, 0),
            "pre_money_valuation": round(pre_money, 0),
            "implied_multiple_of_current": round(post_money / startup.last_valuation, 1) if startup.last_valuation > 0 else "N/A"
        }
    
    def _estimate_round_size(self, stage: str) -> float:
        """Estimate typical round size by stage"""
        sizes = {
            "Pre-seed": 500e3,
            "Seed": 2e6,
            "Series A": 10e6,
            "Series B": 30e6,
            "Series C": 60e6,
            "D+": 100e6
        }
        return sizes.get(stage, 5e6)
    
    def scorecard_valuation(self, startup: Startup,
                           benchmark_valuation: float = 10e6) -> Dict:
        """Scorecard method comparing to similar deals"""
        # Score factors
        scores = {
            "team": startup.team_score,
            "traction": startup.traction_score,
            "market_size": min(10, startup.market_size_tam / 1e9) if startup.market_size_tam > 0 else 5,
            "product": 7,  # Assumed
            "competitive_advantage": 6,  # Assumed
            "marketing": 6,  # Assumed
            "growth": min(10, startup.revenue_growth * 2.5) if startup.revenue_growth > 0 else 5
        }
        
        # Weights
        weights = {
            "team": 0.25,
            "traction": 0.20,
            "market_size": 0.15,
            "product": 0.15,
            "competitive_advantage": 0.10,
            "marketing": 0.10,
            "growth": 0.05
        }
        
        # Weighted average score
        weighted_score = sum(scores[k] * weights[k] for k in scores)
        
        # Compare to benchmark (assumed 6.0 is average)
        adjustment_factor = weighted_score / 6.0
        
        valuation = benchmark_valuation * adjustment_factor
        
        return {
            "method": "Scorecard",
            "benchmark_valuation": benchmark_valuation,
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "weighted_average_score": round(weighted_score, 2),
            "adjustment_factor": round(adjustment_factor, 2),
            "valuation": round(valuation, 0),
            "strengths": [k for k, v in scores.items() if v >= 8],
            "weaknesses": [k for k, v in scores.items() if v <= 5]
        }
    
    def berkus_method(self, startup: Startup) -> Dict:
        """Berkus method for pre-revenue startups"""
        # Only for early stage
        if startup.stage not in ["Pre-seed", "Seed"] and startup.revenue > 1e6:
            return {"error": "Berkus method only for early stage/pre-revenue startups"}
        
        # Maximum value per category ($500K each)
        max_value = 500e3
        
        # Assess each category
        sound_idea = min(max_value, startup.traction_score * 50e3)  # Based on traction proxy
        quality_management = min(max_value, startup.team_score * 50e3)  # Team quality
        
        # Product stage (assumed based on traction)
        if startup.traction_score >= 8:
            product_stage = max_value
        elif startup.traction_score >= 6:
            product_stage = max_value * 0.7
        else:
            product_stage = max_value * 0.4
        
        # Strategic relationships (based on team network assumed)
        strategic = max_value * 0.5 if startup.team_score >= 7 else max_value * 0.2
        
        # Product roll-out/sales (based on revenue)
        if startup.revenue > 0:
            rollout = min(max_value, startup.revenue * 0.1)  # 10% of ARR
        else:
            rollout = 0
        
        total_value = sound_idea + quality_management + product_stage + strategic + rollout
        
        return {
            "method": "Berkus",
            "sound_idea": round(sound_idea, 0),
            "quality_management": round(quality_management, 0),
            "product_stage": round(product_stage, 0),
            "strategic_relationships": round(strategic, 0),
            "product_rollout": round(rollout, 0),
            "total_valuation": round(total_value, 0),
            "risk_adjusted": round(total_value * 0.7, 0)
        }
    
    def risk_factor_summation(self, startup: Startup,
                             base_valuation: float = 2e6) -> Dict:
        """Risk Factor Summation Method"""
        # Start with base
        valuation = base_valuation
        adjustments = []
        
        # Risk factors (+$ for low risk, -$ for high risk)
        # Each rating: -2 (very high risk) to +2 (very low risk)
        
        factors = [
            ("management", startup.team_score / 5 - 1),  # -1 to +1
            ("stage", 0 if startup.stage in ["Series B", "Series C", "D+"] else -0.5),
            ("legislation", 0),  # Neutral
            ("manufacturing", 0.5 if startup.industry not in ["AI/ML", "SaaS"] else 0),
            ("sales_marketing", (startup.traction_score - 5) / 5),  # -1 to +1
            ("funding", 0.5),  # Assumed adequate
            ("competition", -0.3 if startup.market_size_tam > 10e9 else 0),  # Large market = more competition
            ("technology", 0.5 if startup.industry in ["AI/ML", "SaaS", "HealthTech"] else 0),
            ("litigation", 0),  # Neutral
            ("international", 0),  # Neutral
            ("reputation", 0.2),  # Slight positive
            ("exit", 0.5 if startup.revenue_growth > 1.0 else 0)  # Growth indicates exit potential
        ]
        
        # Each +/- is worth $250K
        adjustment_per_point = 250e3
        
        total_adjustment = 0
        for factor, rating in factors:
            adjustment = rating * adjustment_per_point
            total_adjustment += adjustment
            adjustments.append({
                "factor": factor,
                "rating": round(rating, 2),
                "adjustment": round(adjustment, 0)
            })
        
        final_valuation = max(500e3, base_valuation + total_adjustment)  # Minimum $500K
        
        return {
            "method": "Risk Factor Summation",
            "base_valuation": base_valuation,
            "adjustments": adjustments,
            "total_adjustment": round(total_adjustment, 0),
            "final_valuation": round(final_valuation, 0)
        }
    
    def reconcile_valuation(self, startup: Startup) -> Dict:
        """Reconcile all valuation methods"""
        valuations = []
        
        # ARR Multiple (if has revenue)
        if startup.revenue > 0:
            arr_val = self.arr_multiple_valuation(startup)
            if "valuation" in arr_val:
                valuations.append(("ARR Multiple", arr_val["valuation"], 0.35))
        
        # VC Method
        vc_val = self.venture_capital_method(startup)
        if "post_money_valuation" in vc_val:
            valuations.append(("VC Method", vc_val["post_money_valuation"], 0.30))
        
        # Scorecard
        score_val = self.scorecard_valuation(startup)
        if "valuation" in score_val:
            valuations.append(("Scorecard", score_val["valuation"], 0.20))
        
        # Berkus (early stage only)
        if startup.stage in ["Pre-seed", "Seed"]:
            berk_val = self.berkus_method(startup)
            if "total_valuation" in berk_val:
                valuations.append(("Berkus", berk_val["total_valuation"], 0.15))
        
        # Calculate weighted average
        total_weight = sum(w for _, _, w in valuations)
        weighted_valuation = sum(v * w for _, v, w in valuations) / total_weight if total_weight > 0 else 0
        
        # Value range
        values = [v for _, v, _ in valuations]
        if values:
            value_range = {
                "low": min(values),
                "high": max(values),
                "consensus": round(weighted_valuation, 0)
            }
        else:
            value_range = {"low": 0, "high": 0, "consensus": 0}
        
        return {
            "startup": startup.name,
            "stage": startup.stage,
            "individual_methods": {name: round(val, 0) for name, val, _ in valuations},
            "reconciled_valuation": round(weighted_valuation, 0),
            "valuation_range": value_range,
            "recommendation": "PROCEED" if weighted_valuation > startup.last_valuation * 1.5 else "NEGOTIATE" if weighted_valuation > startup.last_valuation else "PASS"
        }
    
    def comparable_analysis(self, startup: Startup,
                           comparables: List[Dict]) -> Dict:
        """Analyze against comparable transactions"""
        if not comparables:
            return {"error": "No comparables provided"}
        
        # Filter by stage and industry
        relevant = [
            c for c in comparables
            if c.get("stage") == startup.stage and c.get("industry") == startup.industry
        ]
        
        if not relevant:
            relevant = comparables  # Use all if no direct matches
        
        # Calculate average multiples
        arr_multiples = [c.get("valuation", 0) / c.get("revenue", 1) for c in relevant if c.get("revenue", 0) > 0]
        avg_multiple = sum(arr_multiples) / len(arr_multiples) if arr_multiples else 10
        
        # Apply to startup
        implied_valuation = startup.revenue * avg_multiple if startup.revenue > 0 else 0
        
        return {
            "num_comparables": len(relevant),
            "avg_arr_multiple": round(avg_multiple, 1),
            "median_valuation": round(sorted([c.get("valuation", 0) for c in relevant])[len(relevant)//2], 0) if relevant else 0,
            "implied_valuation": round(implied_valuation, 0),
            "comparables": relevant[:5]
        }
