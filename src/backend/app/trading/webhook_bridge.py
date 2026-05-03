"""
TradingView Webhook Bridge for Financial Master
Receives TradingView alerts and executes trades via broker APIs
Based on TradersPost-style integration
"""

import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SignalAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    CLOSE = "close"
    LONG = "long"
    SHORT = "short"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


@dataclass
class TradingViewAlert:
    """TradingView webhook alert format"""
    ticker: str
    action: SignalAction
    price: Optional[float] = None
    volume: Optional[int] = 100
    timestamp: Optional[datetime] = None
    strategy_id: Optional[str] = None
    comment: Optional[str] = None
    alert_name: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class WebhookHandler:
    """Configuration for a webhook endpoint"""
    webhook_id: str
    user_id: str
    strategy_id: str
    broker_id: str
    created_at: datetime
    total_alerts: int = 0
    executed_trades: int = 0
    failed_trades: int = 0
    last_alert_at: Optional[datetime] = None
    is_active: bool = True
    secret_key: Optional[str] = None  # For HMAC verification


class WebhookBridgeConfig(BaseModel):
    """Configuration for webhook bridge"""
    enable_hmac_verification: bool = True
    max_alerts_per_minute: int = 60
    default_order_quantity: int = 100
    allow_partial_executions: bool = True
    log_all_alerts: bool = True


