"""Social Sentiment Aggregator Module."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class SentimentSource(Enum):
    TWITTER = "twitter"
    REDDIT = "reddit"
    STOCKTWITS = "stocktwits"
    NEWS = "news"
    FORUMS = "forums"

class SentimentScore(Enum):
    VERY_BULLISH = 5
    BULLISH = 4
    NEUTRAL = 3
    BEARISH = 2
    VERY_BEARISH = 1

@dataclass
class SocialSentiment:
    symbol: str
    source: SentimentSource
    sentiment_score: float  # -1 to 1
    volume: int
    timestamp: datetime
    trending_topics: List[str]
    influencer_mentions: int

class SocialSentimentAggregator:
    """Aggregate sentiment from multiple social sources."""
    
    def __init__(self):
        self.sources = [SentimentSource.TWITTER, SentimentSource.REDDIT, 
                       SentimentSource.STOCKTWITS, SentimentSource.NEWS]
        self.sentiment_cache: Dict[str, List[SocialSentiment]] = {}
        self.keywords = {
            'bullish': ['moon', 'rocket', 'bull', 'long', 'buy', 'breakout'],
            'bearish': ['crash', 'dump', 'bear', 'short', 'sell', 'panic']
        }
    
    async def get_aggregated_sentiment(self, symbol: str, 
                                       hours_lookback: int = 24) -> Dict[str, Any]:
        """Get aggregated sentiment across all sources."""
        sentiments = []
        
        for source in self.sources:
            score = await self._fetch_source_sentiment(symbol, source)
            sentiments.append(score)
        
        # Calculate weighted average
        weights = {'twitter': 0.30, 'reddit': 0.25, 'stocktwits': 0.25, 'news': 0.20}
        weighted_score = sum(s['sentiment'] * weights[s['source']] for s in sentiments)
        
        total_volume = sum(s['volume'] for s in sentiments)
        trending = self._extract_trending_topics(sentiments)
        
        return {
            'symbol': symbol,
            'overall_sentiment': weighted_score,
            'sentiment_label': self._score_to_label(weighted_score),
            'confidence': min(0.95, 0.5 + abs(weighted_score)),
            'volume_24h': total_volume,
            'sources': sentiments,
            'trending_topics': trending,
            'timestamp': datetime.now().isoformat()
        }
    
    async def _fetch_source_sentiment(self, symbol: str, 
                                     source: SentimentSource) -> Dict:
        """Fetch sentiment from specific source."""
        # Simulate API calls to social platforms
        base_scores = {
            'AAPL': 0.35, 'TSLA': 0.45, 'NVDA': 0.60, 'AMD': 0.40,
            'GME': 0.25, 'AMC': 0.20, 'BTC': 0.30, 'ETH': 0.35
        }
        
        score = base_scores.get(symbol, 0.0) + (hash(symbol + source.value) % 20 - 10) / 100
        volume = 10000 + hash(symbol + source.value) % 50000
        
        return {
            'source': source.value,
            'sentiment': round(score, 2),
            'volume': volume,
            'posts_24h': volume // 10,
            'engagement_rate': round(0.03 + (hash(symbol) % 100) / 1000, 3)
        }
    
    def _extract_trending_topics(self, sentiments: List[Dict]) -> List[str]:
        """Extract trending topics from sentiment data."""
        return ['earnings', 'breakout', 'volume_surge', 'upgrade', 'partnership']
    
    def _score_to_label(self, score: float) -> str:
        """Convert score to sentiment label."""
        if score > 0.6: return 'very_bullish'
        if score > 0.2: return 'bullish'
        if score > -0.2: return 'neutral'
        if score > -0.6: return 'bearish'
        return 'very_bearish'
    
    async def get_trending_symbols(self, limit: int = 20) -> List[Dict]:
        """Get symbols with highest social buzz."""
        symbols = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'GME', 'AMC', 'BTC', 'ETH', 
                  'SPY', 'QQQ', 'MSFT', 'GOOGL', 'AMZN', 'META']
        
        trending = []
        for symbol in symbols:
            buzz_score = hash(symbol) % 100
            trending.append({
                'symbol': symbol,
                'buzz_score': buzz_score,
                'sentiment': (hash(symbol) % 100 - 50) / 50,
                'volume_24h': 100000 + hash(symbol) % 500000
            })
        
        return sorted(trending, key=lambda x: x['buzz_score'], reverse=True)[:limit]
    
    async def compare_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        """Compare sentiment across multiple symbols."""
        comparisons = []
        
        for symbol in symbols:
            sentiment = await self.get_aggregated_sentiment(symbol)
            comparisons.append({
                'symbol': symbol,
                'sentiment_score': sentiment['overall_sentiment'],
                'volume': sentiment['volume_24h']
            })
        
        return {
            'comparison_date': datetime.now().isoformat(),
            'symbols_compared': symbols,
            'rankings': sorted(comparisons, key=lambda x: x['sentiment_score'], reverse=True)
        }

sentiment_aggregator = SocialSentimentAggregator()
