"""
Social Trading API Endpoints
=============================
Comprehensive social trading and collaboration API for Veyra
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from ..social_trading.social_trading_manager import (
    get_social_trading_manager,
    CopyTradeMode,
    TradeStatus
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social-trading", tags=["social-trading"])


# Trader Profile Endpoints
@router.post("/traders/profile")
async def create_trader_profile(
    user_id: str,
    username: str,
    display_name: str,
    bio: str,
    trading_style: str,
    risk_level: str
):
    """Create trader profile"""
    try:
        social_trading = get_social_trading_manager()
        profile = await social_trading.create_trader_profile(
            user_id, username, display_name, bio, trading_style, risk_level
        )
        
        return {
            "trader_id": profile.trader_id,
            "username": profile.username,
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url,
            "bio": profile.bio,
            "trading_style": profile.trading_style,
            "risk_level": profile.risk_level,
            "created_at": profile.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traders/{trader_id}/profile")
async def get_trader_profile(trader_id: str):
    """Get trader profile"""
    try:
        social_trading = get_social_trading_manager()
        profile = social_trading.get_trader_profile(trader_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="Trader profile not found")
            
        return {
            "trader_id": profile.trader_id,
            "username": profile.username,
            "display_name": profile.display_name,
            "avatar_url": profile.avatar_url,
            "bio": profile.bio,
            "trading_style": profile.trading_style,
            "risk_level": profile.risk_level,
            "win_rate": profile.win_rate,
            "total_trades": profile.total_trades,
            "profitable_trades": profile.profitable_trades,
            "followers_count": profile.followers_count,
            "following_count": profile.following_count,
            "copied_trades_count": profile.copied_trades_count,
            "avg_return": profile.avg_return,
            "max_drawdown": profile.max_drawdown,
            "sharpe_ratio": profile.sharpe_ratio,
            "is_verified": profile.is_verified,
            "is_premium": profile.is_premium,
            "created_at": profile.created_at.isoformat(),
            "last_active": profile.last_active.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traders/{trader_id}/performance")
async def update_trader_performance(trader_id: str, trade_result: Dict[str, Any]):
    """Update trader performance"""
    try:
        social_trading = get_social_trading_manager()
        await social_trading.update_trader_performance(trader_id, trade_result)
        
        return {"message": "Performance updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Following System
@router.post("/traders/{trader_id}/follow")
async def follow_trader(trader_id: str, user_id: str):
    """Follow a trader"""
    try:
        social_trading = get_social_trading_manager()
        success = await social_trading.follow_trader(user_id, trader_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to follow trader")
            
        return {"message": "Successfully followed trader"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/traders/{trader_id}/unfollow")
async def unfollow_trader(trader_id: str, user_id: str):
    """Unfollow a trader"""
    try:
        social_trading = get_social_trading_manager()
        success = await social_trading.unfollow_trader(user_id, trader_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unfollow trader")
            
        return {"message": "Successfully unfollowed trader"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}/following")
async def get_following_list(user_id: str):
    """Get list of traders followed by user"""
    try:
        social_trading = get_social_trading_manager()
        following = social_trading.get_following_list(user_id)
        
        return {
            "following": [
                {
                    "trader_id": trader.trader_id,
                    "username": trader.username,
                    "display_name": trader.display_name,
                    "avatar_url": trader.avatar_url,
                    "win_rate": trader.win_rate,
                    "followers_count": trader.followers_count
                }
                for trader in following
            ],
            "count": len(following)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traders/{trader_id}/followers")
async def get_followers_list(trader_id: str):
    """Get list of users following trader"""
    try:
        social_trading = get_social_trading_manager()
        followers = social_trading.get_followers_list(trader_id)
        
        return {
            "followers": followers,
            "count": len(followers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Copy Trading
@router.post("/traders/{trader_id}/copy-settings")
async def set_copy_trade_settings(trader_id: str, user_id: str, settings: Dict[str, Any]):
    """Set copy trading settings"""
    try:
        social_trading = get_social_trading_manager()
        success = await social_trading.set_copy_trade_settings(user_id, trader_id, settings)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to set copy trade settings")
            
        return {"message": "Copy trade settings updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trade-signals")
async def create_trade_signal(
    trader_id: str,
    symbol: str,
    action: str,
    quantity: float,
    price: float,
    reasoning: str,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
    confidence: float = 0.8
):
    """Create trade signal for copy trading"""
    try:
        social_trading = get_social_trading_manager()
        signal = await social_trading.create_trade_signal(
            trader_id, symbol, action, quantity, price, reasoning,
            stop_loss, take_profit, confidence
        )
        
        return {
            "signal_id": signal.signal_id,
            "trader_id": signal.trader_id,
            "symbol": signal.symbol,
            "action": signal.action,
            "quantity": signal.quantity,
            "price": signal.price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "confidence": signal.confidence,
            "reasoning": signal.reasoning,
            "created_at": signal.created_at.isoformat(),
            "expires_at": signal.expires_at.isoformat(),
            "status": signal.status.value,
            "copied_by_count": len(signal.copied_by)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trade-signals")
async def get_trade_signals(
    trader_id: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get trade signals"""
    try:
        social_trading = get_social_trading_manager()
        signals = social_trading.get_trade_signals(trader_id, since)
        
        return {
            "signals": [
                {
                    "signal_id": signal.signal_id,
                    "trader_id": signal.trader_id,
                    "symbol": signal.symbol,
                    "action": signal.action,
                    "quantity": signal.quantity,
                    "price": signal.price,
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit,
                    "confidence": signal.confidence,
                    "reasoning": signal.reasoning,
                    "created_at": signal.created_at.isoformat(),
                    "expires_at": signal.expires_at.isoformat(),
                    "status": signal.status.value,
                    "copied_by_count": len(signal.copied_by)
                }
                for signal in signals[:limit]
            ],
            "count": len(signals[:limit])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Leaderboard
@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(50, ge=1, le=100)):
    """Get trading leaderboard"""
    try:
        social_trading = get_social_trading_manager()
        leaderboard = social_trading.get_leaderboard(limit)
        
        return {
            "leaderboard": leaderboard,
            "count": len(leaderboard)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Trading Rooms
@router.post("/rooms")
async def create_trading_room(
    creator_id: str,
    name: str,
    description: str,
    is_public: bool = True,
    max_members: int = 100
):
    """Create trading room"""
    try:
        social_trading = get_social_trading_manager()
        room = await social_trading.create_trading_room(
            creator_id, name, description, is_public, max_members
        )
        
        return {
            "room_id": room.room_id,
            "name": room.name,
            "description": room.description,
            "creator_id": room.creator_id,
            "members": room.members,
            "admins": room.admins,
            "is_public": room.is_public,
            "max_members": room.max_members,
            "created_at": room.created_at.isoformat(),
            "last_activity": room.last_activity.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/join")
async def join_trading_room(room_id: str, user_id: str):
    """Join trading room"""
    try:
        social_trading = get_social_trading_manager()
        success = await social_trading.join_trading_room(room_id, user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to join room")
            
        return {"message": "Successfully joined trading room"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/leave")
async def leave_trading_room(room_id: str, user_id: str):
    """Leave trading room"""
    try:
        social_trading = get_social_trading_manager()
        success = await social_trading.leave_trading_room(room_id, user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to leave room")
            
        return {"message": "Successfully left trading room"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms")
async def get_trading_rooms(
    user_id: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get trading rooms"""
    try:
        social_trading = get_social_trading_manager()
        rooms = social_trading.get_trading_rooms(user_id, is_public)
        
        return {
            "rooms": [
                {
                    "room_id": room.room_id,
                    "name": room.name,
                    "description": room.description,
                    "creator_id": room.creator_id,
                    "members_count": len(room.members),
                    "is_public": room.is_public,
                    "max_members": room.max_members,
                    "created_at": room.created_at.isoformat(),
                    "last_activity": room.last_activity.isoformat()
                }
                for room in rooms[:limit]
            ],
            "count": len(rooms[:limit])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Social Trading Dashboard
@router.get("/dashboard/{user_id}")
async def get_social_trading_dashboard(user_id: str):
    """Get comprehensive social trading dashboard"""
    try:
        social_trading = get_social_trading_manager()
        
        # Get following list
        following = social_trading.get_following_list(user_id)
        
        # Get recent trade signals from followed traders
        recent_signals = []
        for trader in following[:10]:  # Limit to top 10 followed traders
            signals = social_trading.get_trade_signals(
                trader_id=trader.trader_id,
                since=datetime.now() - timedelta(days=7)
            )
            recent_signals.extend(signals[:3])  # Top 3 signals per trader
            
        # Sort by creation time
        recent_signals.sort(key=lambda x: x.created_at, reverse=True)
        
        # Get leaderboard
        leaderboard = social_trading.get_leaderboard(10)
        
        # Get user's trading rooms
        user_rooms = social_trading.get_trading_rooms(user_id=user_id)
        
        return {
            "following_count": len(following),
            "following": [
                {
                    "trader_id": trader.trader_id,
                    "username": trader.username,
                    "display_name": trader.display_name,
                    "win_rate": trader.win_rate,
                    "avg_return": trader.avg_return,
                    "followers_count": trader.followers_count
                }
                for trader in following[:5]
            ],
            "recent_signals": [
                {
                    "signal_id": signal.signal_id,
                    "trader_username": next(
                        (t.username for t in following if t.trader_id == signal.trader_id),
                        "Unknown"
                    ),
                    "symbol": signal.symbol,
                    "action": signal.action,
                    "confidence": signal.confidence,
                    "reasoning": signal.reasoning,
                    "created_at": signal.created_at.isoformat()
                }
                for signal in recent_signals[:10]
            ],
            "leaderboard": leaderboard[:5],
            "trading_rooms": [
                {
                    "room_id": room.room_id,
                    "name": room.name,
                    "members_count": len(room.members),
                    "last_activity": room.last_activity.isoformat()
                }
                for room in user_rooms[:5]
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
