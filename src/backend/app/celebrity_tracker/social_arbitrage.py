"""Social Arbitrage Tracker - Exploit celebrity mention delays"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MentionEvent:
    celebrity: str
    ticker: str
    platform: str
    timestamp: datetime
    follower_count: int
    sentiment: str

class SocialArbitrageTracker:
    """Track and exploit social media arbitrage opportunities"""
    
    def __init__(self):
        self.recent_mentions: List[MentionEvent] = []
        self.platform_speed = {
            "twitter": 1,      # Fastest
            "reddit": 5,       # 5 min delay
            "discord": 3,      # 3 min delay
            "stocktwits": 2,   # 2 min delay
            "news": 30         # 30 min delay
        }
    
    def detect_arbitrage_window(self, mention: MentionEvent) -> Dict:
        """Detect if arbitrage window exists"""
        # Calculate expected impact
        impact = min(10, mention.follower_count / 10_000_000)
        
        # Window duration based on platform
        platform_delay = self.platform_speed.get(mention.platform, 10)
        window_duration = max(1, 10 - platform_delay)  # Faster = longer window
        
        # Check if within window
        age_minutes = (datetime.utcnow() - mention.timestamp).total_seconds() / 60
        
        if age_minutes > window_duration:
            return {
                "window_open": False,
                "reason": f"Window closed after {window_duration} minutes"
            }
        
        return {
            "window_open": True,
            "remaining_minutes": round(window_duration - age_minutes, 1),
            "expected_impact_pct": round(impact, 1),
            "urgency": "HIGH" if age_minutes < 2 else "MEDIUM",
            "strategy": f"Buy {mention.ticker} immediately" if mention.sentiment == "positive" else f"Short {mention.ticker}",
            "confidence": "HIGH" if mention.follower_count > 1_000_000 else "MEDIUM"
        }
    
    def get_platform_delay_table(self) -> Dict:
        """Get expected delays per platform"""
        return {
            "twitter_elite": {"delay_seconds": 0, "reliability": "HIGH"},
            "stocktwits": {"delay_seconds": 120, "reliability": "MEDIUM"},
            "discord_wsb": {"delay_seconds": 180, "reliability": "MEDIUM"},
            "reddit_hot": {"delay_seconds": 300, "reliability": "MEDIUM"},
            "mainstream_news": {"delay_seconds": 1800, "reliability": "HIGH"},
            " bloomberg_terminal": {"delay_seconds": 0, "reliability": "VERY_HIGH"}
        }
    
    def calculate_speed_advantage(self, your_latency_seconds: int) -> Dict:
        """Calculate your speed advantage"""
        avg_retail_latency = 300  # 5 minutes
        
        advantage = avg_retail_latency - your_latency_seconds
        
        return {
            "your_latency_seconds": your_latency_seconds,
            "avg_retail_latency_seconds": avg_retail_latency,
            "advantage_seconds": advantage,
            "advantage_type": "SPEED" if advantage > 0 else "NO_ADVANTAGE",
            "executable_strategies": [
                "Celebrity mention arb" if advantage > 60 else None,
                "News headline arb" if advantage > 180 else None,
                "Earnings reaction arb" if advantage > 30 else None
            ]
        }
