"""
Copy Trading System for Veyra
Follow and copy top traders automatically

Features:
- Trader discovery and ranking
- Automatic trade replication
- Risk management per trader
- Performance analytics
- Social trading features
- Profit sharing
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class TraderStatus(Enum):
    """Trader account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    VERIFIED = "verified"


class CopyStatus(Enum):
    """Copy relationship status"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class TraderProfile:
    """Top trader profile"""
    id: str
    user_id: str
    display_name: str
    bio: str
    avatar_url: Optional[str] = None
    
    # Trading style
    strategy_description: str = ""
    preferred_assets: List[str] = field(default_factory=list)
    trading_style: str = "swing"  # scalping, day, swing, position
    risk_level: str = "medium"  # low, medium, high
    avg_holding_time: str = ""
    
    # Performance metrics
    total_return_30d: float = 0.0
    total_return_90d: float = 0.0
    total_return_all: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    # Trading stats
    total_trades: int = 0
    open_positions: int = 0
    copiers_count: int = 0
    copiers_equity: float = 0.0  # Total equity copying this trader
    
    # Status
    status: TraderStatus = TraderStatus.ACTIVE
    verified: bool = False
    featured: bool = False
    
    # Monthly performance history
    monthly_returns: List[Dict] = field(default_factory=list)
    
    # Settings
    min_copy_amount: float = 100.0
    allow_copying: bool = True
    profit_share_pct: float = 10.0  # % of profits shared with trader
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'display_name': self.display_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'trading_style': {
                'strategy': self.strategy_description,
                'assets': self.preferred_assets,
                'style': self.trading_style,
                'risk_level': self.risk_level,
                'avg_holding_time': self.avg_holding_time
            },
            'performance': {
                'return_30d': self.total_return_30d,
                'return_90d': self.total_return_90d,
                'return_all': self.total_return_all,
                'win_rate': self.win_rate,
                'profit_factor': self.profit_factor,
                'sharpe_ratio': self.sharpe_ratio,
                'max_drawdown': self.max_drawdown
            },
            'stats': {
                'total_trades': self.total_trades,
                'open_positions': self.open_positions,
                'copiers': self.copiers_count,
                'copiers_equity': self.copiers_equity
            },
            'status': self.status.value,
            'badges': {
                'verified': self.verified,
                'featured': self.featured
            },
            'settings': {
                'min_copy_amount': self.min_copy_amount,
                'allow_copying': self.allow_copying,
                'profit_share_pct': self.profit_share_pct
            },
            'monthly_returns': self.monthly_returns
        }


@dataclass
class CopyRelationship:
    """Copy trading relationship between copier and trader"""
    id: str
    copier_id: str  # User copying
    trader_id: str  # Trader being copied
    
    # Copy settings
    allocation_amount: float  # Amount allocated
    allocation_pct: Optional[float] = None  # % of portfolio (alternative to fixed amount)
    max_positions: int = 10  # Max concurrent positions
    max_position_size_pct: float = 5.0  # Max % per trade
    stop_loss_copying: bool = True  # Copy SL settings
    take_profit_copying: bool = True  # Copy TP settings
    
    # Risk limits
    max_daily_loss_pct: float = 2.0
    pause_on_drawdown_pct: float = 10.0
    
    # Status
    status: CopyStatus = CopyStatus.ACTIVE
    created_at: datetime = None
    updated_at: datetime = None
    
    # Performance tracking
    total_copied_trades: int = 0
    profitable_copied_trades: int = 0
    total_pnl: float = 0.0
    fees_paid: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'copier_id': self.copier_id,
            'trader_id': self.trader_id,
            'allocation': {
                'amount': self.allocation_amount,
                'percentage': self.allocation_pct,
                'max_positions': self.max_positions,
                'max_position_size_pct': self.max_position_size_pct
            },
            'risk_settings': {
                'copy_stop_loss': self.stop_loss_copying,
                'copy_take_profit': self.take_profit_copying,
                'max_daily_loss_pct': self.max_daily_loss_pct,
                'pause_on_drawdown_pct': self.pause_on_drawdown_pct
            },
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'performance': {
                'total_trades': self.total_copied_trades,
                'winning_trades': self.profitable_copied_trades,
                'total_pnl': self.total_pnl,
                'fees_paid': self.fees_paid,
                'win_rate': (self.profitable_copied_trades / self.total_copied_trades * 100) 
                           if self.total_copied_trades > 0 else 0
            }
        }


@dataclass
class CopiedTrade:
    """A trade executed through copy trading"""
    id: str
    copy_relationship_id: str
    original_trade_id: str  # Trader's original trade
    
    # Trade details
    symbol: str
    side: str  # buy/sell
    entry_price: float
    exit_price: Optional[float] = None
    quantity: float = 0.0
    position_size: float = 0.0
    
    # Timing
    entry_time: datetime = None
    exit_time: Optional[datetime] = None
    
    # P&L
    pnl: float = 0.0
    pnl_pct: float = 0.0
    fees: float = 0.0
    
    # Status
    status: str = "open"  # open, closed, cancelled
    
    # Copy details
    copied_proportion: float = 1.0  # % of original trade size
    profit_share_paid: float = 0.0
    
    def __post_init__(self):
        if self.entry_time is None:
            self.entry_time = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'position_size': self.position_size,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'pnl': self.pnl,
            'pnl_pct': self.pnl_pct,
            'fees': self.fees,
            'status': self.status,
            'copied_proportion': self.copied_proportion,
            'profit_share_paid': self.profit_share_paid
        }


@dataclass
class TradeSignal:
    """Trade signal from a trader"""
    id: str
    trader_id: str
    
    # Signal details
    symbol: str
    side: str
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size_pct: float = 0.0  # % of trader's portfolio
    
    # Metadata
    signal_time: datetime = None
    rationale: str = ""
    confidence: str = "medium"  # low, medium, high
    
    # Execution
    executed: bool = False
    execution_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.signal_time is None:
            self.signal_time = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'trader_id': self.trader_id,
            'symbol': self.symbol,
            'side': self.side,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size_pct': self.position_size_pct,
            'signal_time': self.signal_time.isoformat() if self.signal_time else None,
            'rationale': self.rationale,
            'confidence': self.confidence,
            'executed': self.executed
        }


class CopyTradingSystem:
    """
    Copy Trading System backend
    Manages trader discovery, copying relationships, and trade replication
    """
    
    def __init__(self):
        self.traders: Dict[str, TraderProfile] = {}
        self.copiers: Dict[str, List[CopyRelationship]] = {}  # copier_id -> relationships
        self.trader_copiers: Dict[str, List[str]] = {}  # trader_id -> copier_relationship_ids
        self.copied_trades: Dict[str, List[CopiedTrade]] = {}  # relationship_id -> trades
        self.signals: Dict[str, List[TradeSignal]] = {}  # trader_id -> signals
        
        # Profit sharing config
        PLATFORM_FEE_PCT = 0.30  # 30% of profit share
        TRADER_FEE_PCT = 0.70  # 70% to trader
    
    def register_trader(self, user_id: str, display_name: str, bio: str,
                       strategy_description: str = "") -> TraderProfile:
        """Register a new trader for copy trading"""
        
        # Check if already registered
        existing = next((t for t in self.traders.values() if t.user_id == user_id), None)
        if existing:
            return existing
        
        trader = TraderProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            display_name=display_name,
            bio=bio,
            strategy_description=strategy_description
        )
        
        self.traders[trader.id] = trader
        self.signals[trader.id] = []
        self.trader_copiers[trader.id] = []
        
        logger.info(f"Registered trader: {trader.id}")
        return trader
    
    def update_trader_performance(self, trader_id: str, 
                                   performance: Dict[str, Any]) -> bool:
        """Update trader's performance metrics"""
        trader = self.traders.get(trader_id)
        if not trader:
            return False
        
        trader.total_return_30d = performance.get('return_30d', 0)
        trader.total_return_90d = performance.get('return_90d', 0)
        trader.total_return_all = performance.get('return_all', 0)
        trader.win_rate = performance.get('win_rate', 0)
        trader.profit_factor = performance.get('profit_factor', 0)
        trader.sharpe_ratio = performance.get('sharpe_ratio', 0)
        trader.max_drawdown = performance.get('max_drawdown', 0)
        trader.total_trades = performance.get('total_trades', 0)
        
        return True
    
    def get_trader(self, trader_id: str) -> Optional[Dict]:
        """Get trader profile"""
        trader = self.traders.get(trader_id)
        if trader:
            return trader.to_dict()
        return None
    
    def discover_traders(self,
                        sort_by: str = "performance",
                        min_return_30d: float = None,
                        max_risk: str = None,
                        trading_style: str = None,
                        verified_only: bool = False,
                        limit: int = 20) -> List[Dict]:
        """Discover top traders to copy"""
        
        traders = list(self.traders.values())
        
        # Filter active traders only
        traders = [t for t in traders if t.status == TraderStatus.ACTIVE and t.allow_copying]
        
        # Apply filters
        if min_return_30d is not None:
            traders = [t for t in traders if t.total_return_30d >= min_return_30d]
        
        if max_risk is not None:
            risk_order = {'low': 1, 'medium': 2, 'high': 3}
            traders = [t for t in traders if risk_order.get(t.risk_level, 4) <= risk_order.get(max_risk, 4)]
        
        if trading_style is not None:
            traders = [t for t in traders if t.trading_style == trading_style]
        
        if verified_only:
            traders = [t for t in traders if t.verified]
        
        # Sorting
        if sort_by == "performance":
            traders.sort(key=lambda t: t.total_return_30d, reverse=True)
        elif sort_by == "copiers":
            traders.sort(key=lambda t: t.copiers_count, reverse=True)
        elif sort_by == "consistency":
            traders.sort(key=lambda t: (t.win_rate, t.sharpe_ratio), reverse=True)
        elif sort_by == "safety":
            traders.sort(key=lambda t: (t.max_drawdown, -t.sharpe_ratio))
        
        return [t.to_dict() for t in traders[:limit]]
    
    def start_copying(self, copier_id: str, trader_id: str,
                      allocation: float, risk_settings: Dict = None) -> Dict:
        """Start copying a trader"""
        
        trader = self.traders.get(trader_id)
        if not trader:
            return {'error': 'Trader not found'}
        
        if not trader.allow_copying:
            return {'error': 'Trader is not accepting copiers'}
        
        if allocation < trader.min_copy_amount:
            return {'error': f'Minimum allocation is ${trader.min_copy_amount}'}
        
        # Check if already copying
        existing = self.copiers.get(copier_id, [])
        for rel in existing:
            if rel.trader_id == trader_id:
                return {'error': 'Already copying this trader'}
        
        # Create relationship
        relationship = CopyRelationship(
            id=str(uuid.uuid4()),
            copier_id=copier_id,
            trader_id=trader_id,
            allocation_amount=allocation,
            max_positions=risk_settings.get('max_positions', 10) if risk_settings else 10,
            max_position_size_pct=risk_settings.get('max_position_pct', 5.0) if risk_settings else 5.0,
            stop_loss_copying=risk_settings.get('copy_sl', True) if risk_settings else True,
            take_profit_copying=risk_settings.get('copy_tp', True) if risk_settings else True
        )
        
        # Store relationship
        if copier_id not in self.copiers:
            self.copiers[copier_id] = []
        self.copiers[copier_id].append(relationship)
        
        # Update trader stats
        self.trader_copiers[trader_id].append(relationship.id)
        trader.copiers_count += 1
        trader.copiers_equity += allocation
        
        # Initialize trade tracking
        self.copied_trades[relationship.id] = []
        
        logger.info(f"Created copy relationship: {relationship.id}")
        
        return {
            'success': True,
            'relationship_id': relationship.id,
            'trader_name': trader.display_name,
            'allocation': allocation
        }
    
    def stop_copying(self, copier_id: str, trader_id: str) -> bool:
        """Stop copying a trader"""
        relationships = self.copiers.get(copier_id, [])
        relationship = next((r for r in relationships if r.trader_id == trader_id), None)
        
        if not relationship:
            return False
        
        # Close all open copied positions
        trades = self.copied_trades.get(relationship.id, [])
        for trade in trades:
            if trade.status == "open":
                # Signal to close position
                trade.status = "closing"
        
        # Update status
        relationship.status = CopyStatus.STOPPED
        relationship.updated_at = datetime.now()
        
        # Update trader stats
        trader = self.traders.get(trader_id)
        if trader:
            trader.copiers_count = max(0, trader.copiers_count - 1)
            trader.copiers_equity -= relationship.allocation_amount
        
        logger.info(f"Stopped copying: {relationship.id}")
        return True
    
    def pause_copying(self, copier_id: str, trader_id: str) -> bool:
        """Pause copying (keep existing positions)"""
        relationships = self.copiers.get(copier_id, [])
        relationship = next((r for r in relationships if r.trader_id == trader_id), None)
        
        if not relationship:
            return False
        
        relationship.status = CopyStatus.PAUSED
        relationship.updated_at = datetime.now()
        
        logger.info(f"Paused copying: {relationship.id}")
        return True
    
    def resume_copying(self, copier_id: str, trader_id: str) -> bool:
        """Resume paused copying"""
        relationships = self.copiers.get(copier_id, [])
        relationship = next((r for r in relationships if r.trader_id == trader_id), None)
        
        if not relationship:
            return False
        
        relationship.status = CopyStatus.ACTIVE
        relationship.updated_at = datetime.now()
        
        logger.info(f"Resumed copying: {relationship.id}")
        return True
    
    def update_copy_settings(self, copier_id: str, trader_id: str, 
                            settings: Dict) -> bool:
        """Update copy relationship settings"""
        relationships = self.copiers.get(copier_id, [])
        relationship = next((r for r in relationships if r.trader_id == trader_id), None)
        
        if not relationship:
            return False
        
        if 'allocation' in settings:
            # Recalculate trader equity
            trader = self.traders.get(relationship.trader_id)
            if trader:
                trader.copiers_equity += settings['allocation'] - relationship.allocation_amount
            relationship.allocation_amount = settings['allocation']
        
        if 'max_positions' in settings:
            relationship.max_positions = settings['max_positions']
        
        if 'max_position_pct' in settings:
            relationship.max_position_size_pct = settings['max_position_pct']
        
        relationship.updated_at = datetime.now()
        
        return True
    
    def create_trade_signal(self, trader_id: str, signal: Dict) -> TradeSignal:
        """Trader creates a new trade signal"""
        
        trade_signal = TradeSignal(
            id=str(uuid.uuid4()),
            trader_id=trader_id,
            symbol=signal['symbol'],
            side=signal['side'],
            entry_price=signal['entry_price'],
            stop_loss=signal.get('stop_loss'),
            take_profit=signal.get('take_profit'),
            position_size_pct=signal.get('position_size_pct', 5.0),
            rationale=signal.get('rationale', ''),
            confidence=signal.get('confidence', 'medium')
        )
        
        # Store signal
        if trader_id not in self.signals:
            self.signals[trader_id] = []
        self.signals[trader_id].append(trade_signal)
        
        # Replicate to copiers
        self._replicate_signal(trader_id, trade_signal)
        
        # Update trader stats
        trader = self.traders.get(trader_id)
        if trader:
            trader.total_trades += 1
            trader.open_positions += 1
        
        logger.info(f"Created trade signal: {trade_signal.id}")
        return trade_signal
    
    def _replicate_signal(self, trader_id: str, signal: TradeSignal):
        """Replicate trade signal to all copiers"""
        
        relationship_ids = self.trader_copiers.get(trader_id, [])
        
        for rel_id in relationship_ids:
            relationship = None
            # Find relationship
            for copier_rels in self.copiers.values():
                relationship = next((r for r in copier_rels if r.id == rel_id), None)
                if relationship:
                    break
            
            if not relationship or relationship.status != CopyStatus.ACTIVE:
                continue
            
            # Check position limits
            existing_trades = self.copied_trades.get(rel_id, [])
            open_positions = len([t for t in existing_trades if t.status == "open"])
            
            if open_positions >= relationship.max_positions:
                continue
            
            # Calculate position size
            max_position_value = relationship.allocation_amount * (relationship.max_position_size_pct / 100)
            trader_position_value = signal.position_size_pct / 100  # % of trader's typical position
            
            # Scale down proportionally
            position_size = min(max_position_value, 
                            relationship.allocation_amount * (signal.position_size_pct / 100))
            
            # Create copied trade
            copied_trade = CopiedTrade(
                id=str(uuid.uuid4()),
                copy_relationship_id=rel_id,
                original_trade_id=signal.id,
                symbol=signal.symbol,
                side=signal.side,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss if relationship.stop_loss_copying else None,
                take_profit=signal.take_profit if relationship.take_profit_copying else None,
                position_size=position_size,
                copied_proportion=signal.position_size_pct / 100
            )
            
            existing_trades.append(copied_trade)
            
            # Update relationship stats
            relationship.total_copied_trades += 1
    
    def close_copied_trade(self, relationship_id: str, trade_id: str,
                          exit_price: float, pnl: float):
        """Close a copied trade when original closes"""
        
        trades = self.copied_trades.get(relationship_id, [])
        trade = next((t for t in trades if t.id == trade_id), None)
        
        if not trade or trade.status != "open":
            return
        
        trade.status = "closed"
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.pnl = pnl
        
        # Calculate P&L %
        if trade.entry_price > 0:
            trade.pnl_pct = (pnl / (trade.entry_price * trade.quantity)) * 100 if trade.quantity > 0 else 0
        
        # Calculate profit share
        if pnl > 0:
            trader = self.traders.get(trade.copy_relationship_id)
            if trader:
                profit_share = pnl * (trader.profit_share_pct / 100)
                trade.profit_share_paid = profit_share
                trade.fees = profit_share * 0.30  # Platform takes 30% of profit share
        
        # Update relationship
        for copier_rels in self.copiers.values():
            relationship = next((r for r in copier_rels if r.id == relationship_id), None)
            if relationship:
                relationship.total_pnl += pnl - trade.profit_share_paid
                if pnl > 0:
                    relationship.profitable_copied_trades += 1
                break
    
    def get_copier_dashboard(self, copier_id: str) -> Dict:
        """Get copier's copy trading dashboard"""
        
        relationships = self.copiers.get(copier_id, [])
        
        total_allocated = sum(r.allocation_amount for r in relationships)
        total_pnl = sum(r.total_pnl for r in relationships)
        total_copied_trades = sum(r.total_copied_trades for r in relationships)
        
        copying_list = []
        for rel in relationships:
            trader = self.traders.get(rel.trader_id)
            if trader:
                trades = self.copied_trades.get(rel.id, [])
                open_trades = [t for t in trades if t.status == "open"]
                
                copying_list.append({
                    'relationship_id': rel.id,
                    'trader': {
                        'id': trader.id,
                        'name': trader.display_name,
                        'return_30d': trader.total_return_30d,
                        'win_rate': trader.win_rate
                    },
                    'status': rel.status.value,
                    'allocation': rel.allocation_amount,
                    'performance': {
                        'total_trades': rel.total_copied_trades,
                        'winning_trades': rel.profitable_copied_trades,
                        'pnl': rel.total_pnl,
                        'open_positions': len(open_trades)
                    }
                })
        
        return {
            'summary': {
                'total_allocated': total_allocated,
                'total_pnl': total_pnl,
                'total_copied_trades': total_copied_trades,
                'active_copies': len([r for r in relationships if r.status == CopyStatus.ACTIVE]),
                'total_copied': len(relationships)
            },
            'copying': copying_list
        }
    
    def get_trader_dashboard(self, trader_id: str) -> Dict:
        """Get trader's copy trading dashboard"""
        
        trader = self.traders.get(trader_id)
        if not trader:
            return {'error': 'Trader not found'}
        
        # Get recent signals
        signals = self.signals.get(trader_id, [])[-10:]  # Last 10
        
        # Get copier details
        relationship_ids = self.trader_copiers.get(trader_id, [])
        copiers = []
        
        for rel_id in relationship_ids:
            for copier_rels in self.copiers.values():
                rel = next((r for r in copier_rels if r.id == rel_id), None)
                if rel:
                    copiers.append({
                        'relationship_id': rel.id,
                        'copier_id': rel.copier_id,
                        'allocation': rel.allocation_amount,
                        'total_pnl': rel.total_pnl,
                        'total_trades': rel.total_copied_trades,
                        'joined': rel.created_at.isoformat() if rel.created_at else None
                    })
                    break
        
        return {
            'profile': trader.to_dict(),
            'performance': {
                'total_copiers': trader.copiers_count,
                'total_copier_equity': trader.copiers_equity,
                'estimated_monthly_revenue': trader.copiers_equity * (trader.profit_share_pct / 100) * 
                                            (trader.total_return_30d / 100) / 12
            },
            'recent_signals': [s.to_dict() for s in signals],
            'copiers': copiers
        }
    
    def get_leaderboard(self, period: str = "30d", limit: int = 10) -> List[Dict]:
        """Get top traders leaderboard"""
        
        traders = [t for t in self.traders.values() if t.status == TraderStatus.ACTIVE]
        
        if period == "30d":
            traders.sort(key=lambda t: (t.total_return_30d, t.sharpe_ratio), reverse=True)
        elif period == "90d":
            traders.sort(key=lambda t: (t.total_return_90d, t.sharpe_ratio), reverse=True)
        elif period == "all":
            traders.sort(key=lambda t: (t.total_return_all, t.sharpe_ratio), reverse=True)
        
        return [
            {
                'rank': i + 1,
                'trader': t.to_dict(),
                'return': t.total_return_30d if period == "30d" else 
                         (t.total_return_90d if period == "90d" else t.total_return_all)
            }
            for i, t in enumerate(traders[:limit])
        ]
