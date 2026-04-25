"""
WebSocket Manager - Real-Time Bidirectional Communication
===========================================================
Handles multiple WebSocket connections, broadcasting, and authentication.
Integrates with real-time data feeds and client dashboards.
"""

import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect, Depends
from starlette.websockets import WebSocketState

from database_layer import DatabaseManager
from realtime_data_integration import RealtimeDataIntegration

logger = logging.getLogger(__name__)


class WebSocketEventType(Enum):
    """Types of WebSocket events."""
    PRICE_UPDATE = "price_update"
    PORTFOLIO_UPDATE = "portfolio_update"
    TRADE_EXECUTED = "trade_executed"
    ALERT_TRIGGERED = "alert_triggered"
    SYSTEM_STATUS = "system_status"
    USER_MESSAGE = "user_message"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    AUTH = "auth"
    PING = "ping"
    PONG = "pong"


@dataclass
class WebSocketMessage:
    """Standard WebSocket message format."""
    type: str
    timestamp: str
    data: dict
    user_id: Optional[str] = None
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "timestamp": self.timestamp,
            "data": self.data,
            "user_id": self.user_id
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> "WebSocketMessage":
        data = json.loads(json_str)
        return cls(
            type=data.get("type", "unknown"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            data=data.get("data", {}),
            user_id=data.get("user_id")
        )


class ConnectionManager:
    """
    Manages WebSocket connections with authentication and broadcasting.
    """
    
    def __init__(self):
        # Active connections: {websocket: {user_id, subscribed_symbols, auth_status}}
        self.active_connections: Dict[WebSocket, dict] = {}
        
        # User connections: {user_id: [websockets]}
        self.user_connections: Dict[str, List[WebSocket]] = {}
        
        # Symbol subscriptions: {symbol: [websockets]}
        self.symbol_subscriptions: Dict[str, Set[WebSocket]] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            "total_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "peak_connections": 0
        }
        
        self._running = True
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        """Accept new WebSocket connection."""
        await websocket.accept()
        
        self.active_connections[websocket] = {
            "user_id": user_id,
            "subscribed_symbols": set(),
            "auth_status": user_id is not None,
            "connected_at": datetime.now().isoformat(),
            "last_ping": datetime.now()
        }
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(websocket)
        
        self.stats["total_connections"] = len(self.active_connections)
        self.stats["peak_connections"] = max(
            self.stats["peak_connections"],
            self.stats["total_connections"]
        )
        
        logger.info(f"WebSocket connected. Total: {self.stats['total_connections']}")
        
        # Send welcome message
        await self.send_personal_message(
            websocket,
            WebSocketMessage(
                type=WebSocketEventType.SYSTEM_STATUS.value,
                timestamp=datetime.now().isoformat(),
                data={
                    "status": "connected",
                    "connection_id": id(websocket),
                    "auth_required": user_id is None
                }
            )
        )
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection."""
        if websocket in self.active_connections:
            conn_info = self.active_connections[websocket]
            user_id = conn_info.get("user_id")
            
            # Remove from symbol subscriptions
            for symbol in conn_info.get("subscribed_symbols", set()):
                if symbol in self.symbol_subscriptions:
                    self.symbol_subscriptions[symbol].discard(websocket)
            
            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].remove(websocket)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from active connections
            del self.active_connections[websocket]
            
            self.stats["total_connections"] = len(self.active_connections)
            logger.info(f"WebSocket disconnected. Total: {self.stats['total_connections']}")
    
    async def send_personal_message(self, websocket: WebSocket, message: WebSocketMessage):
        """Send message to specific client."""
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message.to_json())
                self.stats["messages_sent"] += 1
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: WebSocketMessage, exclude: Optional[WebSocket] = None):
        """Broadcast message to all connected clients."""
        disconnected = []
        
        for websocket in self.active_connections:
            if websocket != exclude:
                try:
                    if websocket.client_state == WebSocketState.CONNECTED:
                        await websocket.send_text(message.to_json())
                        self.stats["messages_sent"] += 1
                except Exception as e:
                    logger.error(f"Error broadcasting: {e}")
                    disconnected.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage):
        """Send message to all connections of a specific user."""
        if user_id not in self.user_connections:
            return
        
        for websocket in self.user_connections[user_id]:
            await self.send_personal_message(websocket, message)
    
    async def broadcast_to_symbol_subscribers(self, symbol: str, message: WebSocketMessage):
        """Send message to clients subscribed to a symbol."""
        if symbol not in self.symbol_subscriptions:
            return
        
        subscribers = list(self.symbol_subscriptions[symbol])
        for websocket in subscribers:
            await self.send_personal_message(websocket, message)
    
    def subscribe_to_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe a client to price updates for a symbol."""
        if websocket not in self.active_connections:
            return
        
        if symbol not in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol] = set()
        
        self.symbol_subscriptions[symbol].add(websocket)
        self.active_connections[websocket]["subscribed_symbols"].add(symbol)
        
        logger.info(f"Client subscribed to {symbol}")
    
    def unsubscribe_from_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a client from price updates for a symbol."""
        if symbol in self.symbol_subscriptions:
            self.symbol_subscriptions[symbol].discard(websocket)
        
        if websocket in self.active_connections:
            self.active_connections[websocket]["subscribed_symbols"].discard(symbol)
        
        logger.info(f"Client unsubscribed from {symbol}")
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """Handle incoming WebSocket message."""
        self.stats["messages_received"] += 1
        
        try:
            data = json.loads(message)
            msg_type = data.get("type", "unknown")
            
            if msg_type == WebSocketEventType.SUBSCRIBE.value:
                symbols = data.get("symbols", [])
                for symbol in symbols:
                    self.subscribe_to_symbol(websocket, symbol)
                
                await self.send_personal_message(
                    websocket,
                    WebSocketMessage(
                        type="subscription_confirmed",
                        timestamp=datetime.now().isoformat(),
                        data={"subscribed_symbols": symbols}
                    )
                )
            
            elif msg_type == WebSocketEventType.UNSUBSCRIBE.value:
                symbols = data.get("symbols", [])
                for symbol in symbols:
                    self.unsubscribe_from_symbol(websocket, symbol)
            
            elif msg_type == WebSocketEventType.AUTH.value:
                # Handle authentication
                token = data.get("token")
                user_id = await self._authenticate(token)
                
                if user_id:
                    self.active_connections[websocket]["user_id"] = user_id
                    self.active_connections[websocket]["auth_status"] = True
                    
                    if user_id not in self.user_connections:
                        self.user_connections[user_id] = []
                    self.user_connections[user_id].append(websocket)
                    
                    await self.send_personal_message(
                        websocket,
                        WebSocketMessage(
                            type="auth_success",
                            timestamp=datetime.now().isoformat(),
                            data={"user_id": user_id}
                        )
                    )
                else:
                    await self.send_personal_message(
                        websocket,
                        WebSocketMessage(
                            type="auth_failed",
                            timestamp=datetime.now().isoformat(),
                            data={"error": "Invalid token"}
                        )
                    )
            
            elif msg_type == WebSocketEventType.PING.value:
                await self.send_personal_message(
                    websocket,
                    WebSocketMessage(
                        type=WebSocketEventType.PONG.value,
                        timestamp=datetime.now().isoformat(),
                        data={}
                    )
                )
            
            else:
                # Handle custom message types
                handler = self.message_handlers.get(msg_type)
                if handler:
                    await handler(websocket, data)
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message[:100]}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _authenticate(self, token: str) -> Optional[str]:
        """Authenticate WebSocket connection."""
        # Implement JWT validation here
        # For now, simple validation
        if token == "valid_token":
            return "user_123"
        return None
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register custom message handler."""
        self.message_handlers[message_type] = handler
    
    async def send_price_update(self, symbol: str, price: float, change: float = 0):
        """Send price update to subscribed clients."""
        message = WebSocketMessage(
            type=WebSocketEventType.PRICE_UPDATE.value,
            timestamp=datetime.now().isoformat(),
            data={
                "symbol": symbol,
                "price": price,
                "change": change,
                "change_percent": (change / (price - change) * 100) if price != change else 0
            }
        )
        
        await self.broadcast_to_symbol_subscribers(symbol, message)
    
    async def send_portfolio_update(self, user_id: str, portfolio_data: dict):
        """Send portfolio update to specific user."""
        message = WebSocketMessage(
            type=WebSocketEventType.PORTFOLIO_UPDATE.value,
            timestamp=datetime.now().isoformat(),
            data=portfolio_data,
            user_id=user_id
        )
        
        await self.broadcast_to_user(user_id, message)
    
    async def send_alert(self, user_id: Optional[str], alert_data: dict):
        """Send alert to user or broadcast."""
        message = WebSocketMessage(
            type=WebSocketEventType.ALERT_TRIGGERED.value,
            timestamp=datetime.now().isoformat(),
            data=alert_data,
            user_id=user_id
        )
        
        if user_id:
            await self.broadcast_to_user(user_id, message)
        else:
            await self.broadcast(message)
    
    def get_stats(self) -> dict:
        """Get connection statistics."""
        return {
            **self.stats,
            "active_connections": len(self.active_connections),
            "authenticated_users": len(self.user_connections),
            "subscribed_symbols": len(self.symbol_subscriptions)
        }


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for FastAPI.
    Usage: ws://localhost:8000/ws
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            await manager.handle_message(websocket, data)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


class WebSocketIntegration:
    """
    Integrates WebSocket with real-time data feeds.
    """
    
    def __init__(self):
        self.realtime_data: Optional[RealtimeDataIntegration] = None
        self._running = False
    
    async def start(self, realtime_data: RealtimeDataIntegration):
        """Start WebSocket integration with real-time data."""
        self.realtime_data = realtime_data
        self._running = True
        
        # Register price callback
        async def on_price_update(symbol: str, price: float):
            # Get previous price for change calculation
            prev_price = self.realtime_data.get_current_price(symbol) if self.realtime_data else price
            change = price - prev_price if prev_price else 0
            
            await manager.send_price_update(symbol, price, change)
        
        # This would integrate with your realtime data provider
        # realtime_data.on_price_update(on_price_update)
        
        logger.info("WebSocket integration started")
    
    async def stop(self):
        """Stop WebSocket integration."""
        self._running = False
        logger.info("WebSocket integration stopped")


# Usage example in api_server.py:
# from websocket_manager import websocket_endpoint
# app.add_api_websocket_route("/ws", websocket_endpoint)
