"""
Litigation Finance Tracker
===========================
Track litigation finance investments, case outcomes
Portfolio IRR, case duration, settlement analysis
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class CaseStatus(Enum):
    FUNDED = "funded"
    ACTIVE = "active"
    SETTLED = "settled"
    WON = "won"
    LOST = "lost"
    APPEAL = "on_appeal"


class CaseType(Enum):
    COMMERCIAL = "commercial"
    IP = "intellectual_property"
    CLASS_ACTION = "class_action"
    ARBITRATION = "arbitration"
    MASS_TORT = "mass_tort"
    INSURANCE = "insurance"


@dataclass
class LitigationCase:
    case_name: str
    case_type: str
    funded_amount: float
    commitment_date: date
    expected_duration_months: int
    potential_recovery_min: float
    potential_recovery_max: float
    status: str
    defendant_credit_quality: str
    jurisdiction: str
    
    # Outcome tracking
    settlement_amount: Optional[float] = None
    settlement_date: Optional[date] = None
    legal_fees_incurred: float = 0


class LitigationFinanceTracker:
    """Track litigation finance investment portfolio"""
    
    def __init__(self):
        self.cases: List[LitigationCase] = []
    
    def add_case(self, case: LitigationCase):
        """Add litigation case to portfolio"""
        self.cases.append(case)
    
    def get_portfolio_metrics(self) -> Dict:
        """Calculate litigation portfolio metrics"""
        if not self.cases:
            return {'error': 'No cases in portfolio'}
        
        total_funded = sum(c.funded_amount for c in self.cases)
        
        # Case counts by status
        by_status = {}
        for case in self.cases:
            status = case.status
            if status not in by_status:
                by_status[status] = {'count': 0, 'funded': 0}
            by_status[status]['count'] += 1
            by_status[status]['funded'] += case.funded_amount
        
        # Resolved cases
        resolved = [c for c in self.cases 
                   if c.status in ['settled', 'won', 'lost']]
        
        if resolved:
            # Calculate realized returns
            total_recovered = sum(
                (c.settlement_amount or 0) for c in resolved
            )
            total_invested_resolved = sum(c.funded_amount for c in resolved)
            
            realized_return = ((total_recovered - total_invested_resolved) 
                               / total_invested_resolved * 100) if total_invested_resolved > 0 else 0
            
            # Win rate
            wins = len([c for c in resolved if c.status in ['settled', 'won']])
            win_rate = wins / len(resolved) * 100
            
            # Average duration
            avg_duration = sum(
                (c.settlement_date - c.commitment_date).days / 30
                for c in resolved if c.settlement_date
            ) / len(resolved) if resolved else 0
        else:
            realized_return = 0
            win_rate = 0
            avg_duration = 0
            total_recovered = 0
        
        # Expected portfolio value (unrealized)
        unrealized_cases = [c for c in self.cases if c.status not in ['settled', 'won', 'lost']]
        expected_unrealized = sum(
            (c.potential_recovery_min + c.potential_recovery_max) / 2 * 0.6  # 60% probability
            for c in unrealized_cases
        )
        
        return {
            'total_cases': len(self.cases),
            'total_funded': round(total_funded, 0),
            'cases_by_status': by_status,
            'resolved_cases': len(resolved),
            'realized_return_pct': round(realized_return, 1),
            'win_rate_pct': round(win_rate, 1),
            'average_duration_months': round(avg_duration, 1),
            'total_recovered': round(total_recovered, 0),
            'expected_unrealized_value': round(expected_unrealized, 0),
            'blended_portfolio_irr_estimate': self._estimate_portfolio_irr(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _estimate_portfolio_irr(self) -> float:
        """Estimate blended portfolio IRR"""
        # Simplified IRR estimate based on case mix
        # Typical litigation finance returns: 25-40% IRR
        
        if not self.cases:
            return 0
        
        case_irrs = []
        for case in self.cases:
            if case.status in ['settled', 'won'] and case.settlement_date:
                # Calculate actual IRR
                months = (case.settlement_date - case.commitment_date).days / 30
                if months > 0 and case.funded_amount > 0:
                    total_return = (case.settlement_amount or 0) - case.funded_amount
                    annual_return = (total_return / case.funded_amount) * (12 / months)
                    case_irrs.append(annual_return * 100)
            else:
                # Expected IRR by case type
                expected = {
                    CaseType.COMMERCIAL.value: 30,
                    CaseType.IP.value: 35,
                    CaseType.MASS_TORT.value: 40,
                    CaseType.CLASS_ACTION.value: 25,
                    CaseType.ARBITRATION.value: 28,
                    CaseType.INSURANCE.value: 32
                }
                case_irrs.append(expected.get(case.case_type, 30))
        
        return round(sum(case_irrs) / len(case_irrs), 1) if case_irrs else 0
    
    def get_case_diligence_checklist(self) -> Dict:
        """Get litigation finance due diligence checklist"""
        return {
            'legal_merits': [
                'Probability of success (min 60%)',
                'Damages quantification',
                'Liability clarity',
                'Precedent analysis'
            ],
            'financial': [
                'Defendant ability to pay',
                'Insurance coverage',
                'Adequate damages vs investment',
                'Fee structure (contingency %)'
            ],
            'timeline': [
                'Expected duration (prefer < 3 years)',
                'Appeal risk',
                'Discovery scope',
                'Court backlog'
            ],
            'structural': [
                'Control rights (settlement approval)',
                'Seniority to other claims',
                'Confidentiality requirements',
                'Regulatory compliance'
            ]
        }
    
    def analyze_litigation_stocks(self) -> Dict:
        """Analyze publicly traded litigation finance companies"""
        return {
            'BUR': {
                'name': 'Burford Capital',
                'market_cap': '$2.5B',
                'focus': 'Commercial litigation, arbitration',
                'portfolio_size': '$3B+',
                'returns': '30%+ IRR historical'
            },
            'LIT': {
                'name': 'Litigation Capital',
                'market_cap': '$500M',
                'focus': 'Insolvency, asset recovery',
                'specialty': 'UK/European cases'
            },
            'investment_thesis': {
                'bullish': [
                    'Non-correlated returns',
                    'Growing legal finance acceptance',
                    'Institutional capital flowing in',
                    'High barriers to entry'
                ],
                'risks': [
                    'Concentration risk',
                    'Long duration',
                    'Binary outcomes',
                    'Regulatory scrutiny'
                ]
            }
        }


# Usage
def analyze_litigation_portfolio(cases: List[Dict]) -> Dict:
    """Quick litigation portfolio analysis"""
    tracker = LitigationFinanceTracker()
    
    for c in cases:
        case = LitigationCase(
            case_name=c['name'],
            case_type=c['type'],
            funded_amount=c['funded'],
            commitment_date=c['date'],
            expected_duration_months=c.get('duration', 24),
            potential_recovery_min=c.get('recovery_min', c['funded'] * 2),
            potential_recovery_max=c.get('recovery_max', c['funded'] * 5),
            status=c.get('status', 'funded'),
            defendant_credit_quality=c.get('credit', 'investment_grade'),
            jurisdiction=c.get('jurisdiction', 'US'),
            settlement_amount=c.get('settlement'),
            settlement_date=c.get('settlement_date')
        )
        tracker.add_case(case)
    
    return tracker.get_portfolio_metrics()


def get_litigation_due_diligence() -> Dict:
    """Get litigation finance DD checklist"""
    tracker = LitigationFinanceTracker()
    return tracker.get_case_diligence_checklist()
