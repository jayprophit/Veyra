"""
Advanced Bot Manager - DCA, Grid, and Custom Trading Bots
Manages automated trading strategies with sophisticated controls

Features:
- DCA (Dollar Cost Averaging) bots
- Enhanced Grid Trading bots
- TWAP/VWAP execution bots
- Smart order routing
- Risk management per bot
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class BotType(Enum):
    """Types of automated trading bots"""
    DCA = "dca"  # Dollar Cost Averaging
    GRID = "grid"  # Grid Trading
    TWAP = "twap"  # Time-Weighted Average Price
    VWAP = "vwap"  # Volume-Weighted Average Price
    PING_PONG = "ping_pong"  # Bounce trading
    ARBITRAGE = "arbitrage"  # Cross-exchange arbitrage
    TRAILING_STOP = "trailing_stop"  # Trailing stop manager
    BASKET = "basket"  # Basket rebalancing


class BotStatus(Enum):
    """Bot operational status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    COMPLETED = "completed"  # For DCA targets reached


@dataclass
class DCABotConfig:
    """DCA Bot configuration"""
    symbol: str
    total_investment: float  # Total amount to invest
    entry_price: float  # Initial entry price
    # DCA Settings
    num_orders: int = 10  # Number of DCA orders
    price_drop_pct: float = 5.0  # % drop to trigger DCA
    investment_per_order: float = 0.0  # Auto-calculated
    # Take Profit
    take_profit_pct: float = 10.0
    take_profit_type: str = "percentage"  # percentage, breakeven, custom
    # Advanced
    use_limit_orders: bool = True
    max_spread_pct: float = 0.5
    timeout_hours: int = 24
    # Safety
    stop_dca_below: Optional[float] = None  # Stop DCA below price
    max_open_orders: int = 5


@dataclass
class GridBotConfig:
    """Grid Trading Bot configuration"""
    symbol: str
    total_investment: float
    # Grid Settings
    lower_price: float
    upper_price: float
    num_grids: int = 10
    grid_spacing: str = "arithmetic"  # arithmetic, geometric
    # Order Settings
    order_size_per_grid: float = 0.0  # Auto-calculated
    use_limit_orders: bool = True
    # Advanced
    trailing_grids: bool = False  # Move grids with price
    rebalance_threshold: float = 20.0  # % deviation to rebalance
    # Exit
    stop_loss_lower: Optional[float] = None
    stop_loss_upper: Optional[float] = None
    take_profit_total: Optional[float] = None


@dataclass
class TWAPConfig:
    """TWAP Bot configuration"""
    symbol: str
    total_quantity: float
    side: str  # buy/sell
    duration_minutes: int = 60
    num_slices: int = 12
    price_limit: Optional[float] = None  # Max/min price
    randomize_intervals: bool = True
    allow_partial: bool = True


