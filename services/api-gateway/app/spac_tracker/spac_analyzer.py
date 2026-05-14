"""
SPAC Analyzer (Special Purpose Acquisition Company)
====================================================
Track SPAC lifecycle: IPO, target search, merger, de-SPAC
Redemption analysis, arbitrage opportunities, PIPE investments
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, date
from enum import Enum


class SPACStage(Enum):
    PRE_IPO = "pre_ipo"
    SEARCHING = "searching"  # Looking for target
    ANNOUNCED = "announced"  # LOI signed
    DEFINITIVE = "definitive"  # Definitive agreement
    MERGED = "merged"  # De-SPAC complete
    LIQUIDATED = "liquidated"


@dataclass
class SPAC:
    ticker: str
    name: str
    ipo_date: date
    trust_value: float  # $ per share in trust
    stage: str
    target_company: Optional[str]
    target_enterprise_value: Optional[float]
    redemption_rate: Optional[float]  # % of shares redeemed
    merger_deadline: Optional[date]
    sponsor_promote_pct: float  # 20% typical
    
    def time_to_deadline(self) -> int:
        """Days to merger deadline"""
        if self.merger_deadline:
            return (self.merger_deadline - date.today()).days
        return 0


class SPACAnalyzer:
    """Analyze SPAC investments and opportunities"""
    
    # Current market conditions
    MARKET_CONDITIONS = {
        'avg_redemption_rate': 0.85,  # 85% redemptions common in 2023-2024
        'trust_yield': 0.055,  # 5.5% on T-bills
        'typical_sponsor_promote': 0.20,
        'avg_time_to_merger_months': 18
    }
    
    def analyze_spac_arbitrage(self, spac: SPAC, 
                               current_price: float) -> Dict:
        """
        Analyze SPAC arbitrage opportunity
        
        Classic SPAC arbitrage:
        - Buy at discount to trust value
        - Redeem if deal is bad
        - Participate in upside if deal is good
        """
        trust_value = spac.trust_value
        
        # Arbitrage metrics
        discount = (trust_value - current_price) / trust_value
        annualized_yield = discount * (12 / 18)  # Assuming 18 month avg
        
        # Risk assessment
        time_to_deadline = spac.time_to_deadline()
        
        if time_to_deadline < 90:
            urgency = 'HIGH - Deadline approaching'
        elif time_to_deadline < 180:
            urgency = 'MEDIUM - Monitor closely'
        else:
            urgency = 'LOW - Time remaining'
        
        return {
            'ticker': spac.ticker,
            'trust_value': trust_value,
            'current_price': current_price,
            'discount_to_trust': round(discount * 100, 1),
            'annualized_return_potential': round(annualized_yield * 100, 1),
            'days_to_deadline': time_to_deadline,
            'urgency': urgency,
            'arbitrage_opportunity': discount > 0.02,  # >2% discount
            'recommendation': self._arbitrage_recommendation(discount, time_to_deadline)
        }
    
    def _arbitrage_recommendation(self, discount: float, 
                                   days_to_deadline: int) -> str:
        """Generate arbitrage recommendation"""
        if discount > 0.05 and days_to_deadline < 90:
            return "STRONG_BUY - High discount, near deadline"
        elif discount > 0.03:
            return "BUY - Attractive discount to trust"
        elif discount > 0.01:
            return "HOLD - Small discount, monitor"
        else:
            return "PASS - No arbitrage margin"
    
    def evaluate_merger(self, spac: SPAC, 
                       target_metrics: Dict) -> Dict:
        """
        Evaluate proposed SPAC merger
        
        Key factors:
        - Valuation vs comparables
        - Growth projections
        - Sponsor quality
        - PIPE participation
        """
        # Valuation analysis
        ev = spac.target_enterprise_value or 0
        revenue = target_metrics.get('revenue', 0)
        growth_rate = target_metrics.get('growth_rate', 0)
        
        ev_revenue = ev / revenue if revenue > 0 else 0
        
        # Quality score
        score = 50  # Base
        
        # Growth bonus
        if growth_rate > 0.50:
            score += 20
        elif growth_rate > 0.30:
            score += 15
        elif growth_rate > 0.15:
            score += 10
        
        # Valuation penalty
        if ev_revenue > 15:
            score -= 20
        elif ev_revenue > 10:
            score -= 10
        elif ev_revenue < 5:
            score += 10
        
        # PIPE validation
        pipe_size = target_metrics.get('pipe_size', 0)
        if pipe_size > ev * 0.20:  # PIPE > 20% of EV
            score += 10
        
        return {
            'ticker': spac.ticker,
            'target': spac.target_company,
            'enterprise_value': round(ev, 0),
            'ev_revenue_multiple': round(ev_revenue, 1),
            'target_growth_rate': growth_rate,
            'quality_score': min(score, 100),
            'assessment': self._merger_assessment(score),
            'vote_recommendation': 'FOR' if score > 60 else 'AGAINST' if score < 40 else 'REVIEW'
        }
    
    def _merger_assessment(self, score: int) -> str:
        """Assess merger quality"""
        if score >= 70:
            return 'ATTRACTIVE - Strong growth, reasonable valuation'
        elif score >= 50:
            return 'FAIR - Reasonable but not compelling'
        elif score >= 30:
            return 'WEAK - Consider redemption'
        else:
            return 'POOR - High risk of failure'
    
    def get_spac_market_overview(self) -> Dict:
        """Get SPAC market overview"""
        return {
            'market_conditions': {
                'status': 'CHALLENGING',
                'avg_redemption_rate': '85%',
                'new_issuance': 'SLOW - Few new SPACs launching',
                'merger_completion': 'DIFFICULT - Many extensions needed'
            },
            'arbitrage_opportunities': {
                'trust_yield': '5.5%',
                'typical_discount': '2-5%',
                'strategy': 'Buy near trust value, redeem if deal weak',
                'risk': 'Deal approval required, deadline risk'
            },
            'de_spac_performance': {
                '2021_cohort': '-60% avg',
                '2022_cohort': '-40% avg',
                '2023_cohort': '-25% avg',
                'trend': 'IMPROVING - Better quality targets'
            },
            'investment_strategies': {
                'pre_deal': 'Trust value arbitrage',
                'post_announcement': 'Evaluate merger quality',
                'post_merger': 'Evaluate as regular equity'
            }
        }
    
    def calculate_redemption_value(self, spac: SPAC,
                                   expected_redemption: float = 0.85) -> Dict:
        """Calculate post-redemption pro-forma"""
        trust_value = spac.trust_value
        
        # Post-redemption cash
        remaining_pct = 1 - expected_redemption
        remaining_cash = trust_value * remaining_pct
        
        # Sponsor dilution
        sponsor_promote = spac.sponsor_promote_pct
        effective_promote = sponsor_promote * remaining_pct
        
        return {
            'trust_value_per_share': trust_value,
            'expected_redemption_rate': expected_redemption,
            'remaining_cash_per_share': round(remaining_cash, 2),
            'sponsor_promote_post_redemption': round(effective_promote * 100, 1),
            'pro_forma_ownership': {
                'public': round((1 - effective_promote) * 100, 1),
                'sponsor': round(effective_promote * 100, 1)
            }
        }


# Usage
def analyze_spac_arbitrage(ticker: str, trust_value: float, 
                           current_price: float, deadline_days: int) -> Dict:
    """Quick SPAC arbitrage analysis"""
    analyzer = SPACAnalyzer()
    
    spac = SPAC(
        ticker=ticker,
        name=ticker,
        ipo_date=date.today(),
        trust_value=trust_value,
        stage=SPACStage.SEARCHING.value,
        target_company=None,
        target_enterprise_value=None,
        redemption_rate=None,
        merger_deadline=date.today() + __import__('datetime').timedelta(days=deadline_days),
        sponsor_promote_pct=0.20
    )
    
    return analyzer.analyze_spac_arbitrage(spac, current_price)


def evaluate_spac_merger(ticker: str, target: str, ev: float,
                         revenue: float, growth: float) -> Dict:
    """Evaluate proposed merger"""
    analyzer = SPACAnalyzer()
    
    spac = SPAC(
        ticker=ticker,
        name=ticker,
        ipo_date=date.today(),
        trust_value=10.00,
        stage=SPACStage.ANNOUNCED.value,
        target_company=target,
        target_enterprise_value=ev,
        redemption_rate=None,
        merger_deadline=None,
        sponsor_promote_pct=0.20
    )
    
    metrics = {
        'revenue': revenue,
        'growth_rate': growth
    }
    
    return analyzer.evaluate_merger(spac, metrics)
