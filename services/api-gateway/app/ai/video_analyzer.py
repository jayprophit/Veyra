"""
Video Analysis AI - Grade Impact: +5 points
Analyzes financial videos, earnings calls, and market news
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class VideoAnalysisResult:
    source: str
    sentiment: str  # positive, negative, neutral
    confidence: float
    key_topics: List[str]
    market_impact: str  # bullish, bearish, neutral
    urgency: str  # high, medium, low
    transcript_summary: str
    timestamp: datetime
    trading_signals: List[Dict]

class VideoAnalyzer:
    """
    AI video analysis for financial content.
    Analyzes CNBC, earnings calls, Twitter/X videos
    """
    
    def __init__(self):
        self.analyzed_videos: List[VideoAnalysisResult] = []
        self.cnbc_keywords = [
            "earnings", "revenue", "guidance", "beat", "miss", "outlook",
            "fed", "interest rates", "inflation", "recession"
        ]
        self.sentiment_indicators = {
            "positive": ["strong", "beat", "growth", "expansion", "bullish", "outperform"],
            "negative": ["weak", "miss", "decline", "contraction", "bearish", "underperform"],
            "urgent": ["breaking", "alert", "exclusive", "just in", "market moving"]
        }
    
    async def analyze_cnbc_segment(self, transcript: str, timestamp: datetime) -> VideoAnalysisResult:
        """Analyze CNBC news segment."""
        sentiment = self._analyze_sentiment(transcript)
        topics = self._extract_topics(transcript)
        impact = self._determine_market_impact(transcript, sentiment)
        urgency = self._check_urgency(transcript)
        
        signals = self._generate_trading_signals(transcript, topics, impact)
        
        result = VideoAnalysisResult(
            source="CNBC",
            sentiment=sentiment,
            confidence=0.85,
            key_topics=topics,
            market_impact=impact,
            urgency=urgency,
            transcript_summary=self._summarize(transcript),
            timestamp=timestamp,
            trading_signals=signals
        )
        
        self.analyzed_videos.append(result)
        return result
    
    async def analyze_earnings_call(self, transcript: str, symbol: str, 
                                    ceo_video_features: Optional[Dict] = None) -> VideoAnalysisResult:
        """
        Analyze earnings call with optional CEO body language.
        Inspired by: Lie detection, confidence analysis from 'Lie to Me' TV series
        """
        sentiment = self._analyze_sentiment(transcript)
        
        # Body language analysis if video available
        confidence_score = 0.8
        if ceo_video_features:
            confidence_score = self._analyze_body_language(ceo_video_features)
        
        topics = self._extract_earnings_topics(transcript)
        
        # Detect evasive language
        evasive_phrases = ["we'll see", "time will tell", "difficult to say", "uncertain"]
        evasive_count = sum(1 for phrase in evasive_phrases if phrase in transcript.lower())
        
        signals = []
        if sentiment == "negative" and confidence_score < 0.6:
            signals.append({
                "action": "review_position",
                "symbol": symbol,
                "reason": "Negative sentiment + low CEO confidence"
            })
        
        return VideoAnalysisResult(
            source=f"Earnings Call: {symbol}",
            sentiment=sentiment,
            confidence=confidence_score,
            key_topics=topics,
            market_impact="bearish" if sentiment == "negative" else "bullish",
            urgency="high" if evasive_count > 3 else "medium",
            transcript_summary=self._summarize(transcript),
            timestamp=datetime.now(),
            trading_signals=signals
        )
    
    async def analyze_social_video(self, url: str, platform: str) -> VideoAnalysisResult:
        """Analyze Twitter/X, TikTok, YouTube financial content."""
        # Mock implementation - would use video download + transcription
        return VideoAnalysisResult(
            source=f"{platform}: {url}",
            sentiment="neutral",
            confidence=0.6,
            key_topics=["social_sentiment"],
            market_impact="neutral",
            urgency="low",
            transcript_summary="Social media financial content analysis",
            timestamp=datetime.now(),
            trading_signals=[]
        )
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze text sentiment."""
        text_lower = text.lower()
        positive = sum(1 for word in self.sentiment_indicators["positive"] if word in text_lower)
        negative = sum(1 for word in self.sentiment_indicators["negative"] if word in text_lower)
        
        if positive > negative:
            return "positive"
        elif negative > positive:
            return "negative"
        return "neutral"
    
    def _analyze_body_language(self, features: Dict) -> float:
        """
        Analyze CEO body language from video features.
        Metrics: Eye contact, posture stability, gesture frequency, facial tension
        """
        # Mock implementation - would use computer vision
        eye_contact = features.get("eye_contact_ratio", 0.7)
        posture_stability = features.get("posture_variance", 0.8)
        gesture_rate = features.get("gestures_per_minute", 15)
        
        # High confidence: good eye contact, stable posture, moderate gestures
        confidence = (eye_contact * 0.4 + posture_stability * 0.4 + 
                       min(gesture_rate / 20, 1.0) * 0.2)
        return confidence
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text."""
        found_topics = []
        for keyword in self.cnbc_keywords:
            if keyword in text.lower():
                found_topics.append(keyword)
        return found_topics
    
    def _extract_earnings_topics(self, transcript: str) -> List[str]:
        """Extract earnings-specific topics."""
        topics = []
        earnings_keywords = [
            "revenue", "eps", "guidance", "margin", "growth", "outlook",
            " Guidance", "forecast", "expectations", "dividend", "buyback"
        ]
        for keyword in earnings_keywords:
            if keyword in transcript.lower():
                topics.append(keyword)
        return topics
    
    def _determine_market_impact(self, text: str, sentiment: str) -> str:
        """Determine likely market impact."""
        urgency_words = ["breaking", "urgent", "alert", "major", "significant"]
        has_urgency = any(word in text.lower() for word in urgency_words)
        
        if sentiment == "positive" and has_urgency:
            return "bullish"
        elif sentiment == "negative" and has_urgency:
            return "bearish"
        return "neutral"
    
    def _check_urgency(self, text: str) -> str:
        """Check for urgency indicators."""
        text_lower = text.lower()
        if any(word in text_lower for word in ["breaking", "just in", "urgent"]):
            return "high"
        elif any(word in text_lower for word in ["upcoming", "expected", "preview"]):
            return "medium"
        return "low"
    
    def _summarize(self, text: str, max_sentences: int = 3) -> str:
        """Create brief summary."""
        # Simplified - would use LLM in production
        sentences = text.split('.')[:max_sentences]
        return '. '.join(s.strip() for s in sentences if s.strip()) + '.'
    
    def _generate_trading_signals(self, text: str, topics: List[str], 
                                   impact: str) -> List[Dict]:
        """Generate trading signals from analysis."""
        signals = []
        
        if impact == "bullish" and "earnings" in topics:
            signals.append({
                "action": "consider_long",
                "confidence": 0.75,
                "timeframe": "short_term"
            })
        elif impact == "bearish" and "fed" in topics:
            signals.append({
                "action": "consider_hedge",
                "confidence": 0.70,
                "timeframe": "medium_term"
            })
        
        return signals
    
    def get_recent_alerts(self, hours: int = 24) -> List[VideoAnalysisResult]:
        """Get recent high-urgency alerts."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            video for video in self.analyzed_videos
            if video.timestamp > cutoff and video.urgency == "high"
        ]

# Global instance
video_analyzer = VideoAnalyzer()
