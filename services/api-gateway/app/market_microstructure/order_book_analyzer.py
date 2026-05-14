"""Order Book Analyzer"""
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class PriceLevel:
    price: float
    size: float
    order_count: int

class OrderBookAnalyzer:
    """Analyze L2/L3 order book data"""
    
    def calculate_spread(self, best_bid: float, best_ask: float) -> Dict:
        """Calculate bid-ask spread metrics"""
        spread = best_ask - best_bid
        mid = (best_ask + best_bid) / 2
        spread_bps = (spread / mid) * 10000
        
        return {
            "bid": best_bid,
            "ask": best_ask,
            "spread": round(spread, 4),
            "mid": round(mid, 4),
            "spread_bps": round(spread_bps, 2)
        }
    
    def depth_analysis(self, bids: List[PriceLevel], 
                      asks: List[PriceLevel]) -> Dict:
        """Analyze order book depth"""
        bid_depth = sum(level.size for level in bids)
        ask_depth = sum(level.size for level in asks)
        
        # Calculate depth at different levels
        bid_depth_1pct = sum(l.size for l in bids if l.price >= bids[0].price * 0.99)
        ask_depth_1pct = sum(l.size for l in asks if l.price <= asks[0].price * 1.01)
        
        imbalance = (bid_depth - ask_depth) / (bid_depth + ask_depth) if (bid_depth + ask_depth) > 0 else 0
        
        return {
            "total_bid_depth": bid_depth,
            "total_ask_depth": ask_depth,
            "bid_depth_1pct": bid_depth_1pct,
            "ask_depth_1pct": ask_depth_1pct,
            "depth_imbalance": round(imbalance, 3),
            "buy_pressure": imbalance > 0.1,
            "sell_pressure": imbalance < -0.1
        }
    
    def price_impact(self, order_size: float, side: str,
                    book_levels: List[PriceLevel]) -> Dict:
        """Estimate price impact for an order"""
        remaining = order_size
        avg_price = 0
        total_cost = 0
        levels_consumed = 0
        
        for level in book_levels:
            if remaining <= 0:
                break
            
            fill_size = min(remaining, level.size)
            total_cost += fill_size * level.price
            remaining -= fill_size
            levels_consumed += 1
        
        if order_size > 0:
            avg_price = total_cost / order_size
        
        fully_filled = remaining <= 0
        
        return {
            "order_size": order_size,
            "avg_fill_price": round(avg_price, 4),
            "total_cost": round(total_cost, 2),
            "levels_consumed": levels_consumed,
            "fully_filled": fully_filled,
            "unfilled": max(0, remaining)
        }
    
    def detect_iceberg_orders(self, level_updates: List[Tuple[float, float]]) -> Dict:
        """Detect potential iceberg orders from level updates"""
        # Iceberg detection: repeated refills at same price
        price_counts = {}
        for price, size in level_updates:
            if price not in price_counts:
                price_counts[price] = {"count": 0, "total_size": 0}
            price_counts[price]["count"] += 1
            price_counts[price]["total_size"] += size
        
        # Suspected icebergs: prices with 3+ refills
        suspected = {p: v for p, v in price_counts.items() if v["count"] >= 3}
        
        return {
            "suspected_iceberg_levels": len(suspected),
            "details": {p: v for p, v in suspected.items()},
            "detection_confidence": "high" if len(suspected) > 0 else "none"
        }
    
    def book_imbalance_signal(self, bid_levels: List[PriceLevel],
                             ask_levels: List[PriceLevel], 
                             lookback: int = 5) -> Dict:
        """Generate trading signal from order book imbalance"""
        # Top of book imbalance
        bid_size_top = bid_levels[0].size if bid_levels else 0
        ask_size_top = ask_levels[0].size if ask_levels else 0
        
        imbalance = (bid_size_top - ask_size_top) / (bid_size_top + ask_size_top) if (bid_size_top + ask_size_top) > 0 else 0
        
        # Signal generation
        if imbalance > 0.3:
            signal = "strong_buy"
            strength = abs(imbalance)
        elif imbalance > 0.1:
            signal = "buy"
            strength = abs(imbalance)
        elif imbalance < -0.3:
            signal = "strong_sell"
            strength = abs(imbalance)
        elif imbalance < -0.1:
            signal = "sell"
            strength = abs(imbalance)
        else:
            signal = "neutral"
            strength = 0
        
        return {
            "imbalance": round(imbalance, 3),
            "signal": signal,
            "strength": round(strength, 2),
            "predictive_power": "high" if abs(imbalance) > 0.4 else "medium" if abs(imbalance) > 0.2 else "low"
        }
