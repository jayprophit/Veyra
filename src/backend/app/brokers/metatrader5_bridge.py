"""
MetaTrader 5 (MT5) Bridge Integration
MQL5 Connector for Forex, CFDs, and automated trading
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MT5OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class MT5TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"


@dataclass
class MT5Symbol:
    name: str
    category: str  # forex, cfd, futures, stock
    bid: float
    ask: float
    spread: float
    digits: int
    point: float
    trade_allowed: bool
    volume_min: float
    volume_max: float
    volume_step: float


@dataclass
class MT5Position:
    ticket: int
    symbol: str
    type: str  # buy/sell
    volume: float
    open_price: float
    current_price: float
    sl: float  # stop loss
    tp: float  # take profit
    profit: float
    swap: float
    commission: float
    open_time: datetime


@dataclass
class MT5Order:
    ticket: int
    symbol: str
    type: str
    volume: float
    price: float
    sl: float
    tp: float
    comment: str
    status: str


class MetaTrader5Bridge:
    """Bridge to MetaTrader 5 terminal via ZeroMQ or MT5 API"""
    
    def __init__(self, account: str = "", password: str = "", server: str = ""):
        self.account = account
        self.password = password
        self.server = server
        self.connected = False
        self.symbols: Dict[str, MT5Symbol] = {}
        self.positions: Dict[int, MT5Position] = {}
        self.orders: Dict[int, MT5Order] = {}
        self.mql5_experts: Dict[str, Any] = {}
        
    async def connect(self) -> bool:
        """Connect to MT5 terminal via ZeroMQ or COM interface"""
        try:
            # Simulation mode - would use mt5 python package or ZeroMQ
            logger.info(f"Connecting to MT5 server: {self.server}")
            await asyncio.sleep(0.1)  # Simulate connection
            self.connected = True
            await self._load_symbols()
            return True
        except Exception as e:
            logger.error(f"MT5 connection failed: {e}")
            return False
    
    async def _load_symbols(self):
        """Load available trading symbols from MT5"""
        # Major forex pairs
        forex_pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", 
            "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
        ]
        
        for pair in forex_pairs:
            self.symbols[pair] = MT5Symbol(
                name=pair,
                category="forex",
                bid=1.0850,
                ask=1.0852,
                spread=0.0002,
                digits=5,
                point=0.00001,
                trade_allowed=True,
                volume_min=0.01,
                volume_max=500.0,
                volume_step=0.01
            )
        
        # CFDs and indices
        cfds = ["US30", "US500", "USTEC", "GER30", "UK100", "JPN225"]
        for cfd in cfds:
            self.symbols[cfd] = MT5Symbol(
                name=cfd,
                category="cfd",
                bid=35000.0,
                ask=35000.5,
                spread=0.5,
                digits=1,
                point=0.1,
                trade_allowed=True,
                volume_min=0.1,
                volume_max=1000.0,
                volume_step=0.1
            )
        
        logger.info(f"Loaded {len(self.symbols)} symbols from MT5")
    
    async def get_symbols(self, category: Optional[str] = None) -> List[MT5Symbol]:
        """Get available symbols, optionally filtered by category"""
        if category:
            return [s for s in self.symbols.values() if s.category == category]
        return list(self.symbols.values())
    
    async def get_symbol_info(self, symbol: str) -> Optional[MT5Symbol]:
        """Get detailed symbol information"""
        return self.symbols.get(symbol)
    
    async def market_order(
        self,
        symbol: str,
        action: MT5TradeAction,
        volume: float,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = ""
    ) -> Optional[MT5Order]:
        """Execute market order"""
        if not self.connected:
            raise ConnectionError("Not connected to MT5")
        
        sym = self.symbols.get(symbol)
        if not sym:
            raise ValueError(f"Symbol {symbol} not found")
        
        price = sym.ask if action == MT5TradeAction.BUY else sym.bid
        
        order = MT5Order(
            ticket=len(self.orders) + 1,
            symbol=symbol,
            type=action.value,
            volume=volume,
            price=price,
            sl=sl or 0.0,
            tp=tp or 0.0,
            comment=comment,
            status="filled"
        )
        
        self.orders[order.ticket] = order
        
        # Create position
        position = MT5Position(
            ticket=order.ticket,
            symbol=symbol,
            type=action.value,
            volume=volume,
            open_price=price,
            current_price=price,
            sl=sl or 0.0,
            tp=tp or 0.0,
            profit=0.0,
            swap=0.0,
            commission=volume * 0.0001,
            open_time=datetime.now()
        )
        self.positions[position.ticket] = position
        
        logger.info(f"MT5 Market order: {action.value} {volume} {symbol} @ {price}")
        return order
    
    async def close_position(self, position_ticket: int) -> bool:
        """Close open position by ticket"""
        if position_ticket not in self.positions:
            return False
        
        position = self.positions[position_ticket]
        
        # Calculate P&L
        sym = self.symbols[position.symbol]
        exit_price = sym.bid if position.type == "buy" else sym.ask
        
        if position.type == "buy":
            profit = (exit_price - position.open_price) * position.volume * 100000
        else:
            profit = (position.open_price - exit_price) * position.volume * 100000
        
        position.profit = profit
        position.current_price = exit_price
        
        logger.info(f"Closed position {position_ticket}: P&L = ${profit:.2f}")
        
        # Remove from active positions
        del self.positions[position_ticket]
        return True
    
    async def get_positions(self) -> List[MT5Position]:
        """Get all open positions"""
        return list(self.positions.values())
    
    async def modify_position(
        self,
        position_ticket: int,
        sl: Optional[float] = None,
        tp: Optional[float] = None
    ) -> bool:
        """Modify stop loss and take profit"""
        if position_ticket not in self.positions:
            return False
        
        position = self.positions[position_ticket]
        if sl is not None:
            position.sl = sl
        if tp is not None:
            position.tp = tp
        
        return True
    
    async def load_mql5_expert(self, name: str, code: str) -> bool:
        """Load MQL5 Expert Advisor code"""
        self.mql5_experts[name] = {
            "code": code,
            "loaded_at": datetime.now(),
            "active": False
        }
        logger.info(f"Loaded MQL5 Expert: {name}")
        return True
    
    async def run_mql5_expert(self, name: str) -> bool:
        """Run loaded MQL5 Expert Advisor"""
        if name not in self.mql5_experts:
            return False
        
        self.mql5_experts[name]["active"] = True
        logger.info(f"Running MQL5 Expert: {name}")
        return True
    
    async def stop_mql5_expert(self, name: str) -> bool:
        """Stop running MQL5 Expert Advisor"""
        if name not in self.mql5_experts:
            return False
        
        self.mql5_experts[name]["active"] = False
        logger.info(f"Stopped MQL5 Expert: {name}")
        return True
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get MT5 account information"""
        return {
            "login": self.account,
            "server": self.server,
            "balance": 10000.0,
            "equity": 10050.0,
            "margin": 100.0,
            "free_margin": 9950.0,
            "margin_level": 10050.0,
            "currency": "USD",
            "positions_count": len(self.positions)
        }
    
    async def get_history(self, from_date: datetime, to_date: datetime) -> List[Dict]:
        """Get trade history for date range"""
        return []  # Would query MT5 history
    
    async def disconnect(self):
        """Disconnect from MT5 terminal"""
        self.connected = False
        logger.info("Disconnected from MT5")


