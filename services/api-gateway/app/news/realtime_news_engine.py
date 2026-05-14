"""
Real-Time News Engine
====================
Bloomberg Terminal-level real-time news integration and analysis
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class NewsSource(Enum):
    """News source types"""
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    WALL_STREET_JOURNAL = "wsj"
    FINANCIAL_TIMES = "ft"
    CNBC = "cnbc"
    YAHOO_FINANCE = "yahoo"
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    TWITTER = "twitter"
    REDDIT = "reddit"


class NewsCategory(Enum):
    """News categories"""
    MARKET_NEWS = "market_news"
    EARNINGS = "earnings"
    ECONOMIC_DATA = "economic_data"
    REGULATORY = "regulatory"
    MERGERS_ACQUISITIONS = "mergers_acquisitions"
    ANALYST_RECOMMENDATIONS = "analyst_recommendations"
    GEOPOLITICAL = "geopolitical"
    TECHNOLOGY = "technology"
    COMMODITIES = "commodities"
    CRYPTO = "crypto"


class Sentiment(Enum):
    """Sentiment analysis results"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class NewsItem:
    """Individual news item"""
    id: str
    title: str
    content: str
    source: NewsSource
    category: NewsCategory
    sentiment: Sentiment
    sentiment_score: float  # -1.0 to 1.0
    relevance_score: float  # 0.0 to 1.0
    timestamp: datetime
    symbols: List[str]
    authors: List[str]
    url: Optional[str]
    keywords: List[str]
    market_impact: str  # high, medium, low
    priority: int  # 1-10, 10 being highest
    metadata: Dict[str, Any]


@dataclass
class NewsAlert:
    """Real-time news alert"""
    alert_id: str
    news_item: NewsItem
    alert_type: str  # breaking, high_impact, price_sensitive
    urgency: str  # critical, high, medium, low
    action_required: bool
    affected_symbols: List[str]
    estimated_price_impact: float
    confidence: float
    created_at: datetime


