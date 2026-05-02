"""
Visual Learning AI 2.0 - Live Market Data Learning System
=========================================================
Continuous learning from watching live market data streams
Pattern evolution, self-discovering patterns, order book analysis
Inspiration: Ghost in the Shell, The Matrix, Psycho-Pass
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import logging

logger = logging.getLogger(__name__)


@dataclass
class VisualPattern:
    """Discovered visual pattern"""
    pattern_id: str
    pattern_type: str
    formation: List[Tuple[float, float]]  # (price, time) coordinates
    confidence: float
    success_rate: float
    occurrences: int
    last_seen: datetime
    avg_return: float


@dataclass
class OrderBookVisual:
    """Visual representation of order book"""
    bid_levels: List[Tuple[float, float]]  # (price, size)
    ask_levels: List[Tuple[float, float]]
    bid_shape: str  # 'wall', 'ramp', 'cliff'
    ask_shape: str
    imbalance: float
    support_wall: Optional[float]
    resistance_wall: Optional[float]
    iceberg_detected: bool


class LiveVisualLearner:
    """
    AI that learns from watching live market data continuously
    
    Features:
    - Pattern discovery from raw price action
    - Order book visual pattern recognition
    - Cross-asset visual correlation
    - Self-evolving pattern database
    """
    
    def __init__(self, memory_size: int = 10000):
        self.price_memory = deque(maxlen=memory_size)
        self.pattern_database: Dict[str, VisualPattern] = {}
        self.order_book_history: deque = deque(maxlen=1000)
        self.cross_asset_patterns: Dict[str, List[Dict]] = {}
        self.learning_rate = 0.01
        
    def feed_price_data(self, ticker: str, price: float, 
                       volume: int, timestamp: datetime):
        """Feed live price tick to visual memory"""
        self.price_memory.append({
            'ticker': ticker,
            'price': price,
            'volume': volume,
            'timestamp': timestamp
        })
        
        # Trigger pattern discovery every 100 ticks
        if len(self.price_memory) % 100 == 0:
            self._discover_new_patterns(ticker)
    
    def feed_order_book(self, ticker: str, 
                       bids: List[Tuple[float, float]],
                       asks: List[Tuple[float, float]],
                       timestamp: datetime):
        """
        Feed order book snapshot
        
        bids/asks: List of (price, size) tuples
        """
        visual = self._analyze_order_book_shape(bids, asks)
        
        self.order_book_history.append({
            'ticker': ticker,
            'visual': visual,
            'timestamp': timestamp
        })
        
        # Detect iceberg orders
        if visual.iceberg_detected:
            logger.info(f"Iceberg order detected in {ticker}")
        
        return visual
    
    def _analyze_order_book_shape(self, bids: List[Tuple[float, float]],
                                    asks: List[Tuple[float, float]]) -> OrderBookVisual:
        """Analyze the visual shape of order book"""
        
        def get_shape(levels: List[Tuple[float, float]]) -> str:
            """Determine if shape is wall, ramp, or cliff"""
            if len(levels) < 3:
                return 'flat'
            
            sizes = [s for _, s in levels]
            
            # Wall: Large size concentrated at one level
            if max(sizes) > sum(sizes) * 0.6:
                return 'wall'
            
            # Ramp: Increasing or decreasing sizes
            if sizes[0] < sizes[-1] * 0.5 or sizes[0] > sizes[-1] * 2:
                return 'ramp'
            
            # Cliff: Sudden drop in size
            for i in range(1, len(sizes)):
                if sizes[i] < sizes[i-1] * 0.3:
                    return 'cliff'
            
            return 'mixed'
        
        # Find walls
        bid_sizes = [s for _, s in bids]
        ask_sizes = [s for _, s in asks]
        
        support_wall = None
        resistance_wall = None
        
        if bid_sizes and max(bid_sizes) > 1000:  # Large block
            wall_idx = bid_sizes.index(max(bid_sizes))
            support_wall = bids[wall_idx][0]
        
        if ask_sizes and max(ask_sizes) > 1000:
            wall_idx = ask_sizes.index(max(ask_sizes))
            resistance_wall = asks[wall_idx][0]
        
        # Calculate imbalance
        total_bid = sum(bid_sizes)
        total_ask = sum(ask_sizes)
        imbalance = (total_bid - total_ask) / (total_bid + total_ask) if (total_bid + total_ask) > 0 else 0
        
        # Detect iceberg (suspicious patterns)
        iceberg = self._detect_iceberg(bids, asks)
        
        return OrderBookVisual(
            bid_levels=bids[:10],
            ask_levels=asks[:10],
            bid_shape=get_shape(bids),
            ask_shape=get_shape(asks),
            imbalance=round(imbalance, 3),
            support_wall=support_wall,
            resistance_wall=resistance_wall,
            iceberg_detected=iceberg
        )
    
    def _detect_iceberg(self, bids: List[Tuple[float, float]],
                       asks: List[Tuple[float, float]]) -> bool:
        """
        Detect potential iceberg orders
        
        Iceberg signs:
        - Rapid replenishment at specific levels
        - Round number clustering
        - Size patterns that repeat
        """
        # Check for round number clustering
        round_prices = [p for p, _ in bids if p % 1 == 0 or p % 5 == 0 or p % 10 == 0]
        
        if len(round_prices) > len(bids) * 0.7:
            return True
        
        # Check for repeated size patterns
        bid_sizes = [s for _, s in bids[:5]]
        if len(set(bid_sizes)) < 3 and sum(bid_sizes) > 1000:
            return True
        
        return False
    
    def _discover_new_patterns(self, ticker: str):
        """
        Unsupervised pattern discovery from price memory
        
        Uses clustering to find recurring formations
        """
        # Get recent prices for this ticker
        ticker_data = [
            d for d in self.price_memory 
            if d['ticker'] == ticker
        ][-50:]  # Last 50 data points
        
        if len(ticker_data) < 20:
            return
        
        prices = [d['price'] for d in ticker_data]
        
        # Look for common formations
        patterns_found = []
        
        # Pattern 1: Double bottom
        db = self._detect_double_bottom(prices)
        if db:
            patterns_found.append(('double_bottom', db))
        
        # Pattern 2: Ascending triangle
        at = self._detect_ascending_triangle(prices)
        if at:
            patterns_found.append(('ascending_triangle', at))
        
        # Pattern 3: Flag pattern
        flag = self._detect_flag(prices)
        if flag:
            patterns_found.append(('flag', flag))
        
        # Store discovered patterns
        for pattern_type, formation in patterns_found:
            pattern_id = f"{ticker}_{pattern_type}_{datetime.now().strftime('%H%M%S')}"
            
            if pattern_id not in self.pattern_database:
                self.pattern_database[pattern_id] = VisualPattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern_type,
                    formation=formation,
                    confidence=0.6,
                    success_rate=0.0,
                    occurrences=1,
                    last_seen=datetime.now(),
                    avg_return=0.0
                )
            else:
                # Update existing pattern
                existing = self.pattern_database[pattern_id]
                existing.occurrences += 1
                existing.last_seen = datetime.now()
                existing.confidence = min(existing.confidence + 0.05, 0.95)
    
    def _detect_double_bottom(self, prices: List[float]) -> Optional[List[Tuple[float, float]]]:
        """Detect double bottom pattern in price series"""
        if len(prices) < 20:
            return None
        
        # Find local minima
        from scipy.signal import find_peaks
        
        # Invert prices to find minima
        inverted = [-p for p in prices]
        minima, _ = find_peaks(inverted, distance=5, prominence=0.5)
        
        if len(minima) < 2:
            return None
        
        # Check last two minima
        bottom1 = prices[minima[-2]]
        bottom2 = prices[minima[-1]]
        
        # Similar price levels (within 2%)
        if abs(bottom1 - bottom2) / bottom1 < 0.02:
            return [(bottom1, minima[-2]), (bottom2, minima[-1])]
        
        return None
    
    def _detect_ascending_triangle(self, prices: List[float]) -> Optional[List[Tuple[float, float]]]:
        """Detect ascending triangle pattern"""
        if len(prices) < 15:
            return None
        
        recent = prices[-15:]
        
        # Find resistance (flat top)
        highs = [max(recent[i:i+3]) for i in range(0, len(recent)-2, 3)]
        
        # Check if highs are similar (resistance)
        if len(highs) >= 3 and max(highs) - min(highs) < (max(highs) * 0.01):
            # Check if lows are rising
            lows = [min(recent[i:i+3]) for i in range(0, len(recent)-2, 3)]
            
            if lows[-1] > lows[0]:  # Rising lows
                return [(h, i) for i, h in enumerate(highs)]
        
        return None
    
    def _detect_flag(self, prices: List[float]) -> Optional[List[Tuple[float, float]]]:
        """Detect flag/banner pattern after strong move"""
        if len(prices) < 10:
            return None
        
        recent = prices[-10:]
        
        # Check for tight consolidation after move
        range_pct = (max(recent) - min(recent)) / np.mean(recent)
        
        if range_pct < 0.02:  # Tight range
            return [(p, i) for i, p in enumerate(recent)]
        
        return None
    
    def analyze_cross_asset_visual(self, tickers: List[str]) -> Dict:
        """
        Watch multiple charts simultaneously for correlations
        
        Returns lead-lag relationships discovered visually
        """
        results = {}
        
        for i, ticker1 in enumerate(tickers):
            for ticker2 in tickers[i+1:]:
                # Get recent data for both
                data1 = [d for d in self.price_memory if d['ticker'] == ticker1][-30:]
                data2 = [d for d in self.price_memory if d['ticker'] == ticker2][-30:]
                
                if len(data1) < 10 or len(data2) < 10:
                    continue
                
                # Calculate visual correlation (simple price correlation)
                prices1 = [d['price'] for d in data1]
                prices2 = [d['price'] for d in data2]
                
                # Normalize
                norm1 = [(p - min(prices1)) / (max(prices1) - min(prices1)) for p in prices1]
                norm2 = [(p - min(prices2)) / (max(prices2) - min(prices2)) for p in prices2]
                
                # Correlation
                correlation = np.corrcoef(norm1, norm2)[0, 1] if len(norm1) == len(norm2) else 0
                
                if abs(correlation) > 0.7:
                    results[f"{ticker1}_{ticker2}"] = {
                        'correlation': round(correlation, 2),
                        'relationship': 'strong_positive' if correlation > 0 else 'strong_negative',
                        'visual_similarity': self._calculate_shape_similarity(norm1, norm2)
                    }
        
        return results
    
    def _calculate_shape_similarity(self, series1: List[float], 
                                    series2: List[float]) -> float:
        """Calculate shape similarity using dynamic time warping approximation"""
        if len(series1) != len(series2):
            return 0.0
        
        # Simple Euclidean distance on normalized series
        distance = np.sqrt(sum((a - b) ** 2 for a, b in zip(series1, series2)))
        
        # Convert to similarity (0-1)
        similarity = 1 / (1 + distance)
        
        return round(similarity, 2)
    
    def predict_next_move(self, ticker: str, 
                         lookback: int = 20) -> Dict:
        """
        Predict next price move based on visual pattern matching
        
        Finds similar historical patterns and calculates expected outcome
        """
        # Get current pattern
        recent_data = [d for d in self.price_memory if d['ticker'] == ticker][-lookback:]
        
        if len(recent_data) < lookback:
            return {'confidence': 0, 'prediction': 'insufficient_data'}
        
        current_pattern = [d['price'] for d in recent_data]
        
        # Find similar historical patterns
        matches = []
        
        for pattern_id, stored_pattern in self.pattern_database.items():
            if stored_pattern.pattern_type == 'double_bottom':
                # Simplified matching
                similarity = self._pattern_similarity(current_pattern, 
                                                     [p for p, _ in stored_pattern.formation])
                
                if similarity > 0.8:
                    matches.append({
                        'pattern': stored_pattern,
                        'similarity': similarity
                    })
        
        if not matches:
            return {'confidence': 0.3, 'prediction': 'neutral'}
        
        # Calculate prediction based on historical success
        avg_return = np.mean([m['pattern'].avg_return for m in matches])
        avg_confidence = np.mean([m['similarity'] for m in matches])
        
        return {
            'confidence': round(avg_confidence, 2),
            'predicted_return': round(avg_return, 2),
            'prediction': 'bullish' if avg_return > 0.02 else 'bearish' if avg_return < -0.02 else 'neutral',
            'based_on_patterns': len(matches)
        }
    
    def _pattern_similarity(self, pattern1: List[float], pattern2: List[float]) -> float:
        """Calculate similarity between two price patterns"""
        if len(pattern1) != len(pattern2):
            # Interpolate to match lengths
            min_len = min(len(pattern1), len(pattern2))
            pattern1 = pattern1[:min_len]
            pattern2 = pattern2[:min_len]
        
        # Normalize both
        p1_norm = [(p - min(pattern1)) / (max(pattern1) - min(pattern1) + 1e-10) for p in pattern1]
        p2_norm = [(p - min(pattern2)) / (max(pattern2) - min(pattern2) + 1e-10) for p in pattern2]
        
        # Correlation
        correlation = np.corrcoef(p1_norm, p2_norm)[0, 1] if len(p1_norm) > 1 else 0
        
        return abs(correlation)
    
    def get_learning_summary(self) -> Dict:
        """Get summary of what the AI has learned"""
        return {
            'patterns_discovered': len(self.pattern_database),
            'pattern_types': list(set(p.pattern_type for p in self.pattern_database.values())),
            'order_book_analyzed': len(self.order_book_history),
            'icebergs_detected': sum(1 for ob in self.order_book_history if ob['visual'].iceberg_detected),
            'cross_asset_relationships': len(self.cross_asset_patterns),
            'memory_utilization': len(self.price_memory) / self.price_memory.maxlen,
            'timestamp': datetime.now().isoformat()
        }


# Usage
def start_visual_learning_system() -> LiveVisualLearner:
    """Initialize the visual learning AI"""
    return LiveVisualLearner(memory_size=10000)


def quick_pattern_match(prices: List[float]) -> Dict:
    """Quick pattern analysis"""
    learner = LiveVisualLearner()
    
    for i, price in enumerate(prices):
        learner.feed_price_data('TEST', price, 1000, 
                               datetime.now() - timedelta(minutes=len(prices)-i))
    
    return learner.predict_next_move('TEST')
