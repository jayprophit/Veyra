"""
Ghost Portfolio - Track Missed Opportunities
=============================================
Track trades you almost made but didn't
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GhostAction(Enum):
    ALMOST_BUY = "almost_buy"
    ALMOST_SELL = "almost_sell"
    WATCHLIST_MISSED = "watchlist_missed"


@dataclass
class GhostTrade:
    symbol: str
    action: GhostAction
    date_contemplated: str
    price_contemplated: float
    quantity_considered: int
    actual_outcome: float  # What price became
    opportunity_cost: float  # P&L missed
    reason_passed: str
    lesson: str


@dataclass
class GhostPortfolio:
    """Collection of missed opportunities"""
    trades: List[GhostTrade] = field(default_factory=list)
    total_opportunity_cost: float = 0.0
    lessons_learned: List[str] = field(default_factory=list)
    
    def add_missed_trade(self, trade: GhostTrade):
        """Record a missed opportunity"""
        self.trades.append(trade)
        self.total_opportunity_cost += trade.opportunity_cost
        
        if trade.lesson not in self.lessons_learned:
            self.lessons_learned.append(trade.lesson)
    
    def get_stats(self) -> Dict:
        """Get ghost portfolio statistics"""
        if not self.trades:
            return {"message": "No ghost trades recorded"}
        
        buy_missed = [t for t in self.trades if t.action == GhostAction.ALMOST_BUY]
        sell_missed = [t for t in self.trades if t.action == GhostAction.ALMOST_SELL]
        
        return {
            "total_missed_opportunities": len(self.trades),
            "total_opportunity_cost": round(self.total_opportunity_cost, 2),
            "avg_opportunity_per_trade": round(self.total_opportunity_cost / len(self.trades), 2),
            "buy_opportunities_missed": len(buy_missed),
            "sell_opportunities_missed": len(sell_missed),
            "biggest_miss": max(self.trades, key=lambda x: x.opportunity_cost).symbol,
            "lessons_count": len(self.lessons_learned),
            "lessons": self.lessons_learned[:5]  # Top 5
        }
    
    def get_recommendations(self) -> List[str]:
        """Generate recommendations based on patterns"""
        recs = []
        
        # Pattern analysis
        fear_trades = [t for t in self.trades if "fear" in t.reason_passed.lower()]
        if len(fear_trades) > 3:
            recs.append("Pattern: You often miss trades due to fear. Consider dollar-cost averaging.")
        
        greed_trades = [t for t in self.trades if "too expensive" in t.reason_passed.lower()]
        if len(greed_trades) > 3:
            recs.append("Pattern: You wait for 'perfect' prices. Consider scaling entries.")
        
        if self.total_opportunity_cost > 10000:
            recs.append("Your ghost portfolio is costly. Review entry criteria.")
        
        return recs


class GhostTracker:
    """Track and analyze missed opportunities"""
    
    def __init__(self):
        self.portfolios: Dict[str, GhostPortfolio] = {}
    
    def record_contemplation(
        self,
        user_id: str,
        symbol: str,
        action: str,
        price: float,
        quantity: int,
        reason_passed: str
    ):
        """Record a trade that was considered but not executed"""
        if user_id not in self.portfolios:
            self.portfolios[user_id] = GhostPortfolio()
        
        # Will be updated later with actual outcome
        ghost_trade = GhostTrade(
            symbol=symbol,
            action=GhostAction(action),
            date_contemplated=datetime.now().isoformat(),
            price_contemplated=price,
            quantity_considered=quantity,
            actual_outcome=0,
            opportunity_cost=0,
            reason_passed=reason_passed,
            lesson=""
        )
        
        self.portfolios[user_id].add_missed_trade(ghost_trade)
        return ghost_trade
    
    def update_outcome(
        self,
        user_id: str,
        symbol: str,
        current_price: float,
        lesson: str
    ):
        """Update ghost trade with actual outcome"""
        if user_id not in self.portfolios:
            return
        
        for trade in self.portfolios[user_id].trades:
            if trade.symbol == symbol and trade.actual_outcome == 0:
                trade.actual_outcome = current_price
                
                if trade.action == GhostAction.ALMOST_BUY:
                    trade.opportunity_cost = (current_price - trade.price_contemplated) * trade.quantity_considered
                else:
                    trade.opportunity_cost = (trade.price_contemplated - current_price) * trade.quantity_considered
                
                trade.lesson = lesson
                break
    
    def get_portfolio(self, user_id: str) -> GhostPortfolio:
        """Get user's ghost portfolio"""
        return self.portfolios.get(user_id, GhostPortfolio())
