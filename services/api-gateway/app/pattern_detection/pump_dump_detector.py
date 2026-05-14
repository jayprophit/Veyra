"""Pump and Dump Detector - Detect coordinated pump and dump schemes"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import statistics

@dataclass
class PumpPhase:
    start_time: datetime
    end_time: datetime
    price_start: float
    price_peak: float
    volume_multiplier: float
    social_mentions: int

@dataclass
class DumpPhase:
    start_time: datetime
    end_time: Optional[datetime]
    price_peak: float
    price_current: float
    volume_multiplier: float

class PumpDumpDetector:
    """Detect pump and dump schemes in stocks and crypto"""
    
    def __init__(self):
        self.detected_schemes: List[Dict] = []
        self.monitoring_symbols: set = set()
        
    def analyze_price_volume_pattern(self, 
                                   symbol: str,
                                   price_data: List[Dict],
                                   volume_data: List[Dict],
                                   social_sentiment: List[Dict] = None) -> Dict:
        """Analyze price/volume for pump and dump patterns"""
        if len(price_data) < 20:
            return {"error": "insufficient_data", "min_required": 20}
        
        results = {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "pump_detected": False,
            "dump_detected": False,
            "confidence": 0.0,
            "phase": "none",
            "indicators": {},
            "risk_level": "low"
        }
        
        # Calculate price and volume metrics
        prices = [p["close"] for p in price_data]
        volumes = [v["volume"] for v in volume_data]
        
        # Baseline calculations
        avg_volume = statistics.mean(volumes[:-5]) if len(volumes) > 5 else statistics.mean(volumes)
        recent_volume = statistics.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
        volume_spike = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # Price calculations
        price_7d_ago = prices[-8] if len(prices) >= 8 else prices[0]
        price_now = prices[-1]
        price_change_7d = (price_now - price_7d_ago) / price_7d_ago if price_7d_ago != 0 else 0
        
        # Find peak in recent period
        recent_prices = prices[-10:]
        peak_price = max(recent_prices)
        peak_idx = recent_prices.index(peak_price)
        
        # Pump detection: Rapid price increase + volume spike
        pump_indicators = {
            "price_increase_7d": price_change_7d * 100,
            "volume_spike": volume_spike,
            "unusual_activity": volume_spike > 3 and price_change_7d > 0.20
        }
        
        if price_change_7d > 0.30 and volume_spike > 3:  # 30% price, 3x volume
            results["pump_detected"] = True
            results["phase"] = "pump"
            results["confidence"] += 0.4
            results["indicators"]["pump"] = pump_indicators
        
        # Dump detection: Price falling from peak + volume
        if peak_idx < len(recent_prices) - 1:  # Peak was recent, now declining
            drop_from_peak = (price_now - peak_price) / peak_price if peak_price != 0 else 0
            
            if drop_from_peak < -0.15 and volume_spike > 2:  # 15% drop from peak
                results["dump_detected"] = True
                results["phase"] = "dump"
                results["confidence"] += 0.3
                results["indicators"]["dump"] = {
                    "drop_from_peak_pct": drop_from_peak * 100,
                    "peak_to_now_hours": (len(recent_prices) - peak_idx) * 1  # Assuming hourly
                }
        
        # Social sentiment analysis
        if social_sentiment:
            social_indicators = self._analyze_social_patterns(social_sentiment)
            results["indicators"]["social"] = social_indicators
            
            # Coordinated social media activity is suspicious
            if social_indicators["coordination_score"] > 0.7:
                results["confidence"] += 0.3
        
        # Risk assessment
        if results["confidence"] > 0.8:
            results["risk_level"] = "critical"
        elif results["confidence"] > 0.6:
            results["risk_level"] = "high"
        elif results["confidence"] > 0.4:
            results["risk_level"] = "medium"
        
        # Generate warning
        if results["pump_detected"] and not results["dump_detected"]:
            results["warning"] = f"PUMP IN PROGRESS: {symbol} showing pump characteristics"
            results["recommendation"] = "DO NOT CHASE - High risk of imminent dump"
        elif results["dump_detected"]:
            results["warning"] = f"DUMP DETECTED: {symbol} falling from pump peak"
            results["recommendation"] = "Avoid catching falling knife"
        
        return results
    
    def _analyze_social_patterns(self, social_data: List[Dict]) -> Dict:
        """Analyze social media for coordinated promotion"""
        if not social_data:
            return {"coordination_score": 0}
        
        # Count mentions over time
        mention_times = [s.get("timestamp") for s in social_data if s.get("timestamp")]
        mention_times.sort()
        
        # Check for burst of mentions (coordinated)
        if len(mention_times) >= 3:
            time_windows = []
            for i in range(1, len(mention_times)):
                diff = (mention_times[i] - mention_times[i-1]).total_seconds() / 60
                time_windows.append(diff)
            
            # Many mentions in short window = coordination
            burst_count = sum(1 for w in time_windows if w < 5)  # Within 5 minutes
            coordination = min(burst_count / max(len(time_windows), 1) * 2, 1.0)
        else:
            coordination = 0
        
        # Check for similar messaging (copy-paste)
        messages = [s.get("message", "") for s in social_data]
        from difflib import SequenceMatcher
        
        similarities = []
        for i in range(len(messages)):
            for j in range(i+1, len(messages)):
                sim = SequenceMatcher(None, messages[i], messages[j]).ratio()
                similarities.append(sim)
        
        avg_similarity = statistics.mean(similarities) if similarities else 0
        
        # Check for bot-like accounts
        new_accounts = sum(1 for s in social_data if s.get("account_age_days", 365) < 30)
        bot_score = new_accounts / max(len(social_data), 1)
        
        return {
            "coordination_score": coordination,
            "message_similarity": avg_similarity,
            "suspicious_accounts_pct": bot_score * 100,
            "mention_velocity": len(social_data) / max(len(set([m.date() for m in mention_times])), 1) if mention_times else 0
        }
    
    def detect_coordination_groups(self, trading_data: List[Dict]) -> Dict:
        """Detect groups of traders acting in coordination"""
        if len(trading_data) < 50:
            return {"groups_detected": 0}
        
        # Look for simultaneous buy orders
        buy_times = {}
        for trade in trading_data:
            if trade.get("side") == "buy":
                time_key = trade["timestamp"].strftime("%Y-%m-%d %H:%M")
                if time_key not in buy_times:
                    buy_times[time_key] = 0
                buy_times[time_key] += trade.get("size", 0)
        
        # Find unusually concentrated buy times
        avg_size = statistics.mean(buy_times.values()) if buy_times else 0
        suspicious_times = {t: s for t, s in buy_times.items() if s > avg_size * 5}
        
        return {
            "groups_detected": len(suspicious_times),
            "suspicious_activity_periods": list(suspicious_times.keys())[:10],
            "largest_coordinated_buy": max(suspicious_times.values()) if suspicious_times else 0,
            "confidence": min(len(suspicious_times) * 0.1, 1.0)
        }
    
    def get_pump_dump_watchlist(self, market_scan: List[Dict]) -> List[Dict]:
        """Generate watchlist of symbols showing pump/dump characteristics"""
        watchlist = []
        
        for symbol_data in market_scan:
            symbol = symbol_data.get("symbol")
            price_change_24h = symbol_data.get("price_change_24h", 0)
            volume_change = symbol_data.get("volume_change", 1)
            
            score = 0
            reasons = []
            
            # High price increase
            if price_change_24h > 0.50:  # 50% up
                score += 0.3
                reasons.append("Extreme price appreciation")
            
            # Volume spike
            if volume_change > 5:  # 5x normal
                score += 0.3
                reasons.append("Massive volume spike")
            
            # Low float stocks more susceptible
            if symbol_data.get("market_cap", 1e12) < 1e9:  # Under $1B
                score += 0.2
                reasons.append("Low market cap - easily manipulated")
            
            if score > 0.5:
                watchlist.append({
                    "symbol": symbol,
                    "risk_score": score,
                    "reasons": reasons,
                    "price_change_24h": price_change_24h * 100,
                    "volume_multiple": volume_change,
                    "warning": "Potential pump and dump target" if score > 0.7 else "Elevated risk"
                })
        
        return sorted(watchlist, key=lambda x: x["risk_score"], reverse=True)
    
    def generate_protection_strategy(self, portfolio: List[str], 
                                   detected_threats: List[Dict]) -> Dict:
        """Generate strategy to protect portfolio from pump/dump"""
        exposed_positions = []
        safe_positions = []
        
        for holding in portfolio:
            threat = next((t for t in detected_threats if t["symbol"] == holding), None)
            if threat:
                exposed_positions.append({
                    "symbol": holding,
                    "risk_level": threat.get("risk_level", "unknown"),
                    "recommended_action": "EXIT IMMEDIATELY" if threat.get("phase") == "pump" else "HOLD - do not add"
                })
            else:
                safe_positions.append(holding)
        
        return {
            "exposed_positions": exposed_positions,
            "safe_positions": safe_positions,
            "portfolio_at_risk_pct": len(exposed_positions) / len(portfolio) * 100 if portfolio else 0,
            "general_recommendations": [
                "Avoid stocks with >30% move in 24h",
                "Avoid stocks with >3x volume spike without news",
                "Check social media for coordinated promotion",
                "Verify company fundamentals before buying"
            ]
        }
