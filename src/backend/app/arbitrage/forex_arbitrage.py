"""Forex Arbitrage Scanner - Cross-broker and latency arbitrage"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ForexQuote:
    pair: str
    bid: float
    ask: float
    broker: str
    timestamp: datetime

class ForexArbitrageScanner:
    """Scan for forex arbitrage opportunities across brokers"""
    
    def __init__(self):
        self.brokers = ["FXCM", "OANDA", "IG", "Saxo", "CMC", "Pepperstone"]
        self.major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD"]
        self.cross_pairs = ["EURGBP", "EURJPY", "GBPJPY", "AUDJPY"]
        self.min_spread_threshold = 0.0001  # 1 pip
        self.quotes: Dict[str, List[ForexQuote]] = {}
    
    def add_quote(self, quote: ForexQuote):
        """Add forex quote from broker"""
        if quote.pair not in self.quotes:
            self.quotes[quote.pair] = []
        self.quotes[quote.pair].append(quote)
    
    def find_simple_arbitrage(self, pair: str) -> List[Dict]:
        """Find simple arbitrage: buy low at one broker, sell high at another"""
        if pair not in self.quotes:
            return []
        
        quotes = self.quotes[pair]
        if len(quotes) < 2:
            return []
        
        opportunities = []
        
        # Find best bid and best ask across brokers
        best_bid = max(quotes, key=lambda q: q.bid)
        best_ask = min(quotes, key=lambda q: q.ask)
        
        if best_bid.broker == best_ask.broker:
            return []
        
        # Calculate profit
        spread = best_bid.bid - best_ask.ask
        spread_pips = spread * 10000  # For most pairs
        
        if spread > self.min_spread_threshold:
            # Account for transaction costs
            profit_after_costs = spread - 0.0002  # 2 pip round-trip cost
            
            if profit_after_costs > 0:
                opportunities.append({
                    "pair": pair,
                    "type": "SIMPLE_ARBITRAGE",
                    "buy_broker": best_ask.broker,
                    "buy_price": best_ask.ask,
                    "sell_broker": best_bid.broker,
                    "sell_price": best_bid.bid,
                    "spread": round(spread, 5),
                    "spread_pips": round(spread_pips, 1),
                    "net_profit_pips": round(profit_after_costs * 10000, 1),
                    "profit_pct": round(profit_after_costs / best_ask.ask * 100, 4),
                    "urgency": "HIGH" if profit_after_costs > 0.0005 else "MEDIUM"
                })
        
        return opportunities
    
    def scan_all_pairs(self) -> List[Dict]:
        """Scan all pairs for arbitrage"""
        all_opportunities = []
        
        for pair in self.major_pairs + self.cross_pairs:
            ops = self.find_simple_arbitrage(pair)
            all_opportunities.extend(ops)
        
        return sorted(all_opportunities, key=lambda x: x["net_profit_pips"], reverse=True)
    
    def calculate_latency_arbitrage_window(self, 
                                         quotes: List[ForexQuote],
                                         latency_ms: int = 100) -> Dict:
        """Calculate if latency arbitrage is possible"""
        if len(quotes) < 2:
            return {"possible": False}
        
        # Sort by timestamp
        quotes_sorted = sorted(quotes, key=lambda q: q.timestamp)
        
        # Find fastest and slowest feeds
        fastest = quotes_sorted[0]
        slowest = quotes_sorted[-1]
        
        # If slow broker hasn't updated price yet
        time_diff = (slowest.timestamp - fastest.timestamp).total_seconds() * 1000
        
        if time_diff > latency_ms:
            # Check if price moved enough
            price_diff = abs(fastest.bid - slowest.bid)
            
            if price_diff > 0.0002:  # 2 pips moved
                return {
                    "possible": True,
                    "strategy": "FRONT_RUN_SLOW_BROKER",
                    "fast_broker": fastest.broker,
                    "slow_broker": slowest.broker,
                    "time_advantage_ms": round(time_diff, 0),
                    "expected_price_move_pips": round(price_diff * 10000, 1),
                    "window_valid": time_diff > latency_ms
                }
        
        return {"possible": False, "reason": "No significant latency difference"}
    
    def get_best_prices(self, pair: str) -> Dict:
        """Get best bid/ask across all brokers"""
        if pair not in self.quotes:
            return {"error": "No quotes available"}
        
        quotes = self.quotes[pair]
        
        best_bid = max(quotes, key=lambda q: q.bid)
        best_ask = min(quotes, key=lambda q: q.ask)
        
        avg_spread = statistics.mean([(q.ask - q.bid) for q in quotes]) * 10000
        
        return {
            "pair": pair,
            "best_bid": best_bid.bid,
            "best_bid_broker": best_bid.broker,
            "best_ask": best_ask.ask,
            "best_ask_broker": best_ask.broker,
            "effective_spread": round((best_ask.ask - best_bid.bid) * 10000, 2),
            "avg_broker_spread": round(avg_spread, 2),
            "savings_pips": round((avg_spread - (best_ask.ask - best_bid.bid) * 10000), 2)
        }
    
    def monitor_for_arbitrage(self, watchlist: List[str], 
                            min_profit_pips: float = 1.0) -> List[Dict]:
        """Continuous monitoring for arbitrage opportunities"""
        alerts = []
        
        for pair in watchlist:
            opportunities = self.find_simple_arbitrage(pair)
            
            for opp in opportunities:
                if opp["net_profit_pips"] >= min_profit_pips:
                    alerts.append({
                        "alert_type": "ARBITRAGE_OPPORTUNITY",
                        "timestamp": datetime.utcnow().isoformat(),
                        **opp
                    })
        
        return sorted(alerts, key=lambda x: x["net_profit_pips"], reverse=True)

import statistics
