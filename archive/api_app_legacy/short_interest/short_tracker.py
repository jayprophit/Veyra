"""Short Interest Tracker - Monitor short selling activity"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ShortInterest:
    ticker: str
    short_interest: int  # Shares short
    float: int  # Shares outstanding
    days_to_cover: float
    short_pct_float: float
    date: datetime

class ShortInterestTracker:
    """Track short interest and detect squeeze opportunities"""
    
    def __init__(self):
        self.data: Dict[str, ShortInterest] = {}
    
    def add_data(self, si: ShortInterest):
        self.data[si.ticker] = si
    
    def detect_squeeze_candidates(self, min_short_pct: float = 20.0, 
                                  min_days_to_cover: float = 5.0) -> List[Dict]:
        """Detect potential short squeeze candidates"""
        candidates = []
        
        for ticker, si in self.data.items():
            if si.short_pct_float >= min_short_pct and si.days_to_cover >= min_days_to_cover:
                candidates.append({
                    'ticker': ticker,
                    'short_pct_float': si.short_pct_float,
                    'days_to_cover': si.days_to_cover,
                    'squeeze_risk': 'HIGH' if si.short_pct_float > 40 else 'MEDIUM',
                    'setup': 'Potential short squeeze'
                })
        
        # Sort by short interest
        candidates.sort(key=lambda x: x['short_pct_float'], reverse=True)
        return candidates[:20]
    
    def get_short_squeeze_score(self, ticker: str) -> Dict:
        """Calculate short squeeze probability score"""
        if ticker not in self.data:
            return {}
        
        si = self.data[ticker]
        
        # Score components
        short_score = min(si.short_pct_float / 50, 1.0) * 40  # Max 40 pts
        dtc_score = min(si.days_to_cover / 10, 1.0) * 30  # Max 30 pts
        momentum_bonus = 30  # Would need price momentum data
        
        total_score = short_score + dtc_score
        
        return {
            'ticker': ticker,
            'squeeze_score': round(total_score, 1),
            'short_pct_float': si.short_pct_float,
            'days_to_cover': si.days_to_cover,
            'probability': 'HIGH' if total_score > 70 else 'MEDIUM' if total_score > 50 else 'LOW'
        }

# Usage
def find_squeeze_candidates() -> List[Dict]:
    tracker = ShortInterestTracker()
    return tracker.detect_squeeze_candidates()
