"""
Sentiment-Behavior Correlation Tracker
======================================
Correlate market sentiment with trader behavior
Social media sentiment vs trading decisions
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import numpy as np


class SentimentSource(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    ANALYST = "analyst"
    OPTIONS_FLOW = "options_flow"


@dataclass
class SentimentReading:
    source: str
    ticker: str
    sentiment_score: float  # -1 to 1
    volume: int  # Number of mentions/trades
    timestamp: datetime
    confidence: float


class SentimentBehaviorTracker:
    """
    Track correlation between market sentiment and trading behavior
    
    Detects:
    - Herd behavior vs contrarian signals
    - Sentiment extremes (contrarian indicators)
    - Retail vs institutional sentiment divergence
    """
    
    def __init__(self):
        self.sentiment_history: List[SentimentReading] = []
        self.correlations: Dict[str, float] = {}
    
    def add_sentiment(self, reading: SentimentReading):
        """Add sentiment reading to history"""
        self.sentiment_history.append(reading)
    
    def calculate_sentiment_index(self, ticker: str, 
                                   lookback_hours: int = 24) -> Dict:
        """
        Calculate composite sentiment index for ticker
        
        Combines multiple sources with weighting
        """
        cutoff = datetime.now() - __import__('datetime').timedelta(hours=lookback_hours)
        
        recent = [
            s for s in self.sentiment_history
            if s.ticker == ticker and s.timestamp > cutoff
        ]
        
        if not recent:
            return {'error': 'No recent sentiment data'}
        
        # Weight by source reliability
        weights = {
            SentimentSource.ANALYST.value: 0.30,
            SentimentSource.OPTIONS_FLOW.value: 0.25,
            SentimentSource.NEWS.value: 0.20,
            SentimentSource.REDDIT.value: 0.15,
            SentimentSource.TWITTER.value: 0.10
        }
        
        # Calculate weighted sentiment
        weighted_sum = 0
        total_weight = 0
        
        by_source = {}
        for reading in recent:
            source = reading.source
            weight = weights.get(source, 0.1)
            
            weighted_sum += reading.sentiment_score * weight * reading.volume
            total_weight += weight * reading.volume
            
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(reading.sentiment_score)
        
        composite = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Source breakdown
        source_avg = {
            source: round(np.mean(scores), 2)
            for source, scores in by_source.items()
        }
        
        # Sentiment classification
        classification = self._classify_sentiment(composite)
        
        return {
            'ticker': ticker,
            'composite_sentiment': round(composite, 2),
            'classification': classification,
            'reading_count': len(recent),
            'by_source': source_avg,
            'extreme_reading': abs(composite) > 0.7,
            'recommendation': self._sentiment_recommendation(composite),
            'timestamp': datetime.now().isoformat()
        }
    
    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment score"""
        if score > 0.6:
            return 'VERY_BULLISH'
        elif score > 0.2:
            return 'BULLISH'
        elif score < -0.6:
            return 'VERY_BEARISH'
        elif score < -0.2:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _sentiment_recommendation(self, score: float) -> str:
        """Generate recommendation based on sentiment"""
        if score > 0.8:
            return 'CONTRARIAN_SELL - Extreme bullishness often signals top'
        elif score > 0.4:
            return 'CAUTION - Elevated bullish sentiment'
        elif score < -0.8:
            return 'CONTRARIAN_BUY - Extreme fear often signals bottom'
        elif score < -0.4:
            return 'OPPORTUNITY - Negative sentiment creates discount'
        else:
            return 'NEUTRAL - No sentiment edge'
    
    def detect_herd_behavior(self, ticker: str) -> Dict:
        """Detect herd behavior vs smart money divergence"""
        
        # Get retail sentiment (Twitter/Reddit)
        retail_sentiment = [
            s for s in self.sentiment_history
            if s.ticker == ticker and s.source in ['twitter', 'reddit']
        ]
        
        # Get smart money sentiment (Options/Analyst)
        smart_sentiment = [
            s for s in self.sentiment_history
            if s.ticker == ticker and s.source in ['options_flow', 'analyst']
        ]
        
        if not retail_sentiment or not smart_sentiment:
            return {'error': 'Insufficient data for comparison'}
        
        retail_avg = np.mean([s.sentiment_score for s in retail_sentiment])
        smart_avg = np.mean([s.sentiment_score for s in smart_sentiment])
        
        divergence = retail_avg - smart_avg
        
        return {
            'ticker': ticker,
            'retail_sentiment': round(retail_avg, 2),
            'smart_money_sentiment': round(smart_avg, 2),
            'divergence': round(divergence, 2),
            'interpretation': self._interpret_divergence(divergence),
            'signal_strength': abs(divergence)
        }
    
    def _interpret_divergence(self, divergence: float) -> str:
        """Interpret sentiment divergence"""
        if divergence > 0.5:
            return 'RETAIL_EUPHORIA - Smart money cautious, retail excited (BEARISH)'
        elif divergence > 0.2:
            return 'RETAIL_LEANING_BULLISH - Mild caution warranted'
        elif divergence < -0.5:
            return 'RETAIL_DESPAIR - Smart money bullish, retail bearish (BULLISH)'
        elif divergence < -0.2:
            return 'RETAIL_LEANING_BEARISH - Possible opportunity'
        else:
            return 'CONSENSUS - Retail and smart money aligned'
    
    def get_market_mood_index(self) -> Dict:
        """Get overall market mood index"""
        
        # Aggregate across all tickers
        all_readings = self.sentiment_history[-1000:]  # Last 1000 readings
        
        if not all_readings:
            return {'error': 'No sentiment data available'}
        
        avg_sentiment = np.mean([r.sentiment_score for r in all_readings])
        sentiment_std = np.std([r.sentiment_score for r in all_readings])
        
        # Fear/Greed index (0-100)
        fear_greed = (avg_sentiment + 1) * 50  # Convert -1,1 to 0,100
        
        return {
            'market_mood': self._classify_sentiment(avg_sentiment),
            'fear_greed_index': round(fear_greed, 1),
            'sentiment_stability': 'HIGH' if sentiment_std < 0.3 else 'LOW',
            'extreme_tickers': self._get_extreme_tickers(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_extreme_tickers(self) -> List[Dict]:
        """Get tickers with extreme sentiment readings"""
        from collections import defaultdict
        
        ticker_sentiment = defaultdict(list)
        for reading in self.sentiment_history[-500:]:
            ticker_sentiment[reading.ticker].append(reading.sentiment_score)
        
        extremes = []
        for ticker, scores in ticker_sentiment.items():
            if len(scores) < 5:
                continue
            avg = np.mean(scores)
            if abs(avg) > 0.6:
                extremes.append({
                    'ticker': ticker,
                    'avg_sentiment': round(avg, 2),
                    'direction': 'EXTREME_BULLISH' if avg > 0 else 'EXTREME_BEARISH'
                })
        
        return sorted(extremes, key=lambda x: abs(x['avg_sentiment']), reverse=True)[:5]


# Usage
def analyze_ticker_sentiment(ticker: str, readings: List[Dict]) -> Dict:
    """Quick sentiment analysis for ticker"""
    tracker = SentimentBehaviorTracker()
    
    for r in readings:
        tracker.add_sentiment(SentimentReading(
            source=r['source'],
            ticker=r['ticker'],
            sentiment_score=r['score'],
            volume=r.get('volume', 1),
            timestamp=r.get('timestamp', datetime.now()),
            confidence=r.get('confidence', 0.8)
        ))
    
    return tracker.calculate_sentiment_index(ticker)


def check_herd_behavior(ticker: str, readings: List[Dict]) -> Dict:
    """Check for herd behavior signals"""
    tracker = SentimentBehaviorTracker()
    
    for r in readings:
        tracker.add_sentiment(SentimentReading(
            source=r['source'],
            ticker=r['ticker'],
            sentiment_score=r['score'],
            volume=r.get('volume', 1),
            timestamp=r.get('timestamp', datetime.now()),
            confidence=r.get('confidence', 0.8)
        ))
    
    return tracker.detect_herd_behavior(ticker)
