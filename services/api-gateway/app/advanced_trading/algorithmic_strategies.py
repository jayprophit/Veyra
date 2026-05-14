"""
Algorithmic Trading Strategies
===========================
Advanced algorithmic trading strategies with machine learning integration
"""

import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import talib

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Algorithmic strategy types"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    PAIR_TRADING = "pair_trading"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    MARKET_MAKING = "market_making"
    SENTIMENT = "sentiment"
    ML_PREDICTION = "ml_prediction"


@dataclass
class StrategySignal:
    """Trading signal from strategy"""
    strategy_name: str
    symbol: str
    action: str  # buy/sell/hold
    confidence: float
    price: Optional[float]
    quantity: float
    timestamp: datetime
    stop_loss: Optional[float]
    take_profit: Optional[float]
    holding_period: Optional[timedelta]
    metadata: Dict[str, Any]


class MomentumStrategy:
    """Momentum-based trading strategy"""
    
    def __init__(self, lookback_period: int = 20, threshold: float = 0.02):
        self.lookback_period = lookback_period
        self.threshold = threshold
        self.position = None
        
    async def generate_signal(self, data: pd.DataFrame) -> Optional[StrategySignal]:
        """Generate momentum trading signal"""
        try:
            if len(data) < self.lookback_period:
                return None
                
            # Calculate momentum indicators
            data['returns'] = data['close'].pct_change()
            data['momentum'] = data['close'] / data['close'].shift(self.lookback_period) - 1
            
            # Calculate RSI
            data['rsi'] = talib.RSI(data['close'].values, timeperiod=14)
            
            # Generate signal
            latest_momentum = data['momentum'].iloc[-1]
            latest_rsi = data['rsi'].iloc[-1]
            current_price = data['close'].iloc[-1]
            
            if latest_momentum > self.threshold and latest_rsi < 70:
                return StrategySignal(
                    strategy_name="Momentum",
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action="buy",
                    confidence=min(abs(latest_momentum) * 100, 95),
                    price=current_price,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price * 0.95,
                    take_profit=current_price * 1.10,
                    holding_period=timedelta(days=5),
                    metadata={
                        "momentum": latest_momentum,
                        "rsi": latest_rsi
                    }
                )
            elif latest_momentum < -self.threshold and latest_rsi > 30:
                return StrategySignal(
                    strategy_name="Momentum",
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action="sell",
                    confidence=min(abs(latest_momentum) * 100, 95),
                    price=current_price,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price * 1.05,
                    take_profit=current_price * 0.90,
                    holding_period=timedelta(days=5),
                    metadata={
                        "momentum": latest_momentum,
                        "rsi": latest_rsi
                    }
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error in momentum strategy: {e}")
            return None


class MeanReversionStrategy:
    """Mean reversion trading strategy"""
    
    def __init__(self, lookback_period: int = 20, std_dev_threshold: float = 2.0):
        self.lookback_period = lookback_period
        self.std_dev_threshold = std_dev_threshold
        
    async def generate_signal(self, data: pd.DataFrame) -> Optional[StrategySignal]:
        """Generate mean reversion signal"""
        try:
            if len(data) < self.lookback_period:
                return None
                
            # Calculate mean reversion indicators
            data['mean'] = data['close'].rolling(window=self.lookback_period).mean()
            data['std'] = data['close'].rolling(window=self.lookback_period).std()
            data['z_score'] = (data['close'] - data['mean']) / data['std']
            
            latest_z_score = data['z_score'].iloc[-1]
            current_price = data['close'].iloc[-1]
            mean_price = data['mean'].iloc[-1]
            
            # Generate signal based on z-score
            if latest_z_score > self.std_dev_threshold:
                return StrategySignal(
                    strategy_name="MeanReversion",
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action="sell",
                    confidence=min(abs(latest_z_score) * 20, 90),
                    price=current_price,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price * 1.02,
                    take_profit=mean_price,
                    holding_period=timedelta(days=3),
                    metadata={
                        "z_score": latest_z_score,
                        "mean": mean_price
                    }
                )
            elif latest_z_score < -self.std_dev_threshold:
                return StrategySignal(
                    strategy_name="MeanReversion",
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action="buy",
                    confidence=min(abs(latest_z_score) * 20, 90),
                    price=current_price,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price * 0.98,
                    take_profit=mean_price,
                    holding_period=timedelta(days=3),
                    metadata={
                        "z_score": latest_z_score,
                        "mean": mean_price
                    }
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {e}")
            return None


class PairTradingStrategy:
    """Pairs trading strategy"""
    
    def __init__(self, lookback_period: int = 252, entry_threshold: float = 2.0):
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.ratio = None
        self.spread_mean = None
        self.spread_std = None
        
    def calculate_spread(self, data1: pd.DataFrame, data2: pd.DataFrame) -> pd.Series:
        """Calculate spread between two assets"""
        # Calculate hedge ratio using linear regression
        returns1 = data1['close'].pct_change().dropna()
        returns2 = data2['close'].pct_change().dropna()
        
        # Align data
        common_index = returns1.index.intersection(returns2.index)
        returns1 = returns1.loc[common_index]
        returns2 = returns2.loc[common_index]
        
        # Calculate hedge ratio
        if len(returns1) > 0:
            self.ratio = np.cov(returns1, returns2)[0, 1] / np.var(returns2)
            spread = data1['close'] - self.ratio * data2['close']
            return spread
        return pd.Series()
        
    async def generate_signal(self, data1: pd.DataFrame, data2: pd.DataFrame) -> Optional[StrategySignal]:
        """Generate pairs trading signal"""
        try:
            spread = self.calculate_spread(data1, data2)
            
            if len(spread) < self.lookback_period:
                return None
                
            # Calculate spread statistics
            self.spread_mean = spread.rolling(window=self.lookback_period).mean()
            self.spread_std = spread.rolling(window=self.lookback_period).std()
            
            latest_spread = spread.iloc[-1]
            latest_mean = self.spread_mean.iloc[-1]
            latest_std = self.spread_std.iloc[-1]
            
            # Calculate z-score of spread
            z_score = (latest_spread - latest_mean) / latest_std if latest_std > 0 else 0
            
            current_price1 = data1['close'].iloc[-1]
            current_price2 = data2['close'].iloc[-1]
            
            # Generate signals
            if z_score > self.entry_threshold:
                # Spread is wide - short first, long second
                return StrategySignal(
                    strategy_name="PairTrading",
                    symbol=f"{data1.get('symbol', 'A')}/{data2.get('symbol', 'B')}",
                    action="short_spread",
                    confidence=min(abs(z_score) * 15, 85),
                    price=current_price1,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price1 * 1.02,
                    take_profit=latest_mean,
                    holding_period=timedelta(days=7),
                    metadata={
                        "spread": latest_spread,
                        "z_score": z_score,
                        "hedge_ratio": self.ratio
                    }
                )
            elif z_score < -self.entry_threshold:
                # Spread is narrow - long first, short second
                return StrategySignal(
                    strategy_name="PairTrading",
                    symbol=f"{data1.get('symbol', 'A')}/{data2.get('symbol', 'B')}",
                    action="long_spread",
                    confidence=min(abs(z_score) * 15, 85),
                    price=current_price1,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price1 * 0.98,
                    take_profit=latest_mean,
                    holding_period=timedelta(days=7),
                    metadata={
                        "spread": latest_spread,
                        "z_score": z_score,
                        "hedge_ratio": self.ratio
                    }
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error in pair trading strategy: {e}")
            return None


class MLPredictionStrategy:
    """Machine learning prediction strategy"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'returns', 'volatility', 'rsi', 'macd', 'volume_ratio',
            'price_momentum', 'mean_reversion_signal'
        ]
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        try:
            # Calculate technical indicators
            data['returns'] = data['close'].pct_change()
            data['volatility'] = data['returns'].rolling(window=20).std()
            data['rsi'] = talib.RSI(data['close'].values, timeperiod=14)
            
            # MACD
            macd, signal, hist = talib.MACD(data['close'].values)
            data['macd'] = macd
            data['macd_signal'] = signal
            
            # Volume ratio
            data['volume_ratio'] = data['volume'] / data['volume'].rolling(window=20).mean()
            
            # Price momentum
            data['price_momentum'] = data['close'] / data['close'].shift(5) - 1
            
            # Mean reversion signal
            data['mean_reversion_signal'] = (data['close'] - data['close'].rolling(window=20).mean()) / data['close'].rolling(window=20).std()
            
            # Select and clean features
            features = data[self.feature_columns].copy()
            features = features.fillna(0)
            
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()
            
    async def train_model(self, training_data: pd.DataFrame):
        """Train ML model"""
        try:
            features = self.prepare_features(training_data)
            
            # Target: next day's return
            target = training_data['close'].shift(-1).pct_change()
            target = target.fillna(0)
            
            # Align features and target
            min_length = min(len(features), len(target))
            features = features.iloc[:min_length-1]
            target = target.iloc[:min_length-1]
            
            if len(features) > 100:  # Minimum training samples
                # Scale features
                features_scaled = self.scaler.fit_transform(features)
                
                # Train model
                self.model.fit(features_scaled, target)
                self.is_trained = True
                
                logger.info(f"ML model trained with {len(features)} samples")
                
        except Exception as e:
            logger.error(f"Error training ML model: {e}")
            
    async def generate_signal(self, data: pd.DataFrame) -> Optional[StrategySignal]:
        """Generate ML prediction signal"""
        try:
            if not self.is_trained:
                return None
                
            features = self.prepare_features(data)
            
            if len(features) == 0:
                return None
                
            # Get latest features
            latest_features = features.iloc[-1:].values
            
            # Scale features
            latest_features_scaled = self.scaler.transform(latest_features)
            
            # Make prediction
            predicted_return = self.model.predict(latest_features_scaled)[0]
            
            current_price = data['close'].iloc[-1]
            
            # Generate signal based on prediction
            if predicted_return > 0.01:  # 1% threshold
                return StrategySignal(
                    strategy_name="MLPrediction",
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action="buy",
                    confidence=min(abs(predicted_return) * 500, 80),
                    price=current_price,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price * 0.97,
                    take_profit=current_price * (1 + predicted_return),
                    holding_period=timedelta(days=1),
                    metadata={
                        "predicted_return": predicted_return,
                        "model_confidence": self.model.score(
                            self.scaler.transform(features.iloc[:-1].values),
                            data['close'].pct_change().shift(-1).fillna(0).iloc[:-1].values
                        )
                    }
                )
            elif predicted_return < -0.01:  # -1% threshold
                return StrategySignal(
                    strategy_name="MLPrediction",
                    symbol=data.get('symbol', 'UNKNOWN'),
                    action="sell",
                    confidence=min(abs(predicted_return) * 500, 80),
                    price=current_price,
                    quantity=1000,
                    timestamp=datetime.now(),
                    stop_loss=current_price * 1.03,
                    take_profit=current_price * (1 + predicted_return),
                    holding_period=timedelta(days=1),
                    metadata={
                        "predicted_return": predicted_return,
                        "model_confidence": self.model.score(
                            self.scaler.transform(features.iloc[:-1].values),
                            data['close'].pct_change().shift(-1).fillna(0).iloc[:-1].values
                        )
                    }
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error in ML prediction strategy: {e}")
            return None


class AlgorithmicStrategies:
    """Main algorithmic strategies manager"""
    
    def __init__(self):
        self.strategies = {
            StrategyType.MOMENTUM: MomentumStrategy(),
            StrategyType.MEAN_REVERSION: MeanReversionStrategy(),
            StrategyType.PAIR_TRADING: PairTradingStrategy(),
            StrategyType.ML_PREDICTION: MLPredictionStrategy()
        }
        self.active_strategies = set()
        self.signals_history = []
        
    async def add_strategy(self, strategy_type: StrategyType, params: Dict[str, Any] = None):
        """Add strategy to active list"""
        if strategy_type in self.strategies:
            self.active_strategies.add(strategy_type)
            logger.info(f"Added strategy: {strategy_type.value}")
            
    async def remove_strategy(self, strategy_type: StrategyType):
        """Remove strategy from active list"""
        self.active_strategies.discard(strategy_type)
        logger.info(f"Removed strategy: {strategy_type.value}")
        
    async def generate_signals(self, market_data: Dict[str, pd.DataFrame]) -> List[StrategySignal]:
        """Generate signals from all active strategies"""
        signals = []
        
        for strategy_type in self.active_strategies:
            strategy = self.strategies[strategy_type]
            
            try:
                if strategy_type == StrategyType.PAIR_TRADING:
                    # Handle pair trading separately
                    symbols = list(market_data.keys())
                    for i in range(len(symbols)-1):
                        for j in range(i+1, len(symbols)):
                            signal = await strategy.generate_signal(
                                market_data[symbols[i]], 
                                market_data[symbols[j]]
                            )
                            if signal:
                                signals.append(signal)
                else:
                    # Handle single-asset strategies
                    for symbol, data in market_data.items():
                        signal = await strategy.generate_signal(data)
                        if signal:
                            signal.symbol = symbol
                            signals.append(signal)
                            
            except Exception as e:
                logger.error(f"Error in strategy {strategy_type.value}: {e}")
                
        # Store signals history
        self.signals_history.extend(signals)
        
        return signals
        
    async def train_ml_models(self, historical_data: Dict[str, pd.DataFrame]):
        """Train ML models with historical data"""
        ml_strategy = self.strategies.get(StrategyType.ML_PREDICTION)
        if ml_strategy:
            for symbol, data in historical_data.items():
                await ml_strategy.train_model(data)
                
    def get_strategy_performance(self) -> Dict[str, Any]:
        """Get strategy performance metrics"""
        if not self.signals_history:
            return {}
            
        # Analyze signal performance
        performance = {}
        strategy_signals = {}
        
        for signal in self.signals_history:
            strategy_name = signal.strategy_name
            if strategy_name not in strategy_signals:
                strategy_signals[strategy_name] = []
            strategy_signals[strategy_name].append(signal)
            
        for strategy_name, signals in strategy_signals.items():
            if signals:
                performance[strategy_name] = {
                    "total_signals": len(signals),
                    "avg_confidence": np.mean([s.confidence for s in signals]),
                    "buy_signals": len([s for s in signals if s.action == "buy"]),
                    "sell_signals": len([s for s in signals if s.action == "sell"]),
                    "last_signal": max([s.timestamp for s in signals])
                }
                
        return performance


# Global algorithmic strategies instance
_algorithmic_strategies = None

def get_algorithmic_strategies() -> AlgorithmicStrategies:
    """Get the global algorithmic strategies instance"""
    global _algorithmic_strategies
    if _algorithmic_strategies is None:
        _algorithmic_strategies = AlgorithmicStrategies()
    return _algorithmic_strategies