class RealTimeNewsEngine:
    """Real-time news processing and analysis engine"""
    
    def __init__(self):
        self.news_sources: Dict[NewsSource, Dict[str, Any]] = {}
        self.news_cache: Dict[str, NewsItem] = {}
        self.active_alerts: List[NewsAlert] = []
        self.symbol_watchlist: Dict[str, List[str]] = defaultdict(list)
        self.keyword_watchlist: List[str] = []
        self.sentiment_analyzer = SentimentAnalyzer()
        self.market_impact_analyzer = MarketImpactAnalyzer()
        self.news_processors: Dict[NewsSource, NewsProcessor] = {}
        
        # Initialize news sources
        self._initialize_news_sources()
        self._initialize_processors()
        
    def _initialize_news_sources(self):
        """Initialize news source configurations"""
        self.news_sources = {
            NewsSource.BLOOMBERG: {
                "api_key": "${BLOOMBERG_API_KEY}",
                "base_url": "https://api.bloomberg.com",
                "rate_limit": 1000,  # requests per hour
                "priority": 1,
                "categories": [NewsCategory.MARKET_NEWS, NewsCategory.EARNINGS, NewsCategory.ECONOMIC_DATA]
            },
            NewsSource.REUTERS: {
                "api_key": "${REUTERS_API_KEY}",
                "base_url": "https://api.reuters.com",
                "rate_limit": 500,
                "priority": 2,
                "categories": [NewsCategory.MARKET_NEWS, NewsCategory.REGULATORY, NewsCategory.MERGERS_ACQUISITIONS]
            },
            NewsSource.WALL_STREET_JOURNAL: {
                "api_key": "${WSJ_API_KEY}",
                "base_url": "https://api.wsj.com",
                "rate_limit": 300,
                "priority": 2,
                "categories": [NewsCategory.MARKET_NEWS, NewsCategory.ANALYST_RECOMMENDATIONS]
            },
            NewsSource.CNBC: {
                "api_key": "${CNBC_API_KEY}",
                "base_url": "https://api.cnbc.com",
                "rate_limit": 400,
                "priority": 3,
                "categories": [NewsCategory.MARKET_NEWS, NewsCategory.TECHNOLOGY]
            },
            NewsSource.ALPHA_VANTAGE: {
                "api_key": "${ALPHA_VANTAGE_API_KEY}",
                "base_url": "https://www.alphavantage.co",
                "rate_limit": 500,
                "priority": 4,
                "categories": [NewsCategory.MARKET_NEWS, NewsCategory.ECONOMIC_DATA]
            },
            NewsSource.TWITTER: {
                "api_key": "${TWITTER_API_KEY}",
                "base_url": "https://api.twitter.com",
                "rate_limit": 300,
                "priority": 5,
                "categories": [NewsCategory.MARKET_NEWS, NewsCategory.TECHNOLOGY, NewsCategory.CRYPTO]
            }
        }
        
    def _initialize_processors(self):
        """Initialize news processors for each source"""
        self.news_processors = {
            NewsSource.BLOOMBERG: BloombergProcessor(),
            NewsSource.REUTERS: ReutersProcessor(),
            NewsSource.WALL_STREET_JOURNAL: WSJProcessor(),
            NewsSource.CNBC: CNBCProcessor(),
            NewsSource.ALPHA_VANTAGE: AlphaVantageProcessor(),
            NewsSource.TWITTER: TwitterProcessor()
        }
        
    async def start_real_time_monitoring(self):
        """Start real-time news monitoring"""
        try:
            tasks = []
            
            # Start monitoring for each news source
            for source, config in self.news_sources.items():
                if source in self.news_processors:
                    task = asyncio.create_task(
                        self._monitor_news_source(source, config)
                    )
                    tasks.append(task)
                    
            # Start alert processing
            alert_task = asyncio.create_task(self._process_alerts())
            tasks.append(alert_task)
            
            logger.info("Real-time news monitoring started")
            
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logger.error(f"Error starting real-time monitoring: {e}")
            raise
            
    async def _monitor_news_source(self, source: NewsSource, config: Dict[str, Any]):
        """Monitor specific news source"""
        processor = self.news_processors[source]
        
        while True:
            try:
                # Fetch latest news
                news_items = await processor.fetch_latest_news(config)
                
                # Process each news item
                for item in news_items:
                    await self._process_news_item(item)
                    
                # Wait before next fetch
                await asyncio.sleep(60)  # 1 minute intervals
                
            except Exception as e:
                logger.error(f"Error monitoring {source}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
                
    async def _process_news_item(self, news_item: NewsItem):
        """Process individual news item"""
        try:
            # Check if already processed
            if news_item.id in self.news_cache:
                return
                
            # Analyze sentiment
            news_item.sentiment, news_item.sentiment_score = await self.sentiment_analyzer.analyze(news_item.content)
            
            # Calculate relevance
            news_item.relevance_score = await self._calculate_relevance(news_item)
            
            # Determine market impact
            news_item.market_impact = await self.market_impact_analyzer.analyze(news_item)
            
            # Set priority based on impact and relevance
            news_item.priority = self._calculate_priority(news_item)
            
            # Cache the news item
            self.news_cache[news_item.id] = news_item
            
            # Check for alerts
            await self._check_for_alerts(news_item)
            
            # Notify subscribers
            await self._notify_subscribers(news_item)
            
            logger.info(f"Processed news item: {news_item.title[:50]}...")
            
        except Exception as e:
            logger.error(f"Error processing news item: {e}")
            
    async def _calculate_relevance(self, news_item: NewsItem) -> float:
        """Calculate relevance score for news item"""
        relevance = 0.5  # Base relevance
        
        # Check symbol relevance
        for symbol in news_item.symbols:
            if symbol in self.symbol_watchlist:
                relevance += 0.2
                
        # Check keyword relevance
        for keyword in self.keyword_watchlist:
            if keyword.lower() in news_item.title.lower() or keyword.lower() in news_item.content.lower():
                relevance += 0.1
                
        # Check source priority
        source_priority = self.news_sources[news_item.source]["priority"]
        relevance += (6 - source_priority) * 0.05  # Higher priority = higher relevance
        
        # Check category relevance
        if news_item.category in [NewsCategory.EARNINGS, NewsCategory.MERGERS_ACQUISITIONS]:
            relevance += 0.15
        elif news_item.category in [NewsCategory.REGULATORY, NewsCategory.ECONOMIC_DATA]:
            relevance += 0.1
            
        return min(1.0, relevance)
        
    def _calculate_priority(self, news_item: NewsItem) -> int:
        """Calculate news priority (1-10)"""
        priority = 5  # Base priority
        
        # Market impact
        if news_item.market_impact == "high":
            priority += 3
        elif news_item.market_impact == "medium":
            priority += 1
            
        # Relevance
        if news_item.relevance_score > 0.8:
            priority += 2
        elif news_item.relevance_score > 0.6:
            priority += 1
            
        # Sentiment
        if news_item.sentiment in [Sentiment.VERY_POSITIVE, Sentiment.VERY_NEGATIVE]:
            priority += 1
            
        return min(10, max(1, priority))
        
    async def _check_for_alerts(self, news_item: NewsItem):
        """Check if news item should generate alerts"""
        try:
            # High priority news always generates alerts
            if news_item.priority >= 8:
                alert = NewsAlert(
                    alert_id=f"alert_{news_item.id}",
                    news_item=news_item,
                    alert_type="high_priority",
                    urgency="high",
                    action_required=True,
                    affected_symbols=news_item.symbols,
                    estimated_price_impact=0.05,
                    confidence=0.8,
                    created_at=datetime.now()
                )
                self.active_alerts.append(alert)
                
            # Breaking news
            if "breaking" in news_item.title.lower() or "urgent" in news_item.title.lower():
                alert = NewsAlert(
                    alert_id=f"breaking_{news_item.id}",
                    news_item=news_item,
                    alert_type="breaking",
                    urgency="critical",
                    action_required=True,
                    affected_symbols=news_item.symbols,
                    estimated_price_impact=0.08,
                    confidence=0.9,
                    created_at=datetime.now()
                )
                self.active_alerts.append(alert)
                
            # Price sensitive news
            if news_item.category in [NewsCategory.EARNINGS, NewsCategory.MERGERS_ACQUISITIONS, NewsCategory.REGULATORY]:
                alert = NewsAlert(
                    alert_id=f"price_sensitive_{news_item.id}",
                    news_item=news_item,
                    alert_type="price_sensitive",
                    urgency="high",
                    action_required=True,
                    affected_symbols=news_item.symbols,
                    estimated_price_impact=0.06,
                    confidence=0.7,
                    created_at=datetime.now()
                )
                self.active_alerts.append(alert)
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
            
    async def _notify_subscribers(self, news_item: NewsItem):
        """Notify subscribers about relevant news"""
        try:
            # WebSocket notification for real-time updates
            await self._send_websocket_notification(news_item)
            
            # Email notification for high-priority news
            if news_item.priority >= 8:
                await self._send_email_notification(news_item)
                
            # Push notification for mobile users
            if news_item.priority >= 7:
                await self._send_push_notification(news_item)
                
        except Exception as e:
            logger.error(f"Error notifying subscribers: {e}")
            
    async def _send_websocket_notification(self, news_item: NewsItem):
        """Send WebSocket notification"""
        # Mock implementation - would integrate with WebSocket server
        pass
        
    async def _send_email_notification(self, news_item: NewsItem):
        """Send email notification"""
        # Mock implementation - would integrate with email service
        pass
        
    async def _send_push_notification(self, news_item: NewsItem):
        """Send push notification"""
        # Mock implementation - would integrate with push notification service
        pass
        
    async def _process_alerts(self):
        """Process active alerts"""
        while True:
            try:
                # Process alerts queue
                for alert in self.active_alerts[:]:  # Copy list to avoid modification during iteration
                    await self._handle_alert(alert)
                    
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(30)  # Process alerts every 30 seconds
                
            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(60)
                
    async def _handle_alert(self, alert: NewsAlert):
        """Handle individual alert"""
        try:
            # Check if alert is still relevant
            if alert.created_at < datetime.now() - timedelta(hours=1):
                self.active_alerts.remove(alert)
                return
                
            # Send alert notifications
            await self._send_alert_notification(alert)
            
            # Log alert for compliance
            await self._log_alert(alert)
            
        except Exception as e:
            logger.error(f"Error handling alert {alert.alert_id}: {e}")
            
    async def _send_alert_notification(self, alert: NewsAlert):
        """Send alert notification"""
        # Mock implementation
        pass
        
    async def _log_alert(self, alert: NewsAlert):
        """Log alert for compliance"""
        # Mock implementation
        pass
        
    async def _cleanup_old_alerts(self):
        """Clean up old alerts"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.active_alerts = [alert for alert in self.active_alerts if alert.created_at > cutoff_time]
        
    async def search_news(self, query: str, category: Optional[NewsCategory] = None, 
                         time_range: str = "24h") -> List[NewsItem]:
        """Search news with filters"""
        try:
            results = []
            
            # Search through cached news
            for news_item in self.news_cache.values():
                # Time filter
                if time_range == "1h" and news_item.timestamp < datetime.now() - timedelta(hours=1):
                    continue
                elif time_range == "24h" and news_item.timestamp < datetime.now() - timedelta(hours=24):
                    continue
                elif time_range == "7d" and news_item.timestamp < datetime.now() - timedelta(days=7):
                    continue
                    
                # Category filter
                if category and news_item.category != category:
                    continue
                    
                # Query filter
                if query.lower() in news_item.title.lower() or query.lower() in news_item.content.lower():
                    results.append(news_item)
                    
            # Sort by relevance and timestamp
            results.sort(key=lambda x: (x.relevance_score, x.timestamp), reverse=True)
            
            return results[:50]  # Return top 50 results
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return []
            
    async def get_symbol_news(self, symbol: str, time_range: str = "24h") -> List[NewsItem]:
        """Get news for specific symbol"""
        try:
            results = []
            
            for news_item in self.news_cache.values():
                # Time filter
                if time_range == "1h" and news_item.timestamp < datetime.now() - timedelta(hours=1):
                    continue
                elif time_range == "24h" and news_item.timestamp < datetime.now() - timedelta(hours=24):
                    continue
                elif time_range == "7d" and news_item.timestamp < datetime.now() - timedelta(days=7):
                    continue
                    
                # Symbol filter
                if symbol in news_item.symbols:
                    results.append(news_item)
                    
            # Sort by timestamp
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            return results[:20]  # Return top 20 results
            
        except Exception as e:
            logger.error(f"Error getting symbol news: {e}")
            return []
            
    def add_symbol_watchlist(self, symbol: str, user_id: str):
        """Add symbol to watchlist"""
        self.symbol_watchlist[symbol].append(user_id)
        
    def remove_symbol_watchlist(self, symbol: str, user_id: str):
        """Remove symbol from watchlist"""
        if user_id in self.symbol_watchlist[symbol]:
            self.symbol_watchlist[symbol].remove(user_id)
            
    def add_keyword_watchlist(self, keyword: str):
        """Add keyword to watchlist"""
        if keyword not in self.keyword_watchlist:
            self.keyword_watchlist.append(keyword)
            
    def get_active_alerts(self) -> List[NewsAlert]:
        """Get active alerts"""
        return self.active_alerts.copy()
        
    def get_news_summary(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get news summary statistics"""
        try:
            cutoff_time = {
                "1h": datetime.now() - timedelta(hours=1),
                "24h": datetime.now() - timedelta(hours=24),
                "7d": datetime.now() - timedelta(days=7)
            }.get(time_range, datetime.now() - timedelta(hours=24))
            
            recent_news = [item for item in self.news_cache.values() if item.timestamp > cutoff_time]
            
            # Count by category
            category_counts = defaultdict(int)
            for item in recent_news:
                category_counts[item.category.value] += 1
                
            # Count by sentiment
            sentiment_counts = defaultdict(int)
            for item in recent_news:
                sentiment_counts[item.sentiment.value] += 1
                
            # Count by source
            source_counts = defaultdict(int)
            for item in recent_news:
                source_counts[item.source.value] += 1
                
            return {
                "total_news": len(recent_news),
                "time_range": time_range,
                "category_breakdown": dict(category_counts),
                "sentiment_breakdown": dict(sentiment_counts),
                "source_breakdown": dict(source_counts),
                "high_priority_count": len([item for item in recent_news if item.priority >= 8]),
                "active_alerts": len(self.active_alerts),
                "average_sentiment_score": sum(item.sentiment_score for item in recent_news) / len(recent_news) if recent_news else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting news summary: {e}")
            return {}


class SentimentAnalyzer:
    """Sentiment analysis for news content"""
    
    def __init__(self):
        # Mock sentiment dictionaries
        self.positive_words = {
            "bullish", "growth", "profit", "gain", "increase", "rise", "strong", "positive",
            "optimistic", "upgrade", "beat", "exceed", "outperform", "rally", "surge"
        }
        
        self.negative_words = {
            "bearish", "decline", "loss", "decrease", "fall", "weak", "negative",
            "pessimistic", "downgrade", "miss", "underperform", "crash", "plunge", "drop"
        }
        
    async def analyze(self, text: str) -> Tuple[Sentiment, float]:
        """Analyze sentiment of text"""
        try:
            # Simple keyword-based sentiment analysis
            words = text.lower().split()
            
            positive_count = sum(1 for word in words if word in self.positive_words)
            negative_count = sum(1 for word in words if word in self.negative_words)
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return Sentiment.NEUTRAL, 0.0
                
            # Calculate sentiment score
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            
            # Determine sentiment category
            if sentiment_score > 0.3:
                sentiment = Sentiment.VERY_POSITIVE if sentiment_score > 0.7 else Sentiment.POSITIVE
            elif sentiment_score < -0.3:
                sentiment = Sentiment.VERY_NEGATIVE if sentiment_score < -0.7 else Sentiment.NEGATIVE
            else:
                sentiment = Sentiment.NEUTRAL
                
            return sentiment, sentiment_score
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return Sentiment.NEUTRAL, 0.0


class MarketImpactAnalyzer:
    """Market impact analysis for news"""
    
    async def analyze(self, news_item: NewsItem) -> str:
        """Analyze potential market impact"""
        try:
            impact_score = 0.0
            
            # Category-based impact
            category_impacts = {
                NewsCategory.EARNINGS: 0.8,
                NewsCategory.MERGERS_ACQUISITIONS: 0.9,
                NewsCategory.REGULATORY: 0.7,
                NewsCategory.ECONOMIC_DATA: 0.6,
                NewsCategory.ANALYST_RECOMMENDATIONS: 0.5,
                NewsCategory.MARKET_NEWS: 0.4
            }
            
            impact_score += category_impacts.get(news_item.category, 0.3)
            
            # Sentiment-based impact
            if news_item.sentiment in [Sentiment.VERY_POSITIVE, Sentiment.VERY_NEGATIVE]:
                impact_score += 0.2
                
            # Source-based impact
            source_impacts = {
                NewsSource.BLOOMBERG: 0.3,
                NewsSource.REUTERS: 0.25,
                NewsSource.WALL_STREET_JOURNAL: 0.25,
                NewsSource.CNBC: 0.2,
                NewsSource.ALPHA_VANTAGE: 0.15
            }
            
            impact_score += source_impacts.get(news_item.source, 0.1)
            
            # Determine impact level
            if impact_score > 0.8:
                return "high"
            elif impact_score > 0.5:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Error analyzing market impact: {e}")
            return "low"


# News processor base class
class NewsProcessor:
    """Base class for news processors"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest news from source"""
        try:
            # Mock implementation - would integrate with actual news APIs
            mock_news = [
                NewsItem(
                    id=f"news_{datetime.now().timestamp()}",
                    title="Market Rally Continues as Tech Stocks Lead Gains",
                    content="Technology stocks led a broader market rally today as investors...",
                    source=NewsSource.BLOOMBERG,
                    category=NewsCategory.MARKET_NEWS,
                    sentiment=Sentiment.POSITIVE,
                    sentiment_score=0.6,
                    relevance_score=0.8,
                    timestamp=datetime.now(),
                    symbols=["AAPL", "GOOGL", "MSFT"],
                    authors=["Market Team"],
                    url="https://example.com/news/1",
                    keywords=["market", "tech", "stocks"],
                    market_impact="medium",
                    priority=7,
                    metadata={}
                )
            ]
            return mock_news
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []


class BloombergProcessor(NewsProcessor):
    """Bloomberg news processor"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest Bloomberg news"""
        try:
            # Mock implementation
            return [
                NewsItem(
                    id="bloomberg_1",
                    title="Fed Signals Potential Rate Cut Amid Economic Uncertainty",
                    content="Federal Reserve officials indicated they may consider cutting interest rates...",
                    source=NewsSource.BLOOMBERG,
                    category=NewsCategory.ECONOMIC_DATA,
                    sentiment=Sentiment.POSITIVE,
                    sentiment_score=0.3,
                    relevance_score=0.8,
                    timestamp=datetime.now(),
                    symbols=["SPY", "QQQ", "DIA"],
                    authors=["Federal Reserve Team"],
                    url="https://bloomberg.com/news/fed-rate-cut",
                    keywords=["fed", "interest rates", "monetary policy"],
                    market_impact="high",
                    priority=9,
                    metadata={}
                )
            ]
        except Exception as e:
            logger.error(f"Error fetching Bloomberg news: {e}")
            return []


class ReutersProcessor(NewsProcessor):
    """Reuters news processor"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest Reuters news"""
        try:
            # Mock implementation
            return []
        except Exception as e:
            logger.error(f"Error fetching Reuters news: {e}")
            return []


class WSJProcessor(NewsProcessor):
    """Wall Street Journal news processor"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest WSJ news"""
        try:
            # Mock implementation
            return []
        except Exception as e:
            logger.error(f"Error fetching WSJ news: {e}")
            return []


class CNBCProcessor(NewsProcessor):
    """CNBC news processor"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest CNBC news"""
        try:
            # Mock implementation
            return []
        except Exception as e:
            logger.error(f"Error fetching CNBC news: {e}")
            return []


class AlphaVantageProcessor(NewsProcessor):
    """Alpha Vantage news processor"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest Alpha Vantage news"""
        try:
            # Mock implementation
            return []
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage news: {e}")
            return []


class TwitterProcessor(NewsProcessor):
    """Twitter news processor"""
    
    async def fetch_latest_news(self, config: Dict[str, Any]) -> List[NewsItem]:
        """Fetch latest Twitter news"""
        try:
            # Mock implementation
            return []
        except Exception as e:
            logger.error(f"Error fetching Twitter news: {e}")
            return []


# Global real-time news engine instance
_realtime_news_engine = None

def get_realtime_news_engine() -> RealTimeNewsEngine:
    """Get the global real-time news engine instance"""
    global _realtime_news_engine
    if _realtime_news_engine is None:
        _realtime_news_engine = RealTimeNewsEngine()
    return _realtime_news_engine
