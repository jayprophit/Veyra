"""News Sentiment Analysis for Market Intelligence."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class SentimentResult:
    source: str
    headline: str
    sentiment_score: float  # -1 to 1
    confidence: float
    entities: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'headline': self.headline,
            'sentiment': 'positive' if self.sentiment_score > 0.1 else 'negative' if self.sentiment_score < -0.1 else 'neutral',
            'sentiment_score': self.sentiment_score,
            'confidence': self.confidence,
            'entities': self.entities,
            'timestamp': self.timestamp.isoformat()
        }

class NewsSentimentAnalyzer:
    """AI-powered news sentiment for trading signals."""
    
    def __init__(self):
        self.model = None
        self.news_cache: List[SentimentResult] = []
        self.symbol_sentiment: Dict[str, List[SentimentResult]] = defaultdict(list)
    
    async def load_model(self):
        """Load sentiment analysis model."""
        if self.model is None:
            try:
                from transformers import pipeline
                self.model = pipeline("sentiment-analysis", model="ProsusAI/finbert")
                logger.info("FinBERT sentiment model loaded")
            except:
                logger.warning("Could not load FinBERT, using fallback")
                self.model = "fallback"
    
    async def analyze(self, headline: str, source: str = "news") -> SentimentResult:
        """Analyze sentiment of news headline."""
        await self.load_model()
        
        # Extract entities (symbols)
        entities = self._extract_entities(headline)
        
        if self.model and self.model != "fallback":
            try:
                result = self.model(headline)[0]
                score = result['score'] if result['label'] == 'positive' else -result['score']
                confidence = result['score']
            except:
                score, confidence = self._fallback_sentiment(headline)
        else:
            score, confidence = self._fallback_sentiment(headline)
        
        sentiment = SentimentResult(
            source=source,
            headline=headline,
            sentiment_score=score,
            confidence=confidence,
            entities=entities,
            timestamp=datetime.now()
        )
        
        # Store for symbol tracking
        for entity in entities:
            self.symbol_sentiment[entity].append(sentiment)
        
        self.news_cache.append(sentiment)
        # Trim cache
        if len(self.news_cache) > 1000:
            self.news_cache = self.news_cache[-500:]
        
        return sentiment
    
    def _fallback_sentiment(self, text: str) -> tuple:
        """Simple keyword-based sentiment."""
        positive_words = ['surge', 'rally', 'gain', 'bull', 'moon', ' ATH', 'breakout', 'adoption']
        negative_words = ['crash', 'dump', 'bear', 'fud', 'hack', 'ban', 'regulation', 'lawsuit']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        
        score = (pos_count - neg_count) / max(pos_count + neg_count, 1)
        confidence = min((pos_count + neg_count) * 0.2, 1.0)
        
        return score, confidence
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract crypto/stock symbols from text."""
        symbols = []
        symbol_map = {
            'bitcoin': 'BTC', 'btc': 'BTC',
            'ethereum': 'ETH', 'eth': 'ETH',
            'solana': 'SOL', 'sol': 'SOL',
            'cardano': 'ADA', 'ada': 'ADA',
            'apple': 'AAPL', 'aapl': 'AAPL',
            'tesla': 'TSLA', 'tsla': 'TSLA'
        }
        
        text_lower = text.lower()
        for keyword, symbol in symbol_map.items():
            if keyword in text_lower and symbol not in symbols:
                symbols.append(symbol)
        
        return symbols
    
    async def get_symbol_sentiment(self, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Get aggregated sentiment for a symbol."""
        sentiments = self.symbol_sentiment.get(symbol, [])
        
        if not sentiments:
            return {'symbol': symbol, 'sentiment': 'neutral', 'score': 0, 'articles': 0}
        
        # Filter by time
        cutoff = datetime.now() - __import__('datetime').timedelta(hours=hours)
        recent = [s for s in sentiments if s.timestamp > cutoff]
        
        if not recent:
            return {'symbol': symbol, 'sentiment': 'neutral', 'score': 0, 'articles': 0}
        
        avg_score = sum(s.sentiment_score for s in recent) / len(recent)
        avg_confidence = sum(s.confidence for s in recent) / len(recent)
        
        sentiment_label = 'positive' if avg_score > 0.1 else 'negative' if avg_score < -0.1 else 'neutral'
        
        return {
            'symbol': symbol,
            'sentiment': sentiment_label,
            'score': avg_score,
            'confidence': avg_confidence,
            'articles_analyzed': len(recent),
            'latest_headlines': [s.headline for s in recent[-5:]]
        }
    
    async def scan_news(self, headlines: List[str]) -> List[SentimentResult]:
        """Batch analyze multiple headlines."""
        results = []
        for headline in headlines:
            result = await self.analyze(headline)
            results.append(result)
        return results

sentiment_analyzer = NewsSentimentAnalyzer()
