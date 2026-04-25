"""Anomaly Detection - Unusual Volume/Price Detection"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    symbol: str
    anomaly_type: str
    severity: str
    z_score: float
    volume_z: float
    price_change_pct: float
    timestamp: str
    description: str


class AnomalyDetector:
    """Detect unusual market activity"""
    
    def __init__(self, lookback: int = 20):
        self.lookback = lookback
        self.threshold = 2.5  # Z-score threshold
    
    def detect(self, symbol: str, data: pd.DataFrame) -> List[Anomaly]:
        """Detect anomalies in price/volume data"""
        anomalies = []
        
        if len(data) < self.lookback:
            return anomalies
        
        # Calculate rolling statistics
        returns = data['close'].pct_change()
        vol_ma = data['volume'].rolling(self.lookback).mean()
        vol_std = data['volume'].rolling(self.lookback).std()
        price_std = returns.rolling(self.lookback).std()
        
        # Check latest point
        latest = data.iloc[-1]
        
        # Volume anomaly
        if vol_std.iloc[-1] > 0:
            vol_z = (latest['volume'] - vol_ma.iloc[-1]) / vol_std.iloc[-1]
            if vol_z > self.threshold:
                anomalies.append(Anomaly(
                    symbol=symbol,
                    anomaly_type="VOLUME_SPIKE",
                    severity="HIGH" if vol_z > 4 else "MEDIUM",
                    z_score=round(vol_z, 2),
                    volume_z=round(vol_z, 2),
                    price_change_pct=round(returns.iloc[-1] * 100, 2),
                    timestamp=str(data.index[-1]),
                    description=f"Unusual volume: {vol_z:.1f}x normal"
                ))
        
        # Price anomaly
        if price_std.iloc[-1] > 0:
            price_z = returns.iloc[-1] / price_std.iloc[-1]
            if abs(price_z) > self.threshold:
                anomalies.append(Anomaly(
                    symbol=symbol,
                    anomaly_type="PRICE_SPIKE",
                    severity="HIGH" if abs(price_z) > 4 else "MEDIUM",
                    z_score=round(price_z, 2),
                    volume_z=round(vol_z, 2) if 'vol_z' in dir() else 0,
                    price_change_pct=round(returns.iloc[-1] * 100, 2),
                    timestamp=str(data.index[-1]),
                    description=f"Large price move: {price_z:.1f}σ"
                ))
        
        return anomalies
    
    def scan_universe(self, universe_data: Dict[str, pd.DataFrame]) -> Dict[str, List[Anomaly]]:
        """Scan multiple symbols for anomalies"""
        results = {}
        for symbol, data in universe_data.items():
            results[symbol] = self.detect(symbol, data)
        return results
