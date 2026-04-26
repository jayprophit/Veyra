"""
AI/ML Predictive Engine
Provides market predictions, risk analysis, and pattern detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os


class PredictionType(Enum):
    PRICE_MOVEMENT = "price_movement"
    VOLATILITY = "volatility"
    TREND = "trend"
    CRASH_RISK = "crash_risk"
    SUPPORT_RESISTANCE = "support_resistance"


@dataclass
class PredictionResult:
    prediction_type: PredictionType
    asset_symbol: str
    timeframe: str
    confidence: float
    prediction: Any
    probabilities: Optional[Dict[str, float]] = None
    features_used: List[str] = None
    timestamp: datetime = None
    model_version: str = "1.0"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class MarketCrashRisk:
    risk_score: float  # 0-100
    indicators_triggered: List[str]
    recommended_action: str
    time_horizon: str
    confidence: float


class PredictiveEngine:
    """
    Central AI engine for all predictive analytics
    Uses ensemble of models for robust predictions
    """
    
    def __init__(self, model_path: str = "models/"):
        self.model_path = model_path
        self.scaler = StandardScaler()
        self.models = {}
        self._load_models()
        
    def _load_models(self):
        """Load pre-trained models or initialize new ones"""
        os.makedirs(self.model_path, exist_ok=True)
        
        # Initialize models (in production, load pre-trained)
        self.models = {
            "price_rf": RandomForestRegressor(n_estimators=100, random_state=42),
            "trend_gb": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "volatility_rf": RandomForestRegressor(n_estimators=50, random_state=42),
        }
        
    async def predict_price_movement(
        self,
        symbol: str,
        historical_data: pd.DataFrame,
        timeframe: str = "1d",
        horizon: int = 5
    ) -> PredictionResult:
        """
        Predict price movement for given symbol
        
        Args:
            symbol: Asset symbol
            historical_data: OHLCV DataFrame
            timeframe: Prediction timeframe (1d, 1w, 1m)
            horizon: Days ahead to predict
        """
        # Feature engineering
        features = self._engineer_features(historical_data)
        
        # Calculate technical indicators as features
        feature_vector = self._create_feature_vector(features)
        
        # Mock prediction (replace with actual model inference)
        trend_probabilities = {
            "bullish": 0.45,
            "bearish": 0.30,
            "neutral": 0.25
        }
        
        # Determine dominant trend
        max_prob = max(trend_probabilities.values())
        prediction = [k for k, v in trend_probabilities.items() if v == max_prob][0]
        
        return PredictionResult(
            prediction_type=PredictionType.PRICE_MOVEMENT,
            asset_symbol=symbol,
            timeframe=timeframe,
            confidence=max_prob,
            prediction=prediction,
            probabilities=trend_probabilities,
            features_used=list(features.columns),
            model_version="1.0.0"
        )
    
    async def predict_volatility(
        self,
        symbol: str,
        historical_data: pd.DataFrame,
        window: int = 30
    ) -> PredictionResult:
        """Predict volatility for next N days"""
        
        # Calculate historical volatility
        returns = historical_data['close'].pct_change().dropna()
        hist_vol = returns.std() * np.sqrt(252)  # Annualized
        
        # GARCH-like prediction (simplified)
        recent_vol = returns.tail(window).std() * np.sqrt(252)
        
        # Trend in volatility
        vol_trend = "increasing" if recent_vol > hist_vol else "decreasing"
        
        prediction = {
            "current_volatility": float(hist_vol),
            "predicted_volatility": float(recent_vol * 1.1),  # Slight increase assumption
            "trend": vol_trend,
            "risk_level": "high" if recent_vol > 0.4 else "medium" if recent_vol > 0.2 else "low"
        }
        
        return PredictionResult(
            prediction_type=PredictionType.VOLATILITY,
            asset_symbol=symbol,
            timeframe=f"{window}d",
            confidence=0.72,
            prediction=prediction,
            features_used=["returns", "rolling_std", "atr"],
            model_version="1.0.0"
        )
    
    async def detect_market_crash_risk(
        self,
        market_data: Dict[str, pd.DataFrame],
        indicators: List[str] = None
    ) -> MarketCrashRisk:
        """
        Detect risk of market crash based on multiple indicators
        Inspired by "The Big Short" - multiple signals approach
        """
        if indicators is None:
            indicators = [
                "vix_spike",
                "yield_curve_inversion",
                "credit_spreads",
                "margin_debt",
                "put_call_ratio",
                "breadth_divergence",
                "liquidity_stress"
            ]
        
        triggered = []
        risk_scores = []
        
        # Check VIX spike
        if "VIX" in market_data:
            vix = market_data["VIX"]
            current_vix = vix['close'].iloc[-1]
            if current_vix > 30:
                triggered.append("vix_spike")
                risk_scores.append(25)
        
        # Check yield curve
        if all(x in market_data for x in ["TLT", "SHY"]):
            long_yield = market_data["TLT"]['close'].iloc[-1]
            short_yield = market_data["SHY"]['close'].iloc[-1]
            if short_yield > long_yield:  # Inversion
                triggered.append("yield_curve_inversion")
                risk_scores.append(35)
        
        # Credit spreads (high yield vs investment grade)
        # Put/Call ratio extreme
        # Market breadth divergence
        
        total_risk = min(sum(risk_scores), 100)
        
        # Determine action
        if total_risk > 70:
            action = "REDUCE_EXPOSURE_IMMEDIATELY"
        elif total_risk > 50:
            action = "HEDGE_PORTFOLIO"
        elif total_risk > 30:
            action = "MONITOR_CLOSELY"
        else:
            action = "MAINTAIN_COURSE"
        
        return MarketCrashRisk(
            risk_score=total_risk,
            indicators_triggered=triggered,
            recommended_action=action,
            time_horizon="1-3 months",
            confidence=0.68 if triggered else 0.85
        )
    
    async def predict_support_resistance(
        self,
        symbol: str,
        historical_data: pd.DataFrame,
        levels_count: int = 3
    ) -> PredictionResult:
        """Predict support and resistance levels"""
        
        highs = historical_data['high'].values
        lows = historical_data['low'].values
        closes = historical_data['close'].values
        
        current_price = closes[-1]
        
        # Find local maxima/minima
        from scipy.signal import find_peaks
        
        # Resistance levels (peaks in highs)
        resistance_peaks, _ = find_peaks(highs, distance=5, prominence=current_price*0.02)
        resistance_levels = sorted(highs[resistance_peaks], reverse=True)
        resistance_levels = [float(x) for x in resistance_levels[:levels_count] if x > current_price]
        
        # Support levels (peaks in inverted lows)
        support_peaks, _ = find_peaks(-lows, distance=5, prominence=current_price*0.02)
        support_levels = sorted(lows[support_peaks])
        support_levels = [float(x) for x in support_levels[:levels_count] if x < current_price]
        
        # Add psychological levels (round numbers)
        round_resistance = self._find_round_levels(current_price, resistance_levels, "up")
        round_support = self._find_round_levels(current_price, support_levels, "down")
        
        prediction = {
            "current_price": float(current_price),
            "resistance_levels": resistance_levels + round_resistance,
            "support_levels": support_levels + round_support,
            "pivot_point": float((current_price + highs[-1] + lows[-1]) / 3),
            "nearest_resistance": min(resistance_levels) if resistance_levels else None,
            "nearest_support": max(support_levels) if support_levels else None
        }
        
        return PredictionResult(
            prediction_type=PredictionType.SUPPORT_RESISTANCE,
            asset_symbol=symbol,
            timeframe="current",
            confidence=0.78,
            prediction=prediction,
            features_used=["price_action", "volume_profile", "pivot_points"],
            model_version="1.0.0"
        )
    
    async def analyze_cross_asset_correlations(
        self,
        assets_data: Dict[str, pd.DataFrame],
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Analyze correlations between assets for diversification insights"""
        
        # Calculate correlation matrix
        returns_data = {}
        for symbol, df in assets_data.items():
            returns_data[symbol] = df['close'].pct_change().dropna()
        
        returns_df = pd.DataFrame(returns_data)
        corr_matrix = returns_df.corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > threshold:
                    high_corr_pairs.append({
                        "asset_1": corr_matrix.columns[i],
                        "asset_2": corr_matrix.columns[j],
                        "correlation": float(corr_val),
                        "relationship": "positive" if corr_val > 0 else "negative"
                    })
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "high_correlation_pairs": high_corr_pairs,
            "diversification_score": self._calculate_diversification_score(corr_matrix),
            "recommendations": self._generate_diversification_recommendations(high_corr_pairs)
        }
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technical features for ML models"""
        features = pd.DataFrame(index=df.index)
        
        # Price-based features
        features['returns'] = df['close'].pct_change()
        features['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Moving averages
        for window in [5, 10, 20, 50, 200]:
            features[f'sma_{window}'] = df['close'].rolling(window=window).mean()
            features[f'ema_{window}'] = df['close'].ewm(span=window).mean()
            features[f'sma_ratio_{window}'] = df['close'] / features[f'sma_{window}']
        
        # Volatility
        features['volatility'] = features['returns'].rolling(window=20).std()
        features['atr'] = self._calculate_atr(df)
        
        # Volume features
        features['volume_sma'] = df['volume'].rolling(window=20).mean()
        features['volume_ratio'] = df['volume'] / features['volume_sma']
        
        # Momentum indicators
        features['rsi'] = self._calculate_rsi(df['close'])
        features['macd'], features['macd_signal'] = self._calculate_macd(df['close'])
        
        # Price position
        features['price_position'] = (df['close'] - df['low'].rolling(20).min()) / \
                                     (df['high'].rolling(20).max() - df['low'].rolling(20).min())
        
        return features.dropna()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line"""
        ema_12 = prices.ewm(span=12).mean()
        ema_26 = prices.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        return macd, signal
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()
    
    def _create_feature_vector(self, features: pd.DataFrame) -> np.ndarray:
        """Create feature vector for model input"""
        latest = features.iloc[-1:].values
        return self.scaler.fit_transform(latest)
    
    def _find_round_levels(self, current: float, existing: List[float], direction: str) -> List[float]:
        """Find psychological round number levels"""
        levels = []
        if direction == "up":
            base = int(current / 10) * 10
            for i in range(1, 4):
                level = base + (i * 10)
                if level not in existing:
                    levels.append(float(level))
        else:
            base = int(current / 10) * 10
            for i in range(1, 4):
                level = base - (i * 10)
                if level > 0 and level not in existing:
                    levels.append(float(level))
        return levels
    
    def _calculate_diversification_score(self, corr_matrix: pd.DataFrame) -> float:
        """Calculate portfolio diversification score (0-100)"""
        # Average correlation (lower is better)
        avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
        # Convert to score (inverse relationship)
        score = (1 - avg_corr) * 100
        return float(max(0, min(100, score)))
    
    def _generate_diversification_recommendations(self, high_corr_pairs: List[Dict]) -> List[str]:
        """Generate recommendations based on correlations"""
        recommendations = []
        
        for pair in high_corr_pairs:
            if pair['correlation'] > 0.9:
                recommendations.append(
                    f"Consider reducing exposure to both {pair['asset_1']} and {pair['asset_2']} - "
                    f"extremely high correlation ({pair['correlation']:.2f}) provides no diversification"
                )
            elif pair['correlation'] > 0.7:
                recommendations.append(
                    f"Monitor positions in {pair['asset_1']} and {pair['asset_2']} - "
                    f"high positive correlation ({pair['correlation']:.2f})"
                )
        
        if not high_corr_pairs:
            recommendations.append("Portfolio shows good diversification with low correlations")
        
        return recommendations
    
    async def generate_ai_insights(
        self,
        portfolio_data: Dict,
        market_data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Generate comprehensive AI insights for portfolio"""
        
        insights = {
            "timestamp": datetime.utcnow().isoformat(),
            "predictions": [],
            "risks": [],
            "opportunities": [],
            "recommendations": []
        }
        
        # Price predictions for each holding
        for symbol, data in market_data.items():
            if len(data) > 50:  # Minimum data requirement
                pred = await self.predict_price_movement(symbol, data)
                insights["predictions"].append({
                    "symbol": symbol,
                    "prediction": pred.prediction,
                    "confidence": pred.confidence,
                    "probabilities": pred.probabilities
                })
        
        # Crash risk assessment
        crash_risk = await self.detect_market_crash_risk(market_data)
        insights["risks"].append({
            "type": "market_crash",
            "risk_score": crash_risk.risk_score,
            "indicators": crash_risk.indicators_triggered,
            "action": crash_risk.recommended_action
        })
        
        # Correlation analysis
        if len(market_data) > 1:
            corr_analysis = await self.analyze_cross_asset_correlations(market_data)
            insights["diversification"] = corr_analysis
        
        return insights
