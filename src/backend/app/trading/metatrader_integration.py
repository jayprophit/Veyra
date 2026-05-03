"""
MetaTrader 4/5 Integration for Financial Master
Connects with MT4/MT5 Expert Advisors and handles trade signals

Features:
- MT4/MT5 API connection via ZeroMQ
- Expert Advisor management
- Trade signal reception and forwarding
- Account synchronization
- Multi-terminal support
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MTVersion(Enum):
    """MetaTrader version"""
    MT4 = 4
    MT5 = 5


class MTAccountType(Enum):
    """MT account type"""
    DEMO = "demo"
    LIVE = "live"


class ConnectionStatus(Enum):
    """Connection status"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class SignalAction(Enum):
    """Trade signal actions from EA"""
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    MODIFY = "modify"
    PENDING_BUY = "pending_buy"
    PENDING_SELL = "pending_sell"
    CANCEL = "cancel"


@dataclass
class MTAccount:
    """MetaTrader account configuration"""
    id: str
    user_id: str
    name: str
    version: MTVersion
    account_type: MTAccountType
    
    # Connection settings
    host: str = "localhost"
    port: int = 15555  # Default ZeroMQ port
    password: str = ""
    
    # Account info (from MT)
    account_number: Optional[int] = None
    account_balance: float = 0.0
    account_equity: float = 0.0
    account_margin: float = 0.0
    account_profit: float = 0.0
    leverage: int = 100
    currency: str = "USD"
    
    # Status
    connection_status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_connected: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Settings
    auto_sync: bool = True
    sync_interval_seconds: int = 5
    allowed_symbols: List[str] = field(default_factory=list)
    max_position_size: float = 100.0  # Lots
    
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version.value,
            'account_type': self.account_type.value,
            'connection': {
                'host': self.host,
                'port': self.port,
                'status': self.connection_status.value,
                'last_connected': self.last_connected.isoformat() if self.last_connected else None
            },
            'account_info': {
                'number': self.account_number,
                'balance': self.account_balance,
                'equity': self.account_equity,
                'margin': self.account_margin,
                'profit': self.account_profit,
                'leverage': self.leverage,
                'currency': self.currency
            },
            'settings': {
                'auto_sync': self.auto_sync,
                'sync_interval': self.sync_interval_seconds,
                'allowed_symbols': self.allowed_symbols,
                'max_position_size': self.max_position_size
            }
        }


@dataclass
class MTPosition:
    """MT4/5 position"""
    ticket: int
    symbol: str
    action: str  # buy/sell
    volume: float
    open_price: float
    current_price: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    swap: float = 0.0
    profit: float = 0.0
    open_time: datetime = None
    magic_number: int = 0
    comment: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'ticket': self.ticket,
            'symbol': self.symbol,
            'action': self.action,
            'volume': self.volume,
            'open_price': self.open_price,
            'current_price': self.current_price,
            'sl': self.sl,
            'tp': self.tp,
            'swap': self.swap,
            'profit': self.profit,
            'open_time': self.open_time.isoformat() if self.open_time else None,
            'magic_number': self.magic_number,
            'comment': self.comment
        }


@dataclass
class MTOrder:
    """Pending order"""
    ticket: int
    symbol: str
    order_type: str  # buy_limit, sell_limit, buy_stop, sell_stop
    volume: float
    price: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    expiration: Optional[datetime] = None
    magic_number: int = 0
    comment: str = ""


@dataclass
class TradeSignal:
    """Trade signal from EA"""
    id: str
    account_id: str
    action: SignalAction
    symbol: str
    volume: float
    price: Optional[float] = None  # For pending orders
    sl: Optional[float] = None
    tp: Optional[float] = None
    magic_number: int = 0
    comment: str = ""
    timestamp: datetime = None
    ea_name: str = ""
    processed: bool = False
    processed_time: Optional[datetime] = None
    result: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'account_id': self.account_id,
            'action': self.action.value,
            'symbol': self.symbol,
            'volume': self.volume,
            'price': self.price,
            'sl': self.sl,
            'tp': self.tp,
            'magic_number': self.magic_number,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat(),
            'ea_name': self.ea_name,
            'processed': self.processed,
            'result': self.result
        }


