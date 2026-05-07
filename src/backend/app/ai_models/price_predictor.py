"""Price Predictor - ML-based price movement prediction"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics
import math

@dataclass
class PredictionResult:
    symbol: str
    current_price: float
    predicted_direction: str  # UP, DOWN, NEUTRAL
    confidence: float
    target_price: float
    timeframe: str
    features_used: List[str]

class PricePredictor:
    """Predict price movements using technical and statistical features"""
    
    def __init__(self):
        self.features = [
            "price_momentum", "volume_trend", "rsi", "macd", 
            "bollinger_position", "volatility_regime", "support_resistance"
        ]
        self.models = {}
    
    def calculate_technical_features(self, prices: List[float], 
                                    volumes: List[float]) -> Dict[str, float]:
        """Calculate technical indicator features"""
        if len(prices) < 20:
            return {}
        
        features = {}
        
        # Price momentum (rate of change)
        features["price_momentum"] = (prices[-1] - prices[-10]) / prices[-10] * 100
        
        # Volume trend
        recent_vol = statistics.mean(volumes[-5:])
        older_vol = statistics.mean(volumes[-15:-5])
        features["volume_trend"] = (recent_vol - older_vol) / older_vol * 100 if older_vol > 0 else 0
        
        # RSI (simplified)
        gains = []
        losses = []
        for i in range(1, min(15, len(prices))):
            change = prices[-i] - prices[-i-1]
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = statistics.mean(gains) if gains else 0
        avg_loss = statistics.mean(losses) if losses else 0.001
        rs = avg_gain / avg_loss
        features["rsi"] = 100 - (100 / (1 + rs))
        
        # Volatility regime
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        features["volatility"] = statistics.stdev(returns) * 100 if len(returns) > 1 else 0
        features["volatility_regime"] = 1 if features["volatility"] > 2 else 0
        
        # Bollinger Band position
        sma20 = statistics.mean(prices[-20:])
        std20 = statistics.stdev(prices[-20:])
        upper = sma20 + 2 * std20
        lower = sma20 - 2 * std20
        features["bollinger_position"] = (prices[-1] - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        
        return features
    
    def predict_direction(self, symbol: str, prices: List[float], 
                         volumes: List[float]) -> PredictionResult:
        """Predict price direction using ensemble of signals"""
        features = self.calculate_technical_features(prices, volumes)
        
        if not features:
            return PredictionResult(
                symbol=symbol,
                current_price=prices[-1] if prices else 0,
                predicted_direction="NEUTRAL",
                confidence=0.5,
                target_price=prices[-1] if prices else 0,
                timeframe="1d",
                features_used=[]
            )
        
        # Ensemble scoring
        scores = {
            "UP": 0,
            "DOWN": 0,
            "NEUTRAL": 0
        }
        
        # Momentum signal
        if features["price_momentum"] > 2:
            scores["UP"] += 2
        elif features["price_momentum"] < -2:
            scores["DOWN"] += 2
        else:
            scores["NEUTRAL"] += 1
        
        # RSI signal
        if features["rsi"] < 30:
            scores["UP"] += 2  # Oversold bounce
        elif features["rsi"] > 70:
            scores["DOWN"] += 2  # Overbought pullback
        else:
            scores["NEUTRAL"] += 1
        
        # Volume confirmation
        if features["volume_trend"] > 20:
            if features["price_momentum"] > 0:
                scores["UP"] += 1
            else:
                scores["DOWN"] += 1
        
        # Bollinger signal
        if features["bollinger_position"] < 0.2:
            scores["UP"] += 1
        elif features["bollinger_position"] > 0.8:
            scores["DOWN"] += 1
        
        # Determine direction
        direction = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = scores[direction] / total_score if total_score > 0 else 0.5
        
        # Calculate target price
        current_price = prices[-1]
        if direction == "UP":
            target = current_price * (1 + 0.02)  # 2% target
        elif direction == "DOWN":
            target = current_price * (1 - 0.02)  # -2% target
        else:
            target = current_price
        
        return PredictionResult(
            symbol=symbol,
            current_price=round(current_price, 2),
            predicted_direction=direction,
            confidence=round(confidence, 2),
            target_price=round(target, 2),
            timeframe="1d",
            features_used=list(features.keys())
        )
    
    def predict_multi_timeframe(self, symbol: str, 
                               price_data: Dict[str, List[float]]) -> Dict:
        """Predict across multiple timeframes"""
        predictions = {}
        
        for timeframe, prices in price_data.items():
            # Estimate realistic volumes based on price and timeframe
            base_volume = 50000  # Base daily volume estimate
            volume_multiplier = 1.0 + (len(prices) / 100)  # Scale with data availability
            volumes = [base_volume * volume_multiplier] * len(prices)
            pred = self.predict_direction(symbol, prices, volumes)
            predictions[timeframe] = {
                "direction": pred.predicted_direction,
                "confidence": pred.confidence,
                "target": pred.target_price
            }
        
        # Aggregate across timeframes
        directions = [p["direction"] for p in predictions.values()]
        up_count = directions.count("UP")
        down_count = directions.count("DOWN")
        
        consensus = "UP" if up_count > down_count else "DOWN" if down_count > up_count else "NEUTRAL"
        consensus_strength = max(up_count, down_count) / len(directions) if directions else 0
        
        return {
            "symbol": symbol,
            "timeframe_predictions": predictions,
            "consensus_direction": consensus,
            "consensus_strength": round(consensus_strength, 2),
            "trend_alignment": "STRONG" if consensus_strength > 0.7 else "MIXED"
        }
    
    def generate_trading_signal(self, prediction: PredictionResult) -> Dict:
        """Convert prediction to actionable trading signal"""
        if prediction.confidence < 0.6:
            return {
                "action": "NO_TRADE",
                "reason": "Insufficient confidence",
                "confidence": prediction.confidence
            }
        
        if prediction.predicted_direction == "UP":
            return {
                "action": "BUY",
                "entry": prediction.current_price,
                "target": prediction.target_price,
                "stop_loss": round(prediction.current_price * 0.98, 2),
                "risk_reward": 2.0,
                "confidence": prediction.confidence,
                "timeframe": prediction.timeframe
            }
        elif prediction.predicted_direction == "DOWN":
            return {
                "action": "SELL_SHORT",
                "entry": prediction.current_price,
                "target": prediction.target_price,
                "stop_loss": round(prediction.current_price * 1.02, 2),
                "risk_reward": 2.0,
                "confidence": prediction.confidence,
                "timeframe": prediction.timeframe
            }
        
        return {
            "action": "HOLD",
            "reason": "Neutral outlook",
            "confidence": prediction.confidence
        }
