"""Copy Trading System - Social Trading Feature."""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class TraderProfile:
    user_id: str
    username: str
    is_pro_trader: bool
    followers: List[str]
    total_return_30d: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    aum: float  # Assets under management
    monthly_fee: float  # Fee for copying
    performance_fee_pct: float  # % of profits taken
    trades_copied_count: int
    copy_traders: List[str]  # Users copying this trader

@dataclass
class CopyTrade:
    copy_id: str
    follower_id: str
    trader_id: str
    allocation: float  # Amount allocated
    copy_percentage: float  # % of trader's position to copy
    max_position_size: float
    stop_loss_pct: Optional[float]
    take_profit_pct: Optional[float]
    created_at: datetime
    is_active: bool
    total_pnl: float
    fees_paid: float

class CopyTradingSystem:
    """Social copy trading with performance tracking."""
    
    def __init__(self):
        self.traders: Dict[str, TraderProfile] = {}
        self.copy_relationships: Dict[str, CopyTrade] = {}
        self.pending_copies: List[Dict] = []
        self.performance_history: Dict[str, List[Dict]] = defaultdict(list)
    
    async def register_as_trader(self, user_id: str, username: str,
                                  monthly_fee: float = 0,
                                  performance_fee_pct: float = 20) -> TraderProfile:
        """Register user as pro trader for others to copy."""
        trader = TraderProfile(
            user_id=user_id,
            username=username,
            is_pro_trader=True,
            followers=[],
            total_return_30d=0.0,
            win_rate=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            aum=0.0,
            monthly_fee=monthly_fee,
            performance_fee_pct=performance_fee_pct,
            trades_copied_count=0,
            copy_traders=[]
        )
        
        self.traders[user_id] = trader
        logger.info(f"Trader registered: {username} ({user_id})")
        return trader
    
    async def start_copying(self, follower_id: str, trader_id: str,
                           allocation: float,
                           copy_percentage: float = 100.0,
                           max_position_size: Optional[float] = None,
                           stop_loss_pct: Optional[float] = None,
                           take_profit_pct: Optional[float] = None) -> CopyTrade:
        """Start copying a trader."""
        if trader_id not in self.traders:
            return None
        
        trader = self.traders[trader_id]
        
        copy_id = f"copy_{follower_id}_{trader_id}_{datetime.now().strftime('%H%M%S')}"
        
        copy_trade = CopyTrade(
            copy_id=copy_id,
            follower_id=follower_id,
            trader_id=trader_id,
            allocation=allocation,
            copy_percentage=copy_percentage,
            max_position_size=max_position_size or allocation * 0.1,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct,
            created_at=datetime.now(),
            is_active=True,
            total_pnl=0.0,
            fees_paid=0.0
        )
        
        self.copy_relationships[copy_id] = copy_trade
        trader.copy_traders.append(follower_id)
        trader.followers.append(follower_id)
        trader.aum += allocation
        
        logger.info(f"Copy started: {follower_id} copying {trader_id} with ${allocation}")
        return copy_trade
    
    async def stop_copying(self, copy_id: str) -> bool:
        """Stop copying a trader."""
        if copy_id not in self.copy_relationships:
            return False
        
        copy = self.copy_relationships[copy_id]
        copy.is_active = False
        
        # Update trader AUM
        trader = self.traders.get(copy.trader_id)
        if trader:
            trader.aum -= copy.allocation
            trader.copy_traders.remove(copy.follower_id)
            trader.followers.remove(copy.follower_id)
        
        return True
    
    async def replicate_trade(self, trader_id: str, trade: Dict):
        """Replicate a trade to all followers."""
        if trader_id not in self.traders:
            return []
        
        trader = self.traders[trader_id]
        replicated_trades = []
        
        for copy_id in self.copy_relationships:
            copy = self.copy_relationships[copy_id]
            if copy.trader_id != trader_id or not copy.is_active:
                continue
            
            # Calculate copy size
            copy_qty = trade['quantity'] * (copy.copy_percentage / 100)
            
            # Apply max position limit
            position_value = copy_qty * trade['price']
            if position_value > copy.max_position_size:
                copy_qty = copy.max_position_size / trade['price']
            
            replicated_trade = {
                'copy_id': copy_id,
                'follower_id': copy.follower_id,
                'original_trade_id': trade['trade_id'],
                'symbol': trade['symbol'],
                'side': trade['side'],
                'quantity': copy_qty,
                'price': trade['price'],
                'timestamp': datetime.now().isoformat(),
                'trader_id': trader_id
            }
            
            replicated_trades.append(replicated_trade)
            trader.trades_copied_count += 1
        
        return replicated_trades
    
    async def update_trader_stats(self, trader_id: str, 
                                  return_30d: float,
                                  win_rate: float,
                                  sharpe: float,
                                  max_dd: float):
        """Update trader performance stats."""
        if trader_id not in self.traders:
            return
        
        trader = self.traders[trader_id]
        trader.total_return_30d = return_30d
        trader.win_rate = win_rate
        trader.sharpe_ratio = sharpe
        trader.max_drawdown = max_dd
        
        # Record history
        self.performance_history[trader_id].append({
            'date': datetime.now().isoformat(),
            'return_30d': return_30d,
            'win_rate': win_rate,
            'sharpe': sharpe
        })
    
    async def calculate_fees(self, copy_id: str, period_pnl: float) -> Dict:
        """Calculate performance fees for a copy relationship."""
        if copy_id not in self.copy_relationships:
            return {'error': 'Copy not found'}
        
        copy = self.copy_relationships[copy_id]
        trader = self.traders.get(copy.trader_id)
        
        if not trader:
            return {'error': 'Trader not found'}
        
        monthly_fee = trader.monthly_fee
        performance_fee = 0
        
        if period_pnl > 0:
            performance_fee = period_pnl * (trader.performance_fee_pct / 100)
        
        total_fee = monthly_fee + performance_fee
        copy.fees_paid += total_fee
        
        return {
            'monthly_fee': monthly_fee,
            'performance_fee': performance_fee,
            'total_fee': total_fee,
            'fee_pct': trader.performance_fee_pct
        }
    
    async def get_top_traders(self, limit: int = 10) -> List[Dict]:
        """Get top performing traders."""
        sorted_traders = sorted(
            self.traders.values(),
            key=lambda t: t.sharpe_ratio * t.total_return_30d,
            reverse=True
        )
        
        return [{
            'user_id': t.user_id,
            'username': t.username,
            'return_30d': t.total_return_30d,
            'win_rate': t.win_rate,
            'sharpe': t.sharpe_ratio,
            'max_drawdown': t.max_drawdown,
            'aum': t.aum,
            'followers': len(t.followers),
            'monthly_fee': t.monthly_fee,
            'performance_fee': t.performance_fee_pct
        } for t in sorted_traders[:limit]]
    
    async def get_follower_portfolio(self, follower_id: str) -> Dict:
        """Get copy trading portfolio for a follower."""
        copies = [c for c in self.copy_relationships.values() 
                  if c.follower_id == follower_id and c.is_active]
        
        total_allocated = sum(c.allocation for c in copies)
        total_pnl = sum(c.total_pnl for c in copies)
        total_fees = sum(c.fees_paid for c in copies)
        
        return {
            'follower_id': follower_id,
            'active_copies': len(copies),
            'total_allocated': total_allocated,
            'total_pnl': total_pnl,
            'total_fees': total_fees,
            'net_return': total_pnl - total_fees,
            'copies': [{
                'copy_id': c.copy_id,
                'trader_id': c.trader_id,
                'trader_name': self.traders.get(c.trader_id, {}).username if c.trader_id in self.traders else 'Unknown',
                'allocation': c.allocation,
                'pnl': c.total_pnl,
                'fees': c.fees_paid,
                'started': c.created_at.isoformat()
            } for c in copies]
        }

copy_trading = CopyTradingSystem()
