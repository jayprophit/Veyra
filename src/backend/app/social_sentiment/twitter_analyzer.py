"""Twitter Sentiment Analyzer - Analyze Twitter sentiment for stocks"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import statistics

@dataclass
class Tweet:
    text: str
    timestamp: datetime
    likes: int
    retweets: int
    author_followers: int
    verified: bool

class TwitterSentimentAnalyzer:
    """Analyze Twitter sentiment for tickers and market trends"""
    
    def __init__(self):
        self.bullish_keywords = [
            "moon", "rocket", "bullish", "buy", "long", "calls", 
            "tendies", "gain", "pump", "breakout", " ATH"
        ]
        self.bearish_keywords = [
            "crash", "bearish", "sell", "short", "puts", "dump", 
            "rug", "tank", "bubble", "bear", "recession"
        ]
        self.cashtags: Dict[str, List[Tweet]] = {}
    
    def add_tweet(self, cashtag: str, tweet: Tweet):
        """Add tweet for a ticker"""
        if cashtag not in self.cashtags:
            self.cashtags[cashtag] = []
        self.cashtags[cashtag].append(tweet)
    
    def analyze_sentiment(self, cashtag: str, 
                         hours: int = 24) -> Dict:
        """Analyze sentiment for a ticker"""
        if cashtag not in self.cashtags:
            return {"error": "No tweets found"}
        
        tweets = self.cashtags[cashtag]
        cutoff = datetime.utcnow() - __import__('datetime').timedelta(hours=hours)
        recent_tweets = [t for t in tweets if t.timestamp > cutoff]
        
        if not recent_tweets:
            return {"error": "No recent tweets"}
        
        # Score each tweet
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        weighted_score = 0
        
        for tweet in recent_tweets:
            text_lower = tweet.text.lower()
            
            # Check for keywords
            bull_score = sum(1 for kw in self.bullish_keywords if kw in text_lower)
            bear_score = sum(1 for kw in self.bearish_keywords if kw in text_lower)
            
            # Weight by engagement
            weight = (1 + tweet.likes * 0.1 + tweet.retweets * 0.3)
            if tweet.verified:
                weight *= 2
            
            if bull_score > bear_score:
                bullish_count += 1
                weighted_score += weight
            elif bear_score > bull_score:
                bearish_count += 1
                weighted_score -= weight
            else:
                neutral_count += 1
        
        total = len(recent_tweets)
        
        # Calculate metrics
        sentiment_score = weighted_score / total if total > 0 else 0
        
        # Normalize to -1 to 1 scale
        normalized_score = max(-1, min(1, sentiment_score / 5))
        
        return {
            "cashtag": cashtag,
            "total_tweets": total,
            "bullish_pct": round(bullish_count / total * 100, 1),
            "bearish_pct": round(bearish_count / total * 100, 1),
            "neutral_pct": round(neutral_count / total * 100, 1),
            "sentiment_score": round(normalized_score, 3),
            "sentiment_label": self._get_sentiment_label(normalized_score),
            "intensity": self._get_intensity(abs(normalized_score)),
            "viral_potential": self._calculate_viral_potential(recent_tweets)
        }
    
    def _get_sentiment_label(self, score: float) -> str:
        """Convert score to label"""
        if score > 0.5:
            return "VERY_BULLISH"
        elif score > 0.2:
            return "BULLISH"
        elif score < -0.5:
            return "VERY_BEARISH"
        elif score < -0.2:
            return "BEARISH"
        return "NEUTRAL"
    
    def _get_intensity(self, abs_score: float) -> str:
        """Get intensity level"""
        if abs_score > 0.7:
            return "EXTREME"
        elif abs_score > 0.4:
            return "HIGH"
        elif abs_score > 0.2:
            return "MODERATE"
        return "LOW"
    
    def _calculate_viral_potential(self, tweets: List[Tweet]) -> Dict:
        """Calculate viral potential"""
        total_engagement = sum(t.likes + t.retweets for t in tweets)
        avg_engagement = total_engagement / len(tweets) if tweets else 0
        
        # Growth rate (simulated)
        growth_rate = 1.2 if avg_engagement > 50 else 0.9
        
        return {
            "engagement_velocity": round(growth_rate, 2),
            "avg_engagement": round(avg_engagement, 1),
            "viral_prediction": "HIGH" if growth_rate > 1.5 else "MEDIUM" if growth_rate > 1.0 else "LOW"
        }
    
    def detect_trending_change(self, cashtag: str) -> Dict:
        """Detect sudden sentiment shifts"""
        if cashtag not in self.cashtags:
            return {"error": "No data"}
        
        tweets = sorted(self.cashtags[cashtag], key=lambda x: x.timestamp)
        
        if len(tweets) < 20:
            return {"error": "Insufficient data"}
        
        # Split into two halves
        mid = len(tweets) // 2
        early = tweets[:mid]
        late = tweets[mid:]
        
        # Calculate sentiment for each half
        early_sentiment = self._quick_sentiment(early)
        late_sentiment = self._quick_sentiment(late)
        
        shift = late_sentiment - early_sentiment
        
        return {
            "cashtag": cashtag,
            "sentiment_shift": round(shift, 3),
            "early_sentiment": round(early_sentiment, 3),
            "late_sentiment": round(late_sentiment, 3),
            "trend_change": "MAJOR_SHIFT" if abs(shift) > 0.5 else "MODERATE" if abs(shift) > 0.2 else "STABLE",
            "direction": "MORE_BULLISH" if shift > 0 else "MORE_BEARISH" if shift < 0 else "UNCHANGED"
        }
    
    def _quick_sentiment(self, tweets: List[Tweet]) -> float:
        """Quick sentiment calculation"""
        scores = []
        for tweet in tweets:
            text_lower = tweet.text.lower()
            bull = sum(1 for kw in self.bullish_keywords if kw in text_lower)
            bear = sum(1 for kw in self.bearish_keywords if kw in text_lower)
            
            if bull > bear:
                scores.append(1)
            elif bear > bull:
                scores.append(-1)
            else:
                scores.append(0)
        
        return statistics.mean(scores) if scores else 0
    
    def get_market_wide_sentiment(self, watchlist: List[str]) -> Dict:
        """Get sentiment for entire watchlist"""
        sentiments = []
        
        for cashtag in watchlist:
            result = self.analyze_sentiment(cashtag)
            if "error" not in result:
                sentiments.append(result)
        
        if not sentiments:
            return {"error": "No sentiment data available"}
        
        avg_score = statistics.mean([s["sentiment_score"] for s in sentiments])
        
        bullish_count = sum(1 for s in sentiments if s["sentiment_label"] in ["BULLISH", "VERY_BULLISH"])
        bearish_count = sum(1 for s in sentiments if s["sentiment_label"] in ["BEARISH", "VERY_BEARISH"])
        
        return {
            "watchlist_size": len(watchlist),
            "with_data": len(sentiments),
            "avg_sentiment_score": round(avg_score, 3),
            "overall_mood": self._get_sentiment_label(avg_score),
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "neutral_count": len(sentiments) - bullish_count - bearish_count,
            "most_bullish": max(sentiments, key=lambda x: x["sentiment_score"])["cashtag"],
            "most_bearish": min(sentiments, key=lambda x: x["sentiment_score"])["cashtag"]
        }

from datetime import timedelta
