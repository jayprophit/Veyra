"""
Volume Analysis
Analyzes trading volume patterns for confirmation signals
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class VolumeSignal:
    symbol: str
    signal_type: str  # 'volume_spike', 'volume_dry_up', 'confirmation', 'divergence'
    strength: float  # 0-1
    current_volume: float
    average_volume: float
    ratio: float
    timestamp: datetime

class VolumeAnalysis:
    """
    Analyze volume patterns for trading signals
    """
    
    def __init__(self, lookback_period: int = 20):
        self.lookback_period = lookback_period
        self.signals: List[VolumeSignal] = []
    
    def calculate_average_volume(self, volumes: List[float]) -> float:
        """Calculate average volume over lookback period"""
        if len(volumes) < self.lookback_period:
            return np.mean(volumes)
        return np.mean(volumes[-self.lookback_period:])
    
    def detect_volume_spike(self, 
                           symbol: str,
                           current_volume: float,
                           volume_history: List[float],
                           threshold: float = 2.0) -> Optional[VolumeSignal]:
        """
        Detect unusual volume spikes
        threshold: multiplier above average (e.g., 2.0 = 2x average)
        """
        avg_volume = self.calculate_average_volume(volume_history)
        
        if avg_volume == 0:
            return None
        
        ratio = current_volume / avg_volume
        
        if ratio >= threshold:
            return VolumeSignal(
                symbol=symbol,
                signal_type='volume_spike',
                strength=min(ratio / threshold, 1.0),
                current_volume=current_volume,
                average_volume=avg_volume,
                ratio=round(ratio, 2),
                timestamp=datetime.now()
            )
        
        return None
    
    def detect_volume_dry_up(self,
                            symbol: str,
                            current_volume: float,
                            volume_history: List[float],
                            threshold: float = 0.5) -> Optional[VolumeSignal]:
        """
        Detect unusually low volume (potential reversal setup)
        threshold: multiplier below average (e.g., 0.5 = 50% of average)
        """
        avg_volume = self.calculate_average_volume(volume_history)
        
        if avg_volume == 0:
            return None
        
        ratio = current_volume / avg_volume
        
        if ratio <= threshold:
            return VolumeSignal(
                symbol=symbol,
                signal_type='volume_dry_up',
                strength=min((1 - ratio) * 2, 1.0),
                current_volume=current_volume,
                average_volume=avg_volume,
                ratio=round(ratio, 2),
                timestamp=datetime.now()
            )
        
        return None
    
    def analyze_price_volume_relationship(self,
                                        symbol: str,
                                        prices: List[float],
                                        volumes: List[float]) -> List[VolumeSignal]:
        """
        Analyze relationship between price movement and volume
        """
        signals = []
        
        if len(prices) < 2 or len(volumes) < self.lookback_period:
            return signals
        
        current_price = prices[-1]
        previous_price = prices[-2]
        current_volume = volumes[-1]
        
        price_change_pct = ((current_price - previous_price) / previous_price) * 100
        avg_volume = self.calculate_average_volume(volumes)
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
        
        # Volume confirmation of price move
        if abs(price_change_pct) > 1.0 and volume_ratio > 1.5:
            signals.append(VolumeSignal(
                symbol=symbol,
                signal_type='confirmation',
                strength=round(volume_ratio / 3, 2),
                current_volume=current_volume,
                average_volume=avg_volume,
                ratio=round(volume_ratio, 2),
                timestamp=datetime.now()
            ))
        
        # Volume divergence (price up, volume down - potential reversal)
        if price_change_pct > 1.0 and volume_ratio < 0.8:
            signals.append(VolumeSignal(
                symbol=symbol,
                signal_type='divergence_bearish',
                strength=round((1 - volume_ratio) * abs(price_change_pct) / 5, 2),
                current_volume=current_volume,
                average_volume=avg_volume,
                ratio=round(volume_ratio, 2),
                timestamp=datetime.now()
            ))
        
        # Volume divergence (price down, volume down - potential reversal)
        if price_change_pct < -1.0 and volume_ratio < 0.8:
            signals.append(VolumeSignal(
                symbol=symbol,
                signal_type='divergence_bullish',
                strength=round((1 - volume_ratio) * abs(price_change_pct) / 5, 2),
                current_volume=current_volume,
                average_volume=avg_volume,
                ratio=round(volume_ratio, 2),
                timestamp=datetime.now()
            ))
        
        return signals
    
    def analyze_accumulation_distribution(self,
                                        prices: List[float],
                                        volumes: List[float]) -> Dict:
        """
        Analyze accumulation vs distribution
        Based on whether price closes near high or low on volume
        """
        if len(prices) < 20 or len(volumes) < 20:
            return {}
        
        acc_volume = 0
        dist_volume = 0
        
        for i in range(-20, 0):
            if i >= -len(prices):
                # Simple proxy: if close is in upper half of range = accumulation
                price_range = max(prices) - min(prices)
                if price_range > 0:
                    position_in_range = (prices[i] - min(prices)) / price_range
                    
                    if position_in_range > 0.6:
                        acc_volume += volumes[i]
                    elif position_in_range < 0.4:
                        dist_volume += volumes[i]
        
        total = acc_volume + dist_volume
        if total == 0:
            return {'accumulation_pct': 50, 'distribution_pct': 50}
        
        return {
            'accumulation_pct': round((acc_volume / total) * 100, 1),
            'distribution_pct': round((dist_volume / total) * 100, 1),
            'interpretation': 'accumulation' if acc_volume > dist_volume else 'distribution'
        }
    
    def scan_symbol(self, symbol: str, prices: List[float], volumes: List[float]) -> List[VolumeSignal]:
        """Full volume analysis for a symbol"""
        all_signals = []
        
        if len(volumes) < self.lookback_period:
            return all_signals
        
        current_volume = volumes[-1]
        volume_history = volumes[:-1]
        
        # Volume spike
        spike = self.detect_volume_spike(symbol, current_volume, volume_history)
        if spike:
            all_signals.append(spike)
        
        # Volume dry up
        dry_up = self.detect_volume_dry_up(symbol, current_volume, volume_history)
        if dry_up:
            all_signals.append(dry_up)
        
        # Price-volume relationship
        pv_signals = self.analyze_price_volume_relationship(symbol, prices, volumes)
        all_signals.extend(pv_signals)
        
        self.signals = all_signals
        return all_signals
