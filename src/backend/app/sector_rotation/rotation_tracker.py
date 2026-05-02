"""
Sector Rotation Tracker
=======================
Track sector performance, relative strength, and rotation patterns
Identify leading/lagging sectors, momentum shifts
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class Sector(Enum):
    TECHNOLOGY = "XLK"
    HEALTHCARE = "XLV"
    FINANCIALS = "XLF"
    ENERGY = "XLE"
    CONSUMER_DISC = "XLY"
    CONSUMER_STAPLES = "XLP"
    INDUSTRIALS = "XLI"
    MATERIALS = "XLB"
    UTILITIES = "XLU"
    REAL_ESTATE = "XLRE"
    COMMUNICATION = "XLC"


@dataclass
class SectorPerformance:
    """Sector performance metrics"""
    sector: str
    ticker: str
    return_1d: float
    return_1w: float
    return_1m: float
    return_3m: float
    return_ytd: float
    relative_strength: float
    momentum_score: float


class SectorRotationTracker:
    """
    Track sector rotation and relative performance
    
    Features:
    - Relative strength analysis
    - Momentum ranking
    - Rotation detection
    - Cyclical vs defensive positioning
    """
    
    SECTOR_ETFS = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Energy': 'XLE',
        'Consumer Disc': 'XLY',
        'Consumer Staples': 'XLP',
        'Industrials': 'XLI',
        'Materials': 'XLB',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Communication': 'XLC'
    }
    
    # Sector classifications
    CYCLICAL_SECTORS = ['Technology', 'Consumer Disc', 'Industrials', 'Materials', 'Energy', 'Financials']
    DEFENSIVE_SECTORS = ['Consumer Staples', 'Utilities', 'Healthcare', 'Real Estate']
    GROWTH_SECTORS = ['Technology', 'Communication', 'Consumer Disc']
    VALUE_SECTORS = ['Financials', 'Energy', 'Materials', 'Utilities']
    
    def __init__(self, spy_benchmark: float = 0):
        self.benchmark_return = spy_benchmark
        self.sector_data: Dict[str, SectorPerformance] = {}
    
    def add_sector_data(self, performance: SectorPerformance):
        """Add sector performance data"""
        self.sector_data[performance.sector] = performance
    
    def calculate_relative_strength(self, sector_returns: pd.DataFrame,
                                   benchmark_col: str = 'SPY') -> pd.DataFrame:
        """Calculate relative strength vs benchmark"""
        rs_df = sector_returns.div(sector_returns[benchmark_col], axis=0) - 1
        return rs_df
    
    def rank_sectors_by_momentum(self, lookback: str = '1M') -> List[Dict]:
        """Rank sectors by momentum score"""
        if not self.sector_data:
            return []
        
        # Get momentum field based on lookback
        momentum_field = f'return_{lookback.lower()}' if lookback != '1M' else 'return_1m'
        
        ranked = []
        for sector, data in self.sector_data.items():
            momentum = getattr(data, momentum_field, data.return_1m)
            
            ranked.append({
                'sector': sector,
                'ticker': data.ticker,
                'momentum': momentum,
                'relative_strength': data.relative_strength,
                'score': data.momentum_score,
                'rank': 0  # Will be set after sorting
            })
        
        # Sort by momentum
        ranked.sort(key=lambda x: x['momentum'], reverse=True)
        
        # Assign ranks
        for i, item in enumerate(ranked):
            item['rank'] = i + 1
        
        return ranked
    
    def detect_rotation(self, current_period: Dict[str, float],
                       previous_period: Dict[str, float]) -> List[Dict]:
        """
        Detect sector rotation between periods
        
        Returns list of sectors with significant rank changes
        """
        rotations = []
        
        # Get current and previous rankings
        current_ranked = sorted(current_period.items(), key=lambda x: x[1], reverse=True)
        previous_ranked = sorted(previous_period.items(), key=lambda x: x[1], reverse=True)
        
        current_ranks = {sector: rank for rank, (sector, _) in enumerate(current_ranked, 1)}
        previous_ranks = {sector: rank for rank, (sector, _) in enumerate(previous_ranked, 1)}
        
        for sector in current_period.keys():
            if sector in previous_ranks:
                rank_change = previous_ranks[sector] - current_ranks[sector]
                
                if abs(rank_change) >= 3:  # Significant rotation
                    rotations.append({
                        'sector': sector,
                        'rank_change': rank_change,
                        'direction': 'IMPROVING' if rank_change > 0 else 'DECLINING',
                        'magnitude': 'MAJOR' if abs(rank_change) >= 5 else 'MODERATE'
                    })
        
        # Sort by absolute rank change
        rotations.sort(key=lambda x: abs(x['rank_change']), reverse=True)
        
        return rotations
    
    def analyze_cyclical_defensive_ratio(self) -> Dict:
        """Analyze cyclical vs defensive sector performance"""
        if not self.sector_data:
            return {}
        
        # Calculate average returns
        cyclical_returns = [
            self.sector_data[s].return_1m for s in self.CYCLICAL_SECTORS
            if s in self.sector_data
        ]
        
        defensive_returns = [
            self.sector_data[s].return_1m for s in self.DEFENSIVE_SECTORS
            if s in self.sector_data
        ]
        
        if not cyclical_returns or not defensive_returns:
            return {}
        
        cyclical_avg = np.mean(cyclical_returns)
        defensive_avg = np.mean(defensive_returns)
        
        ratio = cyclical_avg / defensive_avg if defensive_avg != 0 else 0
        
        return {
            'cyclical_avg_return': round(cyclical_avg, 2),
            'defensive_avg_return': round(defensive_avg, 2),
            'cd_ratio': round(ratio, 2),
            'market_bias': 'RISK_ON' if ratio > 1.2 else 'RISK_OFF' if ratio < 0.8 else 'NEUTRAL',
            'leading_sectors': self.CYCLICAL_SECTORS if ratio > 1 else self.DEFENSIVE_SECTORS,
            'signal': 'Bullish (Cyclicals)' if ratio > 1.2 else 'Bearish (Defensives)' if ratio < 0.8 else 'Neutral'
        }
    
    def analyze_growth_value_rotation(self) -> Dict:
        """Analyze growth vs value rotation"""
        if not self.sector_data:
            return {}
        
        growth_returns = [
            self.sector_data[s].return_1m for s in self.GROWTH_SECTORS
            if s in self.sector_data
        ]
        
        value_returns = [
            self.sector_data[s].return_1m for s in self.VALUE_SECTORS
            if s in self.sector_data
        ]
        
        if not growth_returns or not value_returns:
            return {}
        
        growth_avg = np.mean(growth_returns)
        value_avg = np.mean(value_returns)
        
        return {
            'growth_avg': round(growth_avg, 2),
            'value_avg': round(value_avg, 2),
            'gv_spread': round(growth_avg - value_avg, 2),
            'leading_style': 'GROWTH' if growth_avg > value_avg else 'VALUE',
            'recommendation': 'Overweight Growth' if growth_avg > value_avg * 1.1 else 'Overweight Value' if value_avg > growth_avg * 1.1 else 'Balanced'
        }
    
    def get_sector_recommendations(self) -> List[Dict]:
        """Generate sector allocation recommendations"""
        if not self.sector_data:
            return []
        
        # Rank by momentum
        ranked = self.rank_sectors_by_momentum()
        
        recommendations = []
        
        # Top 3 - Overweight
        for item in ranked[:3]:
            recommendations.append({
                'sector': item['sector'],
                'ticker': item['ticker'],
                'recommendation': 'OVERWEIGHT',
                'momentum': item['momentum'],
                'confidence': 0.8 if item['rank'] <= 2 else 0.7
            })
        
        # Bottom 3 - Underweight
        for item in ranked[-3:]:
            recommendations.append({
                'sector': item['sector'],
                'ticker': item['ticker'],
                'recommendation': 'UNDERWEIGHT',
                'momentum': item['momentum'],
                'confidence': 0.7
            })
        
        return recommendations
    
    def get_rotation_summary(self) -> Dict:
        """Get comprehensive sector rotation summary"""
        return {
            'sector_rankings': self.rank_sectors_by_momentum(),
            'cyclical_defensive_analysis': self.analyze_cyclical_defensive_ratio(),
            'growth_value_analysis': self.analyze_growth_value_rotation(),
            'recommendations': self.get_sector_recommendations(),
            'timestamp': datetime.now().isoformat()
        }


# Usage
def quick_sector_analysis(sector_returns: Dict[str, float]) -> Dict:
    """Quick sector rotation analysis"""
    tracker = SectorRotationTracker()
    
    for sector, ret in sector_returns.items():
        perf = SectorPerformance(
            sector=sector,
            ticker=tracker.SECTOR_ETFS.get(sector, ''),
            return_1d=0,
            return_1w=0,
            return_1m=ret,
            return_3m=0,
            return_ytd=0,
            relative_strength=0,
            momentum_score=ret
        )
        tracker.add_sector_data(perf)
    
    return {
        'rankings': tracker.rank_sectors_by_momentum(),
        'recommendations': tracker.get_sector_recommendations(),
        'market_bias': tracker.analyze_cyclical_defensive_ratio()
    }


def detect_sector_rotation(current: Dict[str, float], 
                          previous: Dict[str, float]) -> List[Dict]:
    """Detect rotation between two periods"""
    tracker = SectorRotationTracker()
    return tracker.detect_rotation(current, previous)
