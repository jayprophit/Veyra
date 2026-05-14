"""Dark Pool Monitor - Track off-exchange institutional trading"""
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TradeSizeTier(Enum):
    SMALL = "small"  # < 10K shares
    MEDIUM = "medium"  # 10K - 100K
    LARGE = "large"  # 100K - 500K
    INSTITUTIONAL = "institutional"  # > 500K

@dataclass
class DarkPoolTrade:
    symbol: str
    price: float
    size: int
    timestamp: datetime
    venue: str  # Dark pool venue
    side: str  # BUY or SELL (inferred)

class DarkPoolMonitor:
    """Monitor dark pool and off-exchange trading activity"""
    
    def __init__(self):
        self.trades: List[DarkPoolTrade] = []
        self.size_thresholds = {
            TradeSizeTier.SMALL: 10000,
            TradeSizeTier.MEDIUM: 100000,
            TradeSizeTier.LARGE: 500000
        }
        self.dark_pool_venues = [
            "Credit Suisse CrossFinder",
            "Goldman Sachs Sigma X",
            "UBS ATS",
            "Morgan Stanley MS Pool",
            "Instinet",
            "ITG Posit",
            "Liquidnet"
        ]
    
    def add_trade(self, trade: DarkPoolTrade):
        """Add dark pool trade"""
        self.trades.append(trade)
        # Keep last 10000
        self.trades = self.trades[-10000:]
    
    def get_trades_by_symbol(self, symbol: str, 
                            hours: int = 24) -> List[DarkPoolTrade]:
        """Get dark pool trades for symbol"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            t for t in self.trades 
            if t.symbol == symbol and t.timestamp >= cutoff
        ]
    
    def classify_trade_size(self, size: int) -> TradeSizeTier:
        """Classify trade by size"""
        if size >= self.size_thresholds[TradeSizeTier.LARGE]:
            return TradeSizeTier.INSTITUTIONAL
        elif size >= self.size_thresholds[TradeSizeTier.MEDIUM]:
            return TradeSizeTier.LARGE
        elif size >= self.size_thresholds[TradeSizeTier.SMALL]:
            return TradeSizeTier.MEDIUM
        return TradeSizeTier.SMALL
    
    def analyze_institutional_activity(self, symbol: str) -> Dict:
        """Analyze institutional activity in dark pools"""
        recent_trades = self.get_trades_by_symbol(symbol, hours=24)
        
        if not recent_trades:
            return {"error": "No recent dark pool activity"}
        
        # Separate by size
        institutional = [t for t in recent_trades 
                        if self.classify_trade_size(t.size) == TradeSizeTier.INSTITUTIONAL]
        large = [t for t in recent_trades 
                if self.classify_trade_size(t.size) == TradeSizeTier.LARGE]
        
        # Estimate buy/sell (using price vs market as proxy)
        buy_volume = sum(t.size for t in recent_trades if t.side == "BUY")
        sell_volume = sum(t.size for t in recent_trades if t.side == "SELL")
        
        total_volume = sum(t.size for t in recent_trades)
        
        buy_pct = buy_volume / total_volume * 100 if total_volume > 0 else 50
        
        # Dark pool % of total market (estimation)
        # Calculate average daily volume from historical data
        if len(self.trades) < 100:
            avg_daily_volume = 1000000  # Fallback if insufficient data
        else:
            recent_trades = self.trades[-100:]
            volume_by_day = {}
            for trade in recent_trades:
                date_key = trade.timestamp.strftime('%Y-%m-%d')
                volume_by_day[date_key] = volume_by_day.get(date_key, 0) + trade.size
            
            avg_daily_volume = sum(volume_by_day.values()) / len(volume_by_day) if volume_by_day else 1000000
        
        dark_pool_pct = (total_volume / avg_daily_volume) * 100 if avg_daily_volume > 0 else 0
        
        return {
            "symbol": symbol,
            "dark_pool_volume_24h": total_volume,
            "institutional_blocks": len(institutional),
            "large_blocks": len(large),
            "buy_percentage": round(buy_pct, 1),
            "sell_percentage": round(100 - buy_pct, 1),
            "sentiment": "ACCUMULATING" if buy_pct > 60 else "DISTRIBUTING" if buy_pct < 40 else "NEUTRAL",
            "dark_pool_pct_of_volume": round(dark_pool_pct, 1),
            "significance": "HIGH" if dark_pool_pct > 40 else "MEDIUM" if dark_pool_pct > 20 else "LOW"
        }
    
    def detect_accumulation_pattern(self, symbol: str, 
                                   days: int = 5) -> Dict:
        """Detect institutional accumulation pattern"""
        recent = [
            t for t in self.trades 
            if t.symbol == symbol and 
            (datetime.utcnow() - t.timestamp).days <= days
        ]
        
        if len(recent) < 10:
            return {"error": "Insufficient data"}
        
        # Daily aggregation
        daily_buy: Dict[str, int] = {}
        daily_sell: Dict[str, int] = {}
        
        for trade in recent:
            day = trade.timestamp.strftime("%Y-%m-%d")
            if day not in daily_buy:
                daily_buy[day] = 0
                daily_sell[day] = 0
            
            if trade.side == "BUY":
                daily_buy[day] += trade.size
            else:
                daily_sell[day] += trade.size
        
        # Analyze pattern
        buy_days = sum(1 for day in daily_buy if daily_buy[day] > daily_sell.get(day, 0))
        total_days = len(daily_buy)
        
        # Stealth accumulation = consistent buying over days
        stealth_score = buy_days / total_days * 100 if total_days > 0 else 0
        
        total_buy = sum(daily_buy.values())
        total_sell = sum(daily_sell.values())
        net = total_buy - total_sell
        
        return {
            "symbol": symbol,
            "pattern": "STEALTH_ACCUMULATION" if stealth_score > 70 else "DISTRIBUTION" if stealth_score < 30 else "MIXED",
            "stealth_score": round(stealth_score, 1),
            "buy_days": buy_days,
            "total_days": total_days,
            "net_shares": net,
            "avg_daily_net": round(net / days, 0),
            "implication": "Institutional building position" if net > 0 else "Institutional reducing position"
        }
    
    def get_premium_pricing(self, symbol: str) -> Dict:
        """Analyze if dark pool trades at premium/discount to market"""
        recent = self.get_trades_by_symbol(symbol, hours=4)
        
        if len(recent) < 5:
            return {"error": "Insufficient recent trades"}
        
        # Market price estimation from multiple sources
        if len(recent) >= 2:
            # Use weighted average of recent dark pool trades
            recent_prices = [t.price for t in recent[-5:]]
            market_price = sum(recent_prices) / len(recent_prices)
        else:
            market_price = recent[-1].price if recent else 100.0
        
        premiums = []
        for trade in recent:
            premium = (trade.price - market_price) / market_price * 100
            premiums.append(premium)
        
        avg_premium = statistics.mean(premiums)
        
        return {
            "symbol": symbol,
            "avg_premium_to_market": round(avg_premium, 3),
            "implication": "PAYING_UP" if avg_premium > 0.05 else "DISCOUNT" if avg_premium < -0.05 else "FAIR_VALUE",
            "urgency": "HIGH" if avg_premium > 0.1 else "MEDIUM" if avg_premium > 0.05 else "LOW",
            "trade_count": len(recent)
        }
    
    def generate_dark_pool_alerts(self, watchlist: List[str]) -> List[Dict]:
        """Generate alerts for unusual dark pool activity"""
        alerts = []
        
        for symbol in watchlist:
            activity = self.analyze_institutional_activity(symbol)
            
            if "error" in activity:
                continue
            
            # Alert on high dark pool %
            if activity["dark_pool_pct_of_volume"] > 50:
                alerts.append({
                    "symbol": symbol,
                    "alert_type": "HIGH_DARK_POOL_VOLUME",
                    "dark_pool_pct": activity["dark_pool_pct_of_volume"],
                    "sentiment": activity["sentiment"],
                    "urgency": "HIGH",
                    "message": f"{activity['dark_pool_pct_of_volume']:.1f}% of volume in dark pools - {activity['sentiment']}"
                })
            
            # Alert on accumulation
            elif activity["buy_percentage"] > 70:
                alerts.append({
                    "symbol": symbol,
                    "alert_type": "INSTITUTIONAL_ACCUMULATION",
                    "buy_pct": activity["buy_percentage"],
                    "urgency": "MEDIUM",
                    "message": f"{activity['buy_percentage']:.1f}% buy-side in dark pools"
                })
        
        return sorted(alerts, key=lambda x: x["urgency"], reverse=True)
    
    def get_market_wide_summary(self) -> Dict:
        """Get market-wide dark pool summary"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        today_trades = [t for t in self.trades if t.timestamp.strftime("%Y-%m-%d") == today]
        
        total_volume = sum(t.size for t in today_trades)
        institutional_volume = sum(
            t.size for t in today_trades 
            if self.classify_trade_size(t.size) == TradeSizeTier.INSTITUTIONAL
        )
        
        # Top tickers
        by_symbol: Dict[str, int] = {}
        for t in today_trades:
            by_symbol[t.symbol] = by_symbol.get(t.symbol, 0) + t.size
        
        top_tickers = sorted(by_symbol.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_dark_pool_volume": total_volume,
            "institutional_volume": institutional_volume,
            "institutional_pct": round(institutional_volume / total_volume * 100, 1) if total_volume > 0 else 0,
            "top_active_tickers": [t[0] for t in top_tickers],
            "avg_trade_size": round(total_volume / len(today_trades), 0) if today_trades else 0,
            "activity_level": "HIGH" if total_volume > 100000000 else "MEDIUM" if total_volume > 50000000 else "LOW"
        }

import statistics
from datetime import timedelta
