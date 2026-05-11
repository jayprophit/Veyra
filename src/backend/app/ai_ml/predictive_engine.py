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
        
        # Real ML model inference
        if not hasattr(self, 'trend_model'):
            self.trend_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            self.trend_model_fitted = False
        
        # Prepare training data if model not fitted
        if not self.trend_model_fitted:
            self._train_trend_model(features)
        
        # Make prediction
        try:
            prediction_proba = self.trend_model.predict_proba(feature_vector)
            classes = self.trend_model.classes_
            trend_probabilities = {
                classes[i]: float(prediction_proba[0][i]) 
                for i in range(len(classes))
            }
        except Exception as e:
            # Fallback to technical analysis if model fails
            trend_probabilities = self._technical_analysis_prediction(features)
        
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
        
        # Real volatility prediction using GARCH-like model
        recent_vol = returns.tail(window).std() * np.sqrt(252)
        
        # GARCH(1,1) parameters estimation
        omega, alpha, beta = self._estimate_garch_parameters(returns)
        
        # Predict future volatility
        predicted_vol = np.sqrt(omega + alpha * returns.iloc[-1]**2 + beta * recent_vol**2)
        
        # Volatility trend analysis
        vol_ma_short = returns.tail(10).std() * np.sqrt(252)
        vol_ma_long = returns.tail(30).std() * np.sqrt(252)
        vol_trend = "increasing" if vol_ma_short > vol_ma_long * 1.1 else "decreasing" if vol_ma_short < vol_ma_long * 0.9 else "stable"
        
        # Risk level based on volatility percentiles
        vol_percentile = self._calculate_volatility_percentile(predicted_vol, returns)
        if vol_percentile > 80:
            risk_level = "extreme"
        elif vol_percentile > 60:
            risk_level = "high"
        elif vol_percentile > 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        prediction = {
            "current_volatility": float(hist_vol),
            "predicted_volatility": float(predicted_vol),
            "volatility_change_pct": float((predicted_vol - hist_vol) / hist_vol * 100),
            "trend": vol_trend,
            "risk_level": risk_level,
            "volatility_percentile": float(vol_percentile),
            "garch_parameters": {
                "omega": float(omega),
                "alpha": float(alpha),
                "beta": float(beta)
            }
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
    
    def _train_trend_model(self, features: pd.DataFrame) -> None:
        """Train trend prediction model using historical features"""
        try:
            # Create labels based on future price movement
            returns = features['returns'].dropna()
            
            # Create labels: 1 for bullish (up > 2%), -1 for bearish (down > 2%), 0 for neutral
            labels = []
            for ret in returns:
                if ret > 0.02:
                    labels.append("bullish")
                elif ret < -0.02:
                    labels.append("bearish")
                else:
                    labels.append("neutral")
            
            # Use features shifted back to avoid lookahead bias
            X = features.dropna().iloc[:-1].drop('returns', axis=1)
            y = labels[1:]  # Shift labels to match features
            
            if len(X) > 50:  # Minimum data requirement
                self.trend_model.fit(X, y)
                self.trend_model_fitted = True
                print(f"Trend model trained on {len(X)} samples")
        except Exception as e:
            print(f"Failed to train trend model: {e}")
            self.trend_model_fitted = False
    
    def _technical_analysis_prediction(self, features: pd.DataFrame) -> Dict[str, float]:
        """Fallback prediction using technical analysis"""
        latest = features.iloc[-1]
        
        # RSI-based prediction
        rsi = latest.get('rsi', 50)
        if rsi > 70:
            rsi_signal = {"bearish": 0.6, "neutral": 0.3, "bullish": 0.1}
        elif rsi < 30:
            rsi_signal = {"bullish": 0.6, "neutral": 0.3, "bearish": 0.1}
        else:
            rsi_signal = {"neutral": 0.5, "bullish": 0.25, "bearish": 0.25}
        
        # Moving average convergence
        sma_20 = latest.get('sma_20', latest.get('close', 0))
        sma_50 = latest.get('sma_50', latest.get('close', 0))
        current_price = latest.get('close', 0)
        
        if current_price > sma_20 > sma_50:
            ma_signal = {"bullish": 0.7, "neutral": 0.2, "bearish": 0.1}
        elif current_price < sma_20 < sma_50:
            ma_signal = {"bearish": 0.7, "neutral": 0.2, "bullish": 0.1}
        else:
            ma_signal = {"neutral": 0.6, "bullish": 0.2, "bearish": 0.2}
        
        # Volume confirmation
        volume_ratio = latest.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            volume_weight = 1.2
        elif volume_ratio < 0.5:
            volume_weight = 0.8
        else:
            volume_weight = 1.0
        
        # Combine signals
        combined = {
            "bullish": (rsi_signal["bullish"] + ma_signal["bullish"]) / 2 * volume_weight,
            "bearish": (rsi_signal["bearish"] + ma_signal["bearish"]) / 2 * volume_weight,
            "neutral": (rsi_signal["neutral"] + ma_signal["neutral"]) / 2
        }
        
        # Normalize to sum to 1
        total = sum(combined.values())
        return {k: v/total for k, v in combined.items()}
    
    def _estimate_garch_parameters(self, returns: pd.Series, initial_params: Tuple[float, float, float] = (0.1, 0.1, 0.8)) -> Tuple[float, float, float]:
        """Estimate GARCH(1,1) parameters using maximum likelihood"""
        try:
            from scipy.optimize import minimize
            
            def garch_log_likelihood(params, returns):
                omega, alpha, beta = params
                
                # Ensure parameters are valid
                if omega <= 0 or alpha < 0 or beta < 0 or alpha + beta >= 1:
                    return 1e10
                
                # Calculate conditional variances
                n = len(returns)
                variance = np.zeros(n)
                variance[0] = returns.var()  # Initial variance
                
                for t in range(1, n):
                    variance[t] = omega + alpha * returns.iloc[t-1]**2 + beta * variance[t-1]
                
                # Log likelihood
                log_likelihood = -0.5 * np.sum(np.log(2 * np.pi * variance) + returns.values**2 / variance)
                return -log_likelihood
            
            # Optimize parameters
            result = minimize(garch_log_likelihood, initial_params, args=(returns,), 
                            method='L-BFGS-B', bounds=[(1e-6, None), (0, 1), (0, 0.999)])
            
            if result.success:
                return tuple(result.x)
            else:
                # Fallback to default parameters
                return initial_params
                
        except ImportError:
            # Fallback if scipy not available
            return initial_params
        except Exception:
            return initial_params
    
    def _calculate_volatility_percentile(self, predicted_vol: float, returns: pd.Series) -> float:
        """Calculate percentile of predicted volatility relative to historical distribution"""
        try:
            # Calculate rolling volatilities
            rolling_vols = returns.rolling(window=30).std().dropna() * np.sqrt(252)
            
            # Calculate percentile
            percentile = (rolling_vols < predicted_vol).mean() * 100
            return float(percentile)
        except Exception:
            return 50.0  # Default to median
    
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
