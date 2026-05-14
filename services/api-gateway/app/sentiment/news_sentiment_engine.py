"""
Real-Time News Sentiment Engine
===============================
Live news sentiment analysis with NLP and entity extraction
Financial news aggregation with real-time scoring
"""

import re
import aiohttp
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# Optional imports
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@dataclass
class NewsArticle:
    """News article with sentiment"""
    title: str
    content: str
    source: str
    published_at: datetime
    url: str
    ticker: Optional[str]
    sentiment_score: float
    sentiment_label: str
    entities: List[str]
    keywords: List[str]


class NewsSentimentEngine:
    """
    Real-time news sentiment analysis engine
    
    Features:
    - Live news aggregation from multiple sources
    - Financial sentiment analysis (FinBERT)
    - Entity extraction (companies, people, events)
    - Keyword detection (earnings, M&A, FDA, etc.)
    - Impact scoring (how much the news matters)
    - Alert generation for significant events
    """
    
    # Financial keywords for impact detection
    IMPACT_KEYWORDS = {
        'earnings': ['earnings', 'eps', 'revenue', 'beat', 'miss', 'guidance'],
        'mna': ['merger', 'acquisition', 'buyout', 'takeover', 'deal'],
        'regulatory': ['fda', 'approval', 'lawsuit', 'sec', 'investigation'],
        'market': ['rally', 'crash', 'correction', 'bull', 'bear'],
        'leadership': ['ceo', 'cfo', 'resigns', 'appointed', 'fired']
    }
    
    def __init__(self):
        self.sentiment_pipeline = None
        self.news_cache: List[NewsArticle] = []
        self.ticker_sentiment: Dict[str, List[Dict]] = defaultdict(list)
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert"
                )
            except Exception as e:
                logger.warning(f"Could not load FinBERT: {e}")
    
    async def fetch_news(self, tickers: List[str], 
                        sources: List[str] = None) -> List[NewsArticle]:
        """
        Fetch news for tickers from multiple sources
        
        In production: Connect to NewsAPI, Bloomberg, Reuters, etc.
        For demo: Generate realistic synthetic news
        """
        if sources is None:
            sources = ['bloomberg', 'reuters', 'cnbc', 'wsj', 'ft']
        
        articles = []
        
        for ticker in tickers:
            # Simulate fetching 3-5 articles per ticker
            n_articles = 3 + hash(ticker) % 3
            
            for i in range(n_articles):
                article = self._generate_synthetic_article(ticker, sources[i % len(sources)])
                articles.append(article)
        
        # Analyze sentiment
        for article in articles:
            self._analyze_sentiment(article)
            self._extract_entities(article)
            self._calculate_impact_score(article)
        
        # Cache articles
        self.news_cache.extend(articles)
        
        # Update ticker sentiment
        for article in articles:
            if article.ticker:
                self.ticker_sentiment[article.ticker].append({
                    'timestamp': article.published_at,
                    'sentiment': article.sentiment_score,
                    'impact': getattr(article, 'impact_score', 0.5)
                })
        
        return articles
    
    def _generate_synthetic_article(self, ticker: str, source: str) -> NewsArticle:
        """Generate realistic synthetic financial news"""
        templates = [
            f"{ticker} Reports Strong Q3 Earnings, Beats Expectations",
            f"{ticker} Announces New Strategic Partnership",
            f"Analysts Upgrade {ticker} Price Target Following Product Launch",
            f"{ticker} Faces Regulatory Scrutiny Over Data Practices",
            f"{ticker} Stock Rallies on Record Revenue Growth",
            f"Market Concerns Rise as {ticker} Misses Guidance",
            f"{ticker} CEO Discusses Future Growth Strategy",
            f"Institutional Investors Increase Stakes in {ticker}"
        ]
        
        title = templates[hash(ticker + source) % len(templates)]
        
        return NewsArticle(
            title=title,
            content=f"Detailed analysis of {ticker} performance and market outlook...",
            source=source,
            published_at=datetime.now() - timedelta(hours=hash(ticker) % 24),
            url=f"https://{source}.com/article/{hash(title)}",
            ticker=ticker,
            sentiment_score=0,
            sentiment_label='neutral',
            entities=[],
            keywords=[]
        )
    
    def _analyze_sentiment(self, article: NewsArticle):
        """Analyze article sentiment"""
        text = f"{article.title} {article.content}"
        
        if self.sentiment_pipeline:
            try:
                result = self.sentiment_pipeline(text[:512])[0]
                article.sentiment_label = result['label'].lower()
                
                # Convert to -1 to 1 scale
                if article.sentiment_label == 'positive':
                    article.sentiment_score = result['score']
                elif article.sentiment_label == 'negative':
                    article.sentiment_score = -result['score']
                else:
                    article.sentiment_score = 0
                    
            except Exception as e:
                logger.debug(f"Sentiment analysis failed: {e}")
                self._fallback_sentiment(article, text)
        else:
            self._fallback_sentiment(article, text)
    
    def _fallback_sentiment(self, article: NewsArticle, text: str):
        """Fallback sentiment using lexicon"""
        positive = ['strong', 'beats', 'growth', 'rally', 'upgrade', 'partnership', 'record']
        negative = ['misses', 'concerns', 'scrutiny', 'regulatory', 'faces', 'decline']
        
        text_lower = text.lower()
        pos_count = sum(1 for w in positive if w in text_lower)
        neg_count = sum(1 for w in negative if w in text_lower)
        
        if pos_count > neg_count:
            article.sentiment_label = 'positive'
            article.sentiment_score = 0.6
        elif neg_count > pos_count:
            article.sentiment_label = 'negative'
            article.sentiment_score = -0.6
        else:
            article.sentiment_label = 'neutral'
            article.sentiment_score = 0
    
    def _extract_entities(self, article: NewsArticle):
        """Extract named entities from article"""
        # Simple entity extraction (would use NER in production)
        text = f"{article.title} {article.content}"
        
        # Company mentions
        company_patterns = [
            r'([A-Z]{2,4}) (?:Corp|Inc|Company|Ltd|Group)',
            r'\b([A-Z]{2,5})\b Stock'
        ]
        
        entities = []
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)
        
        article.entities = list(set(entities))
        
        # Extract keywords
        article.keywords = self._extract_keywords(text)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract financial keywords"""
        keywords = []
        text_lower = text.lower()
        
        for category, words in self.IMPACT_KEYWORDS.items():
            if any(word in text_lower for word in words):
                keywords.append(category)
        
        return keywords
    
    def _calculate_impact_score(self, article: NewsArticle):
        """Calculate news impact score (0-1)"""
        score = 0.5  # Base score
        
        # Sentiment extremity
        score += abs(article.sentiment_score) * 0.2
        
        # Keywords
        if 'earnings' in article.keywords:
            score += 0.2
        if 'mna' in article.keywords:
            score += 0.3
        if 'regulatory' in article.keywords:
            score += 0.25
        
        # Source credibility
        premium_sources = ['bloomberg', 'reuters', 'wsj', 'ft']
        if article.source.lower() in premium_sources:
            score += 0.1
        
        article.impact_score = min(score, 1.0)
    
    def get_ticker_sentiment_summary(self, ticker: str, 
                                     hours: int = 24) -> Dict:
        """Get sentiment summary for a ticker"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_sentiment = [
            s for s in self.ticker_sentiment.get(ticker, [])
            if s['timestamp'] > cutoff
        ]
        
        if not recent_sentiment:
            return {'ticker': ticker, 'sentiment': 'neutral', 'articles': 0}
        
        avg_sentiment = sum(s['sentiment'] for s in recent_sentiment) / len(recent_sentiment)
        avg_impact = sum(s['impact'] for s in recent_sentiment) / len(recent_sentiment)
        
        if avg_sentiment > 0.3:
            overall = 'positive'
        elif avg_sentiment < -0.3:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'ticker': ticker,
            'sentiment': overall,
            'sentiment_score': round(avg_sentiment, 3),
            'impact_score': round(avg_impact, 3),
            'articles': len(recent_sentiment),
            'signal_strength': round(abs(avg_sentiment) * avg_impact, 3)
        }
    
    def detect_sentiment_shifts(self, tickers: List[str], 
                                threshold: float = 0.5) -> List[Dict]:
        """Detect significant sentiment shifts"""
        shifts = []
        
        for ticker in tickers:
            current = self.get_ticker_sentiment_summary(ticker, hours=6)
            previous = self.get_ticker_sentiment_summary(ticker, hours=48)
            
            if current['articles'] == 0 or previous['articles'] == 0:
                continue
            
            score_change = current['sentiment_score'] - previous['sentiment_score']
            
            if abs(score_change) > threshold:
                shifts.append({
                    'ticker': ticker,
                    'change': round(score_change, 3),
                    'from_sentiment': previous['sentiment'],
                    'to_sentiment': current['sentiment'],
                    'severity': 'major' if abs(score_change) > 0.7 else 'moderate',
                    'timestamp': datetime.now().isoformat()
                })
        
        return sorted(shifts, key=lambda x: abs(x['change']), reverse=True)
    
    def get_market_sentiment(self) -> Dict:
        """Get overall market sentiment from all cached news"""
        if not self.news_cache:
            return {'overall': 'neutral', 'score': 0, 'articles': 0}
        
        scores = [a.sentiment_score for a in self.news_cache]
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.2:
            overall = 'bullish'
        elif avg_score < -0.2:
            overall = 'bearish'
        else:
            overall = 'neutral'
        
        # Fear/Greed proxy
        positive_pct = sum(1 for s in scores if s > 0.3) / len(scores) * 100
        
        return {
            'overall': overall,
            'score': round(avg_score, 3),
            'articles_analyzed': len(self.news_cache),
            'positive_pct': round(positive_pct, 1),
            'fear_greed_proxy': 'greed' if positive_pct > 60 else 'fear' if positive_pct < 40 else 'neutral'
        }
    
    async def run_continuous_monitoring(self, tickers: List[str], 
                                       interval_minutes: int = 15):
        """Run continuous news monitoring"""
        logger.info(f"Starting continuous news monitoring for {len(tickers)} tickers")
        
        while True:
            try:
                articles = await self.fetch_news(tickers)
                
                # Check for significant shifts
                shifts = self.detect_sentiment_shifts(tickers)
                
                if shifts:
                    for shift in shifts[:5]:  # Top 5
                        logger.warning(
                            f"SENTIMENT SHIFT: {shift['ticker']} - "
                            f"{shift['from_sentiment']} → {shift['to_sentiment']}"
                        )
                
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"News monitoring error: {e}")
                await asyncio.sleep(60)


# Quick usage
def get_news_sentiment(tickers: List[str]) -> Dict:
    """Quick news sentiment analysis"""
    engine = NewsSentimentEngine()
    asyncio.run(engine.fetch_news(tickers))
    
    results = {}
    for ticker in tickers:
        results[ticker] = engine.get_ticker_sentiment_summary(ticker)
    
    results['market_sentiment'] = engine.get_market_sentiment()
    
    return results


def detect_market_shifts(tickers: List[str]) -> List[Dict]:
    """Detect sentiment shifts"""
    engine = NewsSentimentEngine()
    asyncio.run(engine.fetch_news(tickers))
    return engine.detect_sentiment_shifts(tickers)
