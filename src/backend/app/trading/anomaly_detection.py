"""
Anomaly Detection Module for Financial Master

Implements advanced anomaly detection for:
- Trading pattern anomalies
- Market manipulation detection
- Portfolio risk anomalies
- Unusual trading volume detection

Based on Isolation Forest, Z-Score analysis, and statistical thresholds.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import deque
import asyncio

# ML imports
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies that can be detected."""
    VOLUME_SPIKE = "volume_spike"
    PRICE_MANIPULATION = "price_manipulation"
    UNUSUAL_PATTERN = "unusual_pattern"
    RISK_DEVIATION = "risk_deviation"
    FLASH_CRASH = "flash_crash"
    PUMP_AND_DUMP = "pump_and_dump"
    WASH_TRADING = "wash_trading"
    INSIDER_PATTERN = "insider_pattern"


@dataclass
class AnomalyAlert:
    """Represents a detected anomaly."""
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: str  # 'low', 'medium', 'high', 'critical'
    symbol: str
    description: str
    confidence: float
    metrics: Dict[str, float]
    recommended_action: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'anomaly_type': self.anomaly_type.value,
            'severity': self.severity,
            'symbol': self.symbol,
            'description': self.description,
            'confidence': self.confidence,
            'metrics': self.metrics,
            'recommended_action': self.recommended_action
        }


