"""
Multi-Asset Signal Aggregator
============================
Combine signals from all sources into unified trading decisions
Visual AI + Satellite + Social Media + Crisis Detector + Statistical Arb
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
import numpy as np

logger = logging.getLogger(__name__)


class SignalSource(Enum):
    VISUAL_AI = "visual_ai"
    SATELLITE = "satellite_imagery"
    SOCIAL_MEDIA = "social_media"
    CRISIS_DETECTOR = "crisis_detector"
    STATISTICAL_ARB = "statistical_arbitrage"
    SENTIMENT = "sentiment_analysis"
    OPTIONS_FLOW = "options_flow"
    EARNINGS = "earnings_analysis"


class SignalDirection(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


@dataclass
class TradingSignal:
    """Unified trading signal"""
    ticker: str
    direction: SignalDirection
    confidence: float
    sources: List[SignalSource]
    aggregated_score: float
    timestamp: datetime
    metadata: Dict


class SignalAggregator:
    """
    Aggregates signals from multiple alpha sources
    
    Sources:
    - Visual AI (earnings call analysis)
    - Satellite imagery (retail, shipping, agriculture)
    - Social media (TikTok/YouTube trends)
    - Crisis detector (VIX, credit spreads)
    - Statistical arbitrage (pairs trading)
    - Sentiment analysis (news, social)
    - Options flow (unusual activity)
    """
    
    # Source weights (can be optimized)
    SOURCE_WEIGHTS = {
        SignalSource.VISUAL_AI: 0.15,
        SignalSource.SATELLITE: 0.15,
        SignalSource.SOCIAL_MEDIA: 0.10,
        SignalSource.CRISIS_DETECTOR: 0.20,
        SignalSource.STATISTICAL_ARB: 0.15,
        SignalSource.SENTIMENT: 0.10,
        SignalSource.OPTIONS_FLOW: 0.10,
        SignalSource.EARNINGS: 0.15
    }
    
    def __init__(self, custom_weights: Optional[Dict] = None):
        self.weights = custom_weights or self.SOURCE_WEIGHTS
        self.signals_buffer: Dict[str, List[Dict]] = {}
        self.historical_accuracy: Dict[SignalSource, float] = {
            source: 0.6 for source in SignalSource  # Default 60% accuracy
        }
    
    def add_signal(self, source: SignalSource, signal: Dict):
        """Add signal from a specific source"""
        ticker = signal.get('ticker')
        if not ticker:
            logger.warning("Signal missing ticker")
            return
        
        if ticker not in self.signals_buffer:
            self.signals_buffer[ticker] = []
        
        signal['source'] = source.value
        signal['timestamp'] = datetime.now().isoformat()
        self.signals_buffer[ticker].append(signal)
    
    def aggregate(self, ticker: str) -> Optional[TradingSignal]:
        """
        Aggregate all signals for a specific ticker
        """
        signals = self.signals_buffer.get(ticker, [])
        if not signals:
            return None
        
        # Group by source
        by_source = {}
        for sig in signals:
            src = sig.get('source')
            if src not in by_source:
                by_source[src] = []
            by_source[src].append(sig)
        
        # Calculate weighted score
        total_score = 0
        total_weight = 0
        active_sources = []
        
        for source_name, source_signals in by_source.items():
            try:
                source_enum = SignalSource(source_name)
            except:
                continue
            
            # Average signal from this source
            source_score = np.mean([
                self._signal_to_score(s) for s in source_signals
            ])
            
            weight = self.weights.get(source_enum, 0.1)
            accuracy = self.historical_accuracy.get(source_enum, 0.6)
            
            # Adjust weight by historical accuracy
            adjusted_weight = weight * accuracy
            
            total_score += source_score * adjusted_weight
            total_weight += adjusted_weight
            active_sources.append(source_enum)
        
        if total_weight == 0:
            return None
        
        # Normalized aggregated score (-1 to 1)
        aggregated_score = total_score / total_weight
        
        # Map to direction
        direction = self._score_to_direction(aggregated_score)
        confidence = min(abs(aggregated_score) * 1.5, 0.95)
        
        return TradingSignal(
            ticker=ticker,
            direction=direction,
            confidence=round(confidence, 2),
            sources=active_sources,
            aggregated_score=round(aggregated_score, 3),
            timestamp=datetime.now(),
            metadata={
                'source_count': len(active_sources),
                'source_breakdown': {
                    src.value: np.mean([self._signal_to_score(s) for s in by_source.get(src.value, [])])
                    for src in active_sources
                },
                'raw_signals': len(signals)
            }
        )
    
    def _signal_to_score(self, signal: Dict) -> float:
        """Convert signal to normalized score (-1 to 1)"""
        direction = signal.get('signal', signal.get('direction', 'neutral'))
        strength = signal.get('strength', signal.get('confidence', 0.5))
        
        direction_multipliers = {
            'STRONG_BUY': 1.0,
            'BUY': 0.6,
            'LONG': 0.6,
            'BULLISH': 0.6,
            'NEUTRAL': 0,
            'SELL': -0.6,
            'SHORT': -0.6,
            'BEARISH': -0.6,
            'STRONG_SELL': -1.0,
            'CAUTION': -0.3,
            'HOLD': 0
        }
        
        multiplier = direction_multipliers.get(str(direction).upper(), 0)
        return multiplier * strength
    
    def _score_to_direction(self, score: float) -> SignalDirection:
        """Convert aggregated score to direction"""
        if score > 0.7:
            return SignalDirection.STRONG_BUY
        elif score > 0.3:
            return SignalDirection.BUY
        elif score < -0.7:
            return SignalDirection.STRONG_SELL
        elif score < -0.3:
            return SignalDirection.SELL
        else:
            return SignalDirection.NEUTRAL
    
    def get_all_signals(self) -> List[TradingSignal]:
        """Get aggregated signals for all tickers"""
        results = []
        for ticker in self.signals_buffer.keys():
            signal = self.aggregate(ticker)
            if signal:
                results.append(signal)
        
        # Sort by confidence
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results
    
    def generate_portfolio_recommendations(self, 
                                          current_portfolio: Dict[str, float]) -> Dict:
        """
        Generate portfolio-level recommendations
        
        Args:
            current_portfolio: {ticker: position_value}
        """
        all_signals = self.get_all_signals()
        
        # Separate by direction
        buy_signals = [s for s in all_signals if s.direction in 
                      [SignalDirection.BUY, SignalDirection.STRONG_BUY]]
        sell_signals = [s for s in all_signals if s.direction in 
                       [SignalDirection.SELL, SignalDirection.STRONG_SELL]]
        
        # Check for contradictions in current portfolio
        warnings = []
        for ticker, position in current_portfolio.items():
            sig = next((s for s in sell_signals if s.ticker == ticker), None)
            if sig and position > 0:
                warnings.append({
                    'ticker': ticker,
                    'issue': 'HOLDING_SELL_SIGNAL',
                    'confidence': sig.confidence,
                    'recommendation': 'CONSIDER_REDUCING'
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'top_buy_opportunities': [
                {'ticker': s.ticker, 'confidence': s.confidence, 'score': s.aggregated_score}
                for s in buy_signals[:10]
            ],
            'top_sell_signals': [
                {'ticker': s.ticker, 'confidence': s.confidence, 'score': s.aggregated_score}
                for s in sell_signals[:10]
            ],
            'portfolio_warnings': warnings,
            'diversification_score': self._calculate_diversification(),
            'total_active_signals': len(all_signals)
        }
    
    def _calculate_diversification(self) -> float:
        """Calculate diversification score based on signal sources"""
        # More sources = better diversification
        all_sources = set()
        for signals in self.signals_buffer.values():
            for sig in signals:
                all_sources.add(sig.get('source'))
        
        # Score based on number of unique sources (max 8)
        return min(len(all_sources) / 8, 1.0)
    
    def update_accuracy(self, source: SignalSource, 
                       prediction_correct: bool):
        """Update historical accuracy for a source"""
        current = self.historical_accuracy.get(source, 0.6)
        # Exponential moving average
        new_accuracy = current * 0.9 + (1.0 if prediction_correct else 0) * 0.1
        self.historical_accuracy[source] = new_accuracy


# Quick usage
def aggregate_signals(signals_list: List[Dict]) -> List[Dict]:
    """Quick signal aggregation"""
    agg = SignalAggregator()
    
    for sig in signals_list:
        source_str = sig.get('source', 'sentiment')
        try:
            source = SignalSource(source_str)
        except:
            source = SignalSource.SENTIMENT
        agg.add_signal(source, sig)
    
    results = agg.get_all_signals()
    
    return [
        {
            'ticker': s.ticker,
            'direction': s.direction.value,
            'confidence': s.confidence,
            'score': s.aggregated_score,
            'sources': [src.value for src in s.sources]
        }
        for s in results
    ]
