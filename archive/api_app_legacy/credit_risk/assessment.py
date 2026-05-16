"""Credit Risk Assessment."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CreditRating(Enum):
    AAA = "AAA"
    AA = "AA"
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"

@dataclass
class CreditScore:
    score: int
    rating: CreditRating
    probability_of_default: float
    factors: Dict[str, float]
    confidence: float
    assessment_date: datetime

class CreditRiskAssessment:
    """Credit risk assessment for counterparties."""
    
    def __init__(self):
        self.credit_scores: Dict[str, CreditScore] = {}
        self.exposure_limits: Dict[str, float] = {}
        
        self.pd_by_rating = {
            CreditRating.AAA: 0.0001, CreditRating.AA: 0.0005,
            CreditRating.A: 0.001, CreditRating.BBB: 0.002,
            CreditRating.BB: 0.01, CreditRating.B: 0.05,
            CreditRating.CCC: 0.20, CreditRating.CC: 0.40,
            CreditRating.C: 0.65, CreditRating.D: 1.0
        }
    
    async def assess_creditworthiness(self,
                                     entity_id: str,
                                     financial_data: Dict[str, Any],
                                     payment_history: List[Dict],
                                     industry: str) -> CreditScore:
        """Assess creditworthiness."""
        
        factor_scores = {
            'liquidity': min(100, (financial_data.get('current_assets', 0) / 
                          max(financial_data.get('current_liabilities', 1), 1)) * 40),
            'leverage': max(0, 100 - (financial_data.get('total_debt', 0) / 
                          max(financial_data.get('equity', 1), 1)) * 20),
            'profitability': min(100, max(0, (financial_data.get('net_income', 0) / 
                             max(financial_data.get('equity', 1), 1)) * 500 + 50)),
            'payment_history': (sum(1 for p in payment_history 
                               if p.get('days_late', 0) == 0) / len(payment_history) * 100) if payment_history else 50,
            'cash_flow': min(100, (financial_data.get('ebitda', 0) / 
                          max(financial_data.get('interest_expense', 1), 1)) * 10),
            'industry_risk': {'technology': 85, 'healthcare': 80, 'financials': 70, 'energy': 60}.get(industry.lower(), 70)
        }
        
        weights = {'liquidity': 0.20, 'leverage': 0.25, 'profitability': 0.20, 
                  'payment_history': 0.20, 'cash_flow': 0.10, 'industry_risk': 0.05}
        
        composite_score = sum(factor_scores[f] * weights[f] for f in factor_scores)
        
        rating = self._score_to_rating(composite_score)
        
        credit_score = CreditScore(
            score=int(composite_score),
            rating=rating,
            probability_of_default=self.pd_by_rating[rating],
            factors=factor_scores,
            confidence=0.85,
            assessment_date=datetime.now()
        )
        
        self.credit_scores[entity_id] = credit_score
        return credit_score
    
    def _score_to_rating(self, score: float) -> CreditRating:
        if score >= 90: return CreditRating.AAA
        elif score >= 85: return CreditRating.AA
        elif score >= 80: return CreditRating.A
        elif score >= 70: return CreditRating.BBB
        elif score >= 60: return CreditRating.BB
        elif score >= 50: return CreditRating.B
        elif score >= 40: return CreditRating.CCC
        elif score >= 30: return CreditRating.CC
        elif score >= 20: return CreditRating.C
        else: return CreditRating.D
    
    async def monitor_exposure(self, entity_id: str, current_exposure: float) -> Dict[str, Any]:
        if entity_id not in self.credit_scores:
            return {'error': 'Entity not assessed'}
        
        limit = self.exposure_limits.get(entity_id, 1000000)
        utilization = current_exposure / limit if limit > 0 else 0
        
        return {
            'entity_id': entity_id,
            'current_exposure': current_exposure,
            'exposure_limit': limit,
            'utilization_pct': round(utilization * 100, 2),
            'status': 'breached' if utilization > 1 else 'warning' if utilization > 0.8 else 'normal'
        }

credit_assessment = CreditRiskAssessment()
