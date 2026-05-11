"""
News Widgets - Inspired by FactSet News Widgets Demo
Free open-source alternative using free data sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import feedparser
import requests
from bs4 import BeautifulSoup
import re

from .widget_framework import BaseWidget, WidgetConfig, WidgetData, WidgetType
from ..integrations.free.free_data_sources import get_free_data_sources_manager

logger = logging.getLogger(__name__)

class MarketNewsWidget(BaseWidget):
    """Market news widget showing latest financial news"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            sources = self.config.data_config.get('sources', ['reuters', 'bloomberg', 'marketwatch'])
            limit = self.config.data_config.get('limit', 10)
            
            # Get news from multiple sources
            news_data = {
                'sources': sources,
                'articles': [],
                'summary': {},
                'trending_topics': [],
                'last_updated': datetime.now().isoformat()
            }
            
            for source in sources:
                try:
                    articles = await self._fetch_news_from_source(source, limit)
                    news_data['articles'].extend(articles)
                except Exception as e:
                    logger.warning(f"Error fetching news from {source}: {e}")
            
            # Sort by timestamp and limit
            news_data['articles'].sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            news_data['articles'] = news_data['articles'][:limit]
            
            # Generate summary
            news_data['summary'] = self._generate_news_summary(news_data['articles'])
            
            # Extract trending topics
            news_data['trending_topics'] = self._extract_trending_topics(news_data['articles'])
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=news_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching market news data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="market-news-widget" id="{self.config.widget_id}">
            <h3>Market News</h3>
            <div class="news-filters">
                <!-- News filters will be rendered here -->
            </div>
            <div class="news-summary">
                <!-- News summary will be rendered here -->
            </div>
            <div class="news-articles">
                <!-- News articles will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'market_news',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _fetch_news_from_source(self, source: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from a specific source"""
        if source == 'reuters':
            return await self._fetch_reuters_news(limit)
        elif source == 'bloomberg':
            return await self._fetch_bloomberg_news(limit)
        elif source == 'marketwatch':
            return await self._fetch_marketwatch_news(limit)
        elif source == 'yahoo':
            return await self._fetch_yahoo_news(limit)
        else:
            return []
    
    async def _fetch_reuters_news(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from Reuters RSS feed"""
        try:
            # Reuters business news RSS feed
            rss_url = "https://www.reuters.com/rssfeed/businessNews"
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:limit]:
                article = {
                    'source': 'Reuters',
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'url': entry.link,
                    'timestamp': entry.get('published', ''),
                    'author': entry.get('author', 'Reuters'),
                    'categories': [tag.term for tag in entry.get('tags', [])]
                }
                
                # Clean up summary
                if article['summary']:
                    article['summary'] = BeautifulSoup(article['summary'], 'html.parser').get_text()
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching Reuters news: {e}")
            return []
    
    async def _fetch_bloomberg_news(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from Bloomberg (mock implementation)"""
        # Bloomberg doesn't have a free RSS feed, so we'll use mock data
        mock_articles = [
            {
                'source': 'Bloomberg',
                'title': 'Stock Markets Rise on Economic Optimism',
                'summary': 'Global equity markets climbed as investors expressed optimism about economic recovery.',
                'url': 'https://bloomberg.com/news/articles/mock-url',
                'timestamp': datetime.now().isoformat(),
                'author': 'Bloomberg Staff',
                'categories': ['Markets', 'Economy']
            },
            {
                'source': 'Bloomberg',
                'title': 'Tech Giants Report Strong Earnings',
                'summary': 'Major technology companies exceeded earnings expectations in the latest quarter.',
                'url': 'https://bloomberg.com/news/articles/mock-url-2',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'author': 'Bloomberg Staff',
                'categories': ['Technology', 'Earnings']
            }
        ]
        
        return mock_articles[:limit]
    
    async def _fetch_marketwatch_news(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from MarketWatch RSS feed"""
        try:
            rss_url = "https://www.marketwatch.com/rss/topstories"
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:limit]:
                article = {
                    'source': 'MarketWatch',
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'url': entry.link,
                    'timestamp': entry.get('published', ''),
                    'author': entry.get('author', 'MarketWatch'),
                    'categories': ['Markets']
                }
                
                # Clean up summary
                if article['summary']:
                    article['summary'] = BeautifulSoup(article['summary'], 'html.parser').get_text()
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching MarketWatch news: {e}")
            return []
    
    async def _fetch_yahoo_news(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch news from Yahoo Finance"""
        try:
            # Use Yahoo Finance RSS feed
            rss_url = "https://finance.yahoo.com/news/rssindex"
            
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries[:limit]:
                article = {
                    'source': 'Yahoo Finance',
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'url': entry.link,
                    'timestamp': entry.get('published', ''),
                    'author': entry.get('author', 'Yahoo Finance'),
                    'categories': ['Finance']
                }
                
                # Clean up summary
                if article['summary']:
                    article['summary'] = BeautifulSoup(article['summary'], 'html.parser').get_text()
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo news: {e}")
            return []
    
    def _generate_news_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate news summary"""
        if not articles:
            return {}
        
        # Count articles by source
        source_counts = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        
        # Count articles by category
        category_counts = {}
        for article in articles:
            categories = article.get('categories', [])
            for category in categories:
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            'total_articles': len(articles),
            'sources': source_counts,
            'categories': category_counts,
            'latest_article': articles[0] if articles else None,
            'time_range': self._get_time_range(articles)
        }
    
    def _extract_trending_topics(self, articles: List[Dict[str, Any]]) -> List[str]:
        """Extract trending topics from news articles"""
        if not articles:
            return []
        
        # Extract keywords from titles and summaries
        all_text = []
        for article in articles:
            all_text.append(article.get('title', ''))
            all_text.append(article.get('summary', ''))
        
        # Simple keyword extraction (in production, use NLP)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'he', 'she', 'him', 'her', 'his', 'hers', 'we', 'us', 'our', 'you', 'your'}
        
        word_counts = {}
        
        for text in all_text:
            words = re.findall(r'\b\w+\\\b', text.lower())
            for word in words:
                if word not in common_words and len(word) > 3:
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top trending topics
        trending_topics = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [topic[0].title() for topic in trending_topics]
    
    def _get_time_range(self, articles: List[Dict[str, Any]]) -> str:
        """Get time range of articles"""
        if not articles:
            return "No articles"
        
        timestamps = [article.get('timestamp', '') for article in articles if article.get('timestamp')]
        
        if not timestamps:
            return "Time range unknown"
        
        # Parse timestamps (simplified)
        try:
            latest = datetime.now()
            oldest = latest - timedelta(hours=24)  # Assume last 24 hours
            return f"Last 24 hours"
        except:
            return "Recent"
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string"""
        try:
            # Handle different timestamp formats
            if 'ago' in timestamp_str.lower():
                return datetime.now() - timedelta(hours=1)
            else:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            return datetime.now()

class CompanyNewsWidget(BaseWidget):
    """Company-specific news widget"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            symbols = self.config.data_config.get('symbols', ['AAPL', 'MSFT'])
            limit = self.config.data_config.get('limit', 5)
            
            # Get company-specific news
            company_news_data = {
                'symbols': symbols,
                'news': {},
                'summary': {},
                'sentiment_analysis': {},
                'last_updated': datetime.now().isoformat()
            }
            
            for symbol in symbols:
                try:
                    news = await self._fetch_company_news(symbol, limit)
                    company_news_data['news'][symbol] = news
                    
                    # Analyze sentiment
                    company_news_data['sentiment_analysis'][symbol] = self._analyze_sentiment(news)
                    
                except Exception as e:
                    logger.warning(f"Error fetching news for {symbol}: {e}")
                    company_news_data['news'][symbol] = []
                    company_news_data['sentiment_analysis'][symbol] = {'sentiment': 'neutral', 'confidence': 0}
            
            # Generate summary
            company_news_data['summary'] = self._generate_company_news_summary(company_news_data['news'])
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=company_news_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching company news data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="company-news-widget" id="{self.config.widget_id}">
            <h3>Company News</h3>
            <div class="company-selector">
                <!-- Company selector will be rendered here -->
            </div>
            <div class="news-articles">
                <!-- Company news articles will be rendered here -->
            </div>
            <div class="sentiment-analysis">
                <!-- Sentiment analysis will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'company_news',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _fetch_company_news(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Fetch company-specific news"""
        # Mock company news (in production, integrate with news APIs)
        company_news = [
            {
                'source': 'Financial News',
                'title': f'{symbol} Reports Strong Quarterly Earnings',
                'summary': f'{symbol} announced better-than-expected quarterly earnings, driven by strong product demand and cost management.',
                'url': f'https://example.com/news/{symbol.lower()}-earnings',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'author': 'Financial Analyst',
                'relevance_score': 0.9
            },
            {
                'source': 'Market Update',
                'title': f'{symbol} Stock Rises on Positive Analyst Coverage',
                'summary': f'Several analysts upgraded their price targets for {symbol} following recent product announcements.',
                'url': f'https://example.com/news/{symbol.lower()}-analyst',
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'author': 'Market Reporter',
                'relevance_score': 0.8
            }
        ]
        
        return company_news[:limit]
    
    def _analyze_sentiment(self, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment of news articles"""
        if not news_articles:
            return {'sentiment': 'neutral', 'confidence': 0}
        
        # Simple sentiment analysis (in production, use NLP)
        positive_words = {'good', 'great', 'excellent', 'strong', 'positive', 'up', 'rise', 'growth', 'success', 'beat', 'exceed'}
        negative_words = {'bad', 'poor', 'weak', 'negative', 'down', 'fall', 'decline', 'loss', 'miss', 'below', 'concern'}
        
        positive_count = 0
        negative_count = 0
        
        for article in news_articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            
            for word in positive_words:
                positive_count += text.count(word)
            
            for word in negative_words:
                negative_count += text.count(word)
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return {'sentiment': 'neutral', 'confidence': 0}
        
        positive_ratio = positive_count / total_count
        
        if positive_ratio > 0.6:
            sentiment = 'positive'
        elif positive_ratio < 0.4:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        confidence = min(total_count / 10, 1.0)  # Confidence based on sample size
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'total_analyzed': len(news_articles)
        }
    
    def _generate_company_news_summary(self, news_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Generate summary of company news"""
        total_articles = sum(len(articles) for articles in news_data.values())
        
        # Count sentiment across all companies
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for symbol, articles in news_data.items():
            if symbol in self.config.data_config.get('symbols', []):
                # Use sentiment analysis if available, otherwise assume neutral
                sentiment_counts['neutral'] += len(articles)
        
        return {
            'total_articles': total_articles,
            'companies_with_news': len([k for k, v in news_data.items() if v]),
            'sentiment_distribution': sentiment_counts,
            'most_recent_article': self._get_most_recent_article(news_data)
        }
    
    def _get_most_recent_article(self, news_data: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        """Get the most recent article across all companies"""
        most_recent = None
        latest_timestamp = None
        
        for articles in news_data.values():
            for article in articles:
                timestamp = article.get('timestamp', '')
                if timestamp and (not latest_timestamp or timestamp > latest_timestamp):
                    latest_timestamp = timestamp
                    most_recent = article
        
        return most_recent

class NewsAlertWidget(BaseWidget):
    """News alert widget for breaking news and notifications"""
    
    async def fetch_data(self) -> WidgetData:
        try:
            keywords = self.config.data_config.get('keywords', ['earnings', 'merger', 'acquisition'])
            alert_threshold = self.config.data_config.get('alert_threshold', 0.8)
            
            # Get breaking news alerts
            alert_data = {
                'keywords': keywords,
                'alerts': [],
                'active_alerts': [],
                'alert_history': [],
                'settings': {
                    'alert_threshold': alert_threshold,
                    'notification_enabled': self.config.data_config.get('notification_enabled', True)
                },
                'last_updated': datetime.now().isoformat()
            }
            
            # Fetch recent news and check for alerts
            recent_news = await self._fetch_recent_news()
            
            for article in recent_news:
                alert_score = self._calculate_alert_score(article, keywords)
                
                if alert_score >= alert_threshold:
                    alert = {
                        'id': f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(alert_data['alerts'])}",
                        'article': article,
                        'score': alert_score,
                        'keywords_matched': self._get_matched_keywords(article, keywords),
                        'timestamp': datetime.now().isoformat(),
                        'status': 'active'
                    }
                    
                    alert_data['alerts'].append(alert)
                    alert_data['active_alerts'].append(alert)
            
            # Sort alerts by score
            alert_data['alerts'].sort(key=lambda x: x['score'], reverse=True)
            
            return WidgetData(
                widget_id=self.config.widget_id,
                data=alert_data,
                timestamp=datetime.now(),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error fetching news alert data: {e}")
            raise
    
    def render_html(self) -> str:
        return f"""
        <div class="news-alert-widget" id="{self.config.widget_id}">
            <h3>News Alerts</h3>
            <div class="alert-settings">
                <!-- Alert settings will be rendered here -->
            </div>
            <div class="active-alerts">
                <!-- Active alerts will be rendered here -->
            </div>
            <div class="alert-history">
                <!-- Alert history will be rendered here -->
            </div>
        </div>
        """
    
    def render_json(self) -> Dict[str, Any]:
        return {
            'widget_type': 'news_alert',
            'config': self.config.__dict__,
            'template': self.render_html()
        }
    
    async def _fetch_recent_news(self) -> List[Dict[str, Any]]:
        """Fetch recent news for alert processing"""
        # Use market news widget to get recent news
        market_news_widget = MarketNewsWidget(WidgetConfig(
            widget_id='temp_news',
            widget_type=WidgetType.NEWS,
            title='Temp News',
            size=WidgetSize.MEDIUM,
            data_config={'sources': ['reuters', 'marketwatch'], 'limit': 20}
        ))
        
        try:
            news_data = await market_news_widget.fetch_data()
            return news_data.data.get('articles', [])
        except:
            return []
    
    def _calculate_alert_score(self, article: Dict[str, Any], keywords: List[str]) -> float:
        """Calculate alert score for an article"""
        score = 0.0
        
        # Check title and summary for keywords
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        for keyword in keywords:
            keyword_count = text.count(keyword.lower())
            score += keyword_count * 0.3  # Each keyword occurrence adds 0.3 to score
        
        # Boost score for recent articles
        timestamp = article.get('timestamp', '')
        if timestamp:
            try:
                article_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hours_ago = (datetime.now() - article_time).total_seconds() / 3600
                
                if hours_ago < 1:
                    score += 0.5  # Recent articles get boost
                elif hours_ago < 6:
                    score += 0.3
                elif hours_ago < 24:
                    score += 0.1
            except:
                pass
        
        # Boost score for certain sources
        source = article.get('source', '').lower()
        if source in ['reuters', 'bloomberg', 'associated press']:
            score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_matched_keywords(self, article: Dict[str, Any], keywords: List[str]) -> List[str]:
        """Get keywords that matched in the article"""
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        matched = []
        
        for keyword in keywords:
            if keyword.lower() in text:
                matched.append(keyword)
        
        return matched

# Register news widget templates
def register_news_widgets(widget_manager):
    """Register all news widget templates"""
    
    widget_manager.register_template(WidgetType.NEWS, MarketNewsWidget)
    widget_manager.register_template(WidgetType.NEWS, CompanyNewsWidget)
    widget_manager.register_template(WidgetType.NEWS, NewsAlertWidget)
