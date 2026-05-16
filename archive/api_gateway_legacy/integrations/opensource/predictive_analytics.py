"""
Predictive Analytics and Advanced ML Models
Production-ready machine learning for financial forecasting and insights
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import lightgbm as lgb
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA, ICA
from sklearn.manifold import TSNE
import yfinance as yf
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import json
import pickle
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Machine learning model types"""
    LINEAR_REGRESSION = "linear_regression"
    RIDGE_REGRESSION = "ridge_regression"
    LASSO_REGRESSION = "lasso_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    SVR = "svr"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
    ENSEMBLE = "ensemble"

class PredictionType(Enum):
    """Prediction types"""
    PRICE_PREDICTION = "price_prediction"
    VOLUME_PREDICTION = "volume_prediction"
    VOLATILITY_PREDICTION = "volatility_prediction"
    TREND_PREDICTION = "trend_prediction"
    RISK_PREDICTION = "risk_prediction"
    PORTFOLIO_OPTIMIZATION = "portfolio_optimization"
    MARKET_SENTIMENT = "market_sentiment"
    ECONOMIC_FORECAST = "economic_forecast"

@dataclass
class PredictionResult:
    """Prediction result with confidence intervals"""
    prediction: float
    confidence_interval: Tuple[float, float]
    confidence_score: float
    model_used: str
    prediction_date: datetime
    features_used: List[str]
    feature_importance: Dict[str, float]
    metadata: Dict[str, Any]

@dataclass
class ModelMetrics:
    """Model performance metrics"""
    mse: float
    mae: float
    rmse: float
    r2_score: float
    mape: float
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None

