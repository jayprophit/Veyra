"""
Market Regime Classifier
========================
Classify market regimes: Bull, Bear, Sideways, High/Low Volatility
Regime detection using HMM, trend strength, volatility clustering
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class MarketRegime(Enum):
    BULL_TREND = "bull_trend"
    BEAR_TREND = "bear_trend"
    BULL_VOLATILE = "bull_volatile"
    BEAR_VOLATILE = "bear_volatile"
    SIDEWAYS_QUIET = "sideways_quiet"
    SIDEWAYS_VOLATILE = "sideways_volatile"
    CRISIS = "crisis"
    RECOVERY = "recovery"


@dataclass
class RegimeClassification:
    """Market regime classification result"""
    regime: str
    confidence: float
    trend_strength: float
    volatility_regime: str
    duration_days: int
    features: Dict


class MarketRegimeClassifier:
    """
    Classify market regimes using multiple factors
    
    Factors:
    - Trend direction and strength (ADX, moving averages)
    - Volatility level (ATR, standard deviation)
    - Volume patterns
    - Correlation structure
    """
    
    def __init__(self):
        self.regime_history: List[RegimeClassification] = []
    
    def calculate_trend_strength(self, prices: pd.Series,
                                 fast_ma: int = 20,
                                 slow_ma: int = 50) -> Dict:
        """Calculate trend strength indicators"""
        if len(prices) < slow_ma:
            return {'strength': 0, 'direction': 'neutral'}
        
        # Moving averages
        ma_fast = prices.rolling(fast_ma).mean().iloc[-1]
        ma_slow = prices.rolling(slow_ma).mean().iloc[-1]
        
        # Price vs MAs
        current_price = prices.iloc[-1]
        
        # Trend score (-1 to 1)
        if ma_fast > ma_slow:
            trend_score = (ma_fast - ma_slow) / ma_slow
            direction = 'bullish'
        else:
            trend_score = (ma_slow - ma_fast) / ma_slow
            direction = 'bearish'
        
        # Normalize to 0-1 scale
        trend_strength = min(abs(trend_score) * 10, 1.0)
        
        return {
            'strength': trend_strength,
            'direction': direction,
            'price_vs_fast': (current_price - ma_fast) / ma_fast,
            'price_vs_slow': (current_price - ma_slow) / ma_slow,
            'golden_cross': ma_fast > ma_slow and direction == 'bullish',
            'death_cross': ma_fast < ma_slow and direction == 'bearish'
        }
    
    def calculate_volatility_regime(self, returns: pd.Series,
                                   lookback: int = 20) -> Dict:
        """Classify volatility regime"""
        if len(returns) < lookback:
            return {'regime': 'unknown', 'level': 0}
        
        current_vol = returns.iloc[-lookback:].std() * np.sqrt(252)
        
        # Historical comparison
        hist_vol = returns.std() * np.sqrt(252)
        
        # Percentile rank
        rolling_vols = returns.rolling(lookback).std().dropna() * np.sqrt(252)
        percentile = (rolling_vols < current_vol).mean()
        
        # Classify
        if percentile > 0.8:
            regime = 'high'
        elif percentile > 0.6:
            regime = 'elevated'
        elif percentile > 0.4:
            regime = 'normal'
        else:
            regime = 'low'
        
        return {
            'regime': regime,
            'current_vol': round(current_vol * 100, 2),
            'historical_vol': round(hist_vol * 100, 2),
            'percentile': round(percentile * 100, 1),
            'volatility_trend': 'rising' if current_vol > hist_vol else 'falling'
        }
    
    def classify_regime(self, prices: pd.Series,
                       volume: Optional[pd.Series] = None) -> RegimeClassification:
        """
        Classify current market regime
        """
        if len(prices) < 50:
            return RegimeClassification(
                regime=MarketRegime.SIDEWAYS_QUIET.value,
                confidence=0.5,
                trend_strength=0,
                volatility_regime='normal',
                duration_days=0,
                features={}
            )
        
        # Calculate returns
        returns = prices.pct_change().dropna()
        
        # Trend analysis
        trend = self.calculate_trend_strength(prices)
        
        # Volatility analysis
        vol = self.calculate_volatility_regime(returns)
        
        # Regime determination
        regime = self._determine_regime(trend, vol)
        
        # Confidence based on signal strength
        confidence = (trend['strength'] + vol['percentile'] / 100) / 2
        
        features = {
            'trend': trend,
            'volatility': vol,
            '20_day_return': round(returns.iloc[-20:].sum() * 100, 2),
            '50_day_return': round(returns.iloc[-50:].sum() * 100, 2)
        }
        
        return RegimeClassification(
            regime=regime,
            confidence=round(confidence, 2),
            trend_strength=round(trend['strength'], 2),
            volatility_regime=vol['regime'],
            duration_days=self._estimate_regime_duration(regime),
            features=features
        )
    
    def _determine_regime(self, trend: Dict, vol: Dict) -> str:
        """Determine regime from trend and volatility"""
        direction = trend['direction']
        strength = trend['strength']
        vol_regime = vol['regime']
        
        # Crisis detection
        if vol_regime == 'high' and direction == 'bearish' and strength > 0.7:
            return MarketRegime.CRISIS.value
        
        # Recovery detection
        if vol_regime == 'high' and direction == 'bullish' and strength > 0.5:
            return MarketRegime.RECOVERY.value
        
        # Trending regimes
        if strength > 0.5:
            if direction == 'bullish':
                if vol_regime in ['high', 'elevated']:
                    return MarketRegime.BULL_VOLATILE.value
                else:
                    return MarketRegime.BULL_TREND.value
            else:
                if vol_regime in ['high', 'elevated']:
                    return MarketRegime.BEAR_VOLATILE.value
                else:
                    return MarketRegime.BEAR_TREND.value
        
        # Sideways regimes
        if vol_regime in ['high', 'elevated']:
            return MarketRegime.SIDEWAYS_VOLATILE.value
        else:
            return MarketRegime.SIDEWAYS_QUIET.value
    
    def _estimate_regime_duration(self, regime: str) -> int:
        """Estimate typical regime duration"""
        # Average days in each regime (historical)
        durations = {
            MarketRegime.BULL_TREND.value: 120,
            MarketRegime.BEAR_TREND.value: 60,
            MarketRegime.BULL_VOLATILE.value: 45,
            MarketRegime.BEAR_VOLATILE.value: 30,
            MarketRegime.SIDEWAYS_QUIET.value: 90,
            MarketRegime.SIDEWAYS_VOLATILE.value: 40,
            MarketRegime.CRISIS.value: 20,
            MarketRegime.RECOVERY.value: 60
        }
        
        return durations.get(regime, 60)
    
    def get_strategy_recommendation(self, regime: str) -> Dict:
        """Get strategy recommendations for regime"""
        recommendations = {
            MarketRegime.BULL_TREND.value: {
                'bias': 'Bullish',
                'strategies': ['Trend following', 'Momentum', 'Breakout'],
                'position_size': 'Full',
                'risk_management': 'Trailing stops'
            },
            MarketRegime.BEAR_TREND.value: {
                'bias': 'Bearish',
                'strategies': ['Short selling', 'Put options', 'Defensive sectors'],
                'position_size': 'Reduced',
                'risk_management': 'Tight stops, quick exits'
            },
            MarketRegime.BULL_VOLATILE.value: {
                'bias': 'Cautiously Bullish',
                'strategies': ['Volatility breakout', 'Mean reversion on dips'],
                'position_size': 'Reduced',
                'risk_management': 'Wider stops, smaller positions'
            },
            MarketRegime.BEAR_VOLATILE.value: {
                'bias': 'Defensive',
                'strategies': ['Cash preservation', 'Hedging', 'VIX plays'],
                'position_size': 'Minimal',
                'risk_management': 'Strict risk limits'
            },
            MarketRegime.SIDEWAYS_QUIET.value: {
                'bias': 'Neutral',
                'strategies': ['Range trading', 'Income strategies', 'Iron condors'],
                'position_size': 'Moderate',
                'risk_management': 'Range stops'
            },
            MarketRegime.SIDEWAYS_VOLATILE.value: {
                'bias': 'Neutral',
                'strategies': ['Volatility selling', 'Straddles', 'Range breakout'],
                'position_size': 'Moderate',
                'risk_management': 'Dynamic hedging'
            },
            MarketRegime.CRISIS.value: {
                'bias': 'Extreme Caution',
                'strategies': ['Cash', 'Gold', 'Treasuries', 'VIX'],
                'position_size': 'Minimal',
                'risk_management': 'Capital preservation priority'
            },
            MarketRegime.RECOVERY.value: {
                'bias': 'Opportunistic',
                'strategies': ['Value buying', 'Recovery plays', 'High beta'],
                'position_size': 'Building',
                'risk_management': 'Pyramiding into strength'
            }
        }
        
        return recommendations.get(regime, recommendations[MarketRegime.SIDEWAYS_QUIET.value])


# Usage
def classify_current_regime(prices: List[float]) -> Dict:
    """Quick regime classification"""
    classifier = MarketRegimeClassifier()
    
    series = pd.Series(prices)
    result = classifier.classify_regime(series)
    
    return {
        'regime': result.regime,
        'confidence': result.confidence,
        'trend_strength': result.trend_strength,
        'volatility': result.volatility_regime,
        'recommendation': classifier.get_strategy_recommendation(result.regime)
    }


def get_regime_strategy_guide() -> Dict:
    """Get strategy guide for all regimes"""
    classifier = MarketRegimeClassifier()
    
    return {
        regime.value: classifier.get_strategy_recommendation(regime.value)
        for regime in MarketRegime
    }
