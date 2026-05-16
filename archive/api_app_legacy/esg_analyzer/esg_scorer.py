"""ESG Scorer - Calculate Environmental, Social, Governance scores"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class ESGCategory(Enum):
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"

@dataclass
class ESGScore:
    ticker: str
    environmental: float
    social: float
    governance: float
    overall: float
    grade: str

class ESGScorer:
    """Calculate comprehensive ESG scores for companies"""
    
    def __init__(self):
        self.scoring_weights = {
            "environmental": 0.35,
            "social": 0.35,
            "governance": 0.30
        }
        
        # Industry benchmarks
        self.industry_benchmarks = {
            "technology": {"e": 70, "s": 65, "g": 75},
            "energy": {"e": 40, "s": 55, "g": 65},
            "financials": {"e": 60, "s": 60, "g": 70},
            "healthcare": {"e": 65, "s": 70, "g": 72},
            "consumer": {"e": 55, "s": 60, "g": 68},
            "industrials": {"e": 50, "s": 58, "g": 70}
        }
    
    def calculate_environmental_score(self, metrics: Dict) -> float:
        """Calculate environmental score from metrics"""
        scores = []
        
        # Carbon intensity (lower is better)
        if "carbon_intensity" in metrics:
            ci = metrics["carbon_intensity"]
            if ci < 50:
                scores.append(90)
            elif ci < 100:
                scores.append(75)
            elif ci < 200:
                scores.append(60)
            else:
                scores.append(40)
        
        # Renewable energy %
        if "renewable_pct" in metrics:
            re = metrics["renewable_pct"]
            scores.append(min(100, re * 1.2))  # Bonus for high renewable
        
        # Waste recycling rate
        if "recycling_rate" in metrics:
            scores.append(metrics["recycling_rate"])
        
        # Water usage efficiency
        if "water_efficiency" in metrics:
            scores.append(metrics["water_efficiency"])
        
        return sum(scores) / len(scores) if scores else 50
    
    def calculate_social_score(self, metrics: Dict) -> float:
        """Calculate social score from metrics"""
        scores = []
        
        # Employee satisfaction
        if "employee_satisfaction" in metrics:
            scores.append(metrics["employee_satisfaction"])
        
        # Diversity ratio
        if "diversity_score" in metrics:
            scores.append(metrics["diversity_score"])
        
        # Community investment
        if "community_investment_pct" in metrics:
            ci = metrics["community_investment_pct"]
            scores.append(min(100, ci * 5))  # Scale up percentage
        
        # Safety record (incidents per 1000 employees, lower is better)
        if "safety_incidents" in metrics:
            si = metrics["safety_incidents"]
            if si < 1:
                scores.append(95)
            elif si < 3:
                scores.append(80)
            elif si < 5:
                scores.append(65)
            else:
                scores.append(45)
        
        # Supply chain labor standards
        if "supply_chain_audit_score" in metrics:
            scores.append(metrics["supply_chain_audit_score"])
        
        return sum(scores) / len(scores) if scores else 50
    
    def calculate_governance_score(self, metrics: Dict) -> float:
        """Calculate governance score from metrics"""
        scores = []
        
        # Board independence %
        if "board_independence" in metrics:
            bi = metrics["board_independence"]
            scores.append(min(100, bi * 1.1))
        
        # Executive pay ratio (lower is better)
        if "ceo_pay_ratio" in metrics:
            ratio = metrics["ceo_pay_ratio"]
            if ratio < 50:
                scores.append(95)
            elif ratio < 100:
                scores.append(80)
            elif ratio < 200:
                scores.append(65)
            else:
                scores.append(45)
        
        # Audit quality
        if "audit_quality_score" in metrics:
            scores.append(metrics["audit_quality_score"])
        
        # Ethical violations (lower is better)
        if "ethical_violations" in metrics:
            ev = metrics["ethical_violations"]
            if ev == 0:
                scores.append(100)
            elif ev < 3:
                scores.append(80)
            elif ev < 5:
                scores.append(60)
            else:
                scores.append(30)
        
        # Shareholder rights
        if "shareholder_rights_score" in metrics:
            scores.append(metrics["shareholder_rights_score"])
        
        return sum(scores) / len(scores) if scores else 50
    
    def calculate_overall_esg(self, ticker: str, metrics: Dict, 
                             industry: str = None) -> ESGScore:
        """Calculate overall ESG score"""
        e_score = self.calculate_environmental_score(metrics)
        s_score = self.calculate_social_score(metrics)
        g_score = self.calculate_governance_score(metrics)
        
        overall = (
            e_score * self.scoring_weights["environmental"] +
            s_score * self.scoring_weights["social"] +
            g_score * self.scoring_weights["governance"]
        )
        
        # Grade assignment
        if overall >= 85:
            grade = "AAA"
        elif overall >= 75:
            grade = "AA"
        elif overall >= 65:
            grade = "A"
        elif overall >= 55:
            grade = "BBB"
        elif overall >= 45:
            grade = "BB"
        else:
            grade = "B"
        
        return ESGScore(
            ticker=ticker,
            environmental=round(e_score, 1),
            social=round(s_score, 1),
            governance=round(g_score, 1),
            overall=round(overall, 1),
            grade=grade
        )
    
    def compare_to_industry(self, esg_score: ESGScore, 
                           industry: str) -> Dict:
        """Compare company ESG to industry benchmark"""
        if industry not in self.industry_benchmarks:
            return {"error": "Industry not found"}
        
        benchmark = self.industry_benchmarks[industry]
        
        return {
            "ticker": esg_score.ticker,
            "industry": industry,
            "vs_industry": {
                "environmental": round(esg_score.environmental - benchmark["e"], 1),
                "social": round(esg_score.social - benchmark["s"], 1),
                "governance": round(esg_score.governance - benchmark["g"], 1),
                "overall": round(esg_score.overall - 
                    (benchmark["e"] * 0.35 + benchmark["s"] * 0.35 + benchmark["g"] * 0.30), 1)
            },
            "industry_leader": esg_score.overall > max(benchmark.values()) + 10,
            "laggard": esg_score.overall < min(benchmark.values()) - 10
        }
    
    def esg_momentum(self, ticker: str, 
                    historical_scores: List[ESGScore]) -> Dict:
        """Track ESG score improvement over time"""
        if len(historical_scores) < 2:
            return {"error": "Insufficient history"}
        
        scores = [s.overall for s in historical_scores]
        
        # Trend calculation
        first_half = statistics.mean(scores[:len(scores)//2])
        second_half = statistics.mean(scores[len(scores)//2:])
        
        trend = second_half - first_half
        
        return {
            "ticker": ticker,
            "esg_trend": "IMPROVING" if trend > 5 else "DECLINING" if trend < -5 else "STABLE",
            "score_change": round(trend, 1),
            "current_vs_historical_avg": round(scores[-1] - statistics.mean(scores), 1),
            "trajectory": "Positive" if trend > 2 else "Negative" if trend < -2 else "Neutral"
        }
    
    def screen_universe(self, universe_data: Dict[str, Dict],
                       min_score: float = 60,
                       exclude_controversial: bool = True) -> List[ESGScore]:
        """Screen universe for ESG-compliant investments"""
        results = []
        
        for ticker, data in universe_data.items():
            score = self.calculate_overall_esg(
                ticker, 
                data.get("metrics", {}),
                data.get("industry")
            )
            
            # Filter
            if score.overall >= min_score:
                if exclude_controversial and score.governance < 40:
                    continue
                results.append(score)
        
        return sorted(results, key=lambda x: x.overall, reverse=True)

import statistics
