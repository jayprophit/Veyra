"""
Financial Master ML Prediction Engine
Machine Learning models for price prediction and risk assessment
Version: 1.0
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ML_Prediction_Engine')


class PricePredictionModel:
    """ML model for predicting asset prices"""
    
    def __init__(self, model_type: str = 'ensemble'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create technical indicator features"""
        features = df.copy()
        
        # Price-based features
        features['returns'] = features['price'].pct_change()
        features['log_returns'] = np.log(features['price'] / features['price'].shift(1))
        
        # Moving averages
        features['ma_7'] = features['price'].rolling(7).mean()
        features['ma_30'] = features['price'].rolling(30).mean()
        features['ma_ratio'] = features['ma_7'] / features['ma_30']
        
        # Volatility
        features['volatility_7'] = features['returns'].rolling(7).std()
        features['volatility_30'] = features['returns'].rolling(30).std()
        
        # Price momentum
        features['momentum_7'] = features['price'] / features['price'].shift(7) - 1
        features['momentum_30'] = features['price'] / features['price'].shift(30) - 1
        
        # RSI calculation
        delta = features['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        features['bb_middle'] = features['price'].rolling(20).mean()
        bb_std = features['price'].rolling(20).std()
        features['bb_upper'] = features['bb_middle'] + (bb_std * 2)
        features['bb_lower'] = features['bb_middle'] - (bb_std * 2)
        features['bb_position'] = (features['price'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
        
        # Volume features (if available)
        if 'volume' in features.columns:
            features['volume_ma'] = features['volume'].rolling(20).mean()
            features['volume_ratio'] = features['volume'] / features['volume_ma']
        
        # Time features
        features['day_of_week'] = pd.to_datetime(features.index).dayofweek
        features['month'] = pd.to_datetime(features.index).month
        
        # Drop NaN rows from rolling calculations
        features = features.dropna()
        
        return features
    
    def train(self, df: pd.DataFrame, target_col: str = 'price', 
              forecast_horizon: int = 7, test_size: float = 0.2) -> Dict:
        """Train the prediction model"""
        
        # Prepare features
        features_df = self.prepare_features(df)
        
        # Create target (future price change)
        features_df['target'] = features_df['price'].shift(-forecast_horizon) / features_df['price'] - 1
        features_df = features_df.dropna()
        
        # Feature columns
        feature_cols = [c for c in features_df.columns if c not in ['price', 'target', 'volume']]
        X = features_df[feature_cols]
        y = features_df['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False  # Time series - no shuffle
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if self.model_type == 'ensemble':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        elif self.model_type == 'rf':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            self.model = LinearRegression()
        
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
            'directional_accuracy': np.mean((y_test > 0) == (y_pred > 0)),
            'feature_importance': dict(zip(feature_cols, 
                                         self.model.feature_importances_ if hasattr(self.model, 'feature_importances_') else []))
        }
        
        logger.info(f"Model trained. R²: {metrics['r2']:.3f}, Directional Acc: {metrics['directional_accuracy']:.1%}")
        
        return metrics
    
    def predict(self, current_data: pd.DataFrame) -> Dict:
        """Make prediction for next period"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Prepare features
        features_df = self.prepare_features(current_data)
        latest = features_df.iloc[-1:]
        
        feature_cols = [c for c in latest.columns if c not in ['price', 'target', 'volume']]
        X = latest[feature_cols]
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        confidence = self._calculate_confidence(X_scaled)
        
        current_price = current_data['price'].iloc[-1]
        predicted_price = current_price * (1 + prediction)
        
        return {
            'predicted_return': prediction,
            'predicted_price': predicted_price,
            'current_price': current_price,
            'confidence': confidence,
            'direction': 'UP' if prediction > 0 else 'DOWN',
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate prediction confidence"""
        if hasattr(self.model, 'estimators_'):
            # For tree-based models, use variance across trees
            predictions = [tree.predict(X)[0] for tree in self.model.estimators_]
            variance = np.var(predictions)
            confidence = max(0, 1 - variance)
        else:
            confidence = 0.5
        return confidence


class RiskAssessmentModel:
    """Risk assessment and portfolio optimization"""
    
    def __init__(self):
        self.var_confidence = 0.95
        
    def calculate_var(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        return np.percentile(returns.dropna(), (1 - confidence) * 100)
    
    def calculate_cvar(self, returns: pd.Series, confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self.calculate_var(returns, confidence)
        return returns[returns <= var].mean()
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.03) -> float:
        """Calculate annualized Sharpe ratio"""
        excess_returns = returns - risk_free_rate / 252  # Daily
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    
    def calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        rolling_max = prices.expanding().max()
        drawdown = (prices - rolling_max) / rolling_max
        return drawdown.min()
    
    def assess_portfolio_risk(self, portfolio_data: Dict[str, pd.Series]) -> Dict:
        """Assess risk for entire portfolio"""
        results = {}
        
        for asset, prices in portfolio_data.items():
            returns = prices.pct_change().dropna()
            
            results[asset] = {
                'volatility_annual': returns.std() * np.sqrt(252),
                'var_95': self.calculate_var(returns, 0.95),
                'cvar_95': self.calculate_cvar(returns, 0.95),
                'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                'max_drawdown': self.calculate_max_drawdown(prices),
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'risk_level': self._categorize_risk(returns)
            }
        
        return results
    
    def _categorize_risk(self, returns: pd.Series) -> str:
        """Categorize risk level"""
        volatility = returns.std() * np.sqrt(252)
        
        if volatility < 0.15:
            return 'LOW'
        elif volatility < 0.30:
            return 'MEDIUM'
        elif volatility < 0.50:
            return 'HIGH'
        else:
            return 'CRITICAL'
    
    def optimize_allocation(self, 
                          expected_returns: Dict[str, float],
                          cov_matrix: pd.DataFrame,
                          risk_tolerance: str = 'medium') -> Dict:
        """Simple portfolio optimization"""
        assets = list(expected_returns.keys())
        n = len(assets)
        
        # Risk tolerance multipliers
        risk_multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0
        }
        multiplier = risk_multipliers.get(risk_tolerance, 1.0)
        
        # Simplified optimization: inverse volatility weighting
        volatilities = np.sqrt(np.diag(cov_matrix.values))
        inv_vol = 1 / volatilities
        weights = inv_vol / inv_vol.sum()
        
        # Adjust based on expected returns
        adjusted_weights = weights * (1 + np.array(list(expected_returns.values())) * multiplier)
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        return {
            'optimal_weights': dict(zip(assets, adjusted_weights)),
            'expected_return': sum(w * expected_returns[a] for a, w in zip(assets, adjusted_weights)),
            'risk_tolerance': risk_tolerance
        }


class AutomatedTradingSignals:
    """Generate automated trading signals"""
    
    def __init__(self):
        self.price_model = PricePredictionModel('ensemble')
        self.risk_model = RiskAssessmentModel()
        
    def generate_signal(self, 
                       price_data: pd.DataFrame,
                       position_size: float,
                       current_allocation: float,
                       target_allocation: float) -> Dict:
        """Generate comprehensive trading signal"""
        
        # Train model if not already trained
        if not self.price_model.is_trained:
            try:
                self.price_model.train(price_data)
            except Exception as e:
                logger.warning(f"Could not train model: {e}")
        
        # Get prediction
        try:
            prediction = self.price_model.predict(price_data)
        except:
            prediction = {'direction': 'NEUTRAL', 'confidence': 0}
        
        # Calculate risk metrics
        returns = price_data['price'].pct_change().dropna()
        var_95 = self.risk_model.calculate_var(returns)
        
        # Determine action
        allocation_diff = current_allocation - target_allocation
        
        if prediction['direction'] == 'UP' and prediction['confidence'] > 0.6:
            if allocation_diff < -0.05:  # Underweight
                action = 'BUY'
                strength = 'STRONG' if prediction['confidence'] > 0.8 else 'MODERATE'
            else:
                action = 'HOLD'
                strength = 'NEUTRAL'
        elif prediction['direction'] == 'DOWN' and prediction['confidence'] > 0.6:
            if allocation_diff > 0.05:  # Overweight
                action = 'SELL'
                strength = 'STRONG' if prediction['confidence'] > 0.8 else 'MODERATE'
            else:
                action = 'HOLD'
                strength = 'NEUTRAL'
        else:
            action = 'HOLD'
            strength = 'NEUTRAL'
        
        # Risk check
        if var_95 < -0.05:  # >5% daily VaR
            if action == 'BUY':
                strength = 'REDUCED_DUE_TO_RISK'
            action = 'HOLD' if action == 'BUY' else action
        
        return {
            'action': action,
            'strength': strength,
            'predicted_return': prediction.get('predicted_return', 0),
            'confidence': prediction.get('confidence', 0),
            'var_95': var_95,
            'current_allocation': current_allocation,
            'target_allocation': target_allocation,
            'rebalance_needed': abs(allocation_diff) > 0.05,
            'timestamp': datetime.now().isoformat()
        }
    
    def batch_generate_signals(self, portfolio_data: Dict[str, pd.DataFrame],
                              current_allocations: Dict[str, float],
                              target_allocations: Dict[str, float]) -> Dict[str, Dict]:
        """Generate signals for entire portfolio"""
        signals = {}
        
        for asset, data in portfolio_data.items():
            signals[asset] = self.generate_signal(
                data,
                position_size=current_allocations.get(asset, 0),
                current_allocation=current_allocations.get(asset, 0),
                target_allocation=target_allocations.get(asset, 0.20)
            )
        
        return signals


class MLEngineManager:
    """Central manager for all ML components"""
    
    def __init__(self):
        self.price_predictor = PricePredictionModel()
        self.risk_assessor = RiskAssessmentModel()
        self.signal_generator = AutomatedTradingSignals()
        self.models_trained = {}
        
    def train_all_models(self, historical_data: Dict[str, pd.DataFrame]) -> Dict:
        """Train models for all assets"""
        results = {}
        
        for asset, data in historical_data.items():
            try:
                predictor = PricePredictionModel()
                metrics = predictor.train(data)
                self.models_trained[asset] = predictor
                results[asset] = {'status': 'success', 'metrics': metrics}
                logger.info(f"Trained model for {asset}: R²={metrics['r2']:.3f}")
            except Exception as e:
                results[asset] = {'status': 'error', 'message': str(e)}
                logger.error(f"Failed to train model for {asset}: {e}")
        
        return results
    
    def get_portfolio_assessment(self, portfolio_data: Dict[str, pd.DataFrame]) -> Dict:
        """Get comprehensive portfolio risk assessment"""
        price_series = {k: v['price'] for k, v in portfolio_data.items()}
        return self.risk_assessor.assess_portfolio_risk(price_series)
    
    def generate_all_signals(self, 
                           portfolio_data: Dict[str, pd.DataFrame],
                           allocations: Dict[str, float]) -> Dict:
        """Generate signals for entire portfolio"""
        
        # Default target allocations
        targets = {'BTC': 0.35, 'VWRP': 0.25, 'GOLD': 0.10, 'LISA': 0.20, 'ETH': 0.10}
        
        return self.signal_generator.batch_generate_signals(
            portfolio_data, allocations, targets
        )


# Example usage and testing
def example_usage():
    """Demonstrate ML engine capabilities"""
    
    # Create synthetic price data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', periods=365, freq='D')
    
    # Generate synthetic data for multiple assets
    assets = {}
    for asset in ['BTC', 'ETH', 'VWRP']:
        trend = np.linspace(100, 150, 365) if asset != 'BTC' else np.linspace(30000, 45000, 365)
        noise = np.random.normal(0, trend * 0.02, 365)
        prices = trend + noise
        
        assets[asset] = pd.DataFrame({
            'price': prices,
            'volume': np.random.normal(1000000, 200000, 365)
        }, index=dates)
    
    # Initialize ML engine
    ml_engine = MLEngineManager()
    
    # Train models
    print("\n=== Training ML Models ===")
    training_results = ml_engine.train_all_models(assets)
    for asset, result in training_results.items():
        if result['status'] == 'success':
            print(f"{asset}: R² = {result['metrics']['r2']:.3f}")
    
    # Risk assessment
    print("\n=== Portfolio Risk Assessment ===")
    risk_metrics = ml_engine.get_portfolio_assessment(assets)
    for asset, metrics in risk_metrics.items():
        print(f"{asset}: Vol={metrics['volatility_annual']:.1%}, Sharpe={metrics['sharpe_ratio']:.2f}, Risk={metrics['risk_level']}")
    
    # Generate signals
    print("\n=== Trading Signals ===")
    current_allocations = {'BTC': 0.40, 'ETH': 0.15, 'VWRP': 0.20, 'GOLD': 0.05, 'LISA': 0.20}
    signals = ml_engine.generate_all_signals(assets, current_allocations)
    
    for asset, signal in signals.items():
        if asset in ['BTC', 'ETH', 'VWRP']:
            print(f"{asset}: {signal['action']} (Strength: {signal['strength']}, Confidence: {signal['confidence']:.1%})")
    
    return ml_engine


if __name__ == "__main__":
    ml_engine = example_usage()