class AnomalyDetector:
    """
    Advanced anomaly detection system for trading.
    
    Features:
    - Real-time anomaly detection
    - ML-based pattern recognition
    - Statistical analysis
    - Historical baseline comparison
    """
    
    def __init__(self, 
                 contamination: float = 0.01,
                 window_size: int = 100,
                 z_threshold: float = 3.0):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers
            window_size: Rolling window size for analysis
            z_threshold: Z-score threshold for statistical anomalies
        """
        self.contamination = contamination
        self.window_size = window_size
        self.z_threshold = z_threshold
        
        # Isolation Forest model
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        # Data scaler
        self.scaler = StandardScaler()
        
        # Historical data storage
        self.price_history: Dict[str, deque] = {}
        self.volume_history: Dict[str, deque] = {}
        self.feature_history: Dict[str, deque] = {}
        
        # Baseline statistics
        self.baselines: Dict[str, Dict[str, float]] = {}
        
        # Alert callbacks
        self.alert_handlers: List[callable] = []
        
        logger.info("AnomalyDetector initialized")
    
    def register_alert_handler(self, handler: callable):
        """Register a callback for anomaly alerts."""
        self.alert_handlers.append(handler)
    
    async def process_trade(self, 
                          symbol: str,
                          price: float,
                          volume: float,
                          timestamp: Optional[datetime] = None) -> Optional[AnomalyAlert]:
        """
        Process a single trade and detect anomalies.
        
        Args:
            symbol: Trading pair symbol
            price: Trade price
            volume: Trade volume
            timestamp: Trade timestamp
            
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Update history
        await self._update_history(symbol, price, volume, timestamp)
        
        # Check for anomalies
        alerts = []
        
        # Volume spike detection
        volume_alert = await self._detect_volume_spike(symbol, volume)
        if volume_alert:
            alerts.append(volume_alert)
        
        # Price manipulation detection
        price_alert = await self._detect_price_manipulation(symbol, price)
        if price_alert:
            alerts.append(price_alert)
        
        # Statistical anomaly detection
        statistical_alert = await self._detect_statistical_anomaly(symbol, price, volume)
        if statistical_alert:
            alerts.append(statistical_alert)
        
        # Pump and dump detection
        pump_alert = await self._detect_pump_and_dump(symbol, price, volume)
        if pump_alert:
            alerts.append(pump_alert)
        
        # Notify handlers
        for alert in alerts:
            await self._notify_alert_handlers(alert)
        
        # Return highest severity alert
        if alerts:
            severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            return max(alerts, key=lambda x: severity_order.get(x.severity, 0))
        
        return None
    
    async def _update_history(self, 
                            symbol: str, 
                            price: float, 
                            volume: float,
                            timestamp: datetime):
        """Update historical data for a symbol."""
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.window_size)
            self.volume_history[symbol] = deque(maxlen=self.window_size)
            self.feature_history[symbol] = deque(maxlen=self.window_size)
        
        self.price_history[symbol].append({
            'price': price,
            'timestamp': timestamp
        })
        self.volume_history[symbol].append({
            'volume': volume,
            'timestamp': timestamp
        })
    
    async def _detect_volume_spike(self, 
                                 symbol: str, 
                                 current_volume: float) -> Optional[AnomalyAlert]:
        """Detect unusual volume spikes."""
        if symbol not in self.volume_history or len(self.volume_history[symbol]) < 20:
            return None
        
        volumes = [v['volume'] for v in self.volume_history[symbol]]
        mean_volume = np.mean(volumes)
        std_volume = np.std(volumes)
        
        if std_volume == 0:
            return None
        
        z_score = (current_volume - mean_volume) / std_volume
        
        if z_score > self.z_threshold:
            confidence = min(abs(z_score) / (self.z_threshold * 2), 1.0)
            
            return AnomalyAlert(
                timestamp=datetime.now(),
                anomaly_type=AnomalyType.VOLUME_SPIKE,
                severity='high' if z_score > self.z_threshold * 1.5 else 'medium',
                symbol=symbol,
                description=f"Unusual volume spike detected: {current_volume:,.0f} vs avg {mean_volume:,.0f}",
                confidence=confidence,
                metrics={
                    'current_volume': current_volume,
                    'mean_volume': mean_volume,
                    'z_score': z_score,
                    'spike_ratio': current_volume / mean_volume if mean_volume > 0 else 0
                },
                recommended_action="Review for potential market manipulation or insider trading"
            )
        
        return None
    
    async def _detect_price_manipulation(self, 
                                       symbol: str, 
                                       current_price: float) -> Optional[AnomalyAlert]:
        """Detect potential price manipulation patterns."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 30:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        
        # Check for flash crash (rapid drop)
        if len(prices) >= 10:
            recent_return = (current_price - prices[-10]) / prices[-10]
            
            if recent_return < -0.05:  # 5% drop in 10 periods
                return AnomalyAlert(
                    timestamp=datetime.now(),
                    anomaly_type=AnomalyType.FLASH_CRASH,
                    severity='critical',
                    symbol=symbol,
                    description=f"Potential flash crash: {recent_return:.2%} drop detected",
                    confidence=0.85,
                    metrics={
                        'price_drop': recent_return,
                        'current_price': current_price,
                        'reference_price': prices[-10]
                    },
                    recommended_action="Halt automated trading and investigate market conditions"
                )
        
        # Check for unusual price volatility
        returns = np.diff(prices) / prices[:-1]
        if len(returns) > 20:
            recent_volatility = np.std(returns[-10:])
            historical_volatility = np.std(returns[:-10])
            
            if historical_volatility > 0 and recent_volatility > historical_volatility * 3:
                return AnomalyAlert(
                    timestamp=datetime.now(),
                    anomaly_type=AnomalyType.PRICE_MANIPULATION,
                    severity='high',
                    symbol=symbol,
                    description=f"Unusual price volatility: {recent_volatility:.4f} vs historical {historical_volatility:.4f}",
                    confidence=0.75,
                    metrics={
                        'recent_volatility': recent_volatility,
                        'historical_volatility': historical_volatility,
                        'volatility_ratio': recent_volatility / historical_volatility
                    },
                    recommended_action="Monitor for spoofing or layering activity"
                )
        
        return None
    
    async def _detect_statistical_anomaly(self, 
                                        symbol: str, 
                                        price: float,
                                        volume: float) -> Optional[AnomalyAlert]:
        """Detect anomalies using Isolation Forest."""
        if symbol not in self.feature_history or len(self.feature_history[symbol]) < 50:
            return None
        
        # Extract features
        prices = [p['price'] for p in self.price_history[symbol]]
        volumes = [v['volume'] for v in self.volume_history[symbol]]
        
        if len(prices) < 20:
            return None
        
        # Calculate features
        returns = np.diff(prices[-21:]) / prices[-21:-1]
        
        features = np.array([
            price,
            volume,
            np.mean(returns),
            np.std(returns),
            np.max(returns),
            np.min(returns),
            prices[-1] - prices[-20],  # Price change
            volume / np.mean(volumes[-20:]) if volumes else 1  # Volume ratio
        ]).reshape(1, -1)
        
        # Scale features
        if len(self.feature_history[symbol]) >= 50:
            historical_features = []
            for i in range(min(100, len(prices) - 20)):
                window_prices = prices[-(i+21):-(i+1) or None]
                window_volumes = volumes[-(i+21):-(i+1) or None]
                if len(window_prices) >= 20:
                    window_returns = np.diff(window_prices) / window_prices[:-1]
                    historical_features.append([
                        window_prices[-1],
                        window_volumes[-1] if window_volumes else 0,
                        np.mean(window_returns),
                        np.std(window_returns),
                        np.max(window_returns),
                        np.min(window_returns),
                        window_prices[-1] - window_prices[0],
                        window_volumes[-1] / np.mean(window_volumes) if window_volumes else 1
                    ])
            
            if len(historical_features) >= 30:
                X = np.array(historical_features)
                X_scaled = self.scaler.fit_transform(X)
                
                # Fit Isolation Forest
                self.isolation_forest.fit(X_scaled)
                
                # Predict current
                current_scaled = self.scaler.transform(features)
                prediction = self.isolation_forest.predict(current_scaled)
                score = -self.isolation_forest.score_samples(current_scaled)[0]
                
                if prediction[0] == -1 and score > 0.6:  # Anomaly detected
                    return AnomalyAlert(
                        timestamp=datetime.now(),
                        anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                        severity='medium',
                        symbol=symbol,
                        description=f"Statistical anomaly detected (score: {score:.3f})",
                        confidence=score,
                        metrics={
                            'anomaly_score': score,
                            'price': price,
                            'volume': volume,
                            'return_volatility': np.std(returns)
                        },
                        recommended_action="Flag for manual review"
                    )
        
        return None
    
    async def _detect_pump_and_dump(self, 
                                  symbol: str, 
                                  price: float,
                                  volume: float) -> Optional[AnomalyAlert]:
        """Detect pump and dump patterns."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 50:
            return None
        
        prices = [p['price'] for p in self.price_history[symbol]]
        volumes = [v['volume'] for v in self.volume_history[symbol]]
        
        # Calculate returns and volume changes
        if len(prices) < 30:
            return None
        
        recent_returns = []
        for i in range(1, min(20, len(prices))):
            ret = (prices[-i] - prices[-(i+1)]) / prices[-(i+1)]
            recent_returns.append(ret)
        
        avg_recent_return = np.mean(recent_returns)
        cumulative_return = (price - prices[-20]) / prices[-20]
        
        # Pump and dump indicators:
        # 1. Rapid price increase (>20% in short period)
        # 2. High volume accompanying price moves
        # 3. Sudden volume drop after price peak
        
        if cumulative_return > 0.20:  # 20% increase
            recent_volume = np.mean(volumes[-10:])
            historical_volume = np.mean(volumes[-50:-10])
            
            volume_spike = recent_volume > historical_volume * 2 if historical_volume > 0 else False
            
            if volume_spike:
                return AnomalyAlert(
                    timestamp=datetime.now(),
                    anomaly_type=AnomalyType.PUMP_AND_DUMP,
                    severity='critical',
                    symbol=symbol,
                    description=f"Potential pump and dump: {cumulative_return:.1%} price increase with volume spike",
                    confidence=0.80,
                    metrics={
                        'cumulative_return': cumulative_return,
                        'volume_ratio': recent_volume / historical_volume if historical_volume > 0 else 0,
                        'recent_avg_return': avg_recent_return,
                        'current_price': price
                    },
                    recommended_action="Exercise extreme caution - potential market manipulation"
                )
        
        return None
    
    async def _notify_alert_handlers(self, alert: AnomalyAlert):
        """Notify all registered alert handlers."""
        for handler in self.alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")
    
    def get_baseline_metrics(self, symbol: str) -> Dict[str, float]:
        """Get baseline metrics for a symbol."""
        if symbol not in self.price_history or len(self.price_history[symbol]) < 30:
            return {}
        
        prices = [p['price'] for p in self.price_history[symbol]]
        volumes = [v['volume'] for v in self.volume_history[symbol]]
        
        returns = np.diff(prices) / prices[:-1]
        
        return {
            'mean_price': np.mean(prices),
            'price_volatility': np.std(returns),
            'mean_volume': np.mean(volumes),
            'volume_volatility': np.std(volumes),
            'max_price': np.max(prices),
            'min_price': np.min(prices),
            'price_range': np.max(prices) - np.min(prices)
        }
    
    def get_recent_anomalies(self, 
                           symbol: Optional[str] = None,
                           hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent anomalies (placeholder - would query database in production)."""
        # In production, this would query a database of stored anomalies
        return []


class AnomalyDetectionAPI:
    """FastAPI router for anomaly detection endpoints."""
    
    def __init__(self):
        self.detector = AnomalyDetector()
        self.active_monitors: Dict[str, asyncio.Task] = {}
    
    async def start_monitoring(self, symbol: str, interval: float = 1.0):
        """Start continuous monitoring of a symbol."""
        if symbol in self.active_monitors:
            return
        
        async def monitor():
            while True:
                # In production, this would poll market data
                await asyncio.sleep(interval)
        
        self.active_monitors[symbol] = asyncio.create_task(monitor())
    
    async def stop_monitoring(self, symbol: str):
        """Stop monitoring a symbol."""
        if symbol in self.active_monitors:
            self.active_monitors[symbol].cancel()
            del self.active_monitors[symbol]


# Singleton instance
anomaly_detector = AnomalyDetector()


async def analyze_trade_for_anomalies(symbol: str, 
                                     price: float, 
                                     volume: float) -> Optional[AnomalyAlert]:
    """Convenience function for anomaly detection."""
    return await anomaly_detector.process_trade(symbol, price, volume)
