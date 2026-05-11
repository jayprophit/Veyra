"""
Freqtrade Adapter for Veyra
Integrates with open-source Freqtrade bot framework
https://github.com/freqtrade/freqtrade

Features:
- Strategy import/export from Freqtrade
- Bot management API
- Backtesting integration
- Live trading control
- Performance analytics
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import subprocess
import os

logger = logging.getLogger(__name__)


class FreqtradeMode(Enum):
    """Freqtrade operation modes"""
    DRY_RUN = "dry_run"  # Paper trading
    LIVE = "live"        # Real money
    BACKTEST = "backtest"
    EDGE = "edge"


class StrategyStatus(Enum):
    """Strategy lifecycle status"""
    IMPORTED = "imported"
    TESTING = "testing"
    ACTIVE = "active"
    PAUSED = "paused"
    FAILED = "failed"


@dataclass
class FreqtradeStrategy:
    """Represents a Freqtrade strategy"""
    id: str
    name: str
    description: str
    timeframe: str  # 5m, 15m, 1h, 4h, 1d
    minimal_roi: Dict[str, float]  # {"0": 0.1, "60": 0.05}
    stoploss: float
    trailing_stop: bool
    trailing_stop_positive: Optional[float]
    sell_profit_only: bool
    ignore_roi_if_buy_signal: bool
    startup_candle_count: int
    order_types: Dict[str, str]
    order_time_in_force: Dict[str, str]
    use_exit_signal: bool
    exit_profit_only: bool
    exit_profit_offset: float
    custom_info: Dict[str, Any] = field(default_factory=dict)
    source_code: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    status: StrategyStatus = StrategyStatus.IMPORTED
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'timeframe': self.timeframe,
            'minimal_roi': self.minimal_roi,
            'stoploss': self.stoploss,
            'trailing_stop': self.trailing_stop,
            'trailing_stop_positive': self.trailing_stop_positive,
            'sell_profit_only': self.sell_profit_only,
            'ignore_roi_if_buy_signal': self.ignore_roi_if_buy_signal,
            'startup_candle_count': self.startup_candle_count,
            'order_types': self.order_types,
            'order_time_in_force': self.order_time_in_force,
            'use_exit_signal': self.use_exit_signal,
            'exit_profit_only': self.exit_profit_only,
            'exit_profit_offset': self.exit_profit_offset,
            'custom_info': self.custom_info,
            'performance_metrics': self.performance_metrics,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None
        }


@dataclass
class BotInstance:
    """Represents a running Freqtrade bot instance"""
    id: str
    name: str
    exchange: str
    pair_whitelist: List[str]
    strategy_id: str
    mode: FreqtradeMode
    stake_currency: str
    stake_amount: float
    max_open_trades: int
    status: str  # running, stopped, error
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    profit_stats: Dict[str, float] = field(default_factory=dict)
    open_trades: List[Dict] = field(default_factory=list)
    trade_history: List[Dict] = field(default_factory=list)


class FreqtradeAdapter:
    """
    Adapter for Freqtrade open-source trading bot
    Manages strategies, bots, and performance
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/freqtrade"
        self.strategies: Dict[str, FreqtradeStrategy] = {}
        self.bot_instances: Dict[str, BotInstance] = {}
        self.api_base_url: str = "http://localhost:8080"  # Freqtrade API
        self.api_username: str = ""
        self.api_password: str = ""
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Create default strategies
        self._create_default_strategies()
    
    def _create_default_strategies(self):
        """Create built-in Freqtrade strategies"""
        default_strategies = [
            FreqtradeStrategy(
                id="samplestrategy_v1",
                name="SampleStrategy",
                description="Basic EMA crossover strategy with RSI confirmation",
                timeframe="5m",
                minimal_roi={"0": 0.1, "60": 0.05, "120": 0.025},
                stoploss=-0.10,
                trailing_stop=True,
                trailing_stop_positive=0.02,
                sell_profit_only=False,
                ignore_roi_if_buy_signal=False,
                startup_candle_count=30,
                order_types={
                    "buy": "limit",
                    "sell": "limit",
                    "emergencysell": "market",
                    "forcebuy": "market",
                    "forcesell": "market",
                    "stoploss": "market",
                    "stoploss_on_exchange": False,
                    "stoploss_on_exchange_interval": 60
                },
                order_time_in_force={"buy": "gtc", "sell": "gtc"},
                use_exit_signal=True,
                exit_profit_only=False,
                exit_profit_offset=0.01,
                custom_info={
                    "indicators": ["ema_fast", "ema_slow", "rsi"],
                    "ema_fast_period": 12,
                    "ema_slow_period": 26,
                    "rsi_period": 14,
                    "rsi_overbought": 70,
                    "rsi_oversold": 30
                }
            ),
            
            FreqtradeStrategy(
                id="bbrsi_v1",
                name="BBRSI Strategy",
                description="Bollinger Bands + RSI mean reversion strategy",
                timeframe="15m",
                minimal_roi={"0": 0.05, "30": 0.03, "60": 0.01},
                stoploss=-0.05,
                trailing_stop=True,
                trailing_stop_positive=0.015,
                sell_profit_only=True,
                ignore_roi_if_buy_signal=True,
                startup_candle_count=100,
                order_types={
                    "buy": "limit",
                    "sell": "limit",
                    "emergencysell": "market",
                    "forcebuy": "market",
                    "forcesell": "market",
                    "stoploss": "market"
                },
                order_time_in_force={"buy": "gtc", "sell": "gtc"},
                use_exit_signal=True,
                exit_profit_only=True,
                exit_profit_offset=0.005,
                custom_info={
                    "indicators": ["bb_lower", "bb_middle", "bb_upper", "rsi"],
                    "bb_period": 20,
                    "bb_std": 2,
                    "rsi_period": 14,
                    "rsi_oversold": 35,
                    "rsi_overbought": 65
                }
            ),
            
            FreqtradeStrategy(
                id="macd_v1",
                name="MACD Trend Strategy",
                description="MACD histogram trend following strategy",
                timeframe="1h",
                minimal_roi={"0": 0.15, "120": 0.10, "240": 0.05},
                stoploss=-0.08,
                trailing_stop=True,
                trailing_stop_positive=0.03,
                trailing_stop_positive_offset=0.05,
                sell_profit_only=False,
                ignore_roi_if_buy_signal=False,
                startup_candle_count=100,
                order_types={
                    "buy": "limit",
                    "sell": "limit",
                    "emergencysell": "market",
                    "forcebuy": "market",
                    "forcesell": "market",
                    "stoploss": "market"
                },
                order_time_in_force={"buy": "gtc", "sell": "gtc"},
                use_exit_signal=True,
                exit_profit_only=False,
                exit_profit_offset=0.02,
                custom_info={
                    "indicators": ["macd", "macdsignal", "macdhist"],
                    "macd_fast": 12,
                    "macd_slow": 26,
                    "macd_signal": 9,
                    "trend_ema_period": 200
                }
            ),
            
            FreqtradeStrategy(
                id="grid_v1",
                name="Grid Trading Strategy",
                description="Automated grid trading for ranging markets",
                timeframe="5m",
                minimal_roi={"0": 0.02},  # Small frequent profits
                stoploss=-0.15,  # Wider stop for grid strategy
                trailing_stop=False,
                trailing_stop_positive=None,
                sell_profit_only=False,
                ignore_roi_if_buy_signal=False,
                startup_candle_count=50,
                order_types={
                    "buy": "limit",
                    "sell": "limit",
                    "emergencysell": "market",
                    "forcebuy": "market",
                    "forcesell": "market",
                    "stoploss": "market"
                },
                order_time_in_force={"buy": "gtc", "sell": "gtc"},
                use_exit_signal=False,
                exit_profit_only=False,
                exit_profit_offset=0,
                custom_info={
                    "grid_levels": 10,
                    "grid_spacing_pct": 0.5,
                    "max_grids": 5,
                    "profit_per_grid": 0.5,
                    "trading_range": "auto_detect"
                }
            ),
            
            FreqtradeStrategy(
                id="breakout_v1",
                name="Breakout Strategy",
                description="Support/Resistance breakout with volume confirmation",
                timeframe="15m",
                minimal_roi={"0": 0.08, "60": 0.04, "120": 0.02},
                stoploss=-0.06,
                trailing_stop=True,
                trailing_stop_positive=0.02,
                sell_profit_only=False,
                ignore_roi_if_buy_signal=True,
                startup_candle_count=200,
                order_types={
                    "buy": "market",  # Breakout needs quick entry
                    "sell": "limit",
                    "emergencysell": "market",
                    "forcebuy": "market",
                    "forcesell": "market",
                    "stoploss": "market"
                },
                order_time_in_force={"buy": "ioc", "sell": "gtc"},
                use_exit_signal=True,
                exit_profit_only=False,
                exit_profit_offset=0.01,
                custom_info={
                    "indicators": ["atr", "volume", "resistance", "support"],
                    "lookback_period": 20,
                    "atr_multiplier": 1.5,
                    "volume_threshold": 1.5,
                    "breakout_confirmation": True
                }
            )
        ]
        
        for strategy in default_strategies:
            self.strategies[strategy.id] = strategy
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    def generate_strategy_code(self, strategy: FreqtradeStrategy) -> str:
        """Generate Freqtrade-compatible Python strategy code"""
        
        code = f'''# Generated Freqtrade Strategy: {strategy.name}
# Timestamp: {datetime.now().isoformat()}

from freqtrade.strategy import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class {strategy.name.replace(" ", "")}(IStrategy):
    """
    {strategy.description}
    """
    
    # Strategy parameters
    timeframe = '{strategy.timeframe}'
    stoploss = {strategy.stoploss}
    trailing_stop = {strategy.trailing_stop}
    trailing_stop_positive = {strategy.trailing_stop_positive if strategy.trailing_stop_positive else 'None'}
    startup_candle_count = {strategy.startup_candle_count}
    
    # ROI table
    minimal_roi = {strategy.minimal_roi}
    
    # Stoploss configuration
    use_exit_signal = {strategy.use_exit_signal}
    exit_profit_only = {strategy.exit_profit_only}
    exit_profit_offset = {strategy.exit_profit_offset}
    ignore_roi_if_buy_signal = {strategy.ignore_roi_if_buy_signal}
    
    # Order configuration
    order_types = {strategy.order_types}
    order_time_in_force = {strategy.order_time_in_force}
    
'''
        
        # Add indicator initialization based on strategy type
        if 'ema' in strategy.custom_info.get('indicators', []):
            code += '''
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Add EMA indicators"""
        ema_fast_period = {period}
        ema_slow_period = {slow_period}
        
        dataframe['ema_fast'] = ta.EMA(dataframe, timeperiod=ema_fast_period)
        dataframe['ema_slow'] = ta.EMA(dataframe, timeperiod=ema_slow_period)
        
        if 'rsi' in self.custom_info.get('indicators', []):
            dataframe['rsi'] = ta.RSI(dataframe, timeperiod={rsi_period})
        
        return dataframe
    
    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define buy signal"""
        conditions = []
        
        # EMA Crossover
        conditions.append(dataframe['ema_fast'] > dataframe['ema_slow'])
        conditions.append(dataframe['ema_fast'].shift(1) <= dataframe['ema_slow'].shift(1))
        
        if 'rsi' in self.custom_info.get('indicators', []):
            conditions.append(dataframe['rsi'] < {rsi_oversold})
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'buy'
            ] = 1
        
        return dataframe
    
    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """Define sell signal"""
        conditions = []
        
        # EMA Crossunder
        conditions.append(dataframe['ema_fast'] < dataframe['ema_slow'])
        conditions.append(dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1))
        
        if 'rsi' in self.custom_info.get('indicators', []):
            conditions.append(dataframe['rsi'] > {rsi_overbought})
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'sell'
            ] = 1
        
        return dataframe
'''.format(
                period=strategy.custom_info.get('ema_fast_period', 12),
                slow_period=strategy.custom_info.get('ema_slow_period', 26),
                rsi_period=strategy.custom_info.get('rsi_period', 14),
                rsi_oversold=strategy.custom_info.get('rsi_oversold', 30),
                rsi_overbought=strategy.custom_info.get('rsi_overbought', 70)
            )
        
        return code
    
    def create_bot_config(self, bot: BotInstance) -> Dict:
        """Create Freqtrade-compatible config.json"""
        
        strategy = self.strategies.get(bot.strategy_id)
        if not strategy:
            raise ValueError(f"Strategy {bot.strategy_id} not found")
        
        config = {
            "max_open_trades": bot.max_open_trades,
            "stake_currency": bot.stake_currency,
            "stake_amount": bot.stake_amount,
            "tradable_balance_ratio": 0.99,
            "fiat_display_currency": "USD",
            "dry_run": bot.mode == FreqtradeMode.DRY_RUN,
            "cancel_open_orders_on_exit": False,
            "unfilledtimeout": {
                "buy": 10,
                "sell": 30,
                "exit_timeout_countdown": 30
            },
            "entry_pricing": {
                "price_side": "other",
                "use_order_book": True,
                "order_book_top": 1,
                "price_last_balance": 0.0,
                "check_depth_of_market": {
                    "enabled": False,
                    "bids_to_ask_delta": 1
                }
            },
            "exit_pricing": {
                "price_side": "other",
                "use_order_book": True,
                "order_book_top": 1
            },
            "exchange": {
                "name": bot.exchange,
                "key": "",
                "secret": "",
                "ccxt_config": {},
                "ccxt_async_config": {},
                "pair_whitelist": bot.pair_whitelist,
                "pair_blacklist": [
                    "BNB/.*",
                    "BUSD/.*",
                    "USDC/.*",
                    "USDT/.*"
                ]
            },
            "pairlists": [
                {"method": "StaticPairList"},
                {"method": "AgeFilter", "min_days_listed": 30},
                {"method": "PriceFilter", "low_price_ratio": 0.01}
            ],
            "telegram": {
                "enabled": False
            },
            "api_server": {
                "enabled": True,
                "listen_ip_address": "127.0.0.1",
                "listen_port": 8080,
                "verbosity": "error",
                "jwt_secret_key": "auto_generated_secret",
                "CORS_origins": [],
                "username": "freqtrader",
                "password": "secure_password"
            },
            "bot_name": bot.name,
            "initial_state": "running",
            "forcebuy_enable": False,
            "internals": {
                "process_throttle_secs": 5
            },
            "strategy": strategy.name.replace(" ", ""),
            "strategy_path": "user_data/strategies/"
        }
        
        return config
    
    async def start_bot(self, bot_id: str) -> Dict:
        """Start a Freqtrade bot instance"""
        bot = self.bot_instances.get(bot_id)
        if not bot:
            return {'error': f'Bot {bot_id} not found'}
        
        try:
            # Generate config
            config = self.create_bot_config(bot)
            
            # Save config to file
            config_path = f"{self.config_path}/{bot_id}_config.json"
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Generate strategy code
            strategy = self.strategies.get(bot.strategy_id)
            if strategy:
                strategy_code = self.generate_strategy_code(strategy)
                strategy_path = f"{self.config_path}/strategies/{strategy.name.replace(' ', '')}.py"
                os.makedirs(os.path.dirname(strategy_path), exist_ok=True)
                with open(strategy_path, 'w') as f:
                    f.write(strategy_code)
            
            # Start freqtrade process (simulated)
            # In production, this would use subprocess to start freqtrade
            bot.status = "running"
            bot.started_at = datetime.now()
            
            logger.info(f"Started Freqtrade bot: {bot_id}")
            
            return {
                'status': 'success',
                'bot_id': bot_id,
                'config_path': config_path,
                'started_at': bot.started_at.isoformat()
            }
            
        except Exception as e:
            bot.status = "error"
            logger.error(f"Failed to start bot {bot_id}: {e}")
            return {'error': str(e)}
    
    async def stop_bot(self, bot_id: str) -> Dict:
        """Stop a Freqtrade bot instance"""
        bot = self.bot_instances.get(bot_id)
        if not bot:
            return {'error': f'Bot {bot_id} not found'}
        
        bot.status = "stopped"
        bot.stopped_at = datetime.now()
        
        logger.info(f"Stopped Freqtrade bot: {bot_id}")
        
        return {
            'status': 'success',
            'bot_id': bot_id,
            'stopped_at': bot.stopped_at.isoformat()
        }
    
    async def get_bot_status(self, bot_id: str) -> Dict:
        """Get status of a running bot"""
        bot = self.bot_instances.get(bot_id)
        if not bot:
            return {'error': f'Bot {bot_id} not found'}
        
        return {
            'bot_id': bot.id,
            'name': bot.name,
            'status': bot.status,
            'exchange': bot.exchange,
            'strategy': bot.strategy_id,
            'mode': bot.mode.value,
            'open_trades': len(bot.open_trades),
            'total_trades': len(bot.trade_history),
            'profit_stats': bot.profit_stats,
            'started_at': bot.started_at.isoformat() if bot.started_at else None,
            'uptime_hours': self._calculate_uptime(bot) if bot.started_at else 0
        }
    
    def _calculate_uptime(self, bot: BotInstance) -> float:
        """Calculate bot uptime in hours"""
        if not bot.started_at:
            return 0
        end = bot.stopped_at or datetime.now()
        return (end - bot.started_at).total_seconds() / 3600
    
    def create_bot(self, name: str, exchange: str, pair_whitelist: List[str],
                   strategy_id: str, mode: FreqtradeMode = FreqtradeMode.DRY_RUN,
                   stake_currency: str = "USDT", stake_amount: float = 100,
                   max_open_trades: int = 3) -> BotInstance:
        """Create a new bot instance"""
        
        bot_id = f"bot_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        bot = BotInstance(
            id=bot_id,
            name=name,
            exchange=exchange,
            pair_whitelist=pair_whitelist,
            strategy_id=strategy_id,
            mode=mode,
            stake_currency=stake_currency,
            stake_amount=stake_amount,
            max_open_trades=max_open_trades,
            status="created"
        )
        
        self.bot_instances[bot_id] = bot
        
        logger.info(f"Created Freqtrade bot: {bot_id}")
        
        return bot
    
    def list_strategies(self) -> List[Dict]:
        """List all available strategies"""
        return [s.to_dict() for s in self.strategies.values()]
    
    def list_bots(self) -> List[Dict]:
        """List all bot instances"""
        return [
            {
                'id': b.id,
                'name': b.name,
                'exchange': b.exchange,
                'strategy_id': b.strategy_id,
                'mode': b.mode.value,
                'status': b.status,
                'open_trades': len(b.open_trades),
                'total_profit': b.profit_stats.get('total_profit_usd', 0)
            }
            for b in self.bot_instances.values()
        ]
    
    async def backtest_strategy(self, strategy_id: str, timerange: str,
                               exchange: str = "binance") -> Dict:
        """Run backtest for a strategy"""
        strategy = self.strategies.get(strategy_id)
        if not strategy:
            return {'error': f'Strategy {strategy_id} not found'}
        
        # Simulated backtest results
        # In production, this would call freqtrade backtesting
        results = {
            'strategy': strategy_id,
            'timerange': timerange,
            'exchange': exchange,
            'total_trades': 150,
            'wins': 87,
            'losses': 63,
            'win_rate': 0.58,
            'profit_mean': 0.025,
            'profit_sum': 3.75,
            'profit_total': 0.15,  # 15% return
            'profit_total_abs': 1500,
            'max_drawdown': 0.08,
            'sharpe_ratio': 1.4,
            'sortino_ratio': 2.1,
            'calmar_ratio': 1.9,
            'expectancy': 0.018,
            'avg_trade_duration': "3 hours 45 minutes",
            'best_trade': 0.12,
            'worst_trade': -0.06,
            'backtest_date': datetime.now().isoformat()
        }
        
        strategy.performance_metrics = results
        strategy.status = StrategyStatus.TESTING
        
        return results
    
    def import_strategy(self, name: str, source_code: str,
                       description: str = "") -> FreqtradeStrategy:
        """Import a custom strategy from source code"""
        
        strategy_id = f"imported_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        strategy = FreqtradeStrategy(
            id=strategy_id,
            name=name,
            description=description or f"Imported strategy: {name}",
            timeframe="5m",
            minimal_roi={"0": 0.1},
            stoploss=-0.10,
            trailing_stop=False,
            trailing_stop_positive=None,
            sell_profit_only=False,
            ignore_roi_if_buy_signal=False,
            startup_candle_count=30,
            order_types={"buy": "limit", "sell": "limit"},
            order_time_in_force={"buy": "gtc", "sell": "gtc"},
            use_exit_signal=True,
            exit_profit_only=False,
            exit_profit_offset=0.01,
            source_code=source_code,
            status=StrategyStatus.IMPORTED
        )
        
        self.strategies[strategy_id] = strategy
        
        logger.info(f"Imported strategy: {strategy_id}")
        
        return strategy
