"""Sentiment Accelerator - Track sentiment velocity"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SentimentReading:
    timestamp: datetime
    score: float
    volume: int
    source: str

class SentimentAccelerator:
    """Track acceleration/deceleration of sentiment"""
    
    def __init__(self):
        self.readings: Dict[str, List[SentimentReading]] = {}
    
    def add_reading(self, symbol: str, reading: SentimentReading):
        if symbol not in self.readings:
            self.readings[symbol] = []
        self.readings[symbol].append(reading)
        # Keep only last 100 readings
        self.readings[symbol] = self.readings[symbol][-100:]
    
    def calculate_acceleration(self, symbol: str) -> Dict:
        """Calculate sentiment acceleration"""
        readings = self.readings.get(symbol, [])
        if len(readings) < 3:
            return {"acceleration": 0, "trend": "insufficient_data"}
        
        # Get recent vs older readings
        recent = readings[-3:]
        older = readings[-6:-3] if len(readings) >= 6 else readings[:3]
        
        recent_avg = sum(r.score for r in recent) / len(recent)
        older_avg = sum(r.score for r in older) / len(older)
        
        acceleration = recent_avg - older_avg
        
        return {
            "symbol": symbol,
            "acceleration": round(acceleration, 3),
            "trend": "accelerating" if acceleration > 0.1 else "decelerating" if acceleration < -0.1 else "stable",
            "current_sentiment": round(recent_avg, 2),
            "momentum": "increasing" if acceleration > 0 else "decreasing"
        }
    
    def detect_sentiment_shift(self, symbol: str) -> Dict:
        """Detect major sentiment shifts"""
        readings = self.readings.get(symbol, [])
        if len(readings) < 10:
            return {"shift_detected": False}
        
        first_half = readings[:len(readings)//2]
        second_half = readings[len(readings)//2:]
        
        first_avg = sum(r.score for r in first_half) / len(first_half)
        second_avg = sum(r.score for r in second_half) / len(second_half)
        
        shift = second_avg - first_avg
        
        if abs(shift) > 0.3:  # Significant shift
            return {
                "shift_detected": True,
                "direction": "positive" if shift > 0 else "negative",
                "magnitude": round(abs(shift), 2),
                "from_sentiment": round(first_avg, 2),
                "to_sentiment": round(second_avg, 2),
                "signal": "BUY" if shift > 0.5 else "SELL" if shift < -0.5 else "MONITOR"
            }
        
        return {"shift_detected": False, "current_drift": round(shift, 3)}
    
    def get_velocity_indicator(self, symbol: str) -> Dict:
        """Get sentiment velocity indicator"""
        acc = self.calculate_acceleration(symbol)
        
        velocity = abs(acc["acceleration"])
        
        return {
            "symbol": symbol,
            "velocity": round(velocity, 3),
            "velocity_zone": "high" if velocity > 0.2 else "medium" if velocity > 0.1 else "low",
            "trade_implication": "Enter on acceleration" if acc["trend"] == "accelerating" and velocity > 0.15 else "Wait for clarity"
        }
