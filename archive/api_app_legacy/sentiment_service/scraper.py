"""
Sentiment Scraper - Multi-source sentiment data collection
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json
import re
from dataclasses import dataclass

@dataclass
class SentimentData:
    id: str
    source: str
    ticker: str
    content: str
    sentiment_score: float  # -1.0 to 1.0
    confidence: float  # 0.0 to 1.0
    relevance_score: float
    category: str
    url: Optional[str]
    published_at: datetime
    scraped_at: datetime
    raw_data: Dict[str, Any]

class SentimentScraper:
    """
    Scrapes sentiment data from multiple financial sources
    """
    
    SOURCES = {
        "twitter": {
            "url": "https://api.twitter.com/2/tweets/search/recent",
            "headers": {},
            "rate_limit": 450,  # requests per 15 min
        },
        "reddit": {
            "subreddits": ["wallstreetbets", "stocks", "investing", "stockmarket"],
            "rate_limit": 60,
        },
        "news": {
            "sources": ["bloomberg", "reuters", "cnbc", "marketwatch"],
            "rate_limit": 100,
        },
        "yahoo": {
            "url": "https://finance.yahoo.com/news/",
            "rate_limit": 120,
        }
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._cache: Dict[str, List[SentimentData]] = {}
        self._jobs: List[Dict] = []
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def get_recent_sentiment(
        self,
        ticker: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 50,
        hours: int = 24
    ) -> List[Dict]:
        """Get recent sentiment data from cache or fresh scrape"""
        
        # Try cache first
        cache_key = f"{ticker}:{source}:{hours}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # Filter by time
            cutoff = datetime.now() - timedelta(hours=hours)
            fresh = [item for item in cached if item.scraped_at > cutoff]
            if len(fresh) >= limit * 0.8:  # 80% cache hit
                return self._to_dict_list(fresh[:limit])
        
        # Fresh scrape
        data = await self.scrape_multiple(
            sources=[source] if source else ["twitter", "reddit", "news"],
            tickers=[ticker] if ticker else None,
            limit=limit
        )
        
        return data['items']
    
    async def scrape_multiple(
        self,
        sources: List[str],
        tickers: Optional[List[str]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Scrape multiple sources concurrently"""
        
        start_time = datetime.now()
        all_items: List[SentimentData] = []
        
        # Create tasks for each source
        tasks = []
        for source in sources:
            if source == "twitter":
                tasks.append(self._scrape_twitter(tickers, limit))
            elif source == "reddit":
                tasks.append(self._scrape_reddit(tickers, limit))
            elif source == "news":
                tasks.append(self._scrape_news(tickers, limit))
            elif source == "yahoo":
                tasks.append(self._scrape_yahoo(tickers, limit))
        
        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful results
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        # Sort by published date
        all_items.sort(key=lambda x: x.published_at, reverse=True)
        
        # Store in cache
        if tickers:
            for ticker in tickers:
                self._cache[f"{ticker}:None:24"] = all_items
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "count": len(all_items),
            "items": self._to_dict_list(all_items[:limit]),
            "duration": duration,
            "new_items": len(all_items)
        }
    
    async def _scrape_twitter(
        self,
        tickers: Optional[List[str]],
        limit: int
    ) -> List[SentimentData]:
        """Scrape Twitter/X for financial sentiment"""
        # Placeholder - would integrate with Twitter API v2
        # For now, return mock data
        
        if not tickers:
            tickers = ["AAPL", "TSLA", "NVDA"]
        
        items = []
        for ticker in tickers[:3]:  # Limit to prevent rate limits
            items.append(SentimentData(
                id=f"tw_{ticker}_{datetime.now().timestamp()}",
                source="twitter",
                ticker=ticker,
                content=f"Bullish on ${ticker} after strong earnings report!",
                sentiment_score=0.6,
                confidence=0.8,
                relevance_score=0.9,
                category="social",
                url=None,
                published_at=datetime.now() - timedelta(minutes=5),
                scraped_at=datetime.now(),
                raw_data={}
            ))
        
        return items
    
    async def _scrape_reddit(
        self,
        tickers: Optional[List[str]],
        limit: int
    ) -> List[SentimentData]:
        """Scrape Reddit financial subreddits"""
        # Placeholder - would use PRAW or Pushshift API
        
        if not tickers:
            tickers = ["GME", "AMC"]
        
        items = []
        for ticker in tickers[:2]:
            items.append(SentimentData(
                id=f"rd_{ticker}_{datetime.now().timestamp()}",
                source="reddit",
                ticker=ticker,
                content=f"What do you think about ${ticker} this week?",
                sentiment_score=0.1,
                confidence=0.6,
                relevance_score=0.7,
                category="social",
                url=f"https://reddit.com/r/wallstreetbets/{ticker}",
                published_at=datetime.now() - timedelta(hours=2),
                scraped_at=datetime.now(),
                raw_data={}
            ))
        
        return items
    
    async def _scrape_news(
        self,
        tickers: Optional[List[str]],
        limit: int
    ) -> List[SentimentData]:
        """Scrape financial news sources"""
        # Placeholder - would use NewsAPI or RSS feeds
        
        if not tickers:
            tickers = ["SPY", "QQQ"]
        
        items = []
        for ticker in tickers[:2]:
            items.append(SentimentData(
                id=f"ns_{ticker}_{datetime.now().timestamp()}",
                source="news",
                ticker=ticker,
                content=f"Market analysis shows mixed signals for ${ticker}",
                sentiment_score=0.0,
                confidence=0.85,
                relevance_score=0.9,
                category="news",
                url=None,
                published_at=datetime.now() - timedelta(hours=1),
                scraped_at=datetime.now(),
                raw_data={}
            ))
        
        return items
    
    async def _scrape_yahoo(
        self,
        tickers: Optional[List[str]],
        limit: int
    ) -> List[SentimentData]:
        """Scrape Yahoo Finance news"""
        # Placeholder - would use yfinance or RSS
        
        items = []
        if tickers:
            for ticker in tickers[:2]:
                items.append(SentimentData(
                    id=f"yh_{ticker}_{datetime.now().timestamp()}",
                    source="yahoo",
                    ticker=ticker,
                    content=f"${ticker} technical analysis update",
                    sentiment_score=0.2,
                    confidence=0.7,
                    relevance_score=0.85,
                    category="analyst",
                    url=None,
                    published_at=datetime.now() - timedelta(hours=3),
                    scraped_at=datetime.now(),
                    raw_data={}
                ))
        
        return items
    
    async def get_historical_sentiment(
        self,
        ticker: str,
        days: int,
        aggregation: str = "hourly"
    ) -> List[Dict]:
        """Get aggregated historical sentiment"""
        
        # Generate sample historical data
        data = []
        now = datetime.now()
        
        if aggregation == "hourly":
            points = days * 24
            interval = timedelta(hours=1)
        elif aggregation == "daily":
            points = days
            interval = timedelta(days=1)
        else:  # weekly
            points = days // 7
            interval = timedelta(weeks=1)
        
        for i in range(points):
            timestamp = now - (interval * i)
            # Simulate sentiment with some randomness
            import random
            base_sentiment = random.uniform(-0.3, 0.3)
            
            data.append({
                "timestamp": timestamp.isoformat(),
                "ticker": ticker,
                "average_sentiment": round(base_sentiment, 3),
                "positive_ratio": round(random.uniform(0.3, 0.7), 3),
                "volume": random.randint(50, 500),
                "confidence": round(random.uniform(0.6, 0.9), 3)
            })
        
        return list(reversed(data))
    
    async def get_job_status(self) -> List[Dict]:
        """Get background job status"""
        return [
            {
                "id": "scrape-twitter",
                "name": "Twitter Scraper",
                "status": "running",
                "last_run": (datetime.now() - timedelta(minutes=5)).isoformat(),
                "next_run": (datetime.now() + timedelta(minutes=10)).isoformat(),
                "items_collected": 1250,
                "error_count": 0
            },
            {
                "id": "scrape-reddit",
                "name": "Reddit Scraper", 
                "status": "running",
                "last_run": (datetime.now() - timedelta(minutes=3)).isoformat(),
                "next_run": (datetime.now() + timedelta(minutes=12)).isoformat(),
                "items_collected": 890,
                "error_count": 2
            },
            {
                "id": "scrape-news",
                "name": "News Scraper",
                "status": "running",
                "last_run": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "next_run": (datetime.now() + timedelta(minutes=15)).isoformat(),
                "items_collected": 56,
                "error_count": 0
            }
        ]
    
    def _to_dict_list(self, items: List[SentimentData]) -> List[Dict]:
        """Convert SentimentData list to dict list"""
        return [
            {
                "id": item.id,
                "source": item.source,
                "ticker": item.ticker,
                "content": item.content,
                "sentiment_score": item.sentiment_score,
                "confidence": item.confidence,
                "relevance_score": item.relevance_score,
                "category": item.category,
                "url": item.url,
                "published_at": item.published_at.isoformat(),
                "scraped_at": item.scraped_at.isoformat()
            }
            for item in items
        ]
    
    async def close(self):
        """Close scraper session"""
        if self.session and not self.session.closed:
            await self.session.close()
