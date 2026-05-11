"""
Social Trading Manager
======================
Enterprise social trading with copy trading, leaderboards, and community features
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import aiohttp

logger = logging.getLogger(__name__)


class TradeStatus(Enum):
    """Trade status types"""
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class CopyTradeMode(Enum):
    """Copy trading modes"""
    PROPORTIONAL = "proportional"  # Copy proportionally to portfolio size
    FIXED_AMOUNT = "fixed_amount"  # Copy with fixed amount
    PERCENTAGE = "percentage"  # Copy with percentage of portfolio


@dataclass
class TraderProfile:
    """Trader profile for social trading"""
    trader_id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: str
    bio: str
    trading_style: str
    risk_level: str
    win_rate: float
    total_trades: int
    profitable_trades: int
    followers_count: int
    following_count: int
    copied_trades_count: int
    avg_return: float
    max_drawdown: float
    sharpe_ratio: float
    is_verified: bool
    is_premium: bool
    created_at: datetime
    last_active: datetime


@dataclass
class TradeSignal:
    """Trade signal for copy trading"""
    signal_id: str
    trader_id: str
    symbol: str
    action: str  # buy/sell
    quantity: float
    price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    confidence: float
    reasoning: str
    created_at: datetime
    expires_at: datetime
    status: TradeStatus
    copied_by: List[str]


@dataclass
class CopyTradeSettings:
    """Copy trading settings"""
    user_id: str
    trader_id: str
    mode: CopyTradeMode
    max_amount: float
    min_amount: float
    max_positions: int
    copy_stop_loss: bool
    copy_take_profit: bool
    auto_confirm: bool
    is_active: bool
    created_at: datetime


@dataclass
class TradingRoom:
    """Trading room for collaboration"""
    room_id: str
    name: str
    description: str
    creator_id: str
    members: List[str]
    admins: List[str]
    is_public: bool
    max_members: int
    tags: List[str]
    created_at: datetime
    last_activity: datetime


class SocialTradingManager:
    """Enterprise social trading manager"""
    
    def __init__(self):
        self.trader_profiles: Dict[str, TraderProfile] = {}
        self.trade_signals: Dict[str, TradeSignal] = {}
        self.copy_trade_settings: Dict[Tuple[str, str], CopyTradeSettings] = {}
        self.trading_rooms: Dict[str, TradingRoom] = {}
        self.following_relationships: Dict[str, Set[str]] = defaultdict(set)
        self.leaderboard_data: deque = deque(maxlen=1000)
        self.performance_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    async def create_trader_profile(self, user_id: str, username: str,
                                 display_name: str, bio: str,
                                 trading_style: str, risk_level: str) -> TraderProfile:
        """Create trader profile"""
        try:
            trader_id = str(uuid.uuid4())
            
            profile = TraderProfile(
                trader_id=trader_id,
                user_id=user_id,
                username=username,
                display_name=display_name,
                avatar_url=f"https://api.veyra.com/avatars/{user_id}",
                bio=bio,
                trading_style=trading_style,
                risk_level=risk_level,
                win_rate=0.0,
                total_trades=0,
                profitable_trades=0,
                followers_count=0,
                following_count=0,
                copied_trades_count=0,
                avg_return=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                is_verified=False,
                is_premium=False,
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            
            self.trader_profiles[trader_id] = profile
            
            # Log profile creation
            logger.info(f"Created trader profile: {username} ({trader_id})")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error creating trader profile: {e}")
            raise
            
    async def update_trader_performance(self, trader_id: str, trade_result: Dict[str, Any]):
        """Update trader performance metrics"""
        try:
            profile = self.trader_profiles.get(trader_id)
            if not profile:
                return
                
            # Update basic metrics
            profile.total_trades += 1
            if trade_result.get("profit", 0) > 0:
                profile.profitable_trades += 1
                
            # Calculate win rate
            profile.win_rate = profile.profitable_trades / profile.total_trades if profile.total_trades > 0 else 0.0
            
            # Update performance history
            performance_entry = {
                "timestamp": datetime.now(),
                "profit": trade_result.get("profit", 0),
                "return_pct": trade_result.get("return_pct", 0),
                "symbol": trade_result.get("symbol", ""),
                "action": trade_result.get("action", "")
            }
            
            self.performance_history[trader_id].append(performance_entry)
            
            # Calculate advanced metrics
            await self._calculate_advanced_metrics(trader_id)
            
            # Update last activity
            profile.last_active = datetime.now()
            
            # Update leaderboard
            await self._update_leaderboard()
            
        except Exception as e:
            logger.error(f"Error updating trader performance: {e}")
            
    async def _calculate_advanced_metrics(self, trader_id: str):
        """Calculate advanced performance metrics"""
        try:
            profile = self.trader_profiles.get(trader_id)
            if not profile:
                return
                
            history = self.performance_history[trader_id]
            if len(history) < 2:
                return
                
            # Calculate average return
            returns = [entry["return_pct"] for entry in history]
            profile.avg_return = sum(returns) / len(returns)
            
            # Calculate maximum drawdown
            cumulative_returns = []
            running_return = 0
            for ret in returns:
                running_return += ret
                cumulative_returns.append(running_return)
                
            peak = max(cumulative_returns)
            trough = min(cumulative_returns)
            profile.max_drawdown = abs(peak - trough) / peak if peak > 0 else 0.0
            
            # Calculate Sharpe ratio (simplified)
            if len(returns) > 1:
                mean_return = sum(returns) / len(returns)
                variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
                std_dev = variance ** 0.5
                profile.sharpe_ratio = mean_return / std_dev if std_dev > 0 else 0.0
                
        except Exception as e:
            logger.error(f"Error calculating advanced metrics: {e}")
            
    async def _update_leaderboard(self):
        """Update trading leaderboard"""
        try:
            # Get top traders by performance
            traders = list(self.trader_profiles.values())
            
            # Sort by combined score (win_rate * avg_return * sharpe_ratio)
            def calculate_score(trader):
                if trader.total_trades < 10:  # Minimum trades requirement
                    return 0.0
                return trader.win_rate * trader.avg_return * (trader.sharpe_ratio + 1)
                
            sorted_traders = sorted(traders, key=calculate_score, reverse=True)
            
            # Update leaderboard
            self.leaderboard_data.clear()
            for i, trader in enumerate(sorted_traders[:100]):
                self.leaderboard_data.append({
                    "rank": i + 1,
                    "trader_id": trader.trader_id,
                    "username": trader.username,
                    "display_name": trader.display_name,
                    "win_rate": trader.win_rate,
                    "avg_return": trader.avg_return,
                    "sharpe_ratio": trader.sharpe_ratio,
                    "total_trades": trader.total_trades,
                    "followers": trader.followers_count,
                    "score": calculate_score(trader)
                })
                
        except Exception as e:
            logger.error(f"Error updating leaderboard: {e}")
            
    async def create_trade_signal(self, trader_id: str, symbol: str, action: str,
                                quantity: float, price: float, reasoning: str,
                                stop_loss: Optional[float] = None,
                                take_profit: Optional[float] = None,
                                confidence: float = 0.8) -> TradeSignal:
        """Create trade signal for copy trading"""
        try:
            signal_id = str(uuid.uuid4())
            
            signal = TradeSignal(
                signal_id=signal_id,
                trader_id=trader_id,
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                reasoning=reasoning,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                status=TradeStatus.PENDING,
                copied_by=[]
            )
            
            self.trade_signals[signal_id] = signal
            
            # Notify followers
            await self._notify_followers(trader_id, signal)
            
            # Auto-copy for enabled users
            await self._process_auto_copy_trades(signal)
            
            logger.info(f"Created trade signal: {symbol} {action} by {trader_id}")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error creating trade signal: {e}")
            raise
            
    async def _notify_followers(self, trader_id: str, signal: TradeSignal):
        """Notify followers of new trade signal"""
        try:
            followers = self.following_relationships.get(trader_id, set())
            
            # In production, would send real-time notifications
            for follower_id in followers:
                logger.info(f"Notifying follower {follower_id} of trade signal {signal.signal_id}")
                
        except Exception as e:
            logger.error(f"Error notifying followers: {e}")
            
    async def _process_auto_copy_trades(self, signal: TradeSignal):
        """Process automatic copy trades"""
        try:
            # Get users who are copying this trader
            copy_settings = [
                (user_id, settings) for (user_id, trader_id), settings in self.copy_trade_settings.items()
                if trader_id == signal.trader_id and settings.is_active and settings.auto_confirm
            ]
            
            for user_id, settings in copy_settings:
                await self._execute_copy_trade(user_id, signal, settings)
                
        except Exception as e:
            logger.error(f"Error processing auto copy trades: {e}")
            
    async def _execute_copy_trade(self, user_id: str, signal: TradeSignal, settings: CopyTradeSettings):
        """Execute copy trade for user"""
        try:
            # Calculate trade size based on settings
            if settings.mode == CopyTradeMode.PROPORTIONAL:
                # Get user portfolio size (mock)
                portfolio_size = 10000.0  # Mock portfolio size
                trade_size = portfolio_size * 0.02  # 2% of portfolio
            elif settings.mode == CopyTradeMode.FIXED_AMOUNT:
                trade_size = settings.max_amount
            elif settings.mode == CopyTradeMode.PERCENTAGE:
                portfolio_size = 10000.0  # Mock portfolio size
                trade_size = portfolio_size * (settings.max_amount / 100)
            else:
                trade_size = 100.0  # Default
                
            # Validate trade size
            if trade_size < settings.min_amount or trade_size > settings.max_amount:
                return
                
            # Execute trade (mock)
            logger.info(f"Executing copy trade for {user_id}: {signal.symbol} {signal.action} ${trade_size}")
            
            # Update signal
            signal.copied_by.append(user_id)
            
            # Update trader profile
            trader_profile = self.trader_profiles.get(signal.trader_id)
            if trader_profile:
                trader_profile.copied_trades_count += 1
                
        except Exception as e:
            logger.error(f"Error executing copy trade: {e}")
            
    async def follow_trader(self, user_id: str, trader_id: str) -> bool:
        """Follow a trader"""
        try:
            # Add to following relationships
            self.following_relationships[user_id].add(trader_id)
            
            # Update trader profile
            trader_profile = self.trader_profiles.get(trader_id)
            if trader_profile:
                trader_profile.followers_count += 1
                
            logger.info(f"User {user_id} followed trader {trader_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error following trader: {e}")
            return False
            
    async def unfollow_trader(self, user_id: str, trader_id: str) -> bool:
        """Unfollow a trader"""
        try:
            # Remove from following relationships
            self.following_relationships[user_id].discard(trader_id)
            
            # Update trader profile
            trader_profile = self.trader_profiles.get(trader_id)
            if trader_profile:
                trader_profile.followers_count = max(0, trader_profile.followers_count - 1)
                
            logger.info(f"User {user_id} unfollowed trader {trader_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unfollowing trader: {e}")
            return False
            
    async def set_copy_trade_settings(self, user_id: str, trader_id: str,
                                    settings: Dict[str, Any]) -> bool:
        """Set copy trading settings"""
        try:
            copy_settings = CopyTradeSettings(
                user_id=user_id,
                trader_id=trader_id,
                mode=CopyTradeMode(settings.get("mode", "proportional")),
                max_amount=settings.get("max_amount", 1000.0),
                min_amount=settings.get("min_amount", 10.0),
                max_positions=settings.get("max_positions", 10),
                copy_stop_loss=settings.get("copy_stop_loss", True),
                copy_take_profit=settings.get("copy_take_profit", True),
                auto_confirm=settings.get("auto_confirm", False),
                is_active=settings.get("is_active", True),
                created_at=datetime.now()
            )
            
            self.copy_trade_settings[(user_id, trader_id)] = copy_settings
            
            logger.info(f"Set copy trade settings for {user_id} following {trader_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting copy trade settings: {e}")
            return False
            
    async def create_trading_room(self, creator_id: str, name: str,
                               description: str, is_public: bool = True,
                               max_members: int = 100) -> TradingRoom:
        """Create trading room for collaboration"""
        try:
            room_id = str(uuid.uuid4())
            
            room = TradingRoom(
                room_id=room_id,
                name=name,
                description=description,
                creator_id=creator_id,
                members=[creator_id],
                admins=[creator_id],
                is_public=is_public,
                max_members=max_members,
                tags=[],
                created_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            self.trading_rooms[room_id] = room
            
            logger.info(f"Created trading room: {name} ({room_id})")
            return room
            
        except Exception as e:
            logger.error(f"Error creating trading room: {e}")
            raise
            
    async def join_trading_room(self, room_id: str, user_id: str) -> bool:
        """Join trading room"""
        try:
            room = self.trading_rooms.get(room_id)
            if not room:
                return False
                
            if len(room.members) >= room.max_members:
                return False
                
            if user_id not in room.members:
                room.members.append(user_id)
                room.last_activity = datetime.now()
                
            logger.info(f"User {user_id} joined trading room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error joining trading room: {e}")
            return False
            
    async def leave_trading_room(self, room_id: str, user_id: str) -> bool:
        """Leave trading room"""
        try:
            room = self.trading_rooms.get(room_id)
            if not room:
                return False
                
            if user_id in room.members:
                room.members.remove(user_id)
                
            # Remove from admins if applicable
            if user_id in room.admins:
                room.admins.remove(user_id)
                
            room.last_activity = datetime.now()
            
            logger.info(f"User {user_id} left trading room {room_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error leaving trading room: {e}")
            return False
            
    def get_trader_profile(self, trader_id: str) -> Optional[TraderProfile]:
        """Get trader profile"""
        return self.trader_profiles.get(trader_id)
        
    def get_leaderboard(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trading leaderboard"""
        return list(self.leaderboard_data)[:limit]
        
    def get_trade_signals(self, trader_id: Optional[str] = None,
                         since: Optional[datetime] = None) -> List[TradeSignal]:
        """Get trade signals"""
        signals = list(self.trade_signals.values())
        
        if trader_id:
            signals = [s for s in signals if s.trader_id == trader_id]
            
        if since:
            signals = [s for s in signals if s.created_at >= since]
            
        return sorted(signals, key=lambda x: x.created_at, reverse=True)
        
    def get_trading_rooms(self, user_id: Optional[str] = None,
                        is_public: Optional[bool] = None) -> List[TradingRoom]:
        """Get trading rooms"""
        rooms = list(self.trading_rooms.values())
        
        if user_id:
            rooms = [r for r in rooms if user_id in r.members]
            
        if is_public is not None:
            rooms = [r for r in rooms if r.is_public == is_public]
            
        return sorted(rooms, key=lambda x: x.last_activity, reverse=True)
        
    def get_following_list(self, user_id: str) -> List[TraderProfile]:
        """Get list of traders followed by user"""
        following_ids = self.following_relationships.get(user_id, set())
        return [self.trader_profiles[tid] for tid in following_ids if tid in self.trader_profiles]
        
    def get_followers_list(self, trader_id: str) -> List[str]:
        """Get list of users following trader"""
        followers = []
        for user_id, following_set in self.following_relationships.items():
            if trader_id in following_set:
                followers.append(user_id)
        return followers


# Global social trading manager instance
_social_trading_manager = None

def get_social_trading_manager() -> SocialTradingManager:
    """Get the global social trading manager instance"""
    global _social_trading_manager
    if _social_trading_manager is None:
        _social_trading_manager = SocialTradingManager()
    return _social_trading_manager
