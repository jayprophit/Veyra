"""
Broker Manager
Unified interface for multiple broker APIs
Route orders to best available broker
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import asyncio

from .alpaca_client import AlpacaClient, AlpacaOrder, OrderSide as AlpacaSide
from .trading212_client import Trading212Client, Trading212Order


class BrokerType(Enum):
    ALPACA = "alpaca"
    INTERACTIVE_BROKERS = "interactive_brokers"
    TRADING212 = "trading212"


@dataclass
class LiveTradeOrder:
    """Unified trade order format"""
    order_id: str
    user_id: str
    broker_type: BrokerType
    
    symbol: str
    side: str  # buy or sell
    quantity: Optional[Decimal] = None
    notional: Optional[Decimal] = None  # Dollar amount
    
    order_type: str = "market"  # market, limit, stop, stop_limit
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: str = "day"  # day, gtc, ioc, fok
    
    extended_hours: bool = False
    
    # Metadata
    status: str = "pending"
    broker_order_id: Optional[str] = None
    filled_quantity: Decimal = Decimal("0")
    filled_price: Optional[Decimal] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class BrokerManager:
    """
    Manages multiple broker connections
    Routes orders to best available broker
    Provides unified interface
    """
    
    def __init__(self):
        self.brokers: Dict[BrokerType, Any] = {}
        self.orders: Dict[str, LiveTradeOrder] = {}
        self.user_broker_mapping: Dict[str, BrokerType] = {}  # user_id -> preferred broker
        
        # Routing rules
        self.routing_rules = {
            "fractional": [BrokerType.ALPACA, BrokerType.TRADING212],  # Brokers that support fractional
            "crypto": [BrokerType.ALPACA],  # Brokers that support crypto
            "options": [BrokerType.INTERACTIVE_BROKERS],  # Brokers that support options
            "international": [BrokerType.TRADING212, BrokerType.INTERACTIVE_BROKERS],  # Non-US markets
        }
    
    async def add_broker(
        self,
        broker_type: BrokerType,
        credentials: Dict[str, str],
        paper: bool = True
    ):
        """
        Add and initialize a broker connection
        
        Args:
            broker_type: Type of broker
            credentials: API keys and secrets
            paper: Use paper trading (if supported)
        """
        if broker_type == BrokerType.ALPACA:
            client = AlpacaClient(
                api_key=credentials["api_key"],
                api_secret=credentials["api_secret"],
                paper=paper
            )
            self.brokers[broker_type] = client
            
        elif broker_type == BrokerType.TRADING212:
            client = Trading212Client(
                api_key=credentials["api_key"],
                demo=paper
            )
            self.brokers[broker_type] = client
            
        elif broker_type == BrokerType.INTERACTIVE_BROKERS:
            from .interactive_brokers import InteractiveBrokersClient
            client = InteractiveBrokersClient(
                api_key=credentials["api_key"],
                api_secret=credentials["api_secret"],
                paper_trading=paper
            )
            await client.connect()
            self.brokers[broker_type] = client
    
    async def route_order(
        self,
        user_id: str,
        symbol: str,
        side: str,
        quantity: Optional[Decimal] = None,
        notional: Optional[Decimal] = None,
        order_type: str = "market",
        limit_price: Optional[Decimal] = None,
        **kwargs
    ) -> LiveTradeOrder:
        """
        Route order to best broker
        
        Routing logic:
        1. Check user preference
        2. Check fractional requirements
        3. Check asset type (stock, crypto, options)
        4. Select broker with best execution
        """
        # Determine broker
        broker_type = await self._select_broker(
            user_id=user_id,
            symbol=symbol,
            quantity=quantity,
            notional=notional,
            **kwargs
        )
        
        if broker_type not in self.brokers:
            raise ValueError(f"Broker {broker_type.value} not connected")
        
        # Create unified order
        order = LiveTradeOrder(
            order_id=f"order_{user_id}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            broker_type=broker_type,
            symbol=symbol,
            side=side,
            quantity=quantity,
            notional=notional,
            order_type=order_type,
            limit_price=limit_price,
            **kwargs
        )
        
        self.orders[order.order_id] = order
        
        # Submit to specific broker
        try:
            if broker_type == BrokerType.ALPACA:
                await self._submit_to_alpaca(order)
            elif broker_type == BrokerType.TRADING212:
                await self._submit_to_trading212(order)
            elif broker_type == BrokerType.INTERACTIVE_BROKERS:
                await self._submit_to_ib(order)
                
            order.status = "submitted"
            
        except Exception as e:
            order.status = "failed"
            raise e
        
        return order
    
    async def _select_broker(
        self,
        user_id: str,
        symbol: str,
        quantity: Optional[Decimal],
        notional: Optional[Decimal],
        **kwargs
    ) -> BrokerType:
        """Select best broker for order"""
        
        # Check user preference
        if user_id in self.user_broker_mapping:
            preferred = self.user_broker_mapping[user_id]
            if preferred in self.brokers:
                return preferred
        
        # Check fractional requirement
        is_fractional = False
        if notional and not quantity:
            is_fractional = True
        elif quantity and quantity % 1 != 0:
            is_fractional = True
        
        if is_fractional:
            for broker in self.routing_rules["fractional"]:
                if broker in self.brokers:
                    return broker
        
        # Check crypto
        if symbol.upper() in ["BTC", "ETH", "ADA", "SOL"]:
            for broker in self.routing_rules["crypto"]:
                if broker in self.brokers:
                    return broker
        
        # Default to first available broker
        if self.brokers:
            return list(self.brokers.keys())[0]
        
        raise ValueError("No brokers available")
    
    async def _submit_to_alpaca(self, order: LiveTradeOrder):
        """Submit order to Alpaca"""
        client: AlpacaClient = self.brokers[order.broker_type]
        
        alpaca_order = AlpacaOrder(
            symbol=order.symbol,
            qty=order.quantity,
            notional=order.notional,
            side=AlpacaSide.BUY if order.side == "buy" else AlpacaSide.SELL,
            limit_price=order.limit_price,
            client_order_id=order.order_id
        )
        
        result = await client.submit_order(alpaca_order)
        order.broker_order_id = result.get("id")
    
    async def _submit_to_trading212(self, order: LiveTradeOrder):
        """Submit order to Trading212"""
        client: Trading212Client = self.brokers[order.broker_type]
        
        t212_order = Trading212Order(
            ticker=order.symbol,
            quantity=order.quantity,
            value=order.notional,
            limit_price=order.limit_price
        )
        
        result = await client.submit_order(order.symbol, order.side, t212_order)
        order.broker_order_id = result.get("id")
    
    async def _submit_to_ib(self, order: LiveTradeOrder):
        """Submit order to Interactive Brokers"""
        client = self.brokers[order.broker_type]
        
        result = await client.place_order(
            symbol=order.symbol,
            action=order.side.upper(),
            quantity=int(order.quantity) if order.quantity else 0,
            order_type=order.order_type.upper(),
            price=float(order.limit_price) if order.limit_price else None
        )
        
        order.broker_order_id = result.get("order_id")
    
    async def get_order_status(self, order_id: str) -> Optional[LiveTradeOrder]:
        """Get status of an order"""
        return self.orders.get(order_id)
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        order = self.orders.get(order_id)
        if not order:
            return False
        
        if order.broker_type == BrokerType.ALPACA:
            client: AlpacaClient = self.brokers[order.broker_type]
            return await client.cancel_order(order.broker_order_id)
        
        elif order.broker_type == BrokerType.TRADING212:
            client: Trading212Client = self.brokers[order.broker_type]
            return await client.delete_order(order.broker_order_id)
        
        return False
    
    async def get_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all positions for a user across all brokers"""
        all_positions = []
        
        for broker_type, client in self.brokers.items():
            try:
                if broker_type == BrokerType.ALPACA:
                    positions = await client.get_positions()
                    for pos in positions:
                        all_positions.append({
                            "broker": broker_type.value,
                            "symbol": pos.symbol,
                            "quantity": float(pos.qty),
                            "market_value": float(pos.market_value),
                            "avg_entry": float(pos.avg_entry_price),
                            "unrealized_pnl": float(pos.unrealized_pl),
                            "asset_class": pos.asset_class
                        })
                
                elif broker_type == BrokerType.TRADING212:
                    positions = await client.get_positions()
                    for pos in positions:
                        all_positions.append({
                            "broker": broker_type.value,
                            "symbol": pos.get("ticker"),
                            "quantity": float(pos.get("quantity", 0)),
                            "market_value": float(pos.get("currentPrice", 0)) * float(pos.get("quantity", 0)),
                            "avg_entry": float(pos.get("averagePrice", 0)),
                            "unrealized_pnl": None,
                            "asset_class": "equity"
                        })
                        
            except Exception as e:
                print(f"Error getting positions from {broker_type.value}: {e}")
        
        return all_positions
    
    async def get_account_summary(self, user_id: str) -> Dict[str, Any]:
        """Get combined account summary across all brokers"""
        summary = {
            "user_id": user_id,
            "brokers": [],
            "total_equity": Decimal("0"),
            "total_cash": Decimal("0"),
            "buying_power": Decimal("0")
        }
        
        for broker_type, client in self.brokers.items():
            try:
                if broker_type == BrokerType.ALPACA:
                    account = await client.get_account()
                    summary["brokers"].append({
                        "broker": broker_type.value,
                        "equity": float(account.get("equity", 0)),
                        "cash": float(account.get("cash", 0)),
                        "buying_power": float(account.get("buying_power", 0)),
                        "currency": account.get("currency", "USD")
                    })
                    summary["total_equity"] += Decimal(str(account.get("equity", 0)))
                    summary["total_cash"] += Decimal(str(account.get("cash", 0)))
                    summary["buying_power"] += Decimal(str(account.get("buying_power", 0)))
                    
            except Exception as e:
                print(f"Error getting account from {broker_type.value}: {e}")
        
        summary["total_equity"] = float(summary["total_equity"])
        summary["total_cash"] = float(summary["total_cash"])
        summary["buying_power"] = float(summary["buying_power"])
        
        return summary
    
    async def set_user_broker_preference(self, user_id: str, broker_type: BrokerType):
        """Set user's preferred broker"""
        self.user_broker_mapping[user_id] = broker_type
    
    async def get_broker_status(self) -> Dict[str, Any]:
        """Get status of all connected brokers"""
        return {
            broker_type.value: {
                "connected": True,
                "paper_trading": getattr(client, 'paper', False) or getattr(client, 'demo', False)
            }
            for broker_type, client in self.brokers.items()
        }
