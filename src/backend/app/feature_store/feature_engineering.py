"""Feature Store for ML Feature Engineering."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class FeatureSet:
    feature_set_id: str
    name: str
    version: str
    features: Dict[str, Any]
    created_at: datetime
    ttl_seconds: int

class FeatureStore:
    """
    Enterprise Feature Store for real-time and batch ML features.
    Online and offline feature serving.
    """
    
    def __init__(self):
        self.online_store: Dict[str, Dict[str, Any]] = {}  # Real-time features
        self.offline_store: Dict[str, pd.DataFrame] = {}   # Historical features
        self.feature_metadata: Dict[str, Dict] = {}
        self.feature_stats: Dict[str, Dict] = {}
    
    async def register_feature(self,
                              feature_name: str,
                              feature_type: str,
                              description: str,
                              ttl_seconds: int = 3600):
        """Register a new feature in the store."""
        self.feature_metadata[feature_name] = {
            'name': feature_name,
            'type': feature_type,
            'description': description,
            'ttl': ttl_seconds,
            'registered_at': datetime.now().isoformat()
        }
        logger.info(f"Feature registered: {feature_name}")
    
    async def compute_technical_features(self,
                                       symbol: str,
                                       price_data: List[Dict]) -> Dict[str, Any]:
        """Compute technical analysis features."""
        df = pd.DataFrame(price_data)
        
        features = {
            'symbol': symbol,
            'computed_at': datetime.now().isoformat()
        }
        
        if len(df) >= 20:
            # Moving averages
            features['sma_20'] = df['close'].rolling(20).mean().iloc[-1]
            features['sma_50'] = df['close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            
            # Volatility
            features['volatility_20d'] = df['close'].pct_change().rolling(20).std().iloc[-1]
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(20).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(20).mean()
            rs = gain / loss
            features['rsi_14'] = (100 - (100 / (1 + rs))).iloc[-1]
            
            # MACD
            exp1 = df['close'].ewm(span=12).mean()
            exp2 = df['close'].ewm(span=26).mean()
            features['macd'] = (exp1 - exp2).iloc[-1]
            
            # Bollinger Bands
            sma = df['close'].rolling(20).mean()
            std = df['close'].rolling(20).std()
            features['bb_upper'] = (sma + 2 * std).iloc[-1]
            features['bb_lower'] = (sma - 2 * std).iloc[-1]
            features['bb_position'] = (df['close'].iloc[-1] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])
            
            # Price momentum
            features['momentum_10d'] = (df['close'].iloc[-1] / df['close'].iloc[-10] - 1) if len(df) >= 10 else 0
            
            # Volume features
            features['volume_sma_20'] = df['volume'].rolling(20).mean().iloc[-1]
            features['volume_ratio'] = df['volume'].iloc[-1] / features['volume_sma_20']
        
        return features
    
    async def compute_fundamental_features(self,
                                          symbol: str,
                                          fundamentals: Dict) -> Dict[str, Any]:
        """Compute fundamental analysis features."""
        return {
            'symbol': symbol,
            'pe_ratio': fundamentals.get('pe_ratio', 0),
            'pb_ratio': fundamentals.get('pb_ratio', 0),
            'debt_to_equity': fundamentals.get('debt_to_equity', 0),
            'roe': fundamentals.get('roe', 0),
            'revenue_growth': fundamentals.get('revenue_growth', 0),
            'profit_margin': fundamentals.get('profit_margin', 0),
            'computed_at': datetime.now().isoformat()
        }
    
    async def store_online_features(self,
                                   entity_id: str,
                                   features: Dict[str, Any]):
        """Store features in online store for real-time serving."""
        self.online_store[entity_id] = {
            'features': features,
            'stored_at': datetime.now(),
            'ttl': 3600
        }
    
    async def get_online_features(self,
                                 entity_id: str,
                                 feature_names: List[str]) -> Dict[str, Any]:
        """Retrieve features from online store."""
        if entity_id not in self.online_store:
            return {'error': 'Entity not found'}
        
        stored = self.online_store[entity_id]
        
        # Check TTL
        age = (datetime.now() - stored['stored_at']).total_seconds()
        if age > stored['ttl']:
            return {'error': 'Features expired'}
        
        features = stored['features']
        
        return {
            'entity_id': entity_id,
            'features': {k: v for k, v in features.items() if k in feature_names},
            'staleness_seconds': age
        }
    
    async def get_training_dataset(self,
                                  symbol: str,
                                  start_date: str,
                                  end_date: str,
                                  feature_list: List[str]) -> pd.DataFrame:
        """Get historical features for ML training."""
        # In production: query from offline store
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        data = []
        for date in dates:
            data.append({
                'symbol': symbol,
                'date': date,
                'return_1d': np.random.normal(0, 0.02),
                'volatility': np.random.uniform(0.1, 0.5),
                'rsi': np.random.uniform(0, 100),
                'target': np.random.choice([0, 1])
            })
        
        return pd.DataFrame(data)
    
    async def compute_feature_statistics(self,
                                        feature_name: str,
                                        values: List[float]) -> Dict[str, float]:
        """Compute feature statistics for monitoring."""
        if not values:
            return {}
        
        stats = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values),
            'p5': np.percentile(values, 5),
            'p95': np.percentile(values, 95),
            'missing_pct': sum(1 for v in values if v is None) / len(values) * 100
        }
        
        self.feature_stats[feature_name] = {
            **stats,
            'computed_at': datetime.now().isoformat()
        }
        
        return stats
    
    async def detect_feature_drift(self,
                                  feature_name: str,
                                  current_values: List[float],
                                  reference_values: List[float]) -> Dict[str, Any]:
        """Detect feature drift from reference distribution."""
        from scipy import stats
        
        # KS test
        ks_statistic, p_value = stats.ks_2samp(reference_values, current_values)
        
        # Population stability index
        def calculate_psi(expected, actual, buckets=10):
            def scale_range(input, min_val, max_val):
                return (input - min_val) / (max_val - min_val)
            
            breakpoints = np.linspace(0, 1, buckets + 1)
            breakpoints = np.percentile(expected, breakpoints * 100)
            
            expected_percents = np.histogram(expected, breakpoints)[0] / len(expected)
            actual_percents = np.histogram(actual, breakpoints)[0] / len(actual)
            
            # Add small value to avoid division by zero
            expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
            actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)
            
            psi = np.sum((expected_percents - actual_percents) * np.log(expected_percents / actual_percents))
            return psi
        
        psi = calculate_psi(reference_values, current_values)
        
        return {
            'feature_name': feature_name,
            'ks_statistic': ks_statistic,
            'p_value': p_value,
            'psi': psi,
            'drift_detected': psi > 0.25 or p_value < 0.05,
            'drift_severity': 'high' if psi > 0.25 else 'medium' if psi > 0.1 else 'low'
        }

feature_store = FeatureStore()
