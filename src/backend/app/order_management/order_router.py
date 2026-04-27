"""Smart Order Router - Route orders to optimal venues"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TWAP = "twap"
    VWAP = "vwap"
    ICEBERG = "iceberg"

class TimeInForce(Enum):
    DAY = "day"
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"

@dataclass
class Order:
    symbol: str
    side: str  # BUY or SELL
    quantity: int
    order_type: OrderType
    price: Optional[float]
    time_in_force: TimeInForce
    strategy: str = "NORMAL"

@dataclass
class Venue:
    name: str
    fees_per_share: float
    liquidity_score: float
    latency_ms: float
    market_share_pct: float

class SmartOrderRouter:
    """Intelligently route orders to best execution venues"""
    
    def __init__(self):
        self.venues: List[Venue] = []
        self.order_history: List[Dict] = []
        self._init_default_venues()
    
    def _init_default_venues(self):
        """Initialize default trading venues"""
        self.venues = [
            Venue("NYSE", 0.003, 0.95, 10, 25),
            Venue("NASDAQ", 0.002, 0.92, 8, 20),
            Venue("IEX", 0.001, 0.85, 350, 3),  # Slow but fair
            Venue("BATS", 0.0015, 0.88, 5, 15),
            Venue("Dark Pool A", 0.0025, 0.70, 15, 10),
            Venue("Dark Pool B", 0.002, 0.75, 12, 8)
        ]
    
    def route_order(self, order: Order, 
                   urgency: str = "NORMAL") -> Dict:
        """Determine optimal routing for order"""
        
        # Score each venue
        venue_scores = []
        for venue in self.venues:
            score = self._score_venue(venue, order, urgency)
            venue_scores.append((venue, score))
        
        # Sort by score
        venue_scores.sort(key=lambda x: x[1], reverse=True)
        
        best_venue = venue_scores[0][0]
        
        # Determine execution strategy
        strategy = self._determine_strategy(order, urgency, best_venue)
        
        # Calculate expected costs
        costs = self._estimate_costs(order, best_venue, strategy)
        
        return {
            "order": {
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "type": order.order_type.value
            },
            "routing_decision": {
                "primary_venue": best_venue.name,
                "backup_venues": [v.name for v, s in venue_scores[1:3]],
                "routing_score": round(venue_scores[0][1], 2)
            },
            "execution_strategy": strategy,
            "cost_estimate": costs,
            "market_impact_estimate": self._estimate_market_impact(order),
            "timing_recommendation": self._get_timing_recommendation(order.symbol)
        }
    
    def _score_venue(self, venue: Venue, order: Order, 
                    urgency: str) -> float:
        """Score venue for this order"""
        score = 0
        
        # Liquidity score (higher is better)
        score += venue.liquidity_score * 30
        
        # Cost score (lower fees = higher score)
        max_fee = 0.005
        fee_score = (1 - venue.fees_per_share / max_fee) * 25
        score += max(0, fee_score)
        
        # Latency score (for urgent orders)
        if urgency == "HIGH":
            latency_score = (1 - min(venue.latency_ms, 100) / 100) * 20
            score += latency_score
        elif urgency == "LOW":
            # Prefer low-cost venues for non-urgent
            score += fee_score * 1.5
        
        # Market share (liquidity proxy)
        score += venue.market_share_pct * 0.5
        
        # Dark pool preference for large orders
        if order.quantity > 10000 and "Dark Pool" in venue.name:
            score += 15
        
        return score
    
    def _determine_strategy(self, order: Order, urgency: str, 
                           venue: Venue) -> Dict:
        """Determine execution strategy"""
        
        # Large order check
        if order.quantity > 10000:
            if urgency == "LOW":
                return {
                    "type": "TWAP",
                    "description": "Time-Weighted Average Price",
                    "slices": 10,
                    "duration_minutes": 60,
                    "aggression": "PASSIVE"
                }
            else:
                return {
                    "type": "VWAP",
                    "description": "Volume-Weighted Average Price",
                    "slices": 5,
                    "duration_minutes": 30,
                    "aggression": "ACTIVE"
                }
        
        # Small orders - simple execution
        if order.quantity < 1000:
            return {
                "type": "SINGLE_SHOT",
                "description": "Execute immediately",
                "order_type": "LIMIT" if order.price else "MARKET",
                "aggression": "AGGRESSIVE" if urgency == "HIGH" else "NORMAL"
            }
        
        # Medium orders - iceberg
        return {
            "type": "ICEBERG",
            "description": "Hidden size, show 10% at a time",
            "display_qty": max(100, order.quantity // 10),
            "refresh_trigger": 90
        }
    
    def _estimate_costs(self, order: Order, venue: Venue, 
                       strategy: Dict) -> Dict:
        """Estimate execution costs"""
        # Commission
        commission = venue.fees_per_share * order.quantity
        
        # Spread cost estimate
        spread_cost = 0.01 * order.quantity  # $0.01 per share assumption
        
        # Market impact (simplified model)
        participation_rate = order.quantity / 100000  # Assumed ADV
        impact_bps = 10 * participation_rate ** 0.5  # Square root model
        impact_cost = (impact_bps / 10000) * (order.price or 100) * order.quantity
        
        total_cost = commission + spread_cost + impact_cost
        
        return {
            "commission": round(commission, 2),
            "spread_cost": round(spread_cost, 2),
            "market_impact": round(impact_cost, 2),
            "total_estimate": round(total_cost, 2),
            "bps_of_notional": round((total_cost / ((order.price or 100) * order.quantity)) * 10000, 1)
        }
    
    def _estimate_market_impact(self, order: Order) -> Dict:
        """Estimate temporary and permanent market impact"""
        # Kyle's lambda approximation
        qty = order.quantity
        adv = 1000000  # Assumed average daily volume
        
        participation = qty / adv
        volatility = 0.02  # Assumed 2% daily volatility
        
        # Temporary impact (decays quickly)
        temp_impact = volatility * (participation ** 0.6) * 100  # in bps
        
        # Permanent impact (information leakage)
        perm_impact = volatility * (participation ** 0.3) * 50  # in bps
        
        return {
            "temporary_bps": round(temp_impact, 1),
            "permanent_bps": round(perm_impact, 1),
            "total_expected_bps": round(temp_impact + perm_impact, 1),
            "impact_level": "HIGH" if participation > 0.1 else "MEDIUM" if participation > 0.05 else "LOW"
        }
    
    def _get_timing_recommendation(self, symbol: str) -> str:
        """Recommend optimal execution time"""
        # Simple time-of-day recommendations
        # In real implementation, would analyze volume curves
        return "EXECUTE_DURING_OPEN_HOUR"  # 9:30-10:30 AM typically high liquidity
    
    def analyze_execution_quality(self, orders: List[Dict]) -> Dict:
        """Analyze execution quality metrics"""
        if not orders:
            return {"error": "No orders to analyze"}
        
        total_cost = sum(o.get("slippage_bps", 0) for o in orders)
        avg_cost = total_cost / len(orders)
        
        fill_rates = [o.get("fill_rate", 0) for o in orders]
        avg_fill = sum(fill_rates) / len(fill_rates)
        
        return {
            "orders_analyzed": len(orders),
            "avg_slippage_bps": round(avg_cost, 2),
            "avg_fill_rate": round(avg_fill, 2),
            "execution_score": "EXCELLENT" if avg_cost < 5 else "GOOD" if avg_cost < 10 else "POOR",
            "improvement_areas": self._identify_improvements(orders)
        }
    
    def _identify_improvements(self, orders: List[Dict]) -> List[str]:
        """Identify areas for execution improvement"""
        issues = []
        
        avg_slippage = sum(o.get("slippage_bps", 0) for o in orders) / len(orders)
        if avg_slippage > 10:
            issues.append("Consider more passive execution strategies")
        
        partial_fills = sum(1 for o in orders if o.get("fill_rate", 0) < 1.0)
        if partial_fills / len(orders) > 0.3:
            issues.append("Review venue selection for better fill rates")
        
        return issues if issues else ["Execution quality is satisfactory"]
