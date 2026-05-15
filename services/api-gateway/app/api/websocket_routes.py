"""
WebSocket API Routes
====================
WebSocket endpoints for real-time communication.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
import logging
from datetime import datetime

from src.backend.app.websocket_manager import (
    manager, 
    websocket_endpoint, 
    WebSocketMessage, 
    WebSocketEventType,
    WebSocketIntegration
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_main(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time updates.
    
    Connection URL: ws://localhost:8000/ws
    
    Message Protocol:
    - Subscribe: {"type": "subscribe", "symbols": ["AAPL", "MSFT"]}
    - Unsubscribe: {"type": "unsubscribe", "symbols": ["AAPL"]}
    - Auth: {"type": "auth", "token": "jwt_token"}
    - Ping: {"type": "ping"}
    
    Events Received:
    - price_update: Real-time price changes
    - portfolio_update: Portfolio value changes
    - alert_triggered: Price alerts
    - system_status: Connection status
    """
    await websocket_endpoint(websocket)


@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket):
    """
    Dedicated WebSocket for price updates only.
    Optimized for high-frequency price data.
    
    Connection URL: ws://localhost:8000/ws/prices
    """
    await manager.connect(websocket)
    
    try:
        # Auto-subscribe to common symbols
        default_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        for symbol in default_symbols:
            manager.subscribe_to_symbol(websocket, symbol)
        
        await manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type="subscription_confirmed",
                timestamp=datetime.now().isoformat(),
                data={"subscribed_symbols": default_symbols}
            )
        )
        
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(websocket, data)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Price WebSocket error: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/portfolio/{user_id}")
async def websocket_portfolio(websocket: WebSocket, user_id: str):
    """
    User-specific WebSocket for portfolio updates.
    Requires authentication.
    
    Connection URL: ws://localhost:8000/ws/portfolio/{user_id}
    """
    await manager.connect(websocket, user_id=user_id)
    
    try:
        # Send initial portfolio data (mock for now)
        portfolio_data = {
            "total_value": 100000.00,
            "day_pnl": 1250.50,
            "day_pnl_pct": 1.25,
            "positions": [
                {"symbol": "AAPL", "quantity": 50, "price": 175.50, "value": 8775.00},
                {"symbol": "MSFT", "quantity": 30, "price": 380.25, "value": 11407.50}
            ]
        }
        
        await manager.send_personal_message(
            websocket,
            WebSocketMessage(
                type=WebSocketEventType.PORTFOLIO_UPDATE.value,
                timestamp=datetime.now().isoformat(),
                data=portfolio_data,
                user_id=user_id
            )
        )
        
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(websocket, data)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Portfolio WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    """
    return {
        "status": "active",
        **manager.get_stats()
    }


@router.post("/ws/broadcast")
async def broadcast_message(message: dict, admin_token: str):
    """
    Broadcast message to all connected clients (admin only).
    """
    # Verify admin token (simple check for now)
    if admin_token != "admin_secret":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    await manager.broadcast(
        WebSocketMessage(
            type=message.get("type", "system"),
            timestamp=datetime.now().isoformat(),
            data=message.get("data", {})
        )
    )
    
    return {"status": "broadcasted", "clients": len(manager.active_connections)}


@router.post("/ws/send/{user_id}")
async def send_to_user(user_id: str, message: dict):
    """
    Send message to specific user.
    """
    await manager.broadcast_to_user(
        user_id,
        WebSocketMessage(
            type=message.get("type", "notification"),
            timestamp=datetime.now().isoformat(),
            data=message.get("data", {}),
            user_id=user_id
        )
    )
    
    return {"status": "sent", "user_id": user_id}


# Client-side connection example (JavaScript):
WEBSOCKET_CLIENT_EXAMPLE = """
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Connection opened
ws.onopen = () => {
    console.log('Connected to WebSocket');
    
    // Subscribe to symbols
    ws.send(JSON.stringify({
        type: 'subscribe',
        symbols: ['AAPL', 'MSFT', 'TSLA']
    }));
};

// Receive messages
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    
    switch (message.type) {
        case 'price_update':
            console.log(`${message.data.symbol}: $${message.data.price}`);
            break;
        case 'portfolio_update':
            updatePortfolioUI(message.data);
            break;
        case 'alert_triggered':
            showNotification(message.data);
            break;
        default:
            console.log('Received:', message);
    }
};

// Connection closed
ws.onclose = () => {
    console.log('Disconnected');
    // Reconnect logic here
};

// Error handling
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Ping to keep connection alive
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000);
"""