@dataclass
class TradeExecution:
    """Individual trade execution record"""
    id: str
    bot_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    order_type: str
    timestamp: datetime
    status: str = "pending"  # pending, filled, partial, failed
    fees: float = 0.0
    exchange: str = ""
    order_id: Optional[str] = None
    
    def __post_init__(self):
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        elif self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TradingBot:
    """Trading bot instance"""
    id: str
    user_id: str
    name: str
    bot_type: BotType
    status: BotStatus
    
    # Configuration (type-specific)
    config: Any = None
    
    # Performance tracking
    created_at: datetime = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    
    # Statistics
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_volume: float = 0.0
    total_pnl: float = 0.0
    fees_paid: float = 0.0
    
    # Current state
    current_position: float = 0.0
    average_entry_price: float = 0.0
    unrealized_pnl: float = 0.0
    open_orders: List[str] = field(default_factory=list)
    trade_history: List[TradeExecution] = field(default_factory=list)
    
    # Settings
    notifications_enabled: bool = True
    auto_restart: bool = False
    max_daily_loss_pct: float = 5.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'bot_type': self.bot_type.value,
            'status': self.status.value,
            'config': self._config_to_dict(),
            'performance': {
                'total_trades': self.total_trades,
                'successful_trades': self.successful_trades,
                'failed_trades': self.failed_trades,
                'win_rate': (self.successful_trades / self.total_trades * 100) 
                           if self.total_trades > 0 else 0,
                'total_volume': self.total_volume,
                'total_pnl': self.total_pnl,
                'fees_paid': self.fees_paid,
                'roi': (self.total_pnl / self._get_investment() * 100) 
                      if self._get_investment() > 0 else 0
            },
            'current_state': {
                'position': self.current_position,
                'avg_entry': self.average_entry_price,
                'unrealized_pnl': self.unrealized_pnl,
                'open_orders': len(self.open_orders)
            },
            'timestamps': {
                'created': self.created_at.isoformat() if self.created_at else None,
                'started': self.started_at.isoformat() if self.started_at else None,
                'stopped': self.stopped_at.isoformat() if self.stopped_at else None
            },
            'settings': {
                'notifications': self.notifications_enabled,
                'auto_restart': self.auto_restart,
                'max_daily_loss_pct': self.max_daily_loss_pct
            }
        }
    
    def _config_to_dict(self) -> Dict:
        """Convert config to dictionary based on type"""
        if isinstance(self.config, DCABotConfig):
            return {
                'type': 'dca',
                'symbol': self.config.symbol,
                'total_investment': self.config.total_investment,
                'entry_price': self.config.entry_price,
                'num_orders': self.config.num_orders,
                'price_drop_pct': self.config.price_drop_pct,
                'take_profit_pct': self.config.take_profit_pct
            }
        elif isinstance(self.config, GridBotConfig):
            return {
                'type': 'grid',
                'symbol': self.config.symbol,
                'total_investment': self.config.total_investment,
                'lower_price': self.config.lower_price,
                'upper_price': self.config.upper_price,
                'num_grids': self.config.num_grids
            }
        elif isinstance(self.config, TWAPConfig):
            return {
                'type': 'twap',
                'symbol': self.config.symbol,
                'total_quantity': self.config.total_quantity,
                'side': self.config.side,
                'duration_minutes': self.config.duration_minutes,
                'num_slices': self.config.num_slices
            }
        return {}
    
    def _get_investment(self) -> float:
        """Get total investment amount"""
        if isinstance(self.config, (DCABotConfig, GridBotConfig)):
            return self.config.total_investment
        return 0.0


