"""Adaptive Profile Manager - Handles changing life circumstances"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class EmploymentStatus(Enum):
    FULL_TIME_STABLE = 'full_time_stable'
    FULL_TIME_NEW = 'full_time_new'
    PART_TIME_VARIABLE = 'part_time_variable'
    GIG_ECONOMY = 'gig_economy'
    SELF_EMPLOYED = 'self_employed'
    UNEMPLOYED = 'unemployed'
    STUDENT = 'student'
    RETIRED = 'retired'

class LifeGoal(Enum):
    DEBT_ELIMINATION = 'debt_elimination'
    EMERGENCY_FUND = 'emergency_fund'
    WEALTH_BUILDING = 'wealth_building'
    HOME_DEPOSIT = 'home_deposit'
    RETIREMENT = 'retirement'

@dataclass
class AdaptiveUserProfile:
    user_id: str
    credit_score: int = 0
    monthly_income: float = 0
    employment_status: EmploymentStatus = EmploymentStatus.UNEMPLOYED
    total_debt: float = 0
    high_interest_debt: float = 0
    current_capital: float = 0
    risk_tolerance: str = 'moderate'
    time_horizon_years: int = 5
    primary_goal: LifeGoal = LifeGoal.WEALTH_BUILDING
    profile_history: List[Dict] = field(default_factory=list)

class AdaptiveProfileManager:
    """Manages user profiles that change over time"""
    
    def __init__(self):
        self.profiles = {}
    
    def create_profile(self, user_id: str, **kwargs) -> AdaptiveUserProfile:
        profile = AdaptiveUserProfile(user_id=user_id, **kwargs)
        self.profiles[user_id] = profile
        return profile
    
    def update_profile(self, user_id: str, changes: Dict) -> tuple:
        """Update profile and detect significant changes"""
        profile = self.profiles.get(user_id)
        if not profile:
            raise ValueError(f"Profile not found: {user_id}")
        
        old_snapshot = {
            'credit_score': profile.credit_score,
            'monthly_income': profile.monthly_income,
            'employment': profile.employment_status.value,
            'total_debt': profile.total_debt,
            'capital': profile.current_capital
        }
        
        # Apply changes
        for key, value in changes.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Detect changes
        detected = self._detect_changes(old_snapshot, profile)
        if detected:
            profile.profile_history.append({
                'timestamp': datetime.now(),
                'changes': changes,
                'significance': detected
            })
        
        return profile, detected
    
    def _detect_changes(self, old: Dict, profile: AdaptiveUserProfile) -> Optional[str]:
        """Detect significant changes warranting strategy review"""
        if profile.credit_score > old['credit_score'] + 50:
            return 'credit_improved'
        if profile.credit_score < old['credit_score'] - 50:
            return 'credit_dropped'
        if abs(profile.monthly_income - old['monthly_income']) / max(old['monthly_income'], 1) > 0.20:
            return 'income_changed'
        if profile.employment_status.value != old['employment']:
            return 'employment_changed'
        if old['total_debt'] > 0 and profile.total_debt == 0:
            return 'debt_paid_off'
        if abs(profile.total_debt - old['total_debt']) / max(old['total_debt'], 1) > 0.30:
            return 'debt_changed'
        return None
    
    def get_credit_tier(self, score: int) -> str:
        if score >= 800: return 'excellent'
        if score >= 670: return 'good'
        if score >= 580: return 'fair'
        if score > 0: return 'poor'
        return 'unknown'
    
    def get_available_strategies(self, profile: AdaptiveUserProfile) -> List[str]:
        """Get strategies based on full profile"""
        strategies = ['high_yield_savings', 'premium_bonds']
        credit = self.get_credit_tier(profile.credit_score)
        
        if profile.current_capital >= 25:
            strategies.extend(['government_bonds', 'gold_micro'])
        if profile.current_capital >= 50:
            strategies.extend(['p2p_lending', 'crypto_staking'])
        if credit in ['good', 'excellent'] and profile.current_capital >= 100:
            strategies.extend(['credit_arbitrage', 'margin_leverage'])
        if profile.current_capital >= 500:
            strategies.extend(['grid_bots', 'dividend_aristocrats', 'reits'])
        if profile.current_capital >= 2000:
            strategies.extend(['momentum_trading', 'options', 'private_credit'])
        
        return strategies
    
    def get_recommended_rule(self, profile: AdaptiveUserProfile) -> str:
        """Get recommended allocation rule"""
        if profile.high_interest_debt > 0:
            return 'debt_first_70_30'
        if profile.current_capital < 500:
            return '90_10'
        if profile.employment_status == EmploymentStatus.FULL_TIME_STABLE:
            if profile.risk_tolerance == 'aggressive':
                return '10_90'
            return '50_30_20'
        if profile.employment_status in [EmploymentStatus.GIG_ECONOMY, EmploymentStatus.PART_TIME_VARIABLE]:
            return 'equal_thirds'
        if profile.risk_tolerance == 'conservative':
            return '60_40'
        return '50_30_20'
    
    def generate_report(self, user_id: str) -> Dict:
        """Generate comprehensive profile report"""
        p = self.profiles.get(user_id)
        if not p:
            return {'error': 'Not found'}
        
        return {
            'user_id': user_id,
            'credit_tier': self.get_credit_tier(p.credit_score),
            'employment': p.employment_status.value,
            'monthly_income': f"£{p.monthly_income:,.0f}",
            'total_debt': f"£{p.total_debt:,.0f}",
            'current_capital': f"£{p.current_capital:,.0f}",
            'recommended_rule': self.get_recommended_rule(p),
            'available_strategies': len(self.get_available_strategies(p)),
            'life_changes_logged': len(p.profile_history)
        }
