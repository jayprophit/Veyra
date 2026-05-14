"""WSB Analyzer - WallStreetBets sentiment analysis"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class Sentiment(Enum):
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"

@dataclass
class WSBPost:
    id: str
    title: str
    content: str
    upvotes: int
    tickers: List[str]
    sentiment: Sentiment
    timestamp: datetime

class WSBAnalyzer:
    """Analyze WSB for meme stock signals"""
    
    def __init__(self):
        self.bullish_kw = ["moon", "rocket", "tendies", "diamond hands", "buy", "calls", "yolo"]
        self.bearish_kw = ["put", "short", "crash", "dump", "sell", "rug pull", "tank"]
    
    def analyze_post(self, post: WSBPost) -> Dict:
        content = (post.title + " " + post.content).lower()
        
        bullish_count = sum(1 for kw in self.bullish_kw if kw in content)
        bearish_count = sum(1 for kw in self.bearish_kw if kw in content)
        
        meme_score = min(100, bullish_count * 10 + content.count("🚀") * 5)
        
        return {
            "ticker": post.tickers[0] if post.tickers else None,
            "sentiment": post.sentiment.value,
            "meme_score": meme_score,
            "viral": post.upvotes > 1000,
            "signal": "BUY" if meme_score > 70 and post.sentiment == Sentiment.VERY_BULLISH else "MONITOR"
        }
    
    def scan_trending(self, posts: List[WSBPost]) -> Dict:
        ticker_counts = {}
        for post in posts:
            for ticker in post.tickers:
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
        
        trending = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "trending": [{"ticker": t, "mentions": c} for t, c in trending],
            "total_posts": len(posts)
        }
    
    def inverse_wsb_signal(self, ticker: str, posts: List[WSBPost]) -> Dict:
        ticker_posts = [p for p in posts if ticker in p.tickers]
        if not ticker_posts:
            return {"signal": "NONE"}
        
        bullish = sum(1 for p in ticker_posts if p.sentiment in [Sentiment.BULLISH, Sentiment.VERY_BULLISH])
        pct = (bullish / len(ticker_posts)) * 100
        
        if pct > 85:
            return {"signal": "SELL", "reason": "Extreme euphoria - inverse WSB", "confidence": "HIGH"}
        elif pct < 20:
            return {"signal": "BUY", "reason": "Extreme fear - inverse WSB", "confidence": "MEDIUM"}
        return {"signal": "NEUTRAL", "wsb_bullish_pct": pct}
