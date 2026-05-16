"""Meme Stock Predictor - Detect stocks before they go viral on WSB/Twitter"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import statistics

class MemeStage(Enum):
    DORMANT = "dormant"          # Not on anyone's radar
    GESTATION = "gestation"    # Early mentions, building buzz
    ACCELERATION = "acceleration"  # Rapid growth in mentions
    VIRAL = "viral"            # Full meme status, peak hype
    EUPHORIA = "euphoria"      # Peak insanity, likely top
    DECLINE = "decline"        # Meme dying, momentum fading

@dataclass
class MemeMetrics:
    symbol: str
    stage: MemeStage
    meme_score: float
    mention_velocity: float
    short_interest: float
    options_volume_surge: float
    retail_ownership_estimate: float
    predicted_peak_date: Optional[datetime]

class MemeStockPredictor:
    """Predict which stocks will become meme stocks before they explode"""
    
    def __init__(self):
        self.monitoring_stocks: Dict[str, MemeMetrics] = {}
        self.historical_memes = ["GME", "AMC", "BB", "BBBY", "PLTR", "TSLA", "NVAX"]
        self.meme_database = self._init_meme_patterns()
        
    def _init_meme_patterns(self) -> Dict:
        """Initialize patterns from historical meme stocks"""
        return {
            "characteristics": {
                "high_short_interest": 0.20,      # 20%+ short interest
                "low_float": 0.50,                # Under 50M shares
                "affordable_price": 50.00,        # Under $50 for retail
                "recognizable_brand": True,
                "nostalgia_factor": True,
                "underdog_story": True,
                "catalyst_coming": True
            },
            "signal_weights": {
                "short_interest": 0.25,
                "social_mentions": 0.25,
                "options_volume": 0.20,
                "volume_surge": 0.15,
                "price_momentum": 0.15
            }
        }
    
    def calculate_meme_potential(self, 
                                symbol: str,
                                short_interest: float,
                                float_size: int,
                                price: float,
                                social_mentions_24h: int,
                                social_mentions_7d: int,
                                options_volume_today: int,
                                avg_options_volume: int,
                                volume_today: int,
                                avg_volume: int,
                                price_change_5d: float) -> Dict:
        """Calculate meme stock potential score (0-100)"""
        
        scores = {}
        
        # Short interest score (higher = more potential for squeeze)
        if short_interest > 0.30:
            scores["short_interest"] = 100
        elif short_interest > 0.20:
            scores["short_interest"] = 80
        elif short_interest > 0.15:
            scores["short_interest"] = 60
        else:
            scores["short_interest"] = short_interest * 200
        
        # Float score (lower float = easier to move)
        if float_size < 10_000_000:
            scores["float"] = 100
        elif float_size < 30_000_000:
            scores["float"] = 80
        elif float_size < 50_000_000:
            scores["float"] = 60
        else:
            scores["float"] = max(0, 100 - (float_size / 1_000_000))
        
        # Price accessibility score (lower price = more retail can buy)
        if price < 10:
            scores["price"] = 100
        elif price < 25:
            scores["price"] = 85
        elif price < 50:
            scores["price"] = 70
        elif price < 100:
            scores["price"] = 50
        else:
            scores["price"] = max(0, 100 - price)
        
        # Social media acceleration
        if social_mentions_7d > 0:
            mention_growth = (social_mentions_24h * 7 - social_mentions_7d) / social_mentions_7d
            scores["social"] = min(100, max(0, mention_growth * 100))
        else:
            scores["social"] = 0
        
        # Options volume surge (retail loves options)
        if avg_options_volume > 0:
            options_surge = (options_volume_today - avg_options_volume) / avg_options_volume
            scores["options"] = min(100, options_surge * 50)
        else:
            scores["options"] = 0
        
        # Volume surge
        if avg_volume > 0:
            volume_surge = (volume_today - avg_volume) / avg_volume
            scores["volume"] = min(100, volume_surge * 33)
        else:
            scores["volume"] = 0
        
        # Price momentum
        if price_change_5d > 0.50:  # 50% in 5 days
            scores["momentum"] = 100
        elif price_change_5d > 0.30:
            scores["momentum"] = 80
        elif price_change_5d > 0.20:
            scores["momentum"] = 60
        else:
            scores["momentum"] = max(0, price_change_5d * 200)
        
        # Calculate weighted meme score
        weights = self.meme_database["signal_weights"]
        total_score = (
            scores["short_interest"] * weights["short_interest"] +
            scores["social"] * weights["social_mentions"] +
            scores["options"] * weights["options_volume"] +
            scores["volume"] * weights["volume_surge"] +
            scores["momentum"] * weights["price_momentum"]
        )
        
        # Determine stage
        stage = self._determine_stage(total_score, scores["social"], scores["momentum"])
        
        # Predict peak timing
        predicted_peak = None
        if stage in [MemeStage.ACCELERATION, MemeStage.VIRAL]:
            # Historical meme stocks peak 3-7 days after going viral
            predicted_peak = datetime.utcnow() + timedelta(days=5)
        
        return {
            "symbol": symbol,
            "meme_score": round(total_score, 1),
            "stage": stage.value,
            "component_scores": {k: round(v, 1) for k, v in scores.items()},
            "indicators": {
                "short_squeeze_potential": scores["short_interest"] > 70,
                "retail_friendly": scores["price"] > 60 and scores["float"] > 60,
                "momentum_building": scores["social"] > 50 or scores["volume"] > 70,
                "options_casino": scores["options"] > 80
            },
            "predicted_peak_date": predicted_peak.isoformat() if predicted_peak else None,
            "risk_level": self._calculate_risk_level(stage, total_score),
            "position_sizing_recommendation": self._position_size_recommendation(total_score, stage)
        }
    
    def _determine_stage(self, total_score: float, social_score: float, 
                        momentum_score: float) -> MemeStage:
        """Determine which meme stage a stock is in"""
        if total_score < 20:
            return MemeStage.DORMANT
        elif total_score < 40:
            return MemeStage.GESTATION
        elif total_score < 60:
            return MemeStage.ACCELERATION
        elif total_score < 80:
            if momentum_score > 80:
                return MemeStage.EUPHORIA
            return MemeStage.VIRAL
        else:
            if momentum_score < 50:
                return MemeStage.DECLINE
            return MemeStage.EUPHORIA
    
    def _calculate_risk_level(self, stage: MemeStage, score: float) -> str:
        """Calculate risk level for trading this meme stock"""
        if stage == MemeStage.EUPHORIA:
            return "EXTREME - Likely near top"
        elif stage == MemeStage.VIRAL:
            return "VERY HIGH - High volatility"
        elif stage == MemeStage.ACCELERATION:
            return "HIGH - Entering meme territory"
        elif score > 50:
            return "MODERATE - Watch closely"
        else:
            return "LOW - Not yet a meme"
    
    def _position_size_recommendation(self, score: float, stage: MemeStage) -> str:
        """Recommend position size based on meme potential"""
        if stage == MemeStage.EUPHORIA:
            return "0% - DO NOT ENTER, look for shorts"
        elif stage == MemeStage.DECLINE:
            return "0-1% - Only if believing in long-term"
        elif stage == MemeStage.VIRAL:
            return "1-2% - Small speculative position"
        elif stage == MemeStage.ACCELERATION:
            return "2-5% - Early entry opportunity"
        elif score > 60:
            return "3-5% - High potential, manageable risk"
        else:
            return "Monitor only"
    
    def scan_for_meme_candidates(self, stock_universe: List[Dict]) -> List[Dict]:
        """Scan entire stock universe for meme candidates"""
        candidates = []
        
        for stock in stock_universe:
            # Filter for meme-friendly characteristics
            if stock.get("price", 1000) > 200:  # Skip expensive stocks
                continue
            if stock.get("market_cap", 1e15) > 50e9:  # Skip mega caps
                continue
            
            potential = self.calculate_meme_potential(
                symbol=stock["symbol"],
                short_interest=stock.get("short_interest", 0),
                float_size=stock.get("float", 0),
                price=stock.get("price", 0),
                social_mentions_24h=stock.get("mentions_24h", 0),
                social_mentions_7d=stock.get("mentions_7d", 0),
                options_volume_today=stock.get("options_volume", 0),
                avg_options_volume=stock.get("avg_options_volume", 1),
                volume_today=stock.get("volume", 0),
                avg_volume=stock.get("avg_volume", 1),
                price_change_5d=stock.get("change_5d", 0)
            )
            
            if potential["meme_score"] > 40:
                candidates.append(potential)
        
        return sorted(candidates, key=lambda x: x["meme_score"], reverse=True)
    
    def get_entry_exit_strategy(self, meme_data: Dict) -> Dict:
        """Generate entry and exit strategy for meme stock"""
        stage = meme_data.get("stage")
        score = meme_data.get("meme_score", 0)
        
        strategies = {
            MemeStage.DORMANT.value: {
                "action": "WATCH",
                "entry": "Wait for catalyst",
                "exit": "N/A",
                "timeframe": "Monitor daily"
            },
            MemeStage.GESTATION.value: {
                "action": "ACCUMULATE SMALL",
                "entry": "Dips to 20 EMA",
                "exit": "Stage change to acceleration",
                "timeframe": "1-2 weeks"
            },
            MemeStage.ACCELERATION.value: {
                "action": "BUY MOMENTUM",
                "entry": "Break of previous day high",
                "exit": "Volume dries up OR 50% gain",
                "timeframe": "3-5 days"
            },
            MemeStage.VIRAL.value: {
                "action": "TRADE ONLY",
                "entry": "Opening range break",
                "exit": "Same day close, no overnight",
                "timeframe": "Intraday only"
            },
            MemeStage.EUPHORIA.value: {
                "action": "LOOK FOR SHORT",
                "entry": "Failed breakout, exhaustion candle",
                "exit": "Cover at 20% drop OR VWAP reclaim",
                "timeframe": "1-3 days"
            },
            MemeStage.DECLINE.value: {
                "action": "AVOID",
                "entry": "None",
                "exit": "If trapped, exit any bounce",
                "timeframe": "N/A"
            }
        }
        
        strategy = strategies.get(stage, strategies[MemeStage.DORMANT.value])
        
        # Add specific price targets if we have enough data
        current_price = meme_data.get("current_price", 0)
        if current_price > 0 and score > 60:
            strategy["price_targets"] = {
                "first_target": round(current_price * 1.3, 2),  # 30% gain
                "second_target": round(current_price * 1.5, 2),  # 50% gain
                "moon_target": round(current_price * 2.0, 2),    # 100% gain
                "stop_loss": round(current_price * 0.85, 2)     # 15% loss
            }
        
        return strategy
    
    def compare_to_historical_memes(self, symbol: str, metrics: Dict) -> Dict:
        """Compare current stock to historical meme stock patterns"""
        comparisons = {
            "GME": {
                "pre_squeeze_short_interest": 1.4,  # 140%
                "days_to_peak": 3,
                "peak_gain": 2500,  # 25x
                "characteristics": ["insane_short_interest", "cult_following", "activist_involvement"]
            },
            "AMC": {
                "pre_squeeze_short_interest": 0.20,
                "days_to_peak": 5,
                "peak_gain": 3000,
                "characteristics": ["pandemic_reopening", "retail_favorite", "options_volume"]
            },
            "BBBY": {
                "pre_squeeze_short_interest": 0.45,
                "days_to_peak": 2,
                "peak_gain": 500,
                "characteristics": ["bankruptcy_fears", "activist_buying", "short_squeeze"]
            }
        }
        
        # Find closest match
        current_short = metrics.get("short_interest", 0)
        best_match = None
        closest_diff = float('inf')
        
        for meme, data in comparisons.items():
            diff = abs(data["pre_squeeze_short_interest"] - current_short)
            if diff < closest_diff:
                closest_diff = diff
                best_match = meme
        
        return {
            "symbol": symbol,
            "closest_historical_match": best_match,
            "similarity": max(0, 100 - closest_diff * 100),
            "historical_template": comparisons.get(best_match, {}),
            "implied_potential_gain": comparisons.get(best_match, {}).get("peak_gain", 0) if closest_diff < 0.2 else 100,
            "warning": "Historical performance does not guarantee future results"
        }
