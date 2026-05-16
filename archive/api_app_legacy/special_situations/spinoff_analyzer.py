"""Spinoff Analyzer - Corporate spinoff analysis"""
from typing import Dict

class SpinoffAnalyzer:
    """Analyze spinoff transactions"""
    
    def analyze_spinoff(self, parent_value: float, subsidiary_value: float,
                       synergy_loss: float) -> Dict:
        """Analyze spinoff value creation"""
        combined_pre = parent_value + subsidiary_value + synergy_loss
        
        # Spinoff typically unlocks 10-20% value
        focus_premium = subsidiary_value * 0.15
        
        combined_post = parent_value + subsidiary_value + focus_premium
        
        return {
            "pre_spinoff_value": combined_pre,
            "post_spinoff_value": combined_post,
            "value_unlocked": combined_post - combined_pre,
            "unlock_pct": round((combined_post - combined_pre) / combined_pre * 100, 1),
            "parent_focus_multiple": 1.1,
            "subsidiary_focus_multiple": 1.25
        }
    
    def whenissued_trading(self, parent_shares: int, ratio: float) -> Dict:
        """Calculate when-issued trading values"""
        # Ratio = subsidiary shares per parent share
        subsidiary_shares = parent_shares * ratio
        
        return {
            "parent_shares_retain": parent_shares,
            "subsidiary_shares_receive": subsidiary_shares,
            "when_issued_ratio": ratio,
            "typical_discount": 0.02  # 2% discount pre-spin
        }
