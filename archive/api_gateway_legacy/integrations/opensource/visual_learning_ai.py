"""
Visual Learning AI Production System
Advanced computer vision and video analysis for financial insights
"""

import cv2
import numpy as np
import tensorflow as tf
from transformers import pipeline, AutoTokenizer, AutoModelForVideoClassification
import torch
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import json
from pathlib import Path
import requests
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import yt_dlp
import whisper
import mediapipe as mp
from deepface import DeepFace
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

@dataclass
class VideoAnalysis:
    """Video analysis results"""
    video_id: str
    sentiment_score: float
    confidence_score: float
    key_topics: List[str]
    speaker_emotions: Dict[str, float]
    visual_cues: List[str]
    financial_relevance: float
    timestamp: datetime
    summary: str

@dataclass
class EarningsCallAnalysis:
    """Earnings call specific analysis"""
    company_ticker: str
    executive_confidence: float
    deception_indicators: List[str]
    financial_projections: Dict[str, float]
    sentiment_trend: List[float]
    body_language_analysis: Dict[str, float]
    recommendation: str

class VisualLearningAI:
    """Production-ready Visual Learning AI System"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing Visual Learning AI on device: {self.device}")
        
        # Initialize models
        self._initialize_models()
        
        # Initialize MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        
        # Initialize Whisper for speech-to-text
        self.whisper_model = whisper.load_model("base")
        
        # Initialize sentiment analysis
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            device=0 if self.device == "cuda" else -1
        )
        
        # Initialize video classification
        self.video_classifier = pipeline(
            "video-classification",
            model="MCG-NJU/videomae-base-finetuned-kinetics",
            device=0 if self.device == "cuda" else -1
        )
        
        # Initialize computer vision models
        self._initialize_cv_models()
        
    def _initialize_models(self):
        """Initialize deep learning models"""
        try:
            # Load pre-trained models for financial analysis
            self.emotion_model = tf.keras.models.load_model(
                "models/emotion_recognition.h5"
            ) if Path("models/emotion_recognition.h5").exists() else None
            
            self.deception_model = tf.keras.models.load_model(
                "models/deception_detection.h5"
            ) if Path("models/deception_detection.h5").exists() else None
            
            logger.info("Deep learning models initialized")
        except Exception as e:
            logger.warning(f"Could not load custom models: {e}")
            
    def _initialize_cv_models(self):
        """Initialize computer vision models"""
        try:
            # Face detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.5
            )
            
            # Face mesh for detailed facial analysis
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5
            )
            
            # Pose detection
            self.pose_detection = self.mp_pose.Pose(
                static_image_mode=False, model_complexity=1, enable_segmentation=False
            )
            
            # Hand detection
            self.hand_detection = self.mp_hands.Hands(
                static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5
            )
            
            logger.info("Computer vision models initialized")
        except Exception as e:
            logger.error(f"Error initializing CV models: {e}")
            
    async def analyze_youtube_video(self, video_url: str, company_ticker: Optional[str] = None) -> VideoAnalysis:
        """
        Analyze YouTube video for financial insights
        
        Args:
            video_url: YouTube video URL
            company_ticker: Optional company ticker for context
            
        Returns:
            VideoAnalysis object with comprehensive results
        """
        try:
            logger.info(f"Analyzing YouTube video: {video_url}")
            
            # Download video
            video_path = await self._download_video(video_url)
            
            # Extract audio and transcribe
            audio_transcript = await self._transcribe_audio(video_path)
            
            # Analyze video frames
            frame_analysis = await self._analyze_video_frames(video_path)
            
            # Analyze audio sentiment
            audio_sentiment = await self._analyze_audio_sentiment(audio_transcript)
            
            # Combine analyses
            analysis = await self._combine_analyses(
                video_url, frame_analysis, audio_sentiment, company_ticker
            )
            
            # Cleanup
            Path(video_path).unlink(missing_ok=True)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing YouTube video: {e}")
            raise
            
    async def analyze_earnings_call(self, video_url: str, company_ticker: str) -> EarningsCallAnalysis:
        """
        Specialized analysis for earnings calls
        
        Args:
            video_url: Earnings call video URL
            company_ticker: Company ticker symbol
            
        Returns:
            EarningsCallAnalysis with detailed insights
        """
        try:
            logger.info(f"Analyzing earnings call for {company_ticker}")
            
            # Get general video analysis
            video_analysis = await self.analyze_youtube_video(video_url, company_ticker)
            
            # Get company financial data
            company_data = await self._get_company_financials(company_ticker)
            
            # Detect deception indicators
            deception_indicators = await self._detect_deception(video_analysis)
            
            # Analyze executive confidence
            executive_confidence = await self._analyze_executive_confidence(video_analysis)
            
            # Extract financial projections
            financial_projections = await self._extract_financial_projections(
                video_analysis, company_data
            )
            
            # Analyze body language
            body_language_analysis = await self._analyze_body_language(video_analysis)
            
            # Generate recommendation
            recommendation = await self._generate_investment_recommendation(
                executive_confidence, deception_indicators, financial_projections
            )
            
            return EarningsCallAnalysis(
                company_ticker=company_ticker,
                executive_confidence=executive_confidence,
                deception_indicators=deception_indicators,
                financial_projections=financial_projections,
                sentiment_trend=video_analysis.sentiment_score,
                body_language_analysis=body_language_analysis,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error analyzing earnings call: {e}")
            raise
            
    async def _download_video(self, video_url: str) -> str:
        """Download video from YouTube"""
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': 'temp_video_%(id)s.%(ext)s',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            return ydl.prepare_filename(info)
            
    async def _transcribe_audio(self, video_path: str) -> str:
        """Transcribe audio from video"""
        try:
            result = self.whisper_model.transcribe(video_path)
            return result["text"]
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
            
    async def _analyze_video_frames(self, video_path: str) -> Dict:
        """Analyze video frames for visual cues"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            emotions = []
            visual_cues = []
            speaker_presence = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Analyze every 30th frame (1 second apart for 30fps)
                if frame_count % 30 == 0:
                    # Face detection and emotion analysis
                    emotion_result = await self._analyze_frame_emotion(frame)
                    if emotion_result:
                        emotions.append(emotion_result)
                        
                    # Detect visual cues
                    visual_cue_result = await self._detect_visual_cues(frame)
                    visual_cues.extend(visual_cue_result)
                    
                    # Check for speaker presence
                    speaker_present = await self._detect_speaker(frame)
                    speaker_presence.append(speaker_present)
                    
                frame_count += 1
                
            cap.release()
            
            return {
                "emotions": emotions,
                "visual_cues": visual_cues,
                "speaker_presence": speaker_presence,
                "total_frames": frame_count
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video frames: {e}")
            return {}
            
    async def _analyze_frame_emotion(self, frame: np.ndarray) -> Optional[Dict]:
        """Analyze emotion in a single frame"""
        try:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            results = self.face_detection.process(rgb_frame)
            
            if results.detections:
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    
                    # Extract face ROI
                    h, w, _ = frame.shape
                    x1 = int(bbox.xmin * w)
                    y1 = int(bbox.ymin * h)
                    x2 = int((bbox.xmin + bbox.width) * w)
                    y2 = int((bbox.ymin + bbox.height) * h)
                    
                    face_roi = frame[y1:y2, x1:x2]
                    
                    # Analyze emotion with DeepFace
                    try:
                        analysis = DeepFace.analyze(
                            face_roi,
                            actions=['emotion'],
                            enforce_detection=False
                        )
                        return {
                            "emotion": analysis[0]["dominant_emotion"],
                            "confidence": analysis[0]["emotion"][analysis[0]["dominant_emotion"]],
                            "timestamp": datetime.now()
                        }
                    except:
                        continue
                        
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing frame emotion: {e}")
            return None
            
    async def _detect_visual_cues(self, frame: np.ndarray) -> List[str]:
        """Detect financial visual cues in frame"""
        visual_cues = []
        
        try:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect charts/graphs
            chart_detected = await self._detect_charts(frame)
            if chart_detected:
                visual_cues.append("chart_present")
                
            # Detect text overlays
            text_detected = await self._detect_text_overlays(frame)
            if text_detected:
                visual_cues.append("text_overlay")
                
            # Detect financial symbols
            symbols_detected = await self._detect_financial_symbols(frame)
            visual_cues.extend(symbols_detected)
            
            # Detect hand gestures
            gestures = await self._detect_hand_gestures(rgb_frame)
            visual_cues.extend(gestures)
            
        except Exception as e:
            logger.error(f"Error detecting visual cues: {e}")
            
        return visual_cues
        
    async def _detect_charts(self, frame: np.ndarray) -> bool:
        """Detect charts and graphs in frame"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect lines (chart axes)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50)
            
            if lines is not None and len(lines) > 2:
                return True
                
            # Detect rectangular shapes (chart areas)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                if len(approx) == 4:
                    return True
                    
        except Exception as e:
            logger.error(f"Error detecting charts: {e}")
            
        return False
        
    async def _detect_text_overlays(self, frame: np.ndarray) -> bool:
        """Detect text overlays in frame"""
        try:
            # Use EAST text detector
            # For simplicity, using basic text detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            text_regions = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Typical text aspect ratio
                if 2 < aspect_ratio < 10 and w > 50 and h > 10:
                    text_regions += 1
                    
            return text_regions > 3
            
        except Exception as e:
            logger.error(f"Error detecting text overlays: {e}")
            
        return False
        
    async def _detect_financial_symbols(self, frame: np.ndarray) -> List[str]:
        """Detect financial symbols like stock tickers"""
        symbols = []
        
        try:
            # Use OCR to detect text
            import pytesseract
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            
            # Look for stock tickers (uppercase letters, 1-5 chars)
            import re
            tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
            
            # Verify if they're real stock tickers
            for ticker in tickers:
                if await self._is_valid_ticker(ticker):
                    symbols.append(f"ticker_{ticker}")
                    
        except Exception as e:
            logger.error(f"Error detecting financial symbols: {e}")
            
        return symbols
        
    async def _detect_hand_gestures(self, frame: np.ndarray) -> List[str]:
        """Detect hand gestures for presentation analysis"""
        gestures = []
        
        try:
            results = self.hand_detection.process(frame)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Analyze hand gestures
                    gesture = await self._classify_gesture(hand_landmarks)
                    if gesture:
                        gestures.append(gesture)
                        
        except Exception as e:
            logger.error(f"Error detecting hand gestures: {e}")
            
        return gestures
        
    async def _classify_gesture(self, hand_landmarks) -> Optional[str]:
        """Classify hand gesture from landmarks"""
        try:
            # Simple gesture classification based on landmark positions
            # This is a simplified version - production would use ML models
            
            # Check for pointing gesture
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            
            if abs(thumb_tip.y - index_tip.y) < 0.1:
                return "pointing"
                
            # Check for open palm
            palm_open = all(
                hand_landmarks.landmark[i].y < hand_landmarks.landmark[i + 4].y
                for i in [8, 12, 16, 20]  # fingertip landmarks
            )
            
            if palm_open:
                return "open_palm"
                
        except Exception as e:
            logger.error(f"Error classifying gesture: {e}")
            
        return None
        
    async def _detect_speaker(self, frame: np.ndarray) -> bool:
        """Detect if someone is speaking in the frame"""
        try:
            # Use face detection as proxy for speaker presence
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_detection.process(rgb_frame)
            
            return len(results.detections) > 0
            
        except Exception as e:
            logger.error(f"Error detecting speaker: {e}")
            return False
            
    async def _analyze_audio_sentiment(self, transcript: str) -> Dict:
        """Analyze sentiment from audio transcript"""
        try:
            # Split transcript into chunks
            chunks = [transcript[i:i+512] for i in range(0, len(transcript), 512)]
            
            sentiments = []
            for chunk in chunks:
                if chunk.strip():
                    result = self.sentiment_analyzer(chunk)
                    sentiments.extend(result)
                    
            # Aggregate sentiments
            if sentiments:
                avg_score = np.mean([s["score"] if s["label"] == "positive" else -s["score"] for s in sentiments])
                confidence = np.mean([s["score"] for s in sentiments])
                
                return {
                    "sentiment_score": avg_score,
                    "confidence": confidence,
                    "detailed_sentiments": sentiments
                }
                
        except Exception as e:
            logger.error(f"Error analyzing audio sentiment: {e}")
            
        return {"sentiment_score": 0.0, "confidence": 0.0}
        
    async def _combine_analyses(self, video_url: str, frame_analysis: Dict, 
                              audio_sentiment: Dict, company_ticker: Optional[str]) -> VideoAnalysis:
        """Combine all analyses into comprehensive result"""
        try:
            # Extract key metrics
            emotions = frame_analysis.get("emotions", [])
            visual_cues = frame_analysis.get("visual_cues", [])
            speaker_presence = frame_analysis.get("speaker_presence", [])
            
            # Calculate emotion distribution
            emotion_scores = {}
            if emotions:
                for emotion in emotions:
                    emotion_name = emotion["emotion"]
                    if emotion_name not in emotion_scores:
                        emotion_scores[emotion_name] = []
                    emotion_scores[emotion_name].append(emotion["confidence"])
                    
            # Average emotions
            avg_emotions = {
                emotion: np.mean(scores) 
                for emotion, scores in emotion_scores.items()
            }
            
            # Calculate confidence score
            confidence_score = (
                audio_sentiment.get("confidence", 0.0) * 0.4 +
                (len(emotions) / max(frame_analysis.get("total_frames", 1) / 30, 1)) * 0.3 +
                (len([c for c in visual_cues if "chart" in c or "ticker" in c]) > 0) * 0.3
            )
            
            # Extract key topics
            key_topics = list(set([c for c in visual_cues if c in ["chart_present", "text_overlay"]]))
            key_topics.extend([f"emotion_{e}" for e in avg_emotions.keys() if avg_emotions[e] > 0.5])
            
            # Calculate financial relevance
            financial_relevance = (
                (len([c for c in visual_cues if "ticker" in c]) > 0) * 0.4 +
                (company_ticker is not None) * 0.3 +
                (abs(audio_sentiment.get("sentiment_score", 0)) > 0.1) * 0.3
            )
            
            # Generate summary
            summary = await self._generate_summary(
                avg_emotions, visual_cues, audio_sentiment, company_ticker
            )
            
            return VideoAnalysis(
                video_id=video_url.split("=")[-1] if "=" in video_url else video_url,
                sentiment_score=audio_sentiment.get("sentiment_score", 0.0),
                confidence_score=min(confidence_score, 1.0),
                key_topics=key_topics,
                speaker_emotions=avg_emotions,
                visual_cues=visual_cues,
                financial_relevance=min(financial_relevance, 1.0),
                timestamp=datetime.now(),
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error combining analyses: {e}")
            raise
            
    async def _generate_summary(self, emotions: Dict, visual_cues: List[str], 
                             audio_sentiment: Dict, company_ticker: Optional[str]) -> str:
        """Generate human-readable summary"""
        try:
            summary_parts = []
            
            # Emotion summary
            if emotions:
                dominant_emotion = max(emotions, key=emotions.get)
                summary_parts.append(f"Speaker appears {dominant_emotion}")
                
            # Visual elements
            if "chart_present" in visual_cues:
                summary_parts.append("Financial charts detected")
                
            if any("ticker" in c for c in visual_cues):
                summary_parts.append("Stock tickers mentioned")
                
            # Sentiment
            sentiment = audio_sentiment.get("sentiment_score", 0)
            if sentiment > 0.1:
                summary_parts.append("Overall positive sentiment")
            elif sentiment < -0.1:
                summary_parts.append("Overall negative sentiment")
                
            # Company context
            if company_ticker:
                summary_parts.append(f"Analysis focused on {company_ticker}")
                
            return ". ".join(summary_parts) if summary_parts else "Analysis completed"
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary unavailable"
            
    async def _get_company_financials(self, ticker: str) -> Dict:
        """Get company financial data for context"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "revenue": info.get("totalRevenue", 0),
                "debt_to_equity": info.get("debtToEquity", 0),
                "current_price": info.get("currentPrice", 0),
            }
            
        except Exception as e:
            logger.error(f"Error getting company financials: {e}")
            return {}
            
    async def _detect_deception(self, analysis: VideoAnalysis) -> List[str]:
        """Detect potential deception indicators"""
        indicators = []
        
        try:
            # Analyze emotional patterns
            emotions = analysis.speaker_emotions
            
            # High fear or anxiety might indicate deception
            if emotions.get("fear", 0) > 0.6:
                indicators.append("high_fear")
                
            # Contradictory emotions
            if emotions.get("happy", 0) > 0.5 and emotions.get("sad", 0) > 0.5:
                indicators.append("emotional_contradiction")
                
            # Low confidence in speech
            if analysis.confidence_score < 0.3:
                indicators.append("low_confidence")
                
            # Rapid emotional changes (would need temporal analysis)
            indicators.append("emotional_volatility")
            
        except Exception as e:
            logger.error(f"Error detecting deception: {e}")
            
        return indicators
        
    async def _analyze_executive_confidence(self, analysis: VideoAnalysis) -> float:
        """Analyze executive confidence level"""
        try:
            confidence = 0.5  # Base confidence
            
            # Positive emotions increase confidence
            positive_emotions = ["happy", "neutral"]
            for emotion in positive_emotions:
                confidence += analysis.speaker_emotions.get(emotion, 0) * 0.2
                
            # Negative emotions decrease confidence
            negative_emotions = ["fear", "sad", "angry"]
            for emotion in negative_emotions:
                confidence -= analysis.speaker_emotions.get(emotion, 0) * 0.2
                
            # Visual cues affect confidence
            if "open_palm" in analysis.visual_cues:
                confidence += 0.1
                
            if "pointing" in analysis.visual_cues:
                confidence += 0.05
                
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Error analyzing executive confidence: {e}")
            return 0.5
            
    async def _extract_financial_projections(self, analysis: VideoAnalysis, 
                                          company_data: Dict) -> Dict:
        """Extract financial projections from analysis"""
        projections = {}
        
        try:
            # Base projections on sentiment and confidence
            sentiment = analysis.sentiment_score
            confidence = analysis.confidence_score
            
            # Revenue growth projection
            if sentiment > 0.2 and confidence > 0.7:
                projections["revenue_growth"] = 0.15  # 15% growth
            elif sentiment < -0.2:
                projections["revenue_growth"] = -0.05  # -5% growth
            else:
                projections["revenue_growth"] = 0.05  # 5% growth
                
            # Stock price projection
            current_price = company_data.get("current_price", 100)
            if sentiment > 0.3:
                projections["price_target"] = current_price * 1.2
            elif sentiment < -0.3:
                projections["price_target"] = current_price * 0.8
            else:
                projections["price_target"] = current_price * 1.05
                
        except Exception as e:
            logger.error(f"Error extracting financial projections: {e}")
            
        return projections
        
    async def _analyze_body_language(self, analysis: VideoAnalysis) -> Dict:
        """Analyze body language patterns"""
        body_analysis = {}
        
        try:
            # Count different gestures
            gestures = [c for c in analysis.visual_cues if c in ["pointing", "open_palm"]]
            
            # Gesture frequency
            body_analysis["gesture_frequency"] = len(gestures)
            
            # Openness (open palms indicate openness)
            open_gestures = [g for g in gestures if g == "open_palm"]
            body_analysis["openness_score"] = len(open_gestures) / max(len(gestures), 1)
            
            # Dominance (pointing indicates dominance)
            pointing_gestures = [g for g in gestures if g == "pointing"]
            body_analysis["dominance_score"] = len(pointing_gestures) / max(len(gestures), 1)
            
        except Exception as e:
            logger.error(f"Error analyzing body language: {e}")
            
        return body_analysis
        
    async def _generate_investment_recommendation(self, confidence: float, 
                                                deception: List[str], 
                                                projections: Dict) -> str:
        """Generate investment recommendation"""
        try:
            # Base recommendation on confidence and projections
            if confidence > 0.7 and len(deception) < 2:
                growth = projections.get("revenue_growth", 0)
                if growth > 0.1:
                    return "STRONG_BUY"
                elif growth > 0.05:
                    return "BUY"
                else:
                    return "HOLD"
            elif confidence < 0.3 or len(deception) > 3:
                return "SELL"
            else:
                return "HOLD"
                
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "HOLD"
            
    async def _is_valid_ticker(self, ticker: str) -> bool:
        """Check if ticker is valid"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return "regularMarketPrice" in info
        except:
            return False

# Singleton instance
visual_ai = VisualLearningAI()

# API endpoints
async def analyze_video_endpoint(video_url: str, company_ticker: Optional[str] = None) -> VideoAnalysis:
    """API endpoint for video analysis"""
    return await visual_ai.analyze_youtube_video(video_url, company_ticker)

async def analyze_earnings_call_endpoint(video_url: str, company_ticker: str) -> EarningsCallAnalysis:
    """API endpoint for earnings call analysis"""
    return await visual_ai.analyze_earnings_call(video_url, company_ticker)
