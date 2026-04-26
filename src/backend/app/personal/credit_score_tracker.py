"""
Credit Score Tracking Module
UK Credit Score monitoring from Experian, Equifax, TransUnion
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CreditAgency(Enum):
    EXPERIAN = "experian"
    EQUIFAX = "equifax"
    TRANSUNION = "transunion"  # Previously CallCredit


class ScoreBand(Enum):
    EXCELLENT = (961, 999, "Excellent")
    GOOD = (881, 960, "Good")
    FAIR = (721, 880, "Fair")
    POOR = (561, 720, "Poor")
    VERY_POOR = (0, 560, "Very Poor")
    
    def __init__(self, min_score, max_score, label):
        self.min_score = min_score
        self.max_score = max_score
        self.label = label


@dataclass
class CreditScore:
    agency: CreditAgency
    score: int
    max_score: int
    date_checked: datetime
    score_band: str
    change_30d: int
    change_90d: int
    change_1y: int
    factors: Dict[str, Any]
    report_summary: Dict[str, Any]
    next_update: date


@dataclass
class CreditFactor:
    category: str
    status: str  # positive, negative, neutral
    impact: str  # high, medium, low
    description: str
    recommendation: str
    score_impact_estimate: int


@dataclass
class CreditReportItem:
    account_name: str
    account_type: str
    opened_date: date
    credit_limit: Optional[Decimal]
    current_balance: Decimal
    payment_status: str
    last_reported: date
    is_closed: bool
    missed_payments_12m: int
    missed_payments_24m: int
    utilization_percent: Optional[float]


@dataclass
class CreditInquiry:
    inquiry_date: date
    creditor: str
    inquiry_type: str  # hard, soft
    impact: Optional[str]


class CreditScoreTracker:
    """Track credit scores from all UK agencies"""
    
    # UK Score Ranges
    EXPERIAN_MAX = 999
    EQUIFAX_MAX = 700
    TRANSUNION_MAX = 710
    
    def __init__(self):
        self.scores: Dict[CreditAgency, List[CreditScore]] = {
            CreditAgency.EXPERIAN: [],
            CreditAgency.EQUIFAX: [],
            CreditAgency.TRANSUNION: []
        }
        self.report_items: List[CreditReportItem] = []
        self.inquiries: List[CreditInquiry] = []
        self.factors: Dict[str, List[CreditFactor]] = {}
        self.alerts_enabled = True
        
    def get_score_band(self, score: int, agency: CreditAgency) -> str:
        """Determine score band for agency"""
        # Normalize to 0-999 scale
        if agency == CreditAgency.EQUIFAX:
            normalized = int(score * 999 / 700)
        elif agency == CreditAgency.TRANSUNION:
            normalized = int(score * 999 / 710)
        else:
            normalized = score
        
        for band in ScoreBand:
            if band.min_score <= normalized <= band.max_score:
                return band.label
        return "Unknown"
    
    def add_score(
        self,
        agency: CreditAgency,
        score: int,
        factors: Dict[str, Any],
        report_summary: Optional[Dict[str, Any]] = None
    ) -> CreditScore:
        """Record new credit score reading"""
        # Get previous score for change calculation
        history = self.scores[agency]
        change_30d = 0
        change_90d = 0
        change_1y = 0
        
        if history:
            last = history[-1]
            change_30d = score - last.score
            
            # Find 90 days ago
            for h in reversed(history):
                if (datetime.now() - h.date_checked).days <= 90:
                    change_90d = score - h.score
                    break
            
            # Find 1 year ago
            for h in reversed(history):
                if (datetime.now() - h.date_checked).days <= 365:
                    change_1y = score - h.score
                    break
        
        max_score = {
            CreditAgency.EXPERIAN: self.EXPERIAN_MAX,
            CreditAgency.EQUIFAX: self.EQUIFAX_MAX,
            CreditAgency.TRANSUNION: self.TRANSUNION_MAX
        }[agency]
        
        score_record = CreditScore(
            agency=agency,
            score=score,
            max_score=max_score,
            date_checked=datetime.now(),
            score_band=self.get_score_band(score, agency),
            change_30d=change_30d,
            change_90d=change_90d,
            change_1y=change_1y,
            factors=factors,
            report_summary=report_summary or {},
            next_update=date.today()  # Typically monthly
        )
        
        self.scores[agency].append(score_record)
        
        # Check for significant changes and alert
        if abs(change_30d) >= 20 and self.alerts_enabled:
            logger.warning(f"Significant credit score change ({agency.value}): {change_30d:+d} points")
        
        logger.info(f"Credit score recorded: {agency.value} = {score}/{max_score} ({score_record.score_band})")
        return score_record
    
    def get_latest_scores(self) -> Dict[str, Any]:
        """Get latest scores from all agencies"""
        latest = {}
        for agency, history in self.scores.items():
            if history:
                score = history[-1]
                latest[agency.value] = {
                    "score": score.score,
                    "max_score": score.max_score,
                    "band": score.score_band,
                    "percentile": int(score.score / score.max_score * 100),
                    "change_30d": score.change_30d,
                    "last_checked": score.date_checked.isoformat(),
                    "next_update": score.next_update.isoformat()
                }
        return latest
    
    def get_score_history(
        self,
        agency: CreditAgency,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """Get score history for agency"""
        history = self.scores[agency]
        cutoff = datetime.now().replace(day=1)  # Start of current month
        
        # Filter to last N months
        filtered = [
            h for h in history 
            if (cutoff - h.date_checked).days <= months * 30
        ]
        
        return [
            {
                "date": h.date_checked.isoformat(),
                "score": h.score,
                "band": h.score_band
            }
            for h in filtered
        ]
    
    def analyze_factors(self) -> List[CreditFactor]:
        """Analyze credit factors and provide recommendations"""
        factors = []
        
        # Payment History (35% impact)
        late_payments = sum(1 for item in self.report_items if item.missed_payments_12m > 0)
        if late_payments == 0:
            factors.append(CreditFactor(
                category="Payment History",
                status="positive",
                impact="high",
                description="Perfect payment history in last 12 months",
                recommendation="Keep making payments on time",
                score_impact_estimate=+50
            ))
        elif late_payments >= 3:
            factors.append(CreditFactor(
                category="Payment History",
                status="negative",
                impact="high",
                description=f"{late_payments} late payments in last 12 months",
                recommendation="Set up direct debits to ensure on-time payments",
                score_impact_estimate=-80
            ))
        
        # Credit Utilization (30% impact)
        revolving = [item for item in self.report_items if item.utilization_percent is not None]
        if revolving:
            avg_util = sum(item.utilization_percent for item in revolving) / len(revolving)
            
            if avg_util < 10:
                factors.append(CreditFactor(
                    category="Credit Utilization",
                    status="positive",
                    impact="high",
                    description=f"Excellent utilization at {avg_util:.1f}%",
                    recommendation="Maintain low balances",
                    score_impact_estimate=+40
                ))
            elif avg_util > 75:
                factors.append(CreditFactor(
                    category="Credit Utilization",
                    status="negative",
                    impact="high",
                    description=f"High utilization at {avg_util:.1f}%",
                    recommendation="Pay down balances to below 30%",
                    score_impact_estimate=-60
                ))
        
        # Credit Age (15% impact)
        if self.report_items:
            oldest = min(item.opened_date for item in self.report_items if not item.is_closed)
            age_years = (date.today() - oldest).days / 365
            
            if age_years > 5:
                factors.append(CreditFactor(
                    category="Credit History",
                    status="positive",
                    impact="medium",
                    description=f"Long credit history: {age_years:.1f} years",
                    recommendation="Keep old accounts open",
                    score_impact_estimate=+25
                ))
        
        # Credit Mix (10% impact)
        account_types = set(item.account_type for item in self.report_items)
        if len(account_types) >= 3:
            factors.append(CreditFactor(
                category="Credit Mix",
                status="positive",
                impact="low",
                description="Diverse credit portfolio",
                recommendation="Maintain mix of credit types",
                score_impact_estimate=+15
            ))
        
        # Recent Inquiries (10% impact)
        recent_hard = [
            i for i in self.inquiries 
            if i.inquiry_type == "hard" and (date.today() - i.inquiry_date).days <= 90
        ]
        
        if len(recent_hard) >= 3:
            factors.append(CreditFactor(
                category="Recent Inquiries",
                status="negative",
                impact="medium",
                description=f"{len(recent_hard)} hard inquiries in last 90 days",
                recommendation="Avoid applying for new credit for 6 months",
                score_impact_estimate=-30
            ))
        
        return factors
    
    def get_improvement_plan(self) -> Dict[str, Any]:
        """Generate personalized credit improvement plan"""
        factors = self.analyze_factors()
        
        negative = [f for f in factors if f.status == "negative"]
        positive = [f for f in factors if f.status == "positive"]
        
        # Sort by impact and potential score gain
        negative.sort(key=lambda x: x.score_impact_estimate)
        
        plan = {
            "current_score_summary": self.get_latest_scores(),
            "priority_actions": [
                {
                    "priority": i + 1,
                    "category": f.category,
                    "action": f.recommendation,
                    "potential_impact": f"{f.score_impact_estimate:+d} points",
                    "timeframe": "1-3 months" if f.impact == "high" else "3-6 months"
                }
                for i, f in enumerate(negative[:3])
            ],
            "strengths": [
                {
                    "category": f.category,
                    "description": f.description,
                    "maintain": f.recommendation
                }
                for f in positive
            ],
            "estimated_score_potential": None
        }
        
        # Calculate potential score
        if negative:
            potential_gain = sum(f.score_impact_estimate for f in negative if f.score_impact_estimate > 0)
            for agency_scores in self.scores.values():
                if agency_scores:
                    current = agency_scores[-1].score
                    plan["estimated_score_potential"] = {
                        "agency": agency_scores[-1].agency.value,
                        "current": current,
                        "potential": min(agency_scores[-1].max_score, current + abs(potential_gain)),
                        "improvement_potential": abs(potential_gain)
                    }
                    break
        
        return plan
    
    def simulate_score_change(
        self,
        action: str,
        current_agency: CreditAgency = CreditAgency.EXPERIAN
    ) -> Dict[str, Any]:
        """Simulate impact of credit actions"""
        simulations = {
            "pay_down_credit_cards": {
                "description": "Pay credit card balances to below 30% utilization",
                "impact_range": "+20 to +60 points",
                "timeframe": "1-2 months",
                "confidence": "high"
            },
            "remove_late_payments": {
                "description": "Get late payment removed via goodwill letter",
                "impact_range": "+30 to +80 points",
                "timeframe": "1-3 months",
                "confidence": "medium"
            },
            "become_authorized_user": {
                "description": "Become authorized user on old, high-limit account",
                "impact_range": "+10 to +40 points",
                "timeframe": "1 month",
                "confidence": "medium"
            },
            "dispute_errors": {
                "description": "Dispute and remove credit report errors",
                "impact_range": "+20 to +100 points",
                "timeframe": "1-3 months",
                "confidence": "high"
            },
            "stop_hard_inquiries": {
                "description": "No new credit applications for 6 months",
                "impact_range": "+5 to +20 points",
                "timeframe": "3-6 months",
                "confidence": "high"
            },
            "pay_off_collections": {
                "description": "Pay off collections (may not remove from report)",
                "impact_range": "0 to +50 points",
                "timeframe": "Immediate to 2 years",
                "confidence": "low"
            }
        }
        
        return simulations.get(action, {"error": "Unknown action"})


# Global credit tracker
_credit_tracker: Optional[CreditScoreTracker] = None


def get_credit_tracker() -> CreditScoreTracker:
    """Get or create global credit tracker"""
    global _credit_tracker
    if _credit_tracker is None:
        _credit_tracker = CreditScoreTracker()
    return _credit_tracker