class MQL5CodeGenerator:
    """Generate MQL5 code for Expert Advisors"""
    
    @staticmethod
    def generate_ma_crossover(
        fast_period: int = 10,
        slow_period: int = 20,
        lot_size: float = 0.1
    ) -> str:
        """Generate Moving Average crossover EA code"""
        return f'''
//+------------------------------------------------------------------+
//| Moving Average Crossover EA                                    |
//+------------------------------------------------------------------+
input int FastMA = {fast_period};
input int SlowMA = {slow_period};
input double LotSize = {lot_size};
input int Slippage = 3;
input int MagicNumber = 12345;

double fast_buffer[];
double slow_buffer[];

int OnInit()
{{
   SetIndexBuffer(0, fast_buffer, INDICATOR_DATA);
   SetIndexBuffer(1, slow_buffer, INDICATOR_DATA);
   return(INIT_SUCCEEDED);
}}

void OnTick()
{{
   double fast = iMA(NULL, 0, FastMA, 0, MODE_SMA, PRICE_CLOSE, 0);
   double slow = iMA(NULL, 0, SlowMA, 0, MODE_SMA, PRICE_CLOSE, 0);
   
   static double prev_fast = 0;
   static double prev_slow = 0;
   
   if(prev_fast < prev_slow && fast > slow)
   {{
      // Golden Cross - Buy
      if(OrdersTotal() == 0 && PositionsTotal() == 0)
         OrderSend(Symbol(), OP_BUY, LotSize, Ask, Slippage, 0, 0, "MA Cross", MagicNumber, 0, clrGreen);
   }}
   else if(prev_fast > prev_slow && fast < slow)
   {{
      // Death Cross - Sell
      if(OrdersTotal() == 0 && PositionsTotal() == 0)
         OrderSend(Symbol(), OP_SELL, LotSize, Bid, Slippage, 0, 0, "MA Cross", MagicNumber, 0, clrRed);
   }}
   
   prev_fast = fast;
   prev_slow = slow;
}}
'''
    
    @staticmethod
    def generate_grid_bot(
        grid_size: float = 0.001,
        grid_count: int = 10,
        lot_size: float = 0.01
    ) -> str:
        """Generate Grid Bot EA code"""
        return f'''
//+------------------------------------------------------------------+
//| Grid Trading Bot EA                                              |
//+------------------------------------------------------------------+
input double GridSize = {grid_size};
input int GridLevels = {grid_count};
input double LotSize = {lot_size};
input int MagicNumber = 54321;

double grid_levels[];
bool grid_active[];

int OnInit()
{{
   ArrayResize(grid_levels, GridLevels * 2 + 1);
   ArrayResize(grid_active, GridLevels * 2 + 1);
   
   double center = (Ask + Bid) / 2;
   for(int i = 0; i <= GridLevels * 2; i++)
   {{
      grid_levels[i] = center + (i - GridLevels) * GridSize;
      grid_active[i] = false;
   }}
   
   return(INIT_SUCCEEDED);
}}

void OnTick()
{{
   for(int i = 0; i < ArraySize(grid_levels); i++)
   {{
      if(!grid_active[i])
      {{
         if(Ask <= grid_levels[i])
         {{
            OrderSend(Symbol(), OP_BUY, LotSize, Ask, 3, 0, 0, "Grid Buy", MagicNumber, 0, clrBlue);
            grid_active[i] = true;
         }}
         else if(Bid >= grid_levels[i])
         {{
            OrderSend(Symbol(), OP_SELL, LotSize, Bid, 3, 0, 0, "Grid Sell", MagicNumber, 0, clrOrange);
            grid_active[i] = true;
         }}
      }}
   }}
}}
'''
    
    @staticmethod
    def generate_rsi_strategy(
        period: int = 14,
        overbought: float = 70.0,
        oversold: float = 30.0,
        lot_size: float = 0.1
    ) -> str:
        """Generate RSI strategy EA code"""
        return f'''
//+------------------------------------------------------------------+
//| RSI Strategy EA                                                  |
//+------------------------------------------------------------------+
input int RSIPeriod = {period};
input double Overbought = {overbought};
input double Oversold = {oversold};
input double LotSize = {lot_size};
input int MagicNumber = 99999;

int OnInit()
{{
   return(INIT_SUCCEEDED);
}}

void OnTick()
{{
   double rsi = iRSI(NULL, 0, RSIPeriod, PRICE_CLOSE, 0);
   static bool was_oversold = false;
   static bool was_overbought = false;
   
   if(rsi < Oversold) was_oversold = true;
   if(rsi > Overbought) was_overbought = true;
   
   if(was_oversold && rsi > Oversold && PositionsTotal() == 0)
   {{
      OrderSend(Symbol(), OP_BUY, LotSize, Ask, 3, 0, 0, "RSI Buy", MagicNumber, 0, clrGreen);
      was_oversold = false;
   }}
   
   if(was_overbought && rsi < Overbought && PositionsTotal() == 0)
   {{
      OrderSend(Symbol(), OP_SELL, LotSize, Bid, 3, 0, 0, "RSI Sell", MagicNumber, 0, clrRed);
      was_overbought = false;
   }}
}}
'''


# Global MT5 bridge instance
_mt5_bridge: Optional[MetaTrader5Bridge] = None


async def get_mt5_bridge() -> MetaTrader5Bridge:
    """Get or create MT5 bridge instance"""
    global _mt5_bridge
    if _mt5_bridge is None:
        _mt5_bridge = MetaTrader5Bridge()
    return _mt5_bridge