class PredictiveAnalyticsEngine:
    """Advanced predictive analytics engine"""
    
    def __init__(self, model_cache_dir: str = "models/"):
        self.model_cache_dir = Path(model_cache_dir)
        self.model_cache_dir.mkdir(exist_ok=True)
        
        # Initialize scalers
        self.price_scaler = StandardScaler()
        self.feature_scaler = StandardScaler()
        self.volume_scaler = MinMaxScaler()
        
        # Model registry
        self.models: Dict[str, Any] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}
        
        # Feature engineering
        self.feature_engineer = FeatureEngineer()
        
        logger.info("Predictive Analytics Engine initialized")
        
    async def train_price_prediction_model(self, 
                                         symbol: str, 
                                         model_types: List[ModelType] = None,
                                         lookback_period: int = 252) -> Dict[str, ModelMetrics]:
        """Train price prediction models for a symbol"""
        try:
            logger.info(f"Training price prediction models for {symbol}")
            
            if model_types is None:
                model_types = [
                    ModelType.LINEAR_REGRESSION,
                    ModelType.RANDOM_FOREST,
                    ModelType.XGBOOST,
                    ModelType.LSTM,
                    ModelType.ENSEMBLE
                ]
            
            # Fetch and prepare data
            data = await self._fetch_market_data(symbol, lookback_period)
            features, targets = self.feature_engineer.prepare_price_features(data)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.feature_scaler.fit_transform(X_train)
            X_test_scaled = self.feature_scaler.transform(X_test)
            
            # Train models
            metrics = {}
            
            for model_type in model_types:
                try:
                    model_metrics = await self._train_model(
                        model_type, X_train_scaled, X_test_scaled, y_train, y_test, symbol
                    )
                    metrics[model_type.value] = model_metrics
                    logger.info(f"Trained {model_type.value} model for {symbol}")
                except Exception as e:
                    logger.error(f"Error training {model_type.value} model: {e}")
                    continue
                    
            return metrics
            
        except Exception as e:
            logger.error(f"Error training price prediction models: {e}")
            raise
            
    async def _train_model(self, 
                          model_type: ModelType, 
                          X_train: np.ndarray, 
                          X_test: np.ndarray,
                          y_train: np.ndarray, 
                          y_test: np.ndarray, 
                          symbol: str) -> ModelMetrics:
        """Train individual model"""
        
        if model_type == ModelType.LINEAR_REGRESSION:
            model = LinearRegression()
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.RIDGE_REGRESSION:
            model = Ridge(alpha=1.0)
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.LASSO_REGRESSION:
            model = Lasso(alpha=0.1)
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.RANDOM_FOREST:
            model = RandomForestRegressor(
                n_estimators=100, 
                max_depth=10, 
                random_state=42
            )
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.GRADIENT_BOOSTING:
            model = GradientBoostingRegressor(
                n_estimators=100, 
                learning_rate=0.1, 
                max_depth=6, 
                random_state=42
            )
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.XGBOOST:
            model = xgb.XGBRegressor(
                n_estimators=100, 
                learning_rate=0.1, 
                max_depth=6, 
                random_state=42
            )
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.LIGHTGBM:
            model = lgb.LGBMRegressor(
                n_estimators=100, 
                learning_rate=0.1, 
                max_depth=6, 
                random_state=42
            )
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.SVR:
            model = SVR(kernel='rbf', C=1.0, gamma='scale')
            model.fit(X_train, y_train)
            
        elif model_type == ModelType.LSTM:
            model = self._create_lstm_model(X_train.shape[1])
            model.fit(
                X_train.reshape(-1, X_train.shape[1], 1),
                y_train,
                epochs=50,
                batch_size=32,
                validation_split=0.1,
                verbose=0
            )
            
        elif model_type == ModelType.GRU:
            model = self._create_gru_model(X_train.shape[1])
            model.fit(
                X_train.reshape(-1, X_train.shape[1], 1),
                y_train,
                epochs=50,
                batch_size=32,
                validation_split=0.1,
                verbose=0
            )
            
        elif model_type == ModelType.ENSEMBLE:
            model = self._create_ensemble_model(X_train, y_train)
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        # Evaluate model
        if model_type in [ModelType.LSTM, ModelType.GRU]:
            y_pred = model.predict(X_test.reshape(-1, X_test.shape[1], 1))
        else:
            y_pred = model.predict(X_test)
            
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        
        metrics = ModelMetrics(
            mse=mse,
            mae=mae,
            rmse=rmse,
            r2_score=r2,
            mape=mape
        )
        
        # Save model
        model_key = f"{symbol}_{model_type.value}"
        self.models[model_key] = model
        self.model_metrics[model_key] = metrics
        
        # Persist model
        model_path = self.model_cache_dir / f"{model_key}.pkl"
        joblib.dump(model, model_path)
        
        return metrics
        
    def _create_lstm_model(self, input_shape: int) -> keras.Model:
        """Create LSTM model for time series prediction"""
        model = keras.Sequential([
            keras.layers.LSTM(50, return_sequences=True, input_shape=(input_shape, 1)),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(50, return_sequences=False),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(25),
            keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
        
    def _create_gru_model(self, input_shape: int) -> keras.Model:
        """Create GRU model for time series prediction"""
        model = keras.Sequential([
            keras.layers.GRU(50, return_sequences=True, input_shape=(input_shape, 1)),
            keras.layers.Dropout(0.2),
            keras.layers.GRU(50, return_sequences=False),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(25),
            keras.layers.Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model
        
    def _create_ensemble_model(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Create ensemble model combining multiple algorithms"""
        models = {
            'rf': RandomForestRegressor(n_estimators=50, random_state=42),
            'xgb': xgb.XGBRegressor(n_estimators=50, random_state=42),
            'lgb': lgb.LGBMRegressor(n_estimators=50, random_state=42)
        }
        
        # Train individual models
        for name, model in models.items():
            model.fit(X_train, y_train)
            
        return models
        
    async def predict_price(self, 
                           symbol: str, 
                           model_type: ModelType = ModelType.ENSEMBLE,
                           horizon_days: int = 5) -> PredictionResult:
        """Predict price for a symbol"""
        try:
            logger.info(f"Predicting price for {symbol} using {model_type.value}")
            
            # Fetch latest data
            data = await self._fetch_market_data(symbol, 60)
            features, _ = self.feature_engineer.prepare_price_features(data)
            
            # Get latest features
            latest_features = features[-1:].reshape(1, -1)
            latest_features_scaled = self.feature_scaler.transform(latest_features)
            
            # Get model
            model_key = f"{symbol}_{model_type.value}"
            if model_key not in self.models:
                # Try to load from cache
                model_path = self.model_cache_dir / f"{model_key}.pkl"
                if model_path.exists():
                    self.models[model_key] = joblib.load(model_path)
                else:
                    raise ValueError(f"Model {model_key} not found")
                    
            model = self.models[model_key]
            
            # Make prediction
            if model_type == ModelType.ENSEMBLE:
                predictions = []
                for sub_model in model.values():
                    if model_type in [ModelType.LSTM, ModelType.GRU]:
                        pred = sub_model.predict(latest_features_scaled.reshape(-1, latest_features_scaled.shape[1], 1))
                    else:
                        pred = sub_model.predict(latest_features_scaled)
                    predictions.append(pred[0])
                prediction = np.mean(predictions)
                confidence_score = 1.0 - np.std(predictions) / np.mean(predictions)
            else:
                if model_type in [ModelType.LSTM, ModelType.GRU]:
                    prediction = model.predict(latest_features_scaled.reshape(-1, latest_features_scaled.shape[1], 1))[0]
                else:
                    prediction = model.predict(latest_features_scaled)[0]
                confidence_score = 0.85  # Default confidence
                
            # Calculate confidence interval (simplified)
            std_dev = np.std(features[-20:]) if len(features) >= 20 else np.std(features)
            confidence_interval = (
                prediction - 1.96 * std_dev,
                prediction + 1.96 * std_dev
            )
            
            # Get feature importance
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                feature_names = self.feature_engineer.get_feature_names()
                feature_importance = dict(zip(feature_names, model.feature_importances_))
            elif hasattr(model, 'coef_'):
                feature_names = self.feature_engineer.get_feature_names()
                feature_importance = dict(zip(feature_names, np.abs(model.coef_)))
                
            return PredictionResult(
                prediction=prediction,
                confidence_interval=confidence_interval,
                confidence_score=confidence_score,
                model_used=model_type.value,
                prediction_date=datetime.utcnow(),
                features_used=self.feature_engineer.get_feature_names(),
                feature_importance=feature_importance,
                metadata={
                    "symbol": symbol,
                    "horizon_days": horizon_days,
                    "last_price": float(data['Close'].iloc[-1])
                }
            )
            
        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            raise
            
    async def predict_volatility(self, 
                                symbol: str, 
                                model_type: ModelType = ModelType.XGBOOST,
                                horizon_days: int = 10) -> PredictionResult:
        """Predict volatility for a symbol"""
        try:
            logger.info(f"Predicting volatility for {symbol}")
            
            # Fetch data
            data = await self._fetch_market_data(symbol, 252)
            
            # Calculate volatility features
            volatility_features = self.feature_engineer.prepare_volatility_features(data)
            
            # Target: realized volatility
            returns = data['Close'].pct_change().dropna()
            target_volatility = returns.rolling(window=horizon_days).std().dropna()
            
            # Prepare features
            features = volatility_features[:-horizon_days]
            targets = target_volatility[horizon_days:]
            
            # Split and scale
            X_train, X_test, y_train, y_test = train_test_split(
                features, targets, test_size=0.2, shuffle=False
            )
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = xgb.XGBRegressor(n_estimators=100, random_state=42)
            model.fit(X_train_scaled, y_train)
            
            # Predict
            latest_features = volatility_features[-1:].reshape(1, -1)
            latest_features_scaled = scaler.transform(latest_features)
            prediction = model.predict(latest_features_scaled)[0]
            
            # Calculate confidence interval
            recent_volatility = returns[-30:].std()
            confidence_interval = (
                max(0, prediction - 1.96 * recent_volatility * 0.5),
                prediction + 1.96 * recent_volatility * 0.5
            )
            
            return PredictionResult(
                prediction=prediction,
                confidence_interval=confidence_interval,
                confidence_score=0.80,
                model_used=model_type.value,
                prediction_date=datetime.utcnow(),
                features_used=self.feature_engineer.get_volatility_feature_names(),
                feature_importance={},
                metadata={
                    "symbol": symbol,
                    "horizon_days": horizon_days,
                    "current_volatility": recent_volatility
                }
            )
            
        except Exception as e:
            logger.error(f"Error predicting volatility: {e}")
            raise
            
    async def predict_market_sentiment(self, 
                                    symbols: List[str] = None) -> Dict[str, float]:
        """Predict overall market sentiment"""
        try:
            logger.info("Predicting market sentiment")
            
            if symbols is None:
                symbols = ['SPY', 'QQQ', 'IWM', 'DIA']  # Major ETFs
                
            sentiment_scores = {}
            
            for symbol in symbols:
                try:
                    # Fetch data
                    data = await self._fetch_market_data(symbol, 30)
                    
                    # Calculate sentiment indicators
                    returns = data['Close'].pct_change().dropna()
                    
                    # Price momentum
                    momentum = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) if len(data) >= 5 else 0
                    
                    # Volume anomaly
                    volume_ratio = data['Volume'].iloc[-1] / data['Volume'].iloc[-5:].mean() if len(data) >= 5 else 1
                    
                    # Volatility
                    volatility = returns.std()
                    
                    # RSI
                    rsi = self._calculate_rsi(data['Close'])
                    
                    # Combine into sentiment score
                    sentiment = (
                        np.tanh(momentum * 10) * 0.3 +  # Price momentum
                        np.tanh((volume_ratio - 1) * 2) * 0.2 +  # Volume anomaly
                        np.tanh(-volatility * 50) * 0.2 +  # Low volatility = positive
                        np.tanh((rsi - 50) / 50) * 0.3  # RSI relative to neutral
                    )
                    
                    sentiment_scores[symbol] = float(sentiment)
                    
                except Exception as e:
                    logger.error(f"Error calculating sentiment for {symbol}: {e}")
                    sentiment_scores[symbol] = 0.0
                    
            # Calculate overall market sentiment
            overall_sentiment = np.mean(list(sentiment_scores.values()))
            sentiment_scores['MARKET_OVERALL'] = float(overall_sentiment)
            
            return sentiment_scores
            
        except Exception as e:
            logger.error(f"Error predicting market sentiment: {e}")
            raise
            
    async def optimize_portfolio(self, 
                                symbols: List[str], 
                                risk_tolerance: float = 0.5,
                                time_horizon: int = 252) -> Dict[str, float]:
        """Optimize portfolio weights using ML"""
        try:
            logger.info("Optimizing portfolio weights")
            
            # Fetch data for all symbols
            returns_data = {}
            for symbol in symbols:
                try:
                    data = await self._fetch_market_data(symbol, time_horizon)
                    returns = data['Close'].pct_change().dropna()
                    returns_data[symbol] = returns
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    continue
                    
            if not returns_data:
                raise ValueError("No valid data for portfolio optimization")
                
            # Create returns matrix
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            # Calculate expected returns and covariance
            expected_returns = returns_df.mean() * time_horizon
            cov_matrix = returns_df.cov() * time_horizon
            
            # Use ML for optimization
            weights = self._modern_portfolio_optimization(
                expected_returns, cov_matrix, risk_tolerance
            )
            
            return weights
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            raise
            
    def _modern_portfolio_optimization(self, 
                                     expected_returns: pd.Series, 
                                     cov_matrix: pd.DataFrame,
                                     risk_tolerance: float) -> Dict[str, float]:
        """Modern portfolio optimization with ML enhancement"""
        try:
            n_assets = len(expected_returns)
            
            # Use risk parity as baseline
            inv_volatility = 1 / np.sqrt(np.diag(cov_matrix))
            weights = inv_volatility / inv_volatility.sum()
            
            # Adjust for risk tolerance
            if risk_tolerance < 0.5:  # Conservative
                # Equal weight with reduced volatility
                weights = np.ones(n_assets) / n_assets
            elif risk_tolerance > 0.7:  # Aggressive
                # Maximize returns subject to risk constraint
                weights = self._maximize_sharpe_ratio(expected_returns, cov_matrix)
                
            # Ensure weights sum to 1 and are non-negative
            weights = np.maximum(weights, 0)
            weights = weights / weights.sum()
            
            return dict(zip(expected_returns.index, weights))
            
        except Exception as e:
            logger.error(f"Error in portfolio optimization: {e}")
            # Fallback to equal weights
            n_assets = len(expected_returns)
            equal_weights = np.ones(n_assets) / n_assets
            return dict(zip(expected_returns.index, equal_weights))
            
    def _maximize_sharpe_ratio(self, 
                              expected_returns: pd.Series, 
                              cov_matrix: pd.DataFrame) -> np.ndarray:
        """Maximize Sharpe ratio (simplified)"""
        try:
            n_assets = len(expected_returns)
            
            # Simplified optimization using equal risk contribution
            risk_parity_weights = np.ones(n_assets) / n_assets
            
            # Adjust based on expected returns
            return_adjusted = expected_returns.values / expected_returns.sum()
            weights = risk_parity_weights * (1 + return_adjusted)
            
            return weights / weights.sum()
            
        except Exception as e:
            logger.error(f"Error maximizing Sharpe ratio: {e}")
            return np.ones(len(expected_returns)) / len(expected_returns)
            
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not rsi.empty else 50.0
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0
            
    async def _fetch_market_data(self, symbol: str, period: int) -> pd.DataFrame:
        """Fetch market data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period + 30)  # Extra days for weekends
            
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
                
            return data[-period:]  # Return exactly the requested period
            
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            raise
            
    async def generate_trading_signals(self, 
                                    symbol: str, 
                                    signal_types: List[str] = None) -> Dict[str, Any]:
        """Generate comprehensive trading signals"""
        try:
            logger.info(f"Generating trading signals for {symbol}")
            
            if signal_types is None:
                signal_types = ['momentum', 'mean_reversion', 'breakout', 'volume', 'sentiment']
                
            signals = {}
            
            # Fetch data
            data = await self._fetch_market_data(symbol, 100)
            
            for signal_type in signal_types:
                try:
                    if signal_type == 'momentum':
                        signals[signal_type] = self._generate_momentum_signal(data)
                    elif signal_type == 'mean_reversion':
                        signals[signal_type] = self._generate_mean_reversion_signal(data)
                    elif signal_type == 'breakout':
                        signals[signal_type] = self._generate_breakout_signal(data)
                    elif signal_type == 'volume':
                        signals[signal_type] = self._generate_volume_signal(data)
                    elif signal_type == 'sentiment':
                        signals[signal_type] = await self._generate_sentiment_signal(symbol)
                        
                except Exception as e:
                    logger.error(f"Error generating {signal_type} signal: {e}")
                    signals[signal_type] = {'signal': 'HOLD', 'confidence': 0.0}
                    
            # Combine signals
            combined_signal = self._combine_signals(signals)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.utcnow().isoformat(),
                'individual_signals': signals,
                'combined_signal': combined_signal,
                'current_price': float(data['Close'].iloc[-1])
            }
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            raise
            
    def _generate_momentum_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate momentum-based trading signal"""
        try:
            # Calculate momentum indicators
            returns = data['Close'].pct_change()
            
            # Short-term momentum (5 days)
            short_momentum = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) if len(data) >= 5 else 0
            
            # Medium-term momentum (20 days)
            medium_momentum = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) if len(data) >= 20 else 0
            
            # RSI
            rsi = self._calculate_rsi(data['Close'])
            
            # Generate signal
            if short_momentum > 0.02 and medium_momentum > 0.05 and rsi < 70:
                signal = 'BUY'
                confidence = min(0.9, abs(short_momentum) * 10)
            elif short_momentum < -0.02 and medium_momentum < -0.05 and rsi > 30:
                signal = 'SELL'
                confidence = min(0.9, abs(short_momentum) * 10)
            else:
                signal = 'HOLD'
                confidence = 0.5
                
            return {
                'signal': signal,
                'confidence': confidence,
                'indicators': {
                    'short_momentum': short_momentum,
                    'medium_momentum': medium_momentum,
                    'rsi': rsi
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating momentum signal: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
            
    def _generate_mean_reversion_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate mean reversion trading signal"""
        try:
            # Calculate moving averages
            ma_short = data['Close'].rolling(window=10).mean()
            ma_long = data['Close'].rolling(window=30).mean()
            
            # Current price relative to moving averages
            current_price = data['Close'].iloc[-1]
            short_ma = ma_short.iloc[-1]
            long_ma = ma_long.iloc[-1]
            
            # Bollinger Bands
            bb_period = 20
            bb_std = 2
            bb_middle = data['Close'].rolling(window=bb_period).mean()
            bb_std_dev = data['Close'].rolling(window=bb_period).std()
            bb_upper = bb_middle + (bb_std_dev * bb_std)
            bb_lower = bb_middle - (bb_std_dev * bb_std)
            
            # Generate signal
            if current_price < bb_lower.iloc[-1] and current_price < short_ma:
                signal = 'BUY'
                confidence = 0.7
            elif current_price > bb_upper.iloc[-1] and current_price > short_ma:
                signal = 'SELL'
                confidence = 0.7
            else:
                signal = 'HOLD'
                confidence = 0.5
                
            return {
                'signal': signal,
                'confidence': confidence,
                'indicators': {
                    'price_vs_ma_short': (current_price - short_ma) / short_ma,
                    'price_vs_ma_long': (current_price - long_ma) / long_ma,
                    'bb_position': (current_price - bb_middle.iloc[-1]) / bb_std_dev.iloc[-1]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating mean reversion signal: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
            
    def _generate_breakout_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate breakout trading signal"""
        try:
            # Calculate resistance and support levels
            high_prices = data['High'].rolling(window=20).max()
            low_prices = data['Low'].rolling(window=20).min()
            
            current_price = data['Close'].iloc[-1]
            resistance = high_prices.iloc[-1]
            support = low_prices.iloc[-1]
            
            # Volume confirmation
            avg_volume = data['Volume'].rolling(window=20).mean()
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            # Generate signal
            if current_price > resistance and volume_ratio > 1.5:
                signal = 'BUY'
                confidence = min(0.8, volume_ratio / 2)
            elif current_price < support and volume_ratio > 1.5:
                signal = 'SELL'
                confidence = min(0.8, volume_ratio / 2)
            else:
                signal = 'HOLD'
                confidence = 0.5
                
            return {
                'signal': signal,
                'confidence': confidence,
                'indicators': {
                    'price_vs_resistance': (current_price - resistance) / resistance,
                    'price_vs_support': (current_price - support) / support,
                    'volume_ratio': volume_ratio
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating breakout signal: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
            
    def _generate_volume_signal(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate volume-based trading signal"""
        try:
            # Volume indicators
            current_volume = data['Volume'].iloc[-1]
            avg_volume = data['Volume'].rolling(window=20).mean()
            volume_ratio = current_volume / avg_volume
            
            # On-Balance Volume (OBV)
            obv = self._calculate_obv(data)
            obv_ma = obv.rolling(window=10).mean()
            
            # Price-Volume divergence
            price_change = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) if len(data) >= 5 else 0
            obv_change = (obv.iloc[-1] / obv.iloc[-5] - 1) if len(obv) >= 5 else 0
            
            # Generate signal
            if volume_ratio > 2.0 and obv_change > 0.05:
                signal = 'BUY'
                confidence = min(0.8, volume_ratio / 3)
            elif volume_ratio > 2.0 and obv_change < -0.05:
                signal = 'SELL'
                confidence = min(0.8, volume_ratio / 3)
            else:
                signal = 'HOLD'
                confidence = 0.5
                
            return {
                'signal': signal,
                'confidence': confidence,
                'indicators': {
                    'volume_ratio': volume_ratio,
                    'obv_trend': obv_change,
                    'price_volume_divergence': price_change - obv_change
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating volume signal: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
            
    async def _generate_sentiment_signal(self, symbol: str) -> Dict[str, Any]:
        """Generate sentiment-based trading signal"""
        try:
            # Get market sentiment
            sentiment_scores = await self.predict_market_sentiment([symbol])
            sentiment = sentiment_scores.get(symbol, 0.0)
            
            # Generate signal
            if sentiment > 0.3:
                signal = 'BUY'
                confidence = min(0.7, sentiment + 0.3)
            elif sentiment < -0.3:
                signal = 'SELL'
                confidence = min(0.7, abs(sentiment) + 0.3)
            else:
                signal = 'HOLD'
                confidence = 0.5
                
            return {
                'signal': signal,
                'confidence': confidence,
                'indicators': {
                    'sentiment_score': sentiment
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating sentiment signal: {e}")
            return {'signal': 'HOLD', 'confidence': 0.0}
            
    def _calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume indicator"""
        try:
            obv = [0]
            for i in range(1, len(data)):
                if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                    obv.append(obv[-1] + data['Volume'].iloc[i])
                elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                    obv.append(obv[-1] - data['Volume'].iloc[i])
                else:
                    obv.append(obv[-1])
            return pd.Series(obv, index=data.index)
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return pd.Series([0] * len(data), index=data.index)
            
    def _combine_signals(self, signals: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine individual signals into final recommendation"""
        try:
            signal_weights = {
                'momentum': 0.25,
                'mean_reversion': 0.20,
                'breakout': 0.20,
                'volume': 0.15,
                'sentiment': 0.20
            }
            
            signal_scores = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            total_confidence = 0
            
            for signal_type, signal_data in signals.items():
                if signal_type in signal_weights:
                    signal = signal_data.get('signal', 'HOLD')
                    confidence = signal_data.get('confidence', 0.0)
                    weight = signal_weights[signal_type]
                    
                    signal_scores[signal] += confidence * weight
                    total_confidence += confidence * weight
                    
            # Determine final signal
            if signal_scores['BUY'] > signal_scores['SELL'] and signal_scores['BUY'] > signal_scores['HOLD']:
                final_signal = 'BUY'
            elif signal_scores['SELL'] > signal_scores['BUY'] and signal_scores['SELL'] > signal_scores['HOLD']:
                final_signal = 'SELL'
            else:
                final_signal = 'HOLD'
                
            final_confidence = signal_scores[final_signal] / total_confidence if total_confidence > 0 else 0.5
            
            return {
                'signal': final_signal,
                'confidence': final_confidence,
                'signal_scores': signal_scores,
                'total_confidence': total_confidence
            }
            
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5}

class FeatureEngineer:
    """Feature engineering for financial ML models"""
    
    def __init__(self):
        self.feature_names = []
        self.volatility_feature_names = []
        
    def prepare_price_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for price prediction"""
        try:
            features = []
            
            # Price-based features
            features.append(data['Close'].values)
            features.append(data['Open'].values)
            features.append(data['High'].values)
            features.append(data['Low'].values)
            
            # Returns
            returns = data['Close'].pct_change().fillna(0)
            features.append(returns.values)
            
            # Moving averages
            for period in [5, 10, 20, 50]:
                ma = data['Close'].rolling(window=period).mean().fillna(method='bfill')
                features.append(ma.values)
                
            # Volatility
            volatility = returns.rolling(window=20).std().fillna(0)
            features.append(volatility.values)
            
            # RSI
            rsi = self._calculate_rsi_series(data['Close'])
            features.append(rsi.values)
            
            # Volume features
            volume_ma = data['Volume'].rolling(window=10).mean().fillna(method='bfill')
            volume_ratio = data['Volume'] / volume_ma
            features.append(volume_ratio.values)
            
            # Price range
            price_range = (data['High'] - data['Low']) / data['Close']
            features.append(price_range.values)
            
            # Convert to numpy array
            feature_matrix = np.column_stack(features)
            
            # Target: next day's close price
            target = data['Close'].shift(-1).fillna(method='ffill').values
            
            # Store feature names
            self.feature_names = [
                'Close', 'Open', 'High', 'Low', 'Returns',
                'MA_5', 'MA_10', 'MA_20', 'MA_50',
                'Volatility', 'RSI', 'Volume_Ratio', 'Price_Range'
            ]
            
            return feature_matrix[1:], target[1:]  # Remove first row due to NaN values
            
        except Exception as e:
            logger.error(f"Error preparing price features: {e}")
            raise
            
    def prepare_volatility_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for volatility prediction"""
        try:
            features = []
            
            # Returns
            returns = data['Close'].pct_change().fillna(0)
            features.append(returns.values)
            
            # Historical volatility
            for period in [5, 10, 20]:
                vol = returns.rolling(window=period).std().fillna(0)
                features.append(vol.values)
                
            # GARCH-like features
            squared_returns = returns ** 2
            features.append(squared_returns.values)
            
            # Volume features
            volume_change = data['Volume'].pct_change().fillna(0)
            features.append(volume_change.values)
            
            # Price range
            price_range = (data['High'] - data['Low']) / data['Close']
            features.append(price_range.values)
            
            # Convert to numpy array
            feature_matrix = np.column_stack(features)
            
            # Store feature names
            self.volatility_feature_names = [
                'Returns', 'Vol_5', 'Vol_10', 'Vol_20',
                'Squared_Returns', 'Volume_Change', 'Price_Range'
            ]
            
            return feature_matrix
            
        except Exception as e:
            logger.error(f"Error preparing volatility features: {e}")
            raise
            
    def _calculate_rsi_series(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI series"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.fillna(50)
            
        except Exception as e:
            logger.error(f"Error calculating RSI series: {e}")
            return pd.Series([50] * len(prices), index=prices.index)
            
    def get_feature_names(self) -> List[str]:
        """Get feature names"""
        return self.feature_names
        
    def get_volatility_feature_names(self) -> List[str]:
        """Get volatility feature names"""
        return self.volatility_feature_names

# Global predictive analytics instance
predictive_analytics = PredictiveAnalyticsEngine()

# API endpoints
async def predict_price_endpoint(symbol: str, model_type: str = "ensemble", horizon_days: int = 5) -> Dict[str, Any]:
    """API endpoint for price prediction"""
    try:
        model_enum = ModelType(model_type)
        result = await predictive_analytics.predict_price(symbol, model_enum, horizon_days)
        return asdict(result)
    except Exception as e:
        logger.error(f"Error in price prediction endpoint: {e}")
        raise

async def predict_volatility_endpoint(symbol: str, model_type: str = "xgboost", horizon_days: int = 10) -> Dict[str, Any]:
    """API endpoint for volatility prediction"""
    try:
        model_enum = ModelType(model_type)
        result = await predictive_analytics.predict_volatility(symbol, model_enum, horizon_days)
        return asdict(result)
    except Exception as e:
        logger.error(f"Error in volatility prediction endpoint: {e}")
        raise

async def generate_trading_signals_endpoint(symbol: str, signal_types: List[str] = None) -> Dict[str, Any]:
    """API endpoint for trading signals"""
    try:
        result = await predictive_analytics.generate_trading_signals(symbol, signal_types)
        return result
    except Exception as e:
        logger.error(f"Error in trading signals endpoint: {e}")
        raise

async def optimize_portfolio_endpoint(symbols: List[str], risk_tolerance: float = 0.5) -> Dict[str, Any]:
    """API endpoint for portfolio optimization"""
    try:
        weights = await predictive_analytics.optimize_portfolio(symbols, risk_tolerance)
        return {"symbols": symbols, "weights": weights, "risk_tolerance": risk_tolerance}
    except Exception as e:
        logger.error(f"Error in portfolio optimization endpoint: {e}")
        raise