@dataclass
class EAConfiguration:
    """Expert Advisor configuration"""
    id: str
    account_id: str
    name: str
    magic_number: int
    
    # Strategy settings
    strategy_type: str = ""
    timeframe: str = "H1"
    symbols: List[str] = field(default_factory=list)
    
    # Risk settings
    risk_per_trade_pct: float = 1.0
    max_daily_trades: int = 10
    max_spread_points: float = 20.0
    
    # Features
    use_trailing_stop: bool = False
    use_breakeven: bool = False
    use_partial_close: bool = False
    
    # Status
    enabled: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'account_id': self.account_id,
            'name': self.name,
            'magic_number': self.magic_number,
            'strategy': {
                'type': self.strategy_type,
                'timeframe': self.timeframe,
                'symbols': self.symbols
            },
            'risk': {
                'per_trade_pct': self.risk_per_trade_pct,
                'max_daily_trades': self.max_daily_trades,
                'max_spread_points': self.max_spread_points
            },
            'features': {
                'trailing_stop': self.use_trailing_stop,
                'breakeven': self.use_breakeven,
                'partial_close': self.use_partial_close
            },
            'enabled': self.enabled
        }


class MetaTraderIntegration:
    """
    MetaTrader 4/5 Integration Manager
    """
    
    def __init__(self):
        self.accounts: Dict[str, MTAccount] = {}
        self.user_accounts: Dict[str, List[str]] = {}  # user_id -> account_ids
        self.ea_configs: Dict[str, EAConfiguration] = {}
        self.account_eas: Dict[str, List[str]] = {}  # account_id -> ea_ids
        self.signals: Dict[str, List[TradeSignal]] = {}  # account_id -> signals
        self.positions: Dict[str, List[MTPosition]] = {}  # account_id -> positions
        self.pending_orders: Dict[str, List[MTOrder]] = {}  # account_id -> orders
    
    def add_account(self, user_id: str, name: str, version: int,
                   account_type: str, host: str = "localhost",
                   port: int = 15555) -> MTAccount:
        """Add a new MT4/5 account"""
        
        account = MTAccount(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            version=MTVersion(version),
            account_type=MTAccountType(account_type),
            host=host,
            port=port
        )
        
        self.accounts[account.id] = account
        
        if user_id not in self.user_accounts:
            self.user_accounts[user_id] = []
        self.user_accounts[user_id].append(account.id)
        
        # Initialize storage
        self.signals[account.id] = []
        self.positions[account.id] = []
        self.pending_orders[account.id] = []
        self.account_eas[account.id] = []
        
        logger.info(f"Added MT{version} account: {account.id}")
        return account
    
    def get_account(self, account_id: str) -> Optional[Dict]:
        """Get account details"""
        account = self.accounts.get(account_id)
        if account:
            return account.to_dict()
        return None
    
    def list_user_accounts(self, user_id: str) -> List[Dict]:
        """List all accounts for a user"""
        account_ids = self.user_accounts.get(user_id, [])
        return [self.accounts[aid].to_dict() for aid in account_ids if aid in self.accounts]
    
    def update_connection_status(self, account_id: str, status: str, error: str = None):
        """Update connection status"""
        account = self.accounts.get(account_id)
        if not account:
            return False
        
        account.connection_status = ConnectionStatus(status)
        
        if status == 'connected':
            account.last_connected = datetime.now()
        elif error:
            account.last_error = error
        
        return True
    
    def update_account_info(self, account_id: str, info: Dict):
        """Update account information from MT"""
        account = self.accounts.get(account_id)
        if not account:
            return False
        
        account.account_number = info.get('account_number', account.account_number)
        account.account_balance = info.get('balance', account.account_balance)
        account.account_equity = info.get('equity', account.account_equity)
        account.account_margin = info.get('margin', account.account_margin)
        account.account_profit = info.get('profit', account.account_profit)
        account.leverage = info.get('leverage', account.leverage)
        account.currency = info.get('currency', account.currency)
        
        return True
    
    def update_positions(self, account_id: str, positions: List[Dict]):
        """Update positions from MT"""
        if account_id not in self.positions:
            return False
        
        mt_positions = []
        for pos in positions:
            mt_positions.append(MTPosition(
                ticket=pos['ticket'],
                symbol=pos['symbol'],
                action=pos['action'],
                volume=pos['volume'],
                open_price=pos['open_price'],
                current_price=pos['current_price'],
                sl=pos.get('sl'),
                tp=pos.get('tp'),
                swap=pos.get('swap', 0.0),
                profit=pos.get('profit', 0.0),
                open_time=datetime.fromisoformat(pos['open_time']) if 'open_time' in pos else None,
                magic_number=pos.get('magic_number', 0),
                comment=pos.get('comment', '')
            ))
        
        self.positions[account_id] = mt_positions
        return True
    
    def update_pending_orders(self, account_id: str, orders: List[Dict]):
        """Update pending orders from MT"""
        if account_id not in self.pending_orders:
            return False
        
        mt_orders = []
        for order in orders:
            mt_orders.append(MTOrder(
                ticket=order['ticket'],
                symbol=order['symbol'],
                order_type=order['order_type'],
                volume=order['volume'],
                price=order['price'],
                sl=order.get('sl'),
                tp=order.get('tp'),
                expiration=datetime.fromisoformat(order['expiration']) if 'expiration' in order else None,
                magic_number=order.get('magic_number', 0),
                comment=order.get('comment', '')
            ))
        
        self.pending_orders[account_id] = mt_orders
        return True
    
    def configure_ea(self, account_id: str, name: str, magic_number: int,
                    config: Dict = None) -> EAConfiguration:
        """Configure an Expert Advisor"""
        
        ea = EAConfiguration(
            id=str(uuid.uuid4()),
            account_id=account_id,
            name=name,
            magic_number=magic_number,
            strategy_type=config.get('strategy_type', '') if config else '',
            timeframe=config.get('timeframe', 'H1') if config else 'H1',
            symbols=config.get('symbols', []) if config else [],
            risk_per_trade_pct=config.get('risk_per_trade_pct', 1.0) if config else 1.0,
            max_daily_trades=config.get('max_daily_trades', 10) if config else 10,
            use_trailing_stop=config.get('use_trailing_stop', False) if config else False,
            use_breakeven=config.get('use_breakeven', False) if config else False,
            use_partial_close=config.get('use_partial_close', False) if config else False
        )
        
        self.ea_configs[ea.id] = ea
        
        if account_id not in self.account_eas:
            self.account_eas[account_id] = []
        self.account_eas[account_id].append(ea.id)
        
        logger.info(f"Configured EA: {ea.id} for account {account_id}")
        return ea
    
    def get_ea_config(self, ea_id: str) -> Optional[Dict]:
        """Get EA configuration"""
        ea = self.ea_configs.get(ea_id)
        if ea:
            return ea.to_dict()
        return None
    
    def list_account_eas(self, account_id: str) -> List[Dict]:
        """List all EAs for an account"""
        ea_ids = self.account_eas.get(account_id, [])
        return [self.ea_configs[eid].to_dict() for eid in ea_ids if eid in self.ea_configs]
    
    def receive_signal(self, account_id: str, signal_data: Dict) -> TradeSignal:
        """Receive a trade signal from MT EA"""
        
        signal = TradeSignal(
            id=str(uuid.uuid4()),
            account_id=account_id,
            action=SignalAction(signal_data['action']),
            symbol=signal_data['symbol'],
            volume=signal_data['volume'],
            price=signal_data.get('price'),
            sl=signal_data.get('sl'),
            tp=signal_data.get('tp'),
            magic_number=signal_data.get('magic_number', 0),
            comment=signal_data.get('comment', ''),
            ea_name=signal_data.get('ea_name', '')
        )
        
        self.signals[account_id].append(signal)
        
        logger.info(f"Received signal: {signal.id} - {signal.action.value} {signal.symbol}")
        return signal
    
    def process_signal(self, signal_id: str, result: str) -> bool:
        """Mark a signal as processed with result"""
        for signals in self.signals.values():
            for signal in signals:
                if signal.id == signal_id:
                    signal.processed = True
                    signal.processed_time = datetime.now()
                    signal.result = result
                    return True
        return False
    
    def get_signals(self, account_id: str, unprocessed_only: bool = False,
                   limit: int = 100) -> List[Dict]:
        """Get signals for an account"""
        signals = self.signals.get(account_id, [])
        
        if unprocessed_only:
            signals = [s for s in signals if not s.processed]
        
        signals.sort(key=lambda s: s.timestamp, reverse=True)
        
        return [s.to_dict() for s in signals[:limit]]
    
    def get_positions(self, account_id: str) -> List[Dict]:
        """Get current positions for an account"""
        positions = self.positions.get(account_id, [])
        return [p.to_dict() for p in positions]
    
    def get_pending_orders(self, account_id: str) -> List[Dict]:
        """Get pending orders for an account"""
        orders = self.pending_orders.get(account_id, [])
        return [
            {
                'ticket': o.ticket,
                'symbol': o.symbol,
                'order_type': o.order_type,
                'volume': o.volume,
                'price': o.price,
                'sl': o.sl,
                'tp': o.tp,
                'magic_number': o.magic_number,
                'comment': o.comment
            }
            for o in orders
        ]
    
    def generate_mt_code(self, ea_config_id: str) -> Optional[str]:
        """Generate MQL4/5 code for EA configuration"""
        ea = self.ea_configs.get(ea_config_id)
        if not ea:
            return None
        
        account = self.accounts.get(ea.account_id)
        if not account:
            return None
        
        version = account.version.value
        
        code_lines = [
            f"// Auto-generated EA Configuration for {ea.name}",
            f"// MetaTrader {version}",
            f"// Generated: {datetime.now().isoformat()}",
            "",
            "#property copyright \"Financial Master\"",
            f"#property link \"https://financialmaster.com\"",
            f"#property version   \"1.00\"",
            "",
            "// Input Parameters",
            f"input int MagicNumber = {ea.magic_number};",
            f"input double RiskPerTrade = {ea.risk_per_trade_pct};",
            f"input int MaxDailyTrades = {ea.max_daily_trades};",
            f"input double MaxSpread = {ea.max_spread_points};",
            "input group \"=== Risk Management ===\"",
            f"input bool UseTrailingStop = {str(ea.use_trailing_stop).lower()};",
            f"input bool UseBreakeven = {str(ea.use_breakeven).lower()};",
            f"input bool UsePartialClose = {str(ea.use_partial_close).lower()};",
            "",
            "// Global variables",
            "int tradeCountToday = 0;",
            "datetime lastTradeDay = 0;",
            "",
            "//+------------------------------------------------------------------+",
            "//| Expert initialization function                                   |",
            "//+------------------------------------------------------------------+",
            "int OnInit()",
            "{",
            "   // Initialize connection to Financial Master",
            f"   Print(\"EA {ea.name} initialized\");",
            "   return(INIT_SUCCEEDED);",
            "}",
            "",
            "//+------------------------------------------------------------------+",
            "//| Expert deinitialization function                                 |",
            "//+------------------------------------------------------------------+",
            "void OnDeinit(const int reason)",
            "{",
            "   Print(\"EA deinitialized\");",
            "}",
            "",
            "//+------------------------------------------------------------------+",
            "//| Expert tick function                                             |",
            "//+------------------------------------------------------------------+",
            "void OnTick()",
            "{",
            "   // Check daily trade limit",
            "   if(TimeDay(TimeCurrent()) != TimeDay(lastTradeDay))",
            "   {",
            "      tradeCountToday = 0;",
            "      lastTradeDay = TimeCurrent();",
            "   }",
            "",
            "   // Check spread",
            "   if(MarketInfo(Symbol(), MODE_SPREAD) > MaxSpread)",
            "      return;",
            "",
            "   // Your strategy logic here",
            "   // ...",
            "",
            "   // Send signal to Financial Master when trade triggered",
            "   // SendSignal(action, symbol, volume, price, sl, tp);",
            "}",
            "",
            "//+------------------------------------------------------------------+",
            "//| Send signal to Financial Master                                  |",
            "//+------------------------------------------------------------------+",
            f"void SendSignal(string action, string symbol, double volume, ",
            f"               double price, double sl, double tp)",
            "{",
            "   // Format signal for ZeroMQ transmission",
            "   string signal = StringFormat(\"{\\\"action\\\":\\\"%s\\\",\\\"symbol\\\":\\\"%s\\\",\\\"volume\\\":%f,\\\"price\\\":%f,\\\"sl\\\":%f,\\\"tp\\\":%f,\\\"magic\\\":%d}\",",
            "                    action, symbol, volume, price, sl, tp, MagicNumber);",
            "   ",
            "   // Send via ZeroMQ (requires socket setup)",
            "   Print(\"Signal sent: \", signal);",
            "}",
            "",
            "//+------------------------------------------------------------------+"
        ]
        
        return '\n'.join(code_lines)
    
    def get_account_summary(self, account_id: str) -> Dict:
        """Get account summary"""
        account = self.accounts.get(account_id)
        if not account:
            return {'error': 'Account not found'}
        
        positions = self.positions.get(account_id, [])
        orders = self.pending_orders.get(account_id, [])
        recent_signals = self.signals.get(account_id, [])[-20:]  # Last 20
        
        return {
            'account': account.to_dict(),
            'summary': {
                'open_positions': len(positions),
                'pending_orders': len(orders),
                'unrealized_pnl': sum(p.profit for p in positions),
                'total_volume_open': sum(p.volume for p in positions),
                'signals_24h': len([s for s in recent_signals 
                                   if s.timestamp > datetime.now() - timedelta(hours=24)])
            },
            'positions': [p.to_dict() for p in positions],
            'recent_signals': [s.to_dict() for s in recent_signals]
        }
