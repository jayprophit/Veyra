"""Celebrity Influence Analyzer - Track celebrity impact on stock prices"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum

class CelebrityTier(Enum):
    MEGA = "mega"           # 100M+ followers (Elon, Taylor Swift)
    MACRO = "macro"         # 10M-100M (Major influencers)
    MID = "mid"             # 1M-10M
    MICRO = "micro"         # 100K-1M
    NANO = "nano"           # <100K

@dataclass
class CelebrityMention:
    celebrity: str
    platform: str
    mention_text: str
    timestamp: datetime
    follower_count: int
    engagement_rate: float
    sentiment: str
    ticker_mentioned: str

class CelebrityInfluenceAnalyzer:
    """Analyze how celebrity mentions affect stock prices"""
    
    def __init__(self):
        self.influencer_database = self._init_influencer_db()
        self.mention_history: List[CelebrityMention] = []
        self.impact_model = self._init_impact_model()
        
    def _init_influencer_db(self) -> Dict:
        """Database of influential celebrities and their market impact"""
        return {
            "Elon Musk": {
                "tier": CelebrityTier.MEGA,
                "followers": {"twitter": 180000000},
                "typical_impact_pct": 5.0,
                "primary_sectors": ["Tech", "EV", "Crypto", "Space"],
                "impact_duration_hours": 24,
                "mention_frequency": "high",
                "reliability": "medium"  # Sometimes jokes/memes
            },
            "Cathie Wood": {
                "tier": CelebrityTier.MACRO,
                "followers": {"twitter": 1500000},
                "typical_impact_pct": 3.0,
                "primary_sectors": ["Tech", "Biotech", "Innovation"],
                "impact_duration_hours": 48,
                "mention_frequency": "medium",
                "reliability": "high"
            },
            "Chamath Palihapitiya": {
                "tier": CelebrityTier.MACRO,
                "followers": {"twitter": 1700000},
                "typical_impact_pct": 4.0,
                "primary_sectors": ["SPACs", "Tech", "Climate"],
                "impact_duration_hours": 12,
                "mention_frequency": "medium",
                "reliability": "medium"
            },
            "Jim Cramer": {
                "tier": CelebrityTier.MACRO,
                "followers": {"twitter": 2000000},
                "typical_impact_pct": -2.0,  # Inverse Cramer!
                "primary_sectors": ["All"],
                "impact_duration_hours": 6,
                "mention_frequency": "high",
                "reliability": "low"  # Inverse is often correct
            },
            "Mark Cuban": {
                "tier": CelebrityTier.MACRO,
                "followers": {"twitter": 8900000},
                "typical_impact_pct": 2.5,
                "primary_sectors": ["Tech", "Crypto", "Sports"],
                "impact_duration_hours": 12,
                "mention_frequency": "medium",
                "reliability": "high"
            },
            "Warren Buffett": {
                "tier": CelebrityTier.MEGA,
                "followers": {"twitter": 0},  # Not on Twitter
                "typical_impact_pct": 2.0,
                "primary_sectors": ["All"],
                "impact_duration_hours": 72,
                "mention_frequency": "low",
                "reliability": "very_high"
            }
        }
    
    def _init_impact_model(self) -> Dict:
        """Model for calculating impact based on celebrity and context"""
        return {
            "follower_multiplier": 0.0001,  # Per follower
            "engagement_weight": 0.3,
            "sentiment_multiplier": {
                "very_positive": 1.5,
                "positive": 1.0,
                "neutral": 0.2,
                "negative": -1.0,
                "very_negative": -1.5
            },
            "sector_alignment_bonus": 0.5,  # If celeb is expert in sector
            "timing_decay": 0.9  # Per hour
        }
    
    def calculate_mention_impact(self, mention: CelebrityMention) -> Dict:
        """Calculate expected stock impact from celebrity mention"""
        
        celeb_data = self.influencer_database.get(mention.celebrity, {})
        
        if not celeb_data:
            # Unknown influencer - estimate based on followers
            base_impact = mention.follower_count * self.impact_model["follower_multiplier"]
        else:
            base_impact = celeb_data.get("typical_impact_pct", 2.0)
            
            # Adjust for engagement
            engagement_boost = mention.engagement_rate * self.impact_model["engagement_weight"]
            
            # Adjust for sentiment
            sentiment_mult = self.impact_model["sentiment_multiplier"].get(mention.sentiment, 0.2)
            
            # Sector alignment bonus
            sector_bonus = 0
            if mention.ticker_mentioned in celeb_data.get("primary_sectors", []):
                sector_bonus = self.impact_model["sector_alignment_bonus"]
            
            base_impact = base_impact * (1 + engagement_boost) * abs(sentiment_mult) + sector_bonus
            
            # Apply sentiment direction
            if sentiment_mult < 0:
                base_impact = -base_impact
        
        # Calculate timing decay
        hours_since = (datetime.utcnow() - mention.timestamp).total_seconds() / 3600
        decay = self.impact_model["timing_decay"] ** hours_since
        
        current_impact = base_impact * decay
        
        return {
            "celebrity": mention.celebrity,
            "ticker": mention.ticker_mentioned,
            "immediate_impact_pct": round(base_impact, 2),
            "current_expected_impact_pct": round(current_impact, 2),
            "peak_impact_timing": "0-6 hours post-mention",
            "impact_fades": f"{int(hours_since + celeb_data.get('impact_duration_hours', 24))} hours",
            "confidence": self._calculate_confidence(mention, celeb_data),
            "direction": "up" if current_impact > 0 else "down" if current_impact < 0 else "neutral"
        }
    
    def _calculate_confidence(self, mention: CelebrityMention, 
                             celeb_data: Dict) -> str:
        """Calculate confidence in impact prediction"""
        confidence_score = 0.5
        
        # Known influencer = higher confidence
        if celeb_data:
            confidence_score += 0.2
            if celeb_data.get("reliability") == "very_high":
                confidence_score += 0.2
            elif celeb_data.get("reliability") == "high":
                confidence_score += 0.1
        
        # High engagement = more likely to move
        if mention.engagement_rate > 0.05:
            confidence_score += 0.1
        
        # Clear sentiment = higher confidence
        if mention.sentiment in ["very_positive", "very_negative"]:
            confidence_score += 0.1
        
        if confidence_score > 0.8:
            return "HIGH"
        elif confidence_score > 0.6:
            return "MEDIUM"
        else:
            return "LOW"
    
    def detect_coordinated_promotion(self, 
                                    mentions: List[CelebrityMention],
                                    timeframe_hours: int = 24) -> Dict:
        """Detect if multiple celebrities are promoting same stock"""
        
        # Group by ticker
        ticker_mentions = {}
        for mention in mentions:
            if (datetime.utcnow() - mention.timestamp).total_seconds() / 3600 <= timeframe_hours:
                if mention.ticker_mentioned not in ticker_mentions:
                    ticker_mentions[mention.ticker_mentioned] = []
                ticker_mentions[mention.ticker_mentioned].append(mention)
        
        # Find coordinated promotions
        coordinated = []
        for ticker, ticker_list in ticker_mentions.items():
            if len(ticker_list) >= 3:  # 3+ celebrities
                total_followers = sum(m.follower_count for m in ticker_list)
                
                coordinated.append({
                    "ticker": ticker,
                    "celebrity_count": len(ticker_list),
                    "celebrities": [m.celebrity for m in ticker_list],
                    "combined_reach": total_followers,
                    "time_window_hours": timeframe_hours,
                    "is_coordinated": self._check_coordination_timing(ticker_list),
                    "estimated_impact_pct": min(len(ticker_list) * 2.5, 20),  # Cap at 20%
                    "risk_level": "HIGH" if len(ticker_list) > 5 else "MEDIUM"
                })
        
        return {
            "coordinated_promotions_detected": len(coordinated),
            "promotions": sorted(coordinated, key=lambda x: x["estimated_impact_pct"], reverse=True),
            "warning": "Potential pump scheme" if any(p["is_coordinated"] for p in coordinated) else None
        }
    
    def _check_coordination_timing(self, mentions: List[CelebrityMention]) -> bool:
        """Check if mentions appear coordinated (too close in time)"""
        if len(mentions) < 3:
            return False
        
        timestamps = sorted([m.timestamp for m in mentions])
        
        # If all within 2 hours, likely coordinated
        time_spread = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        
        return time_spread < 2.0
    
    def get_inverse_cramer_signal(self, cramer_mentions: List[Dict]) -> Dict:
        """Generate inverse Cramer trading signal"""
        if not cramer_mentions:
            return {"signal": "none", "reason": "No recent Cramer mentions"}
        
        latest = cramer_mentions[-1]
        
        # Inverse Cramer strategy
        if latest.get("recommendation") == "buy":
            signal = "SELL"
            confidence = 0.65  # Historical accuracy of inverse Cramer
        elif latest.get("recommendation") == "sell":
            signal = "BUY"
            confidence = 0.65
        else:
            signal = "HOLD"
            confidence = 0.5
        
        return {
            "signal": signal,
            "original_cramer_call": latest.get("recommendation"),
            "ticker": latest.get("ticker"),
            "confidence": confidence,
            "historical_accuracy": "65% (as of 2023)",
            "timeframe": "1-7 days",
            "disclaimer": "For entertainment purposes, not financial advice"
        }
    
    def track_elon_effect(self, ticker: str, mention_history: List[Dict]) -> Dict:
        """Special tracking for Elon Musk's impact on specific tickers"""
        
        # Elon-specific analysis
        elon_mentions = [m for m in mention_history if m.get("celebrity") == "Elon Musk"]
        
        if not elon_mentions:
            return {"elon_impact": "none", "reason": "No recent mentions"}
        
        # Calculate historical response
        avg_response = statistics.mean([m.get("price_change_24h", 0) for m in elon_mentions])
        
        # Doge/ crypto effect
        if ticker in ["DOGE", "BTC", "SHIB"]:
            expected_bounce = 8.0  # 8% typical for crypto
        elif ticker in ["TSLA"]:
            expected_bounce = 3.0  # 3% for Tesla
        else:
            expected_bounce = abs(avg_response)
        
        return {
            "elon_mentions_count": len(elon_mentions),
            "avg_historical_response": round(avg_response, 2),
            "expected_next_impact_pct": round(expected_bounce, 2),
            "timing": "Immediate to 6 hours",
            "duration": "1-3 days",
            "correlation": "HIGH" if abs(avg_response) > 2 else "MEDIUM",
            "tweet_momentum": "EXPLOSIVE" if len(elon_mentions) > 2 else "NORMAL"
        }
    
    def generate_social_arbitrage_opportunities(self, 
                                              recent_mentions: List[CelebrityMention]) -> List[Dict]:
        """Generate arbitrage opportunities from celebrity mentions"""
        opportunities = []
        
        for mention in recent_mentions:
            if (datetime.utcnow() - mention.timestamp).total_seconds() / 3600 > 1:
                continue  # Skip old mentions
            
            impact = self.calculate_mention_impact(mention)
            
            if impact["confidence"] in ["HIGH", "MEDIUM"] and abs(impact["immediate_impact_pct"]) > 2:
                opportunities.append({
                    "ticker": mention.ticker_mentioned,
                    "celebrity": mention.celebrity,
                    "direction": impact["direction"],
                    "expected_move_pct": abs(impact["immediate_impact_pct"]),
                    "urgency": "IMMEDIATE",
                    "window_minutes": 30,
                    "strategy": f"Buy calls if up, buy puts if down" if impact["direction"] != "neutral" else "Avoid",
                    "risk": "HIGH - Binary event"
                })
        
        return sorted(opportunities, key=lambda x: x["expected_move_pct"], reverse=True)

# Import for statistics
import statistics
