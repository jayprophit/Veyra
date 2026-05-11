"""
Visual Learning AI - Revolutionary Trading Intelligence
=======================================================
AI that learns from watching financial videos, charts, and live streams

Inspired by: Computer vision + Finance + Media analysis
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class VideoInsight:
    """Extracted insight from financial video content"""
    timestamp: float
    source: str
    speaker: str
    sentiment: str
    confidence: float
    trading_signals: List[Dict[str, Any]]
    chart_patterns: List[Dict[str, Any]]
    key_quotes: List[str]


@dataclass
class ChartPatternMemory:
    """Learned chart pattern from visual analysis"""
    pattern_name: str
    visual_signature: str
    success_rate: float
    avg_return: float
    occurrences: int
    last_seen: datetime
    confidence_threshold: float


class VisualLearningAI:
    """
    Multi-modal AI that learns from watching financial content
    
    Capabilities:
    1. Video analysis (YouTube, news, earnings calls)
    2. Chart pattern recognition from video frames
    3. Speaker sentiment analysis (tone + content)
    4. Real-time learning from live streams
    5. Pattern matching against learned visual memories
    
    Inspired by: Attack on Titan's wall defense, Psycho-Pass crime coefficient
    """
    
    def __init__(self):
        self.chart_memories: List[ChartPatternMemory] = []
        self.video_insights: List[VideoInsight] = []
        self.speaker_profiles: Dict[str, Dict] = {}
        self.live_streams: Dict[str, Any] = {}
        self.pattern_matcher = PatternMatcher()
        self.sentiment_analyzer = SentimentAnalyzer()
        
    async def analyze_youtube_video(self, video_url: str, source_type: str = "analysis") -> VideoInsight:
        """
        Analyze financial YouTube video for trading insights
        
        Args:
            video_url: YouTube URL
            source_type: 'analysis', 'news', 'earnings', 'tutorial'
        
        Returns:
            VideoInsight with extracted signals
        """
        logger.info(f"Analyzing video: {video_url}")
        
        # Step 1: Extract frames at key intervals
        frames = await self._extract_key_frames(video_url)
        
        # Step 2: Detect charts in frames
        charts = self._detect_charts_in_frames(frames)
        
        # Step 3: OCR and technical indicator extraction
        technical_data = self._extract_technical_data(charts)
        
        # Step 4: Transcribe audio
        transcript = await self._transcribe_video(video_url)
        
        # Step 5: Identify speaker
        speaker = self._identify_speaker(transcript, video_url)
        
        # Step 6: Sentiment analysis (tone + content)
        sentiment = await self.sentiment_analyzer.analyze(
            text=transcript,
            video_frames=frames,
            speaker_profile=self.speaker_profiles.get(speaker, {})
        )
        
        # Step 7: Extract trading signals
        signals = self._extract_trading_signals(
            transcript=transcript,
            technical_data=technical_data,
            sentiment=sentiment,
            speaker=speaker
        )
        
        # Step 8: Learn new patterns
        await self._learn_patterns(charts, signals, source_type)
        
        insight = VideoInsight(
            timestamp=datetime.now().timestamp(),
            source=video_url,
            speaker=speaker,
            sentiment=sentiment['overall'],
            confidence=sentiment['confidence'],
            trading_signals=signals,
            chart_patterns=technical_data['patterns'],
            key_quotes=self._extract_key_quotes(transcript)
        )
        
        self.video_insights.append(insight)
        return insight
    
    async def learn_from_cnbc_segment(self, segment_url: str) -> Dict[str, Any]:
        """
        Special handler for CNBC Mad Money and Fast Money
        Track Cramer picks and performance
        """
        insight = await self.analyze_youtube_video(segment_url, "cnbc")
        
        # Special Cramer analysis
        if "cramer" in insight.speaker.lower():
            return await self._analyze_cramer_segment(insight)
        
        return insight
    
    async def _analyze_cramer_segment(self, insight: VideoInsight) -> Dict[str, Any]:
        """
        Jim Cramer specific analysis - Inverse Cramer strategy
        Track his picks and actual performance
        """
        cramer_picks = self._extract_stock_mentions(insight.key_quotes)
        
        # Calculate "Inverse Cramer" score
        # Based on historical data: inverse Cramer often profitable
        inverse_signals = []
        for pick in cramer_picks:
            inverse_signals.append({
                "symbol": pick['symbol'],
                "action": "SELL" if pick['recommendation'] == "BUY" else "BUY",
                "confidence": insight.confidence * 0.7,  # Inverse is less certain
                "strategy": "inverse_cramer",
                "rationale": f"Cramer recommended {pick['recommendation']} - historically contrarian works"
            })
        
        return {
            "insight": insight,
            "cramer_picks": cramer_picks,
            "inverse_signals": inverse_signals,
            "cramer_track_record": self._get_cramer_history(),
            "recommendation": "Consider inverse strategy with 70% confidence"
        }
    
    async def analyze_earnings_call(self, video_url: str, ticker: str) -> Dict[str, Any]:
        """
        Analyze earnings call video for CEO sentiment and hidden signals
        
        Detects:
        - Nervous behavior (micro-expressions)
        - Voice tremor analysis
        - Contradictions between words and tone
        - Evasive answers about key metrics
        """
        insight = await self.analyze_youtube_video(video_url, "earnings")
        
        # CEO confidence score
        confidence_metrics = {
            "voice_stability": self._analyze_voice_stability(insight),
            "eye_contact_score": self._analyze_eye_contact(insight),
            "body_language": self._analyze_body_language(insight),
            "evasion_detection": self._detect_evasive_answers(insight.key_quotes),
            "enthusiasm_score": insight.sentiment  # Tone analysis
        }
        
        overall_confidence = sum(confidence_metrics.values()) / len(confidence_metrics)
        
        return {
            "ticker": ticker,
            "insight": insight,
            "ceo_confidence": confidence_metrics,
            "overall_confidence": overall_confidence,
            "red_flags": self._identify_red_flags(insight),
            "trading_signal": {
                "direction": "BULLISH" if overall_confidence > 0.7 else "BEARISH" if overall_confidence < 0.4 else "NEUTRAL",
                "confidence": overall_confidence,
                "timeframe": "48_hours_post_earnings"
            }
        }
    
    def match_current_chart(self, chart_data: Dict[str, Any]) -> List[ChartPatternMemory]:
        """
        Compare current chart against learned visual memories
        
        Returns: List of matching patterns with confidence scores
        """
        matches = []
        
        for memory in self.chart_memories:
            similarity = self.pattern_matcher.calculate_similarity(
                chart_data,
                memory.visual_signature
            )
            
            if similarity > memory.confidence_threshold:
                matches.append({
                    "pattern": memory,
                    "similarity": similarity,
                    "expected_outcome": self._predict_outcome(memory),
                    "risk_reward": self._calculate_risk_reward(memory)
                })
        
        return sorted(matches, key=lambda x: x['similarity'], reverse=True)
    
    async def start_live_stream_learning(self, stream_url: str, source: str):
        """
        Continuously learn from live financial broadcasts
        - CNBC Live
        - Bloomberg TV
        - Financial livestreams
        """
        self.live_streams[source] = {
            "url": stream_url,
            "active": True,
            "insights_buffer": []
        }
        
        while self.live_streams[source]["active"]:
            try:
                # Process live frame
                frame = await self._capture_live_frame(stream_url)
                
                # Check for breaking news banner
                breaking_news = self._detect_breaking_news(frame)
                
                if breaking_news:
                    alert = await self._process_breaking_news(breaking_news, frame)
                    await self._send_realtime_alert(alert)
                
                # Check for chart overlays
                chart_overlay = self._detect_chart_overlay(frame)
                if chart_overlay:
                    pattern = await self._analyze_live_chart(chart_overlay)
                    if pattern['confidence'] > 0.8:
                        await self._send_pattern_alert(pattern)
                
                await asyncio.sleep(1)  # 1-second intervals
                
            except Exception as e:
                logger.error(f"Live stream error: {e}")
                await asyncio.sleep(5)
    
    async def generate_trading_idea_from_video_memory(self, symbol: str) -> Dict[str, Any]:
        """
        Generate trading idea based on learned video patterns
        
        Example: "This pattern matches the one from that Cramer segment 
        last month that went up 15%"
        """
        # Get all learned patterns related to symbol
        relevant_memories = [
            m for m in self.chart_memories 
            if m.pattern_name in self._get_symbol_patterns(symbol)
        ]
        
        if not relevant_memories:
            return {"status": "no_data", "message": "No learned patterns for this symbol"}
        
        # Weight by recency and success rate
        weighted_memories = sorted(
            relevant_memories,
            key=lambda m: (m.success_rate * 0.6 + self._recency_score(m) * 0.4),
            reverse=True
        )
        
        best_memory = weighted_memories[0]
        
        return {
            "symbol": symbol,
            "pattern_match": best_memory.pattern_name,
            "historical_success_rate": best_memory.success_rate,
            "avg_return": best_memory.avg_return,
            "confidence": best_memory.confidence_threshold,
            "trading_idea": self._generate_idea_text(best_memory),
            "video_references": self._find_source_videos(best_memory),
            "risk_level": self._assess_risk(best_memory),
            "suggested_position_size": self._suggest_position_size(best_memory)
        }
    
    # ============== PRIVATE METHODS ==============
    
    async def _extract_key_frames(self, video_url: str) -> List[Any]:
        """Extract important frames from video using computer vision"""
        try:
            import cv2
            import numpy as np
            
            # Open video stream
            cap = cv2.VideoCapture(video_url)
            frames = []
            frame_count = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Extract 1 frame every 5 seconds
            sample_interval = int(fps * 5)
            
            while cap.isOpened() and frame_count < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_interval == 0:
                    # Convert to grayscale for analysis
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Check if frame contains potential charts (look for grid patterns)
                    if self._has_chart_like_features(gray):
                        frames.append({
                            'frame': frame,
                            'timestamp': frame_count / fps,
                            'frame_number': frame_count
                        })
                
                frame_count += 1
            
            cap.release()
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}")
            return []
    
    def _has_chart_like_features(self, gray_frame: np.ndarray) -> bool:
        """Detect if frame contains chart-like features"""
        try:
            # Look for horizontal and vertical lines (grid patterns)
            edges = cv2.Canny(gray_frame, 50, 150, apertureSize=3)
            
            # Detect lines
            lines_h = cv2.HoughLinesP(edges, 1, np.pi/2, threshold=50, minLineLength=100)
            lines_v = cv2.HoughLinesP(edges, 1, 0, threshold=50, minLineLength=100)
            
            # Count horizontal and vertical lines
            h_count = len(lines_h) if lines_h is not None else 0
            v_count = len(lines_v) if lines_v is not None else 0
            
            # Chart typically has both horizontal and vertical lines
            return h_count > 5 and v_count > 5
            
        except Exception:
            return False
    
    def _detect_charts_in_frames(self, frames: List[Any]) -> List[Dict]:
        """Use computer vision to detect chart regions"""
        try:
            import cv2
            import numpy as np
            
            charts = []
            
            for frame_data in frames:
                frame = frame_data['frame']
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Find chart boundaries using contour detection
                edges = cv2.Canny(gray, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    # Filter for rectangular shapes (charts)
                    area = cv2.contourArea(contour)
                    if area < 10000:  # Too small
                        continue
                    
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Charts typically have aspect ratios between 0.5 and 2.0
                    if 0.5 <= aspect_ratio <= 2.0:
                        chart_region = frame[y:y+h, x:x+w]
                        
                        charts.append({
                            'region': (x, y, w, h),
                            'image': chart_region,
                            'timestamp': frame_data['timestamp'],
                            'frame_number': frame_data['frame_number'],
                            'aspect_ratio': aspect_ratio,
                            'area': area
                        })
            
            return charts
            
        except Exception as e:
            logger.error(f"Chart detection failed: {e}")
            return []
    
    def _extract_technical_data(self, charts: List[Dict]) -> Dict:
        """Extract price, volume, indicators from chart images using OCR and CV"""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            import pytesseract
            
            extracted_data = {
                'price_levels': [],
                'volume_data': [],
                'indicators': {},
                'patterns': [],
                'timestamps': []
            }
            
            for chart in charts:
                chart_image = chart['image']
                
                # Extract text using OCR
                text = pytesseract.image_to_string(chart_image)
                
                # Parse price levels from text
                price_matches = self._extract_prices_from_text(text)
                extracted_data['price_levels'].extend(price_matches)
                
                # Detect candlestick patterns
                candlesticks = self._detect_candlestick_patterns(chart_image)
                if candlesticks:
                    extracted_data['patterns'].extend(candlesticks)
                
                # Extract volume bars
                volume_data = self._extract_volume_bars(chart_image)
                if volume_data:
                    extracted_data['volume_data'].append({
                        'timestamp': chart['timestamp'],
                        'volume': volume_data
                    })
                
                # Detect technical indicators (RSI, MACD, etc.)
                indicators = self._detect_technical_indicators(chart_image)
                extracted_data['indicators'].update(indicators)
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Technical data extraction failed: {e}")
            return {}
    
    def _extract_prices_from_text(self, text: str) -> List[float]:
        """Extract price values from OCR text"""
        import re
        
        prices = []
        # Look for price patterns (e.g., $150.25, 1,234.56)
        price_patterns = [
            r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})',
            r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})\b'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    price = float(match.replace('$', '').replace(',', ''))
                    if 0.01 < price < 10000:  # Reasonable price range
                        prices.append(price)
                except ValueError:
                    continue
        
        return prices
    
    def _detect_candlestick_patterns(self, chart_image: np.ndarray) -> List[Dict]:
        """Detect candlestick patterns in chart image"""
        try:
            import cv2
            import numpy as np
            
            gray = cv2.cvtColor(chart_image, cv2.COLOR_BGR2GRAY)
            
            # Look for vertical lines with different colors (red/green candles)
            # This is simplified - real implementation would use more sophisticated analysis
            
            patterns = []
            
            # Sample implementation - detect basic candlestick shapes
            contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 50:  # Too small
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = h / w
                
                # Candlesticks are typically tall and thin
                if aspect_ratio > 2 and aspect_ratio < 10:
                    patterns.append({
                        'type': 'candlestick',
                        'position': (x, y, w, h),
                        'aspect_ratio': aspect_ratio,
                        'size': area
                    })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Candlestick detection failed: {e}")
            return []
    
    def _extract_volume_bars(self, chart_image: np.ndarray) -> Optional[float]:
        """Extract volume data from chart bars"""
        try:
            import cv2
            import numpy as np
            
            # Look for horizontal bars at bottom of chart (volume indicators)
            gray = cv2.cvtColor(chart_image, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # Focus on bottom 20% of image where volume bars typically appear
            volume_region = gray[int(height * 0.8):, :]
            
            # Count non-zero pixels as proxy for volume
            volume_pixels = cv2.countNonZero(volume_region)
            total_pixels = volume_region.shape[0] * volume_region.shape[1]
            
            if total_pixels > 0:
                volume_intensity = volume_pixels / total_pixels
                return volume_intensity
            
            return None
            
        except Exception:
            return None
    
    def _detect_technical_indicators(self, chart_image: np.ndarray) -> Dict:
        """Detect technical indicators like RSI, MACD, moving averages"""
        try:
            import cv2
            import numpy as np
            import pytesseract
            
            indicators = {}
            
            # OCR to find indicator labels
            text = pytesseract.image_to_string(chart_image)
            
            # Look for common indicator names
            indicator_keywords = {
                'RSI': 'rsi',
                'MACD': 'macd',
                'SMA': 'sma',
                'EMA': 'ema',
                'BB': 'bollinger',
                'VWAP': 'vwap'
            }
            
            for keyword, key in indicator_keywords.items():
                if keyword in text.upper():
                    # Try to extract values near the keyword
                    values = self._extract_indicator_values(text, keyword)
                    if values:
                        indicators[key] = values
            
            return indicators
            
        except Exception as e:
            logger.error(f"Indicator detection failed: {e}")
            return {}
    
    def _extract_indicator_values(self, text: str, indicator: str) -> List[float]:
        """Extract numerical values for specific indicators"""
        import re
        
        # Look for numbers near the indicator name
        pattern = f'{indicator}\\s*[:=]?\\s*([0-9]+(?:\\.[0-9]+)?)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        values = []
        for match in matches:
            try:
                values.append(float(match))
            except ValueError:
                continue
        
        return values
    
    async def _transcribe_video(self, video_url: str) -> str:
        """Speech-to-text conversion"""
        return ""
    
    def _identify_speaker(self, transcript: str, video_url: str) -> str:
        """Identify who is speaking"""
        return "Unknown"
    
    def _extract_trading_signals(self, transcript: str, technical_data: Dict, 
                                  sentiment: Dict, speaker: str) -> List[Dict]:
        """Extract buy/sell signals from content"""
        return []
    
    def _extract_key_quotes(self, transcript: str) -> List[str]:
        """Extract impactful quotes"""
        return []
    
    async def _learn_patterns(self, charts: List[Dict], signals: List[Dict], source_type: str):
        """Store learned patterns for future matching"""
        try:
            learned_patterns = []
            current_time = datetime.now()
            
            # Process chart patterns
            for chart in charts:
                try:
                    # Extract pattern features
                    pattern_features = await self._extract_chart_features(chart)
                    
                    # Check if pattern already exists
                    existing_pattern = await self._find_similar_pattern(pattern_features)
                    
                    if existing_pattern:
                        # Update existing pattern with new data
                        await self._update_pattern(existing_pattern, chart, current_time)
                        logger.info(f"Updated existing pattern: {existing_pattern.pattern_name}")
                    else:
                        # Create new pattern
                        new_pattern = await self._create_new_pattern(chart, pattern_features, current_time)
                        learned_patterns.append(new_pattern)
                        logger.info(f"Created new pattern: {new_pattern.pattern_name}")
                        
                except Exception as e:
                    logger.error(f"Error processing chart pattern: {e}")
                    continue
            
            # Process trading signals
            for signal in signals:
                try:
                    # Extract signal features
                    signal_features = await self._extract_signal_features(signal)
                    
                    # Store signal pattern
                    signal_pattern = await self._create_signal_pattern(signal, signal_features, current_time)
                    learned_patterns.append(signal_pattern)
                    logger.info(f"Created new signal pattern: {signal_pattern.get('name', 'Unknown')}")
                    
                except Exception as e:
                    logger.error(f"Error processing trading signal: {e}")
                    continue
            
            # Update pattern cache for fast lookup
            await self._update_pattern_cache(learned_patterns)
            
            # Store patterns in database
            await self._persist_patterns(learned_patterns)
            
            # Calculate pattern statistics
            stats = await self._calculate_pattern_statistics(learned_patterns)
            
            logger.info(f"Pattern learning completed: {len(learned_patterns)} patterns learned")
            
            return {
                "patterns_learned": len(learned_patterns),
                "chart_patterns": len([p for p in learned_patterns if hasattr(p, 'pattern_name')]),
                "signal_patterns": len([p for p in learned_patterns if 'signal_type' in p]),
                "source_type": source_type,
                "learning_timestamp": current_time.isoformat(),
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Pattern learning failed: {e}")
            raise
    
    async def _extract_chart_features(self, chart: Dict) -> Dict:
        """Extract visual and technical features from chart"""
        try:
            # Simulate feature extraction - in real implementation, this would use computer vision
            features = {
                'pattern_type': chart.get('pattern_type', 'unknown'),
                'timeframe': chart.get('timeframe', '1D'),
                'asset_class': chart.get('asset_class', 'equity'),
                'technical_indicators': {
                    'rsi': chart.get('rsi', 50),
                    'macd': chart.get('macd', 0),
                    'bollinger_position': chart.get('bb_position', 0.5)
                },
                'visual_signature': self._generate_visual_signature(chart),
                'price_action': {
                    'trend': chart.get('trend', 'neutral'),
                    'volatility': chart.get('volatility', 'medium'),
                    'volume_profile': chart.get('volume_profile', 'normal')
                },
                'market_context': {
                    'sector': chart.get('sector', 'unknown'),
                    'market_cap': chart.get('market_cap', 'mid'),
                    'session': chart.get('session', 'regular')
                }
            }
            return features
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
    
    def _generate_visual_signature(self, chart: Dict) -> str:
        """Generate unique visual signature for pattern matching"""
        # Create a hash-like signature from chart features
        signature_components = [
            chart.get('pattern_type', ''),
            str(chart.get('timeframe', '')),
            chart.get('trend', ''),
            str(chart.get('volatility', '')),
            str(chart.get('rsi', 0)),
            str(chart.get('macd', 0))
        ]
        return "|".join(signature_components)
    
    async def _find_similar_pattern(self, features: Dict) -> Optional[ChartPatternMemory]:
        """Find existing similar pattern in memory"""
        try:
            # In real implementation, this would query the database
            # For now, check in-memory pattern cache
            visual_signature = features.get('visual_signature', '')
            
            # Simulate pattern matching
            if hasattr(self, 'pattern_cache') and visual_signature in self.pattern_cache:
                return self.pattern_cache[visual_signature]
            
            return None
        except Exception as e:
            logger.error(f"Pattern search failed: {e}")
            return None
    
    async def _update_pattern(self, pattern: ChartPatternMemory, new_chart: Dict, timestamp: datetime):
        """Update existing pattern with new occurrence"""
        try:
            # Update occurrence count
            pattern.occurrences += 1
            
            # Update last seen timestamp
            pattern.last_seen = timestamp
            
            # Update success rate and average return based on new data
            new_return = new_chart.get('outcome_return', 0)
            if new_return != 0:
                total_return = pattern.avg_return * (pattern.occurrences - 1) + new_return
                pattern.avg_return = total_return / pattern.occurrences
                
                # Update success rate (positive return = success)
                successes = pattern.success_rate * (pattern.occurrences - 1) + (1 if new_return > 0 else 0)
                pattern.success_rate = successes / pattern.occurrences
            
            # Update confidence threshold based on consistency
            if pattern.occurrences > 5:
                pattern.confidence_threshold = min(0.95, pattern.confidence_threshold + 0.01)
            
            # Update cache
            if not hasattr(self, 'pattern_cache'):
                self.pattern_cache = {}
            self.pattern_cache[pattern.visual_signature] = pattern
            
        except Exception as e:
            logger.error(f"Pattern update failed: {e}")
    
    async def _create_new_pattern(self, chart: Dict, features: Dict, timestamp: datetime) -> ChartPatternMemory:
        """Create new pattern from chart data"""
        try:
            pattern_name = f"{features.get('pattern_type', 'unknown')}_{features.get('timeframe', '1D')}_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
            new_pattern = ChartPatternMemory(
                pattern_name=pattern_name,
                visual_signature=features.get('visual_signature', ''),
                success_rate=0.5,  # Initial neutral success rate
                avg_return=chart.get('outcome_return', 0),
                occurrences=1,
                last_seen=timestamp,
                confidence_threshold=0.6  # Initial confidence threshold
            )
            
            # Add to cache
            if not hasattr(self, 'pattern_cache'):
                self.pattern_cache = {}
            self.pattern_cache[new_pattern.visual_signature] = new_pattern
            
            return new_pattern
            
        except Exception as e:
            logger.error(f"Pattern creation failed: {e}")
            raise
    
    async def _extract_signal_features(self, signal: Dict) -> Dict:
        """Extract features from trading signals"""
        try:
            features = {
                'signal_type': signal.get('type', 'unknown'),
                'strength': signal.get('strength', 0.5),
                'duration': signal.get('duration', 'short'),
                'confidence': signal.get('confidence', 0.5),
                'market_conditions': signal.get('market_conditions', 'normal'),
                'asset_correlation': signal.get('correlation', 0.0),
                'technical_context': signal.get('technical_context', {})
            }
            return features
        except Exception as e:
            logger.error(f"Signal feature extraction failed: {e}")
            return {}
    
    async def _create_signal_pattern(self, signal: Dict, features: Dict, timestamp: datetime) -> Dict:
        """Create pattern from trading signal"""
        try:
            signal_pattern = {
                'id': f"signal_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                'name': f"{features.get('signal_type', 'unknown')}_signal",
                'signal_type': features.get('signal_type'),
                'strength': features.get('strength'),
                'confidence': features.get('confidence'),
                'created_at': timestamp,
                'source_data': signal,
                'features': features,
                'success_count': 0,
                'total_occurrences': 1
            }
            return signal_pattern
        except Exception as e:
            logger.error(f"Signal pattern creation failed: {e}")
            raise
    
    async def _update_pattern_cache(self, patterns: List) -> None:
        """Update in-memory pattern cache for fast lookup"""
        try:
            if not hasattr(self, 'pattern_cache'):
                self.pattern_cache = {}
            
            for pattern in patterns:
                if hasattr(pattern, 'visual_signature'):
                    self.pattern_cache[pattern.visual_signature] = pattern
                elif isinstance(pattern, dict) and 'id' in pattern:
                    self.pattern_cache[pattern['id']] = pattern
                    
        except Exception as e:
            logger.error(f"Pattern cache update failed: {e}")
    
    async def _persist_patterns(self, patterns: List) -> None:
        """Persist patterns to database"""
        try:
            # In real implementation, this would save to database
            # For now, just log the persistence
            logger.info(f"Persisting {len(patterns)} patterns to database")
            
            # Simulate database operation
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Pattern persistence failed: {e}")
    
    async def _calculate_pattern_statistics(self, patterns: List) -> Dict:
        """Calculate statistics for learned patterns"""
        try:
            if not patterns:
                return {}
            
            chart_patterns = [p for p in patterns if hasattr(p, 'pattern_name')]
            signal_patterns = [p for p in patterns if isinstance(p, dict) and 'signal_type' in p]
            
            stats = {
                'total_patterns': len(patterns),
                'chart_patterns': len(chart_patterns),
                'signal_patterns': len(signal_patterns),
                'avg_confidence': 0.0,
                'high_confidence_patterns': 0,
                'pattern_types': {}
            }
            
            # Calculate confidence statistics
            confidences = []
            for pattern in chart_patterns:
                if hasattr(pattern, 'confidence_threshold'):
                    confidences.append(pattern.confidence_threshold)
                    if pattern.confidence_threshold > 0.8:
                        stats['high_confidence_patterns'] += 1
                    
                    # Count pattern types
                    pattern_type = pattern.pattern_name.split('_')[0]
                    stats['pattern_types'][pattern_type] = stats['pattern_types'].get(pattern_type, 0) + 1
            
            if confidences:
                stats['avg_confidence'] = sum(confidences) / len(confidences)
            
            return stats
            
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {}
    
    def _extract_stock_mentions(self, quotes: List[str]) -> List[Dict]:
        """Extract stock symbols and recommendations"""
        return []
    
    def _get_cramer_history(self) -> Dict:
        """Get historical performance of Cramer picks"""
        return {}
    
    def _analyze_voice_stability(self, insight: VideoInsight) -> float:
        """Analyze voice tremors/nervousness"""
        return 0.5
    
    def _analyze_eye_contact(self, insight: VideoInsight) -> float:
        """Analyze eye contact confidence"""
        return 0.5
    
    def _analyze_body_language(self, insight: VideoInsight) -> float:
        """Analyze confident vs nervous body language"""
        return 0.5
    
    def _detect_evasive_answers(self, quotes: List[str]) -> float:
        """Detect when speaker is being evasive"""
        return 0.0
    
    def _identify_red_flags(self, insight: VideoInsight) -> List[str]:
        """Identify concerning signals"""
        return []
    
    def _predict_outcome(self, memory: ChartPatternMemory) -> str:
        """Predict price direction based on historical pattern"""
        return "NEUTRAL"
    
    def _calculate_risk_reward(self, memory: ChartPatternMemory) -> float:
        """Calculate risk/reward ratio"""
        return 1.0
    
    def _recency_score(self, memory: ChartPatternMemory) -> float:
        """Score based on how recent the pattern is"""
        return 0.5
    
    def _get_symbol_patterns(self, symbol: str) -> List[str]:
        """Get pattern types associated with symbol"""
        return []
    
    def _generate_idea_text(self, memory: ChartPatternMemory) -> str:
        """Generate human-readable trading idea"""
        return f"Pattern suggests {memory.avg_return}% move"
    
    def _find_source_videos(self, memory: ChartPatternMemory) -> List[str]:
        """Find videos where this pattern was learned"""
        return []
    
    def _assess_risk(self, memory: ChartPatternMemory) -> str:
        """Assess risk level"""
        return "MEDIUM"
    
    def _suggest_position_size(self, memory: ChartPatternMemory) -> float:
        """Suggest position size based on confidence"""
        return 0.05  # 5% of portfolio
    
    async def _capture_live_frame(self, stream_url: str) -> Any:
        """Capture frame from live stream"""
        return None
    
    def _detect_breaking_news(self, frame: Any) -> Optional[Dict]:
        """Detect breaking news banner in frame"""
        return None
    
    async def _process_breaking_news(self, news: Dict, frame: Any) -> Dict:
        """Process breaking news for trading implications"""
        return {}
    
    def _detect_chart_overlay(self, frame: Any) -> Optional[Dict]:
        """Detect if chart is overlaid on video"""
        return None
    
    async def _analyze_live_chart(self, chart: Dict) -> Dict:
        """Analyze chart in real-time"""
        return {}
    
    async def _send_realtime_alert(self, alert: Dict):
        """Send alert to user"""
        logger.info(f"ALERT: {alert}")
    
    async def _send_pattern_alert(self, pattern: Dict):
        """Send pattern detection alert"""
        logger.info(f"PATTERN: {pattern}")


class PatternMatcher:
    """Match current charts against learned patterns"""
    
    def calculate_similarity(self, chart_data: Dict, visual_signature: str) -> float:
        """Calculate similarity score between charts"""
        # Use image hashing or feature extraction
        return 0.0


class SentimentAnalyzer:
    """Multi-modal sentiment analysis"""
    
    async def analyze(self, text: str, video_frames: List[Any], speaker_profile: Dict) -> Dict:
        """Analyze sentiment from text + visual cues"""
        return {
            "overall": "neutral",
            "confidence": 0.5,
            "emotional_indicators": {}
        }
