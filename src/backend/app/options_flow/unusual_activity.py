"""Unusual Options Activity Detector - Find smart money flows"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

@dataclass
class OptionsTrade:
    symbol: str
    option_type: OptionType
    strike: float
    expiry: datetime
    volume: int
    open_interest: int
    premium: float
    timestamp: datetime

class UnusualActivityDetector:
    """Detect unusual options activity indicating smart money"""
    
    def __init__(self):
        self.volume_threshold = 2.0  # 2x average volume
        self.premium_threshold = 100000  # $100k minimum
        self.history: Dict[str, List[OptionsTrade]] = {}
    
    def add_trade(self, trade: OptionsTrade):
        """Add options trade to history"""
        if trade.symbol not in self.history:
            self.history[trade.symbol] = []
        self.history[trade.symbol].append(trade)
    
    def detect_unusual_volume(self, symbol: str, 
                             lookback_days: int = 20) -> List[Dict]:
        """Detect options with unusual volume"""
        if symbol not in self.history:
            return []
        
        trades = self.history[symbol]
        if len(trades) < lookback_days:
            return []
        
        # Calculate average volume by strike/expiry
        volume_by_contract: Dict[str, List[int]] = {}
        for trade in trades:
            key = f"{trade.strike}_{trade.expiry}_{trade.option_type.value}"
            if key not in volume_by_contract:
                volume_by_contract[key] = []
            volume_by_contract[key].append(trade.volume)
        
        unusual = []
        
        # Check today's trades
        today_trades = [t for t in trades if (datetime.utcnow() - t.timestamp).days < 1]
        
        for trade in today_trades:
            key = f"{trade.strike}_{trade.expiry}_{trade.option_type.value}"
            avg_volume = statistics.mean(volume_by_contract.get(key, [trade.volume]))
            
            volume_ratio = trade.volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > self.volume_threshold:
                unusual.append({
                    "symbol": symbol,
                    "strike": trade.strike,
                    "expiry": trade.expiry.strftime("%Y-%m-%d"),
                    "type": trade.option_type.value.upper(),
                    "volume": trade.volume,
                    "avg_volume": round(avg_volume, 0),
                    "volume_ratio": round(volume_ratio, 1),
                    "premium": trade.premium,
                    "signal_strength": "HIGH" if volume_ratio > 5 else "MEDIUM"
                })
        
        return sorted(unusual, key=lambda x: x["volume_ratio"], reverse=True)
    
    def detect_sweep_activity(self, trades: List[OptionsTrade]) -> List[Dict]:
        """Detect sweep activity (aggressive buying across exchanges)"""
        sweeps = []
        
        # Group by contract
        by_contract: Dict[str, List[OptionsTrade]] = {}
        for trade in trades:
            key = f"{trade.symbol}_{trade.strike}_{trade.expiry}_{trade.option_type.value}"
            if key not in by_contract:
                by_contract[key] = []
            by_contract[key].append(trade)
        
        for contract_key, contract_trades in by_contract.items():
            # Multiple rapid trades = sweep
            if len(contract_trades) >= 3:
                total_volume = sum(t.volume for t in contract_trades)
                total_premium = sum(t.premium for t in contract_trades)
                
                if total_premium > self.premium_threshold:
                    parts = contract_key.split("_")
                    sweeps.append({
                        "symbol": parts[0],
                        "strike": float(parts[1]),
                        "expiry": parts[2],
                        "type": parts[3].upper(),
                        "trade_count": len(contract_trades),
                        "total_volume": total_volume,
                        "total_premium": total_premium,
                        "urgency": "HIGH" if len(contract_trades) > 5 else "MEDIUM",
                        "implication": "Smart money urgent entry"
                    })
        
        return sorted(sweeps, key=lambda x: x["total_premium"], reverse=True)
    
    def analyze_put_call_ratio(self, symbol: str) -> Dict:
        """Analyze put/call ratio for sentiment"""
        if symbol not in self.history:
            return {"error": "No data"}
        
        trades = self.history[symbol]
        
        calls = sum(t.volume for t in trades if t.option_type == OptionType.CALL)
        puts = sum(t.volume for t in trades if t.option_type == OptionType.PUT)
        
        if calls == 0:
            pcr = float('inf')
        else:
            pcr = puts / calls
        
        # Interpret
        if pcr < 0.7:
            sentiment = "BULLISH"
            contrarian = "Caution - extreme bullishness"
        elif pcr < 1.0:
            sentiment = "SLIGHTLY_BULLISH"
            contrarian = "Neutral"
        elif pcr < 1.3:
            sentiment = "SLIGHTLY_BEARISH"
            contrarian = "Neutral"
        else:
            sentiment = "BEARISH"
            contrarian = "Opportunity - extreme fear"
        
        return {
            "symbol": symbol,
            "put_call_ratio": round(pcr, 2),
            "call_volume": calls,
            "put_volume": puts,
            "sentiment": sentiment,
            "contrarian_signal": contrarian,
            "total_premium": sum(t.premium for t in trades)
        }
    
    def detect_whale_positions(self, min_premium: float = 500000) -> List[Dict]:
        """Detect large whale positions"""
        whales = []
        
        for symbol, trades in self.history.items():
            large_trades = [t for t in trades if t.premium >= min_premium]
            
            for trade in large_trades:
                whales.append({
                    "symbol": symbol,
                    "type": trade.option_type.value.upper(),
                    "strike": trade.strike,
                    "expiry": trade.expiry.strftime("%Y-%m-%d"),
                    "premium": trade.premium,
                    "volume": trade.volume,
                    "direction": "BULLISH" if trade.option_type == OptionType.CALL else "BEARISH",
                    "confidence": "HIGH" if trade.premium > 1000000 else "MEDIUM"
                })
        
        return sorted(whales, key=lambda x: x["premium"], reverse=True)
    
    def get_unusual_activity_summary(self, watchlist: List[str]) -> Dict:
        """Get summary of unusual activity for watchlist"""
        summary = {
            "high_volume_alerts": [],
            "sweep_activity": [],
            "whale_positions": [],
            "sentiment_summary": {}
        }
        
        for symbol in watchlist:
            # High volume
            unusual = self.detect_unusual_volume(symbol)
            summary["high_volume_alerts"].extend(unusual[:3])
            
            # Sentiment
            if symbol in self.history:
                sentiment = self.analyze_put_call_ratio(symbol)
                if "error" not in sentiment:
                    summary["sentiment_summary"][symbol] = sentiment
        
        # Whale positions
        summary["whale_positions"] = self.detect_whale_positions()[:10]
        
        # Total signals
        summary["total_unusual_signals"] = (
            len(summary["high_volume_alerts"]) +
            len(summary["sweep_activity"]) +
            len(summary["whale_positions"])
        )
        
        return summary

import statistics
