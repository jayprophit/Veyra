"""Market Manipulation Detector - Spoofing, layering, algo manipulation detection"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import statistics

class ManipulationType(Enum):
    SPOOFING = "spoofing"  # Fake orders to manipulate price
    LAYERING = "layering"  # Multiple fake orders at different levels
    PUMP_DUMP = "pump_and_dump"  # Artificial inflation then crash
    WASH_TRADING = "wash_trading"  # Self-trading to fake volume
    BEAR_RAID = "bear_raid"  # Coordinated short attack
    CHURNING = "churning"  # Excessive trading for commissions
    FRONT_RUNNING = "front_running"  # Trading ahead of client orders
    INSIDER_TRADING = "insider_trading"  # Trading on non-public info

@dataclass
class SuspiciousPattern:
    pattern_type: ManipulationType
    symbol: str
    confidence: float
    timestamp: datetime
    evidence: Dict
    severity: str  # low, medium, high, critical

class ManipulationDetector:
    """Detect market manipulation patterns in real-time"""
    
    def __init__(self):
        self.detected_patterns: List[SuspiciousPattern] = []
        self.order_book_history: Dict[str, List[Dict]] = {}
        self.volume_baseline: Dict[str, float] = {}
        self.alert_threshold = 0.75
        
    def analyze_order_book(self, symbol: str, 
                          bids: List[Tuple[float, float]], 
                          asks: List[Tuple[float, float]],
                          recent_trades: List[Dict]) -> Dict:
        """Analyze order book for manipulation patterns"""
        results = {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
            "patterns_detected": [],
            "risk_score": 0.0,
            "recommendations": []
        }
        
        # Check for spoofing (large orders that disappear)
        spoofing_score = self._detect_spoofing(symbol, bids, asks, recent_trades)
        if spoofing_score > 0.6:
            results["patterns_detected"].append({
                "type": "spoofing",
                "confidence": spoofing_score,
                "description": "Large orders appearing and disappearing rapidly"
            })
            results["risk_score"] += spoofing_score * 0.25
        
        # Check for layering (orders at multiple levels)
        layering_score = self._detect_layering(symbol, bids, asks)
        if layering_score > 0.7:
            results["patterns_detected"].append({
                "type": "layering",
                "confidence": layering_score,
                "description": "Structured orders at incremental price levels"
            })
            results["risk_score"] += layering_score * 0.25
        
        # Check for wash trading (same buyer/seller)
        wash_score = self._detect_wash_trading(recent_trades)
        if wash_score > 0.8:
            results["patterns_detected"].append({
                "type": "wash_trading",
                "confidence": wash_score,
                "description": "Suspected self-trading to inflate volume"
            })
            results["risk_score"] += wash_score * 0.30
        
        # Generate recommendations
        if results["risk_score"] > 0.7:
            results["recommendations"].append("Avoid trading this symbol temporarily")
            results["recommendations"].append("Wait for order book normalization")
        elif results["risk_score"] > 0.4:
            results["recommendations"].append("Use limit orders only")
            results["recommendations"].append("Reduce position size")
        
        return results
    
    def _detect_spoofing(self, symbol: str, bids: List[Tuple], 
                        asks: List[Tuple], trades: List[Dict]) -> float:
        """Detect spoofing: large orders that cancel without execution"""
        if not bids or not asks:
            return 0.0
        
        # Calculate order book imbalance
        total_bid_size = sum(b[1] for b in bids[:5])
        total_ask_size = sum(a[1] for a in asks[:5])
        
        # Large orders at best bid/ask that don't execute is suspicious
        best_bid_size = bids[0][1] if bids else 0
        best_ask_size = asks[0][1] if asks else 0
        
        # Check if large orders are disproportionate to recent volume
        if trades:
            avg_trade_size = statistics.mean([t.get("size", 0) for t in trades[-20:]])
            if best_bid_size > avg_trade_size * 10 or best_ask_size > avg_trade_size * 10:
                return 0.8  # High confidence of spoofing
        
        # Check rapid cancellation pattern
        if symbol in self.order_book_history:
            history = self.order_book_history[symbol]
            if len(history) > 3:
                # Check for repeated large orders at same level
                recent_bids = [h.get("best_bid_size", 0) for h in history[-3:]]
                if len(set(recent_bids)) > 1 and max(recent_bids) > 1000:
                    return 0.7
        
        return 0.0
    
    def _detect_layering(self, symbol: str, bids: List[Tuple], asks: List[Tuple]) -> float:
        """Detect layering: orders at every price level to create false depth"""
        if len(bids) < 5 or len(asks) < 5:
            return 0.0
        
        # Check for uniform size distribution (unnatural)
        bid_sizes = [b[1] for b in bids[:10]]
        ask_sizes = [a[1] for a in asks[:10]]
        
        if len(bid_sizes) > 3 and len(ask_sizes) > 3:
            bid_cv = statistics.stdev(bid_sizes) / statistics.mean(bid_sizes) if statistics.mean(bid_sizes) > 0 else 0
            ask_cv = statistics.stdev(ask_sizes) / statistics.mean(ask_sizes) if statistics.mean(ask_sizes) > 0 else 0
            
            # Low coefficient of variation indicates artificial uniformity
            if bid_cv < 0.2 and statistics.mean(bid_sizes) > 100:
                return 0.75
            if ask_cv < 0.2 and statistics.mean(ask_sizes) > 100:
                return 0.75
        
        # Check for incremental price steps
        bid_prices = [b[0] for b in bids[:5]]
        ask_prices = [a[0] for a in asks[:5]]
        
        bid_gaps = [bid_prices[i] - bid_prices[i+1] for i in range(len(bid_prices)-1)]
        if len(bid_gaps) > 2 and statistics.stdev(bid_gaps) < 0.01:
            return 0.8  # Suspiciously regular increments
        
        return 0.0
    
    def _detect_wash_trading(self, trades: List[Dict]) -> float:
        """Detect wash trading: same entity trading with itself"""
        if len(trades) < 10:
            return 0.0
        
        # Look for alternating buy/sell from same addresses
        buy_sell_alternation = 0
        for i in range(1, len(trades)):
            if trades[i]["side"] != trades[i-1]["side"]:
                buy_sell_alternation += 1
        
        alternation_rate = buy_sell_alternation / (len(trades) - 1)
        
        # Check for matching volumes in alternating trades
        matching_volumes = 0
        for i in range(1, len(trades)):
            if trades[i]["side"] != trades[i-1]["side"]:
                vol_diff = abs(trades[i]["size"] - trades[i-1]["size"])
                if vol_diff / max(trades[i]["size"], 0.001) < 0.05:
                    matching_volumes += 1
        
        if alternation_rate > 0.7 and matching_volumes > len(trades) * 0.3:
            return 0.85
        
        return 0.0
    
    def detect_bear_raid(self, symbol: str, 
                        price_data: List[Dict],
                        short_interest: float) -> Dict:
        """Detect coordinated short selling attack"""
        if len(price_data) < 20:
            return {"detected": False, "confidence": 0}
        
        # Calculate price velocity and acceleration
        prices = [p["close"] for p in price_data]
        volumes = [p["volume"] for p in price_data]
        
        recent_drop = (prices[-1] - prices[-5]) / prices[-5] if prices[-5] != 0 else 0
        volume_spike = statistics.mean(volumes[-5:]) / statistics.mean(volumes[:-5]) if len(volumes) > 5 else 1
        
        # Bear raid indicators
        indicators = {
            "rapid_price_decline": recent_drop < -0.05,  # 5% drop
            "volume_spike": volume_spike > 3.0,  # 3x volume
            "high_short_interest": short_interest > 0.20,  # 20% short
            "continuous_selling_pressure": all(p < prices[i-1] for i, p in enumerate(prices[-5:], -4))
        }
        
        score = sum(indicators.values()) / len(indicators)
        
        return {
            "detected": score > 0.6,
            "confidence": score,
            "indicators": indicators,
            "price_drop_pct": recent_drop * 100,
            "volume_multiple": volume_spike,
            "recommendation": "Hold or buy the dip" if score > 0.7 else "Monitor closely"
        }
    
    def detect_insider_pattern(self, symbol: str,
                             unusual_volume_days: List[datetime],
                             news_release_dates: List[datetime]) -> Dict:
        """Detect potential insider trading: unusual volume before news"""
        suspicious_matches = 0
        
        for news_date in news_release_dates:
            # Check for unusual volume 1-5 days before news
            for vol_date in unusual_volume_days:
                days_before = (news_date - vol_date).days
                if 1 <= days_before <= 5:
                    suspicious_matches += 1
        
        confidence = min(suspicious_matches / max(len(news_release_dates), 1), 1.0)
        
        return {
            "potential_insider_activity": confidence > 0.5,
            "confidence": confidence,
            "suspicious_volume_events": suspicious_matches,
            "avg_days_before_news": 3 if suspicious_matches > 0 else 0,
            "regulatory_flag": confidence > 0.8
        }
    
    def front_running_detection(self, 
                               large_order_announcement: Dict,
                               pre_announcement_trades: List[Dict]) -> Dict:
        """Detect front-running: trading before large order execution"""
        if not pre_announcement_trades:
            return {"front_running_detected": False}
        
        announcement_time = large_order_announcement.get("timestamp")
        announcement_side = large_order_announcement.get("side")  # buy or sell
        
        # Check trades in 5 minutes before announcement
        suspicious_trades = []
        for trade in pre_announcement_trades:
            trade_time = trade.get("timestamp")
            if isinstance(trade_time, str):
                trade_time = datetime.fromisoformat(trade_time.replace('Z', '+00:00'))
            
            time_diff = (announcement_time - trade_time).total_seconds() / 60
            if 0 < time_diff <= 5:  # Within 5 minutes
                # Same direction as upcoming large order
                if trade.get("side") == announcement_side:
                    suspicious_trades.append(trade)
        
        suspicious_volume = sum(t.get("size", 0) for t in suspicious_trades)
        total_volume = sum(t.get("size", 0) for t in pre_announcement_trades)
        
        ratio = suspicious_volume / total_volume if total_volume > 0 else 0
        
        return {
            "front_running_detected": ratio > 0.3 and len(suspicious_trades) >= 3,
            "confidence": min(ratio * 2, 1.0),
            "suspicious_trades_count": len(suspicious_trades),
            "suspicious_volume": suspicious_volume,
            "pre_announcement_window_min": 5,
            "recommendation": "Report to compliance" if ratio > 0.5 else "Monitor"
        }
    
    def get_manipulation_report(self, symbol: str = None) -> Dict:
        """Get comprehensive manipulation detection report"""
        patterns = self.detected_patterns
        if symbol:
            patterns = [p for p in patterns if p.symbol == symbol]
        
        by_type = {}
        for p in patterns:
            t = p.pattern_type.value
            by_type[t] = by_type.get(t, {"count": 0, "max_confidence": 0})
            by_type[t]["count"] += 1
            by_type[t]["max_confidence"] = max(by_type[t]["max_confidence"], p.confidence)
        
        return {
            "total_patterns_detected": len(patterns),
            "by_type": by_type,
            "high_severity_count": sum(1 for p in patterns if p.severity in ["high", "critical"]),
            "symbols_monitored": len(set(p.symbol for p in patterns)),
            "last_24h_patterns": sum(1 for p in patterns 
                                    if p.timestamp > datetime.utcnow() - timedelta(hours=24)),
            "market_health_score": max(0, 100 - len(patterns) * 2)
        }
