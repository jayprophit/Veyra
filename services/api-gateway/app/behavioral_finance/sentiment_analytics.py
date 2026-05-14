"""Sentiment Analytics"""
from typing import Dict

class SentimentAnalytics:
    def sentiment_score(self, positive: int, negative: int, neutral: int) -> Dict:
        total = positive + negative + neutral
        if total == 0:
            return {"score": 0, "sentiment": "neutral"}
        score = (positive - negative) / total
        sentiment = "bullish" if score > 0.2 else "bearish" if score < -0.2 else "neutral"
        return {"score": round(score, 2), "sentiment": sentiment, "total_mentions": total}
    
    def social_volume_impact(self, volume: int, price_change: float) -> Dict:
        correlation = volume * price_change
        return {"correlation": correlation, "significance": "high" if abs(correlation) > 1000 else "low"}