class TradingViewWebhookBridge:
    """
    Bridge TradingView alerts to broker execution
    Similar to TradersPost functionality
    
    Features:
    - Webhook endpoint generation
    - Alert processing and validation
    - Broker order execution
    - Statistics tracking
    - Rate limiting
    """
    
    def __init__(self, config: WebhookBridgeConfig = None):
        self.config = config or WebhookBridgeConfig()
        self.webhook_handlers: Dict[str, WebhookHandler] = {}
        self.broker_connectors: Dict[str, 'BaseBrokerConnector'] = {}
        self.alert_history: List[Dict] = []
        self.max_history_size = 10000
        
        # Rate limiting
        self.alert_counters: Dict[str, List[datetime]] = {}
        
        # Signal transformers
        self.signal_transformers: Dict[str, Callable] = {}
        
    def register_broker_connector(self, broker_id: str, 
                                   connector: 'BaseBrokerConnector'):
        """Register a broker connector for execution"""
        self.broker_connectors[broker_id] = connector
        logger.info(f"Registered broker connector: {broker_id}")
    
    def create_webhook_endpoint(self, user_id: str, strategy_id: str,
                               broker_id: str, enable_hmac: bool = True) -> Dict:
        """
        Create a new webhook URL for TradingView alerts
        
        Returns:
            Dict with webhook_id, webhook_url, and secret_key (if HMAC enabled)
        """
        webhook_id = f"{user_id}_{strategy_id}_{uuid.uuid4().hex[:8]}"
        webhook_url = f"https://api.financialmaster.com/webhook/{webhook_id}"
        
        # Generate secret key for HMAC verification
        secret_key = None
        if enable_hmac and self.config.enable_hmac_verification:
            secret_key = hashlib.sha256(
                f"{webhook_id}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:32]
        
        handler = WebhookHandler(
            webhook_id=webhook_id,
            user_id=user_id,
            strategy_id=strategy_id,
            broker_id=broker_id,
            created_at=datetime.now(),
            secret_key=secret_key
        )
        
        self.webhook_handlers[webhook_id] = handler
        
        logger.info(f"Created webhook endpoint: {webhook_id} for user {user_id}")
        
        return {
            'webhook_id': webhook_id,
            'webhook_url': webhook_url,
            'secret_key': secret_key,
            'created_at': handler.created_at.isoformat()
        }
    
    def verify_webhook_signature(self, webhook_id: str, 
                                 payload: str, 
                                 signature: str) -> bool:
        """Verify HMAC signature for webhook security"""
        handler = self.webhook_handlers.get(webhook_id)
        if not handler or not handler.secret_key:
            return False
        
        expected_signature = hmac.new(
            handler.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def check_rate_limit(self, webhook_id: str) -> bool:
        """Check if webhook is within rate limits"""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Get alerts in last minute
        alerts = self.alert_counters.get(webhook_id, [])
        recent_alerts = [a for a in alerts if a > minute_ago]
        
        # Update counter
        self.alert_counters[webhook_id] = recent_alerts
        
        return len(recent_alerts) < self.config.max_alerts_per_minute
    
    async def handle_tradingview_alert(self, webhook_id: str, 
                                      alert_data: Dict,
                                      signature: Optional[str] = None) -> Dict:
        """
        Process incoming TradingView webhook alert
        
        Args:
            webhook_id: The webhook endpoint ID
            alert_data: The alert payload from TradingView
            signature: Optional HMAC signature for verification
            
        Returns:
            Dict with execution result
        """
        # Validate webhook exists
        handler = self.webhook_handlers.get(webhook_id)
        if not handler:
            raise HTTPException(status_code=404, detail="Invalid webhook")
        
        if not handler.is_active:
            raise HTTPException(status_code=403, detail="Webhook deactivated")
        
        # Verify signature if HMAC is enabled
        if handler.secret_key and self.config.enable_hmac_verification:
            payload = json.dumps(alert_data, sort_keys=True)
            if not signature or not self.verify_webhook_signature(webhook_id, payload, signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Check rate limits
        if not self.check_rate_limit(webhook_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Parse TradingView alert format
        try:
            alert = self._parse_tradingview_alert(alert_data)
        except ValueError as e:
            logger.error(f"Invalid alert format: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid alert format: {e}")
        
        # Update handler stats
        handler.total_alerts += 1
        handler.last_alert_at = datetime.now()
        self.alert_counters[webhook_id].append(datetime.now())
        
        # Get broker connector
        broker = self.broker_connectors.get(handler.broker_id)
        if not broker:
            logger.error(f"Broker connector not found: {handler.broker_id}")
            raise HTTPException(status_code=500, detail="Broker connector not available")
        
        # Execute trade
        try:
            result = await self._execute_trade(broker, alert, handler)
            handler.executed_trades += 1
            
            # Log alert
            if self.config.log_all_alerts:
                self._log_alert(webhook_id, alert, result)
            
            return {
                'status': 'success',
                'webhook_id': webhook_id,
                'order_id': result.get('order_id'),
                'symbol': alert.ticker,
                'action': alert.action.value,
                'timestamp': datetime.now().isoformat(),
                'message': f"Executed {alert.action.value} order for {alert.ticker}"
            }
            
        except Exception as e:
            handler.failed_trades += 1
            logger.error(f"Trade execution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Trade execution failed: {e}")
    
    def _parse_tradingview_alert(self, alert_data: Dict) -> TradingViewAlert:
        """Parse TradingView alert payload"""
        # TradingView webhook format:
        # {
        #   "ticker": "AAPL",
        #   "action": "buy",
        #   "price": 150.00,
        #   "volume": 100,
        #   "strategy_id": "my_strategy",
        #   "comment": "Breakout detected"
        # }
        
        ticker = alert_data.get('ticker') or alert_data.get('symbol')
        if not ticker:
            raise ValueError("Missing ticker/symbol in alert")
        
        action_str = alert_data.get('action', '').lower()
        try:
            action = SignalAction(action_str)
        except ValueError:
            raise ValueError(f"Invalid action: {action_str}")
        
        return TradingViewAlert(
            ticker=ticker.upper(),
            action=action,
            price=alert_data.get('price'),
            volume=alert_data.get('volume', self.config.default_order_quantity),
            strategy_id=alert_data.get('strategy_id'),
            comment=alert_data.get('comment'),
            alert_name=alert_data.get('alert_name')
        )
    
    async def _execute_trade(self, broker: 'BaseBrokerConnector', 
                            alert: TradingViewAlert,
                            handler: WebhookHandler) -> Dict:
        """Execute trade via broker connector"""
        
        # Map signal action to order side
        side_map = {
            SignalAction.BUY: 'buy',
            SignalAction.LONG: 'buy',
            SignalAction.SELL: 'sell',
            SignalAction.SHORT: 'sell',
            SignalAction.CLOSE: 'close'
        }
        
        side = side_map.get(alert.action)
        
        if alert.action == SignalAction.CLOSE:
            # Close existing position
            return await broker.close_position(alert.ticker)
        
        # Place market order
        order = await broker.place_market_order(
            symbol=alert.ticker,
            side=side,
            quantity=alert.volume,
            metadata={
                'webhook_id': handler.webhook_id,
                'strategy_id': handler.strategy_id,
                'signal_price': alert.price,
                'alert_comment': alert.comment
            }
        )
        
        return order
    
    def _log_alert(self, webhook_id: str, alert: TradingViewAlert, result: Dict):
        """Log alert to history"""
        log_entry = {
            'webhook_id': webhook_id,
            'ticker': alert.ticker,
            'action': alert.action.value,
            'price': alert.price,
            'volume': alert.volume,
            'timestamp': datetime.now().isoformat(),
            'order_id': result.get('order_id'),
            'status': result.get('status', 'unknown')
        }
        
        self.alert_history.append(log_entry)
        
        # Trim history if needed
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]
    
    def get_webhook_stats(self, webhook_id: str) -> Dict:
        """Get statistics for a webhook endpoint"""
        handler = self.webhook_handlers.get(webhook_id)
        if not handler:
            return {'error': 'Webhook not found'}
        
        # Calculate success rate
        total = handler.executed_trades + handler.failed_trades
        success_rate = (handler.executed_trades / total * 100) if total > 0 else 0
        
        return {
            'webhook_id': webhook_id,
            'user_id': handler.user_id,
            'strategy_id': handler.strategy_id,
            'broker_id': handler.broker_id,
            'is_active': handler.is_active,
            'created_at': handler.created_at.isoformat(),
            'total_alerts': handler.total_alerts,
            'executed_trades': handler.executed_trades,
            'failed_trades': handler.failed_trades,
            'success_rate': round(success_rate, 2),
            'last_alert_at': handler.last_alert_at.isoformat() if handler.last_alert_at else None
        }
    
    def list_user_webhooks(self, user_id: str) -> List[Dict]:
        """List all webhooks for a user"""
        user_webhooks = [
            self.get_webhook_stats(wh_id)
            for wh_id, handler in self.webhook_handlers.items()
            if handler.user_id == user_id
        ]
        return user_webhooks
    
    def deactivate_webhook(self, webhook_id: str) -> bool:
        """Deactivate a webhook endpoint"""
        handler = self.webhook_handlers.get(webhook_id)
        if handler:
            handler.is_active = False
            logger.info(f"Deactivated webhook: {webhook_id}")
            return True
        return False
    
    def reactivate_webhook(self, webhook_id: str) -> bool:
        """Reactivate a webhook endpoint"""
        handler = self.webhook_handlers.get(webhook_id)
        if handler:
            handler.is_active = True
            logger.info(f"Reactivated webhook: {webhook_id}")
            return True
        return False


class BaseBrokerConnector:
    """Base class for broker connectors"""
    
    async def place_market_order(self, symbol: str, side: str, 
                                 quantity: int, metadata: Dict = None) -> Dict:
        """Place a market order"""
        raise NotImplementedError
    
    async def close_position(self, symbol: str) -> Dict:
        """Close existing position"""
        raise NotImplementedError
    
    async def get_account_info(self) -> Dict:
        """Get account information"""
        raise NotImplementedError


# FastAPI Routes for Webhook Bridge
from fastapi import APIRouter

webhook_router = APIRouter(prefix="/webhook", tags=["webhooks"])

# Global bridge instance
webhook_bridge = TradingViewWebhookBridge()


@webhook_router.post("/{webhook_id}")
async def receive_tradingview_alert(
    webhook_id: str,
    request: Request,
    x_signature: Optional[str] = Header(None, alias="X-Signature")
):
    """
    Receive TradingView webhook alert
    
    TradingView sends POST requests to this endpoint when alerts trigger
    """
    try:
        alert_data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    result = await webhook_bridge.handle_tradingview_alert(
        webhook_id=webhook_id,
        alert_data=alert_data,
        signature=x_signature
    )
    
    return result


@webhook_router.get("/{webhook_id}/stats")
async def get_webhook_statistics(webhook_id: str):
    """Get statistics for a webhook endpoint"""
    stats = webhook_bridge.get_webhook_stats(webhook_id)
    if 'error' in stats:
        raise HTTPException(status_code=404, detail=stats['error'])
    return stats


@webhook_router.delete("/{webhook_id}")
async def deactivate_webhook_endpoint(webhook_id: str):
    """Deactivate a webhook endpoint"""
    success = webhook_bridge.deactivate_webhook(webhook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return {"status": "deactivated", "webhook_id": webhook_id}
