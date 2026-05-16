"""
Video Market Learner AI
=======================
Learn from video content: financial news, earnings calls, conferences
Real-time video stream analysis for market intelligence
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class VideoContentType(Enum):
    EARNINGS_CALL = "earnings_call"
    NEWS_BROADCAST = "news_broadcast"
    CONFERENCE = "conference"
    EXECUTIVE_INTERVIEW = "executive_interview"
    ANALYST_BRIEFING = "analyst_briefing"


@dataclass
class VideoInsight:
    """Insight extracted from video"""
    timestamp: float  # seconds into video
    content_type: str
    ticker: Optional[str]
    sentiment: str  # 'bullish', 'bearish', 'neutral'
    confidence: float
    key_quote: str
    body_language_stress: Optional[float]
    voice_stress: Optional[float]
    visual_cues: List[str]


@dataclass
class ExecutivePresence:
    """Executive appearance analysis"""
    name: str
    title: str
    confidence_level: float
    stress_indicators: List[str]
    deception_signals: List[str]
    conviction_score: float  # 0-1
    eye_contact_score: float
    posture_score: float


class VideoMarketLearner:
    """
    AI that learns from watching financial video content
    
    Capabilities:
    - Earnings call video analysis
    - Executive body language reading
    - Multi-modal sentiment (visual + audio + text)
    - Conference presentation scoring
    - News broadcast parsing
    """
    
    def __init__(self):
        self.video_memory: List[Dict] = []
        self.executive_profiles: Dict[str, ExecutivePresence] = {}
        self.ticker_mentions: Dict[str, List[VideoInsight]] = {}
        self.pattern_database: Dict[str, List[Dict]] = {}
        
    def analyze_earnings_video(self, ticker: str, video_duration: float,
                               transcript_segments: List[Dict],
                               executive_segments: List[Dict]) -> Dict:
        """
        Analyze earnings call video for visual and verbal cues
        
        Args:
            ticker: Company ticker
            video_duration: Video length in seconds
            transcript_segments: List of {timestamp, speaker, text, sentiment}
            executive_segments: List of {timestamp, executive, video_features}
        """
        insights = []
        
        for segment in transcript_segments:
            timestamp = segment['timestamp']
            speaker = segment['speaker']
            text = segment['text']
            sentiment = segment.get('sentiment', 'neutral')
            
            # Find corresponding executive video features
            exec_features = None
            for exec_seg in executive_segments:
                if abs(exec_seg['timestamp'] - timestamp) < 5:
                    exec_features = exec_seg
                    break
            
            # Calculate stress indicators
            body_stress = None
            voice_stress = None
            visual_cues = []
            
            if exec_features:
                body_stress = self._calculate_body_stress(exec_features)
                voice_stress = self._calculate_voice_stress(exec_features)
                visual_cues = self._extract_visual_cues(exec_features)
            
            # Determine confidence based on stress alignment with sentiment
            confidence = self._calculate_confidence(sentiment, body_stress, voice_stress)
            
            insight = VideoInsight(
                timestamp=timestamp,
                content_type=VideoContentType.EARNINGS_CALL.value,
                ticker=ticker,
                sentiment=sentiment,
                confidence=confidence,
                key_quote=text[:100] + "..." if len(text) > 100 else text,
                body_language_stress=body_stress,
                voice_stress=voice_stress,
                visual_cues=visual_cues
            )
            
            insights.append(insight)
            
            # Store for ticker
            if ticker not in self.ticker_mentions:
                self.ticker_mentions[ticker] = []
            self.ticker_mentions[ticker].append(insight)
        
        # Generate summary
        return self._generate_earnings_summary(ticker, insights)
    
    def _calculate_body_stress(self, features: Dict) -> float:
        """Calculate body language stress score (0-1)"""
        stress_signals = 0
        
        # Fidgeting
        if features.get('hand_movements', 0) > 0.5:
            stress_signals += 0.2
        
        # Posture changes
        if features.get('posture_shifts', 0) > 3:
            stress_signals += 0.2
        
        # Facial tension
        if features.get('jaw_tension', False):
            stress_signals += 0.3
        
        # Blink rate (elevated = stress)
        blink_rate = features.get('blink_rate', 15)
        if blink_rate > 20:
            stress_signals += 0.2
        
        # Shoulder tension
        if features.get('shoulder_tension', False):
            stress_signals += 0.1
        
        return min(stress_signals, 1.0)
    
    def _calculate_voice_stress(self, features: Dict) -> float:
        """Calculate voice stress score (0-1)"""
        stress_signals = 0
        
        # Pitch variation (high = stress)
        pitch_var = features.get('pitch_variation', 0)
        if pitch_var > 50:
            stress_signals += 0.3
        
        # Speech rate changes
        rate_change = features.get('speech_rate_change', 0)
        if abs(rate_change) > 20:
            stress_signals += 0.2
        
        # Pause frequency
        pauses = features.get('pause_frequency', 0)
        if pauses > 5:
            stress_signals += 0.3
        
        # Volume inconsistency
        volume_var = features.get('volume_variance', 0)
        if volume_var > 30:
            stress_signals += 0.2
        
        return min(stress_signals, 1.0)
    
    def _extract_visual_cues(self, features: Dict) -> List[str]:
        """Extract meaningful visual cues"""
        cues = []
        
        if features.get('furrowed_brow', False):
            cues.append('concentration/concern')
        
        if features.get('forced_smile', False):
            cues.append('insincerity')
        
        if features.get('eye_darting', False):
            cues.append('nervousness')
        
        if features.get('palm_sweating_visible', False):
            cues.append('high_stress')
        
        if features.get('open_posture', False):
            cues.append('confidence')
        
        if features.get('leaning_in', False):
            cues.append('engagement')
        
        return cues
    
    def _calculate_confidence(self, sentiment: str, 
                              body_stress: Optional[float],
                              voice_stress: Optional[float]) -> float:
        """Calculate overall confidence in sentiment reading"""
        base_confidence = 0.7
        
        # Stress alignment check
        if body_stress is not None and voice_stress is not None:
            avg_stress = (body_stress + voice_stress) / 2
            
            # If sentiment is positive but stress is high, reduce confidence
            if sentiment == 'bullish' and avg_stress > 0.5:
                base_confidence -= 0.2
            
            # If sentiment is negative and stress is high, increase confidence
            if sentiment == 'bearish' and avg_stress > 0.5:
                base_confidence += 0.1
        
        return max(0.5, min(0.95, base_confidence))
    
    def _generate_earnings_summary(self, ticker: str, 
                                   insights: List[VideoInsight]) -> Dict:
        """Generate earnings call video analysis summary"""
        if not insights:
            return {'error': 'No insights generated'}
        
        # Sentiment distribution
        bullish = len([i for i in insights if i.sentiment == 'bullish'])
        bearish = len([i for i in insights if i.sentiment == 'bearish'])
        neutral = len([i for i in insights if i.sentiment == 'neutral'])
        total = len(insights)
        
        # Stress analysis
        stress_readings = [i.body_language_stress for i in insights 
                          if i.body_language_stress is not None]
        avg_stress = np.mean(stress_readings) if stress_readings else 0
        
        # Key visual moments
        high_stress_moments = [i for i in insights 
                              if i.body_language_stress and i.body_language_stress > 0.6]
        
        # Confidence trend
        avg_confidence = np.mean([i.confidence for i in insights])
        
        return {
            'ticker': ticker,
            'total_insights': total,
            'sentiment_distribution': {
                'bullish_pct': round(bullish / total * 100, 1),
                'bearish_pct': round(bearish / total * 100, 1),
                'neutral_pct': round(neutral / total * 100, 1)
            },
            'overall_sentiment': 'bullish' if bullish > bearish else 'bearish' if bearish > bullish else 'neutral',
            'average_stress_level': round(avg_stress, 2),
            'high_stress_moments': len(high_stress_moments),
            'average_confidence': round(avg_confidence, 2),
            'key_concerns': self._extract_concerns(high_stress_moments),
            'executive_composure_score': round(1 - avg_stress, 2),
            'recommendation': self._generate_recommendation(
                bullish, bearish, avg_stress, avg_confidence
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def _extract_concerns(self, high_stress_moments: List[VideoInsight]) -> List[str]:
        """Extract key concerns from high-stress moments"""
        concerns = []
        
        for moment in high_stress_moments[:3]:  # Top 3
            if moment.visual_cues:
                concerns.append({
                    'timestamp': moment.timestamp,
                    'quote': moment.key_quote,
                    'cues': moment.visual_cues
                })
        
        return concerns
    
    def _generate_recommendation(self, bullish: int, bearish: int,
                                  stress: float, confidence: float) -> str:
        """Generate trading recommendation"""
        if bullish > bearish * 1.5 and stress < 0.3 and confidence > 0.75:
            return "STRONG_BUY - Confident bullish signals with low executive stress"
        elif bullish > bearish and stress < 0.4:
            return "BUY - Positive sentiment with acceptable stress levels"
        elif bearish > bullish * 1.2 and stress > 0.5:
            return "AVOID/SHORT - Negative signals with high executive stress"
        elif stress > 0.6:
            return "WAIT - High executive stress suggests uncertainty"
        else:
            return "NEUTRAL - Mixed signals, wait for clarity"
    
    def detect_deception(self, executive_name: str, 
                       video_segments: List[Dict]) -> Dict:
        """
        Detect potential deception in executive communications
        
        Warning: This is probabilistic and should not be used as sole evidence
        """
        deception_signals = []
        
        for segment in video_segments:
            signals = []
            
            # Micro-expressions
            if segment.get('micro_expression_mismatch', False):
                signals.append('facial_expression_mismatch')
            
            # Eye movement patterns
            if segment.get('eye_darting_pattern', False):
                signals.append('avoiding_eye_contact')
            
            # Verbal-nonverbal mismatch
            if segment.get('positive_words_negative_body', False):
                signals.append('verbal_nonverbal_mismatch')
            
            # Overly specific details (overcompensation)
            if segment.get('excessive_specificity', False):
                signals.append('excessive_detail')
            
            # Self-soothing behaviors
            if segment.get('self_touch', 0) > 3:
                signals.append('self_soothing')
            
            if signals:
                deception_signals.append({
                    'timestamp': segment['timestamp'],
                    'signals': signals,
                    'severity': len(signals)
                })
        
        # Calculate deception probability
        if not deception_signals:
            deception_prob = 0.1
        else:
            avg_severity = np.mean([s['severity'] for s in deception_signals])
            deception_prob = min(0.1 + (avg_severity * 0.1), 0.8)
        
        return {
            'executive': executive_name,
            'deception_probability': round(deception_prob, 2),
            'deception_signals_count': len(deception_signals),
            'key_moments': deception_signals[:5],
            'assessment': 'HIGH_SUSPICION' if deception_prob > 0.6 else 
                         'MODERATE_SUSPICION' if deception_prob > 0.4 else 
                         'LOW_SUSPICION',
            'disclaimer': 'This is an AI assessment and should be verified by human analysis'
        }
    
    def analyze_conference_presentation(self, ticker: str, 
                                       slides: List[Dict],
                                       presenter_video: List[Dict]) -> Dict:
        """
        Analyze conference presentation for investor confidence
        
        Returns presentation quality score and key takeaways
        """
        # Slide analysis
        slide_scores = []
        for slide in slides:
            score = 0
            
            # Data density (good)
            if slide.get('charts_count', 0) > 0:
                score += 0.2
            
            # Forward looking statements (good if specific)
            if slide.get('forward_guidance', False):
                score += 0.3
            
            # Clear metrics
            if slide.get('kpi_count', 0) > 2:
                score += 0.2
            
            # Visual clarity
            if slide.get('text_density', 100) < 100:
                score += 0.3
            
            slide_scores.append(score)
        
        avg_slide_score = np.mean(slide_scores) if slide_scores else 0
        
        # Presenter analysis
        presenter_confidence = 0
        if presenter_video:
            posture_scores = [v.get('posture_confidence', 0.5) for v in presenter_video]
            presenter_confidence = np.mean(posture_scores)
        
        # Overall presentation score
        presentation_score = (avg_slide_score * 0.6) + (presenter_confidence * 0.4)
        
        return {
            'ticker': ticker,
            'presentation_score': round(presentation_score, 2),
            'slide_quality': round(avg_slide_score, 2),
            'presenter_confidence': round(presenter_confidence, 2),
            'slide_count': len(slides),
            'assessment': 'EXCELLENT' if presentation_score > 0.8 else 
                         'GOOD' if presentation_score > 0.6 else 
                         'NEEDS_IMPROVEMENT',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_learning_summary(self) -> Dict:
        """Get summary of video learning"""
        return {
            'videos_analyzed': len(self.video_memory),
            'tickers_covered': len(self.ticker_mentions),
            'executives_profiled': len(self.executive_profiles),
            'total_insights': sum(len(v) for v in self.ticker_mentions.values()),
            'timestamp': datetime.now().isoformat()
        }


# Usage
def analyze_earnings_call(ticker: str, video_data: Dict) -> Dict:
    """Quick earnings video analysis"""
    learner = VideoMarketLearner()
    
    return learner.analyze_earnings_video(
        ticker=ticker,
        video_duration=video_data.get('duration', 3600),
        transcript_segments=video_data.get('transcript', []),
        executive_segments=video_data.get('executive_features', [])
    )


def check_executive_deception(executive: str, segments: List[Dict]) -> Dict:
    """Check for deception signals"""
    learner = VideoMarketLearner()
    return learner.detect_deception(executive, segments)
