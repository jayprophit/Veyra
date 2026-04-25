"""
Conspiracy Detection Engine
=============================
Detect coordinated market manipulation

Legal Note: For educational purposes only
Inspired by: The Big Short, Wolf of Wall St
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ManipulationType(Enum):
    PUMP_AND_DUMP = "pump_and_dump"
    SHORT_DISTORT = "short_and_distort"
    INSIDER_RING = "insider_ring"
    SPOOFING = "spoofing"
    WASH_TRADING = "wash_trading"


@dataclass
class ManipulationAlert:
    symbol: str
    manipulation_type: ManipulationType
    confidence: float
    indicators: List[str]
    severity: str
    timestamp: str
    description: str
    evidence: Dict


class ConspiracyDetector:
    """Detect market manipulation patterns"""
    
    def __init__(self):
        self.lookback_days = 30
        self.confidence_threshold = 0.7
    
    def analyze(self, symbol: str, data: pd.DataFrame, social_data: Optional[List] = None) -> List[ManipulationAlert]:
        """Analyze for manipulation patterns"""
        alerts = []
        
        # Pump and dump detection
        pump_alert = self._detect_pump_dump(symbol, data)
        if pump_alert:
            alerts.append(pump_alert)
        
        # Short and distort detection
        short_alert = self._detect_short_distort(symbol, data)
        if short_alert:
            alerts.append(short_alert)
        
        # Spoofing detection (requires level 2 data)
        spoof_alert = self._detect_spoofing(symbol, data)
        if spoof_alert:
            alerts.append(spoof_alert)
        
        # Wash trading detection
        wash_alert = self._detect_wash_trading(symbol, data)
        if wash_alert:
            alerts.append(wash_alert)
        
        return alerts
    
    def _detect_pump_dump(self, symbol: str, data: pd.DataFrame) -> Optional[ManipulationAlert]:
        """Detect pump and dump patterns"""
        if len(data) < 10:
            return None
        
        recent = data.tail(10)
        price_change = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
        volume_spike = recent['volume'].mean() / data['volume'].mean()
        
        # Classic pump: price up + volume spike, then drop
        indicators = []
        confidence = 0.0
        
        if price_change > 0.5:  # 50% gain
            indicators.append(f"Price surge: {price_change*100:.1f}%")
            confidence += 0.3
        
        if volume_spike > 3:  # 3x volume
            indicators.append(f"Volume spike: {volume_spike:.1f}x")
            confidence += 0.3
        
        if price_change > 0.3 and volume_spike > 2 and data['close'].iloc[-1] < recent['close'].iloc[-3]:
            indicators.append("Early dump phase detected")
            confidence += 0.2
        
        if confidence >= self.confidence_threshold:
            return ManipulationAlert(
                symbol=symbol,
                manipulation_type=ManipulationType.PUMP_AND_DUMP,
                confidence=round(confidence, 2),
                indicators=indicators,
                severity="HIGH" if confidence > 0.85 else "MEDIUM",
                timestamp=datetime.now().isoformat(),
                description="Potential pump and dump scheme detected",
                evidence={
                    "price_change": price_change,
                    "volume_spike": volume_spike,
                    "timeline": "last_10_days"
                }
            )
        return None
    
    def _detect_short_distort(self, symbol: str, data: pd.DataFrame) -> Optional[ManipulationAlert]:
        """Detect short and distort campaigns"""
        recent = data.tail(5)
        price_drop = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
        
        if price_drop < -0.3:  # 30% drop
            return ManipulationAlert(
                symbol=symbol,
                manipulation_type=ManipulationType.SHORT_DISTORT,
                confidence=0.6,
                indicators=[f"Rapid price decline: {price_drop*100:.1f}%"],
                severity="MEDIUM",
                timestamp=datetime.now().isoformat(),
                description="Potential short and distort campaign",
                evidence={"price_drop": price_drop}
            )
        return None
    
    def _detect_spoofing(self, symbol: str, data: pd.DataFrame) -> Optional[ManipulationAlert]:
        """Detect order book spoofing (requires L2 data)"""
        # Placeholder - requires bid/ask level data
        return None
    
    def _detect_wash_trading(self, symbol: str, data: pd.DataFrame) -> Optional[ManipulationAlert]:
        """Detect wash trading patterns"""
        # Look for unusual volume with flat price
        if len(data) < 5:
            return None
        
        recent = data.tail(5)
        price_range = (recent['high'].max() - recent['low'].min()) / recent['close'].mean()
        volume_spike = recent['volume'].mean() / data['volume'].mean()
        
        if volume_spike > 5 and price_range < 0.02:  # High volume, flat price
            return ManipulationAlert(
                symbol=symbol,
                manipulation_type=ManipulationType.WASH_TRADING,
                confidence=0.75,
                indicators=["High volume with flat price"],
                severity="HIGH",
                timestamp=datetime.now().isoformat(),
                description="Potential wash trading (volume manipulation)",
                evidence={
                    "volume_spike": volume_spike,
                    "price_range": price_range
                }
            )
        return None
