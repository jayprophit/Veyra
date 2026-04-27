"""Viral Trading Engine - Trade meme momentum"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class ViralStage(Enum):
    DORMANT = "dormant"
    EMERGING = "emerging"
    ACCELERATING = "accelerating"
    PEAK = "peak"
    DECLINING = "declining"

@dataclass
class ViralMetrics:
    symbol: str
    stage: ViralStage
    velocity: float
    social_score: float
    volume_surge: float
    price_momentum: float

class ViralTradingEngine:
    """Trade viral/meme stock momentum"""
    
    def __init__(self):
        self.monitored_stocks: Dict[str, ViralMetrics] = {}
    
    def calculate_viral_score(self, symbol: str, metrics: Dict) -> Dict:
        """Calculate viral trading score"""
        social = min(100, metrics.get("mention_growth", 0) * 10)
        volume = min(100, metrics.get("volume_ratio", 1) * 25)
        price = min(100, abs(metrics.get("price_change", 0)) * 2)
        
        viral_score = (social * 0.4 + volume * 0.35 + price * 0.25)
        
        stage = self._get_stage(viral_score, social)
        
        return {
            "symbol": symbol,
            "viral_score": round(viral_score, 1),
            "stage": stage.value,
            "components": {
                "social": round(social, 1),
                "volume": round(volume, 1),
                "price": round(price, 1)
            },
            "trade_signal": self._get_signal(stage, viral_score)
        }
    
    def _get_stage(self, score: float, social: float) -> ViralStage:
        if score < 20:
            return ViralStage.DORMANT
        elif score < 40:
            return ViralStage.EMERGING
        elif score < 70:
            return ViralStage.ACCELERATING
        elif score < 90:
            return ViralStage.PEAK
        return ViralStage.DECLINING
    
    def _get_signal(self, stage: ViralStage, score: float) -> Dict:
        signals = {
            ViralStage.DORMANT: {"action": "WATCH", "size": "0%"},
            ViralStage.EMERGING: {"action": "ACCUMULATE", "size": "2%"},
            ViralStage.ACCELERATING: {"action": "BUY", "size": "5%"},
            ViralStage.PEAK: {"action": "TRADE", "size": "3%", "note": "Intraday only"},
            ViralStage.DECLINING: {"action": "AVOID", "size": "0%"}
        }
        return signals.get(stage, {"action": "HOLD", "size": "0%"})
    
    def get_momentum_entry(self, metrics: ViralMetrics) -> Dict:
        """Get optimal entry for momentum trade"""
        if metrics.stage == ViralStage.ACCELERATING:
            return {
                "entry_type": "BREAKOUT",
                "trigger": "High volume break of previous day high",
                "stop_loss": "-8%",
                "target_1": "+25%",
                "target_2": "+50%",
                "timeframe": "2-5 days"
            }
        elif metrics.stage == ViralStage.EMERGING:
            return {
                "entry_type": "EARLY",
                "trigger": "First day of increased social mentions",
                "stop_loss": "-5%",
                "target_1": "+15%",
                "target_2": "+30%",
                "timeframe": "1-2 weeks"
            }
        return {"entry_type": "NONE", "reason": "Not in optimal stage"}
    
    def detect_momentum_reversal(self, history: List[Dict]) -> Dict:
        """Detect when viral momentum is reversing"""
        if len(history) < 3:
            return {"reversal": False}
        
        scores = [h["viral_score"] for h in history[-3:]]
        volumes = [h.get("volume", 0) for h in history[-3:]]
        
        # Declining score with high volume = distribution
        if scores[-1] < scores[0] * 0.7 and volumes[-1] > volumes[0]:
            return {
                "reversal": True,
                "confidence": "HIGH",
                "signal": "EXIT",
                "reason": "Distribution detected - declining momentum with high volume"
            }
        
        return {"reversal": False, "trend": "stable" if scores[-1] > scores[0] else "weakening"}