class BotManager:
    """
    Advanced Bot Manager for DCA, Grid, and custom bots
    """
    
    def __init__(self):
        self.bots: Dict[str, TradingBot] = {}
        self.user_bots: Dict[str, List[str]] = {}  # user_id -> bot_ids
        self.active_bots: set = set()
        self.executions: Dict[str, List[TradeExecution]] = {}  # bot_id -> executions
    
    def create_dca_bot(self, user_id: str, name: str, config: Dict) -> TradingBot:
        """Create a new DCA bot"""
        
        dca_config = DCABotConfig(
            symbol=config['symbol'],
            total_investment=config['total_investment'],
            entry_price=config['entry_price'],
            num_orders=config.get('num_orders', 10),
            price_drop_pct=config.get('price_drop_pct', 5.0),
            take_profit_pct=config.get('take_profit_pct', 10.0),
            take_profit_type=config.get('take_profit_type', 'percentage'),
            use_limit_orders=config.get('use_limit_orders', True),
            max_spread_pct=config.get('max_spread_pct', 0.5),
            timeout_hours=config.get('timeout_hours', 24),
            stop_dca_below=config.get('stop_dca_below'),
            max_open_orders=config.get('max_open_orders', 5)
        )
        
        # Calculate investment per order
        dca_config.investment_per_order = dca_config.total_investment / dca_config.num_orders
        
        bot = TradingBot(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            bot_type=BotType.DCA,
            status=BotStatus.CREATED,
            config=dca_config
        )
        
        self.bots[bot.id] = bot
        
        if user_id not in self.user_bots:
            self.user_bots[user_id] = []
        self.user_bots[user_id].append(bot.id)
        
        self.executions[bot.id] = []
        
        logger.info(f"Created DCA bot: {bot.id}")
        return bot
    
    def create_grid_bot(self, user_id: str, name: str, config: Dict) -> TradingBot:
        """Create a new Grid Trading bot"""
        
        grid_config = GridBotConfig(
            symbol=config['symbol'],
            total_investment=config['total_investment'],
            lower_price=config['lower_price'],
            upper_price=config['upper_price'],
            num_grids=config.get('num_grids', 10),
            grid_spacing=config.get('grid_spacing', 'arithmetic'),
            use_limit_orders=config.get('use_limit_orders', True),
            trailing_grids=config.get('trailing_grids', False),
            rebalance_threshold=config.get('rebalance_threshold', 20.0),
            stop_loss_lower=config.get('stop_loss_lower'),
            stop_loss_upper=config.get('stop_loss_upper'),
            take_profit_total=config.get('take_profit_total')
        )
        
        # Calculate order size per grid
        grid_config.order_size_per_grid = grid_config.total_investment / grid_config.num_grids
        
        bot = TradingBot(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            bot_type=BotType.GRID,
            status=BotStatus.CREATED,
            config=grid_config
        )
        
        self.bots[bot.id] = bot
        
        if user_id not in self.user_bots:
            self.user_bots[user_id] = []
        self.user_bots[user_id].append(bot.id)
        
        self.executions[bot.id] = []
        
        logger.info(f"Created Grid bot: {bot.id}")
        return bot
    
    def create_twap_bot(self, user_id: str, name: str, config: Dict) -> TradingBot:
        """Create a TWAP execution bot"""
        
        twap_config = TWAPConfig(
            symbol=config['symbol'],
            total_quantity=config['total_quantity'],
            side=config['side'],
            duration_minutes=config.get('duration_minutes', 60),
            num_slices=config.get('num_slices', 12),
            price_limit=config.get('price_limit'),
            randomize_intervals=config.get('randomize_intervals', True),
            allow_partial=config.get('allow_partial', True)
        )
        
        bot = TradingBot(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            bot_type=BotType.TWAP,
            status=BotStatus.CREATED,
            config=twap_config
        )
        
        self.bots[bot.id] = bot
        
        if user_id not in self.user_bots:
            self.user_bots[user_id] = []
        self.user_bots[user_id].append(bot.id)
        
        self.executions[bot.id] = []
        
        logger.info(f"Created TWAP bot: {bot.id}")
        return bot
    
    def start_bot(self, bot_id: str) -> bool:
        """Start a bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return False
        
        if bot.status == BotStatus.RUNNING:
            return True
        
        bot.status = BotStatus.RUNNING
        bot.started_at = datetime.now()
        self.active_bots.add(bot_id)
        
        logger.info(f"Started bot: {bot_id}")
        return True
    
    def pause_bot(self, bot_id: str) -> bool:
        """Pause a bot (keep positions)"""
        bot = self.bots.get(bot_id)
        if not bot:
            return False
        
        bot.status = BotStatus.PAUSED
        if bot_id in self.active_bots:
            self.active_bots.remove(bot_id)
        
        logger.info(f"Paused bot: {bot_id}")
        return True
    
    def stop_bot(self, bot_id: str, close_positions: bool = False) -> bool:
        """Stop a bot (optionally close positions)"""
        bot = self.bots.get(bot_id)
        if not bot:
            return False
        
        bot.status = BotStatus.STOPPED
        bot.stopped_at = datetime.now()
        
        if bot_id in self.active_bots:
            self.active_bots.remove(bot_id)
        
        if close_positions and bot.current_position > 0:
            # Signal to close all positions
            pass
        
        logger.info(f"Stopped bot: {bot_id}")
        return True
    
    def get_bot(self, bot_id: str) -> Optional[Dict]:
        """Get bot details"""
        bot = self.bots.get(bot_id)
        if bot:
            return bot.to_dict()
        return None
    
    def list_user_bots(self, user_id: str, bot_type: str = None, 
                      status: str = None) -> List[Dict]:
        """List all bots for a user"""
        bot_ids = self.user_bots.get(user_id, [])
        bots = [self.bots[bid] for bid in bot_ids]
        
        if bot_type:
            bots = [b for b in bots if b.bot_type.value == bot_type]
        
        if status:
            bots = [b for b in bots if b.status.value == status]
        
        return [b.to_dict() for b in bots]
    
    def get_bot_stats(self, bot_id: str) -> Dict:
        """Get detailed statistics for a bot"""
        bot = self.bots.get(bot_id)
        if not bot:
            return {'error': 'Bot not found'}
        
        executions = self.executions.get(bot_id, [])
        
        # Calculate statistics
        buy_trades = [e for e in executions if e.side == 'buy']
        sell_trades = [e for e in executions if e.side == 'sell']
        
        avg_buy_price = sum(e.price * e.quantity for e in buy_trades) / sum(e.quantity for e in buy_trades) if buy_trades else 0
        avg_sell_price = sum(e.price * e.quantity for e in sell_trades) / sum(e.quantity for e in sell_trades) if sell_trades else 0
        
        return {
            'bot_id': bot_id,
            'executions_count': len(executions),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'avg_buy_price': avg_buy_price,
            'avg_sell_price': avg_sell_price,
            'total_fees': sum(e.fees for e in executions),
            'recent_executions': [
                {
                    'id': e.id,
                    'symbol': e.symbol,
                    'side': e.side,
                    'quantity': e.quantity,
                    'price': e.price,
                    'status': e.status,
                    'timestamp': e.timestamp.isoformat()
                }
                for e in executions[-10:]  # Last 10
            ]
        }
    
    def duplicate_bot(self, bot_id: str, new_name: str) -> Optional[TradingBot]:
        """Duplicate an existing bot"""
        source = self.bots.get(bot_id)
        if not source:
            return None
        
        new_bot = TradingBot(
            id=str(uuid.uuid4()),
            user_id=source.user_id,
            name=new_name,
            bot_type=source.bot_type,
            status=BotStatus.CREATED,
            config=source.config  # Same config
        )
        
        self.bots[new_bot.id] = new_bot
        
        if source.user_id not in self.user_bots:
            self.user_bots[source.user_id] = []
        self.user_bots[source.user_id].append(new_bot.id)
        
        self.executions[new_bot.id] = []
        
        logger.info(f"Duplicated bot: {bot_id} -> {new_bot.id}")
        return new_bot
    
    def record_execution(self, bot_id: str, execution: TradeExecution):
        """Record a trade execution"""
        if bot_id in self.executions:
            self.executions[bot_id].append(execution)
        
        bot = self.bots.get(bot_id)
        if bot:
            bot.total_trades += 1
            bot.total_volume += execution.quantity * execution.price
            
            if execution.status == 'filled':
                bot.successful_trades += 1
            elif execution.status == 'failed':
                bot.failed_trades += 1
            
            bot.fees_paid += execution.fees
    
    def get_active_bots_summary(self) -> Dict:
        """Get summary of all active bots"""
        active = [self.bots[bid] for bid in self.active_bots]
        
        return {
            'total_active': len(active),
            'by_type': {
                'dca': len([b for b in active if b.bot_type == BotType.DCA]),
                'grid': len([b for b in active if b.bot_type == BotType.GRID]),
                'twap': len([b for b in active if b.bot_type == BotType.TWAP]),
                'other': len([b for b in active if b.bot_type not in [BotType.DCA, BotType.GRID, BotType.TWAP]])
            },
            'total_volume_24h': sum(b.total_volume for b in active),
            'total_pnl_active': sum(b.total_pnl for b in active)
        }
    
    def calculate_dca_levels(self, bot_id: str) -> List[Dict]:
        """Calculate DCA entry levels for a bot"""
        bot = self.bots.get(bot_id)
        if not bot or bot.bot_type != BotType.DCA:
            return []
        
        config = bot.config
        levels = []
        
        for i in range(config.num_orders):
            drop_pct = config.price_drop_pct * (i + 1)
            price = config.entry_price * (1 - drop_pct / 100)
            levels.append({
                'level': i + 1,
                'trigger_price': round(price, 4),
                'investment': config.investment_per_order,
                'drop_pct': drop_pct
            })
        
        return levels
    
    def calculate_grid_levels(self, bot_id: str) -> List[Dict]:
        """Calculate grid levels for a bot"""
        bot = self.bots.get(bot_id)
        if not bot or bot.bot_type != BotType.GRID:
            return []
        
        config = bot.config
        levels = []
        
        if config.grid_spacing == 'arithmetic':
            step = (config.upper_price - config.lower_price) / (config.num_grids - 1)
            for i in range(config.num_grids):
                price = config.lower_price + (step * i)
                levels.append({
                    'level': i + 1,
                    'price': round(price, 4),
                    'size': config.order_size_per_grid,
                    'type': 'buy' if i < config.num_grids // 2 else 'sell'
                })
        else:  # geometric
            ratio = (config.upper_price / config.lower_price) ** (1 / (config.num_grids - 1))
            price = config.lower_price
            for i in range(config.num_grids):
                levels.append({
                    'level': i + 1,
                    'price': round(price, 4),
                    'size': config.order_size_per_grid,
                    'type': 'buy' if i < config.num_grids // 2 else 'sell'
                })
                price *= ratio
        
        return levels
