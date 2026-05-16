"""
Social Trading Platform - Community Features
============================================
TradingView-style social network for traders

Inspired by: Instagram (visual), Reddit (community), Twitter (real-time)
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class IdeaType(Enum):
    CHART_ANALYSIS = "chart_analysis"
    TRADE_SETUP = "trade_setup"
    MARKET_OUTLOOK = "market_outlook"
    EDUCATIONAL = "educational"
    QUESTION = "question"


@dataclass
class TradingIdea:
    """A trading idea shared by user"""
    id: str
    author_id: str
    author_name: str
    author_avatar: str
    symbol: str
    idea_type: IdeaType
    title: str
    description: str
    chart_image: Optional[str] = None
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    direction: str = "LONG"  # LONG, SHORT, NEUTRAL
    created_at: datetime = field(default_factory=datetime.now)
    likes: int = 0
    comments: List[Dict] = field(default_factory=list)
    views: int = 0
    is_featured: bool = False
    tags: List[str] = field(default_factory=list)
    status: str = "ACTIVE"  # ACTIVE, CLOSED, TARGET_HIT, STOP_HIT
    actual_result: Optional[float] = None  # Actual return %


@dataclass
class UserProfile:
    """Trader profile with stats"""
    user_id: str
    username: str
    avatar: str
    bio: str
    followers: int = 0
    following: int = 0
    total_ideas: int = 0
    winning_ideas: int = 0
    win_rate: float = 0.0
    avg_return: float = 0.0
    reputation_score: float = 0.0
    badges: List[str] = field(default_factory=list)
    top_tags: List[str] = field(default_factory=list)
    rank: str = "BEGINNER"  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT, LEGEND


class SocialTradingPlatform:
    """
    Social trading features inspired by TradingView + Instagram
    
    Features:
    - Share trading ideas with charts
    - Follow top traders
    - Copy trading (auto-replicate)
    - Live streams
    - Leaderboards
    - Reputation system
    """
    
    def __init__(self):
        self.ideas: Dict[str, TradingIdea] = {}
        self.users: Dict[str, UserProfile] = {}
        self.followers: Dict[str, List[str]] = {}  # user_id -> list of follower ids
        self.leaderboard: List[UserProfile] = []
        self.trending_tags: List[str] = []
        self.live_streams: Dict[str, Any] = {}
        
    async def post_idea(self, user_id: str, idea_data: Dict) -> TradingIdea:
        """Post a new trading idea to the community"""
        idea_id = f"idea_{datetime.now().timestamp()}"
        
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        idea = TradingIdea(
            id=idea_id,
            author_id=user_id,
            author_name=user.username,
            author_avatar=user.avatar,
            symbol=idea_data['symbol'],
            idea_type=IdeaType(idea_data['type']),
            title=idea_data['title'],
            description=idea_data['description'],
            chart_image=idea_data.get('chart_image'),
            entry_price=idea_data.get('entry_price'),
            target_price=idea_data.get('target_price'),
            stop_loss=idea_data.get('stop_loss'),
            direction=idea_data.get('direction', 'LONG'),
            tags=idea_data.get('tags', [])
        )
        
        self.ideas[idea_id] = idea
        
        # Update user stats
        user.total_ideas += 1
        
        # Notify followers
        await self._notify_followers(user_id, idea)
        
        logger.info(f"New idea posted: {idea.title} by {user.username}")
        return idea
    
    async def like_idea(self, idea_id: str, user_id: str):
        """Like a trading idea"""
        idea = self.ideas.get(idea_id)
        if idea:
            idea.likes += 1
            # Update author's reputation
            await self._update_reputation(idea.author_id, 'like_received')
    
    async def add_comment(self, idea_id: str, user_id: str, comment: str):
        """Comment on a trading idea"""
        idea = self.ideas.get(idea_id)
        if idea:
            idea.comments.append({
                "user_id": user_id,
                "username": self.users.get(user_id, {}).username if user_id in self.users else "Unknown",
                "comment": comment,
                "timestamp": datetime.now()
            })
    
    async def follow_trader(self, follower_id: str, trader_id: str):
        """Follow a successful trader"""
        if trader_id not in self.followers:
            self.followers[trader_id] = []
        
        if follower_id not in self.followers[trader_id]:
            self.followers[trader_id].append(follower_id)
            
            # Update stats
            trader = self.users.get(trader_id)
            if trader:
                trader.followers += 1
            
            follower = self.users.get(follower_id)
            if follower:
                follower.following += 1
            
            logger.info(f"{follower_id} started following {trader_id}")
    
    async def enable_copy_trading(self, follower_id: str, trader_id: str, 
                                   allocation_percent: float = 10.0):
        """
        Auto-copy a trader's moves with percentage allocation
        
        Example: Allocate 10% of portfolio to copy this trader
        """
        # Store copy trading relationship
        copy_settings = {
            "follower_id": follower_id,
            "trader_id": trader_id,
            "allocation_percent": allocation_percent,
            "max_position_size": 1000,  # Max £ per trade
            "enabled": True
        }
        
        logger.info(f"Copy trading enabled: {follower_id} copying {trader_id} at {allocation_percent}%")
        return copy_settings
    
    async def execute_copy_trade(self, trader_id: str, trade: Dict):
        """
        When a copied trader makes a trade, replicate for followers
        """
        followers = self.followers.get(trader_id, [])
        
        for follower_id in followers:
            # Check if copy trading enabled
            # Calculate position size based on allocation
            # Execute trade for follower
            logger.info(f"Copy trade executed for {follower_id}: {trade['symbol']}")
    
    def get_leaderboard(self, timeframe: str = "monthly") -> List[UserProfile]:
        """
        Get top traders ranked by performance
        
        Timeframes: daily, weekly, monthly, yearly, all_time
        """
        # Sort by reputation score and win rate
        ranked = sorted(
            self.users.values(),
            key=lambda u: (u.reputation_score * 0.6 + u.win_rate * 0.4),
            reverse=True
        )
        return ranked[:100]  # Top 100
    
    def get_trending_ideas(self) -> List[TradingIdea]:
        """Get trending trading ideas"""
        # Sort by engagement (likes + comments + views)
        trending = sorted(
            self.ideas.values(),
            key=lambda i: (i.likes * 2 + len(i.comments) * 3 + i.views * 0.5),
            reverse=True
        )
        return trending[:20]
    
    def get_feed(self, user_id: str) -> List[TradingIdea]:
        """Personalized feed for user"""
        # Get ideas from followed traders + trending + recommended
        user = self.users.get(user_id)
        if not user:
            return self.get_trending_ideas()
        
        followed_ids = self._get_followed_ids(user_id)
        
        feed_ideas = []
        for idea in self.ideas.values():
            if idea.author_id in followed_ids:
                feed_ideas.append((idea, 10))  # High priority
            elif any(tag in user.top_tags for tag in idea.tags):
                feed_ideas.append((idea, 5))  # Medium priority
            else:
                feed_ideas.append((idea, 1))  # Low priority
        
        # Sort by priority and recency
        feed_ideas.sort(key=lambda x: (x[1], x[0].created_at), reverse=True)
        return [idea for idea, _ in feed_ideas[:50]]
    
    async def start_live_stream(self, user_id: str, title: str):
        """Start live trading stream (like Twitch for trading)"""
        stream_id = f"stream_{datetime.now().timestamp()}"
        
        self.live_streams[stream_id] = {
            "streamer_id": user_id,
            "title": title,
            "started_at": datetime.now(),
            "viewers": [],
            "chat_messages": [],
            "is_live": True
        }
        
        logger.info(f"Live stream started: {title} by {user_id}")
        return stream_id
    
    async def join_live_stream(self, stream_id: str, user_id: str):
        """Join a live trading stream"""
        stream = self.live_streams.get(stream_id)
        if stream and stream['is_live']:
            stream['viewers'].append(user_id)
            logger.info(f"User {user_id} joined stream {stream_id}")
    
    def search_traders(self, query: str) -> List[UserProfile]:
        """Search for traders by username or specialty"""
        results = []
        query_lower = query.lower()
        
        for user in self.users.values():
            if (query_lower in user.username.lower() or 
                any(query_lower in tag.lower() for tag in user.top_tags)):
                results.append(user)
        
        return sorted(results, key=lambda u: u.reputation_score, reverse=True)
    
    async def update_idea_result(self, idea_id: str, actual_return: float):
        """
        Update idea with actual performance after trade closes
        Used for tracking win rate and reputation
        """
        idea = self.ideas.get(idea_id)
        if idea:
            idea.status = "CLOSED"
            idea.actual_result = actual_return
            
            # Update author stats
            author = self.users.get(idea.author_id)
            if author:
                if actual_return > 0:
                    author.winning_ideas += 1
                
                # Recalculate win rate
                if author.total_ideas > 0:
                    author.win_rate = author.winning_ideas / author.total_ideas
                
                # Update avg return
                author.avg_return = ((author.avg_return * (author.total_ideas - 1)) + actual_return) / author.total_ideas
                
                # Update reputation
                await self._update_reputation(idea.author_id, 'idea_result', actual_return)
    
    async def _notify_followers(self, user_id: str, idea: TradingIdea):
        """Notify followers of new idea"""
        followers = self.followers.get(user_id, [])
        for follower_id in followers:
            logger.info(f"Notifying {follower_id}: New idea from {idea.author_name}")
            # Push notification logic here
    
    async def _update_reputation(self, user_id: str, action: str, value: float = 0):
        """Update user reputation score"""
        user = self.users.get(user_id)
        if not user:
            return
        
        if action == 'like_received':
            user.reputation_score += 1
        elif action == 'idea_result':
            if value > 0:
                user.reputation_score += value * 2  # Win bonus
            else:
                user.reputation_score -= abs(value)  # Loss penalty
        
        # Update rank
        user.rank = self._calculate_rank(user)
    
    def _calculate_rank(self, user: UserProfile) -> str:
        """Calculate trader rank based on performance"""
        if user.reputation_score > 1000 and user.win_rate > 0.7:
            return "LEGEND"
        elif user.reputation_score > 500 and user.win_rate > 0.6:
            return "EXPERT"
        elif user.reputation_score > 100 and user.win_rate > 0.55:
            return "ADVANCED"
        elif user.reputation_score > 10:
            return "INTERMEDIATE"
        return "BEGINNER"
    
    def _get_followed_ids(self, user_id: str) -> List[str]:
        """Get list of users that user_id is following"""
        followed = []
        for trader_id, followers in self.followers.items():
            if user_id in followers:
                followed.append(trader_id)
        return followed


class CopyTradingEngine:
    """
    Automatically replicate trades from followed traders
    """
    
    def __init__(self, social_platform: SocialTradingPlatform):
        self.social = social_platform
        self.copy_settings: Dict[str, Dict] = {}
    
    async def configure_copy_trading(self, user_id: str, config: Dict):
        """Configure copy trading settings"""
        self.copy_settings[user_id] = {
            "traders_to_copy": config.get('traders', []),
            "allocation_per_trader": config.get('allocation', 10),  # % per trader
            "risk_limits": {
                "max_position_size": config.get('max_position', 1000),
                "max_daily_loss": config.get('max_daily_loss', 100),
                "stop_copy_if_drawdown": config.get('drawdown_limit', 20)
            },
            "filters": {
                "min_trader_win_rate": config.get('min_win_rate', 0.55),
                "min_trader_reputation": config.get('min_reputation', 100),
                "symbols_to_exclude": config.get('excluded_symbols', [])
            }
        }
    
    async def on_trader_action(self, trader_id: str, action: Dict):
        """Process action from copied trader"""
        # Find all users copying this trader
        for user_id, settings in self.copy_settings.items():
            if trader_id in settings['traders_to_copy']:
                await self._replicate_action(user_id, trader_id, action)
    
    async def _replicate_action(self, follower_id: str, trader_id: str, action: Dict):
        """Replicate trade for follower with proper sizing"""
        settings = self.copy_settings[follower_id]
        
        # Check filters
        trader = self.social.users.get(trader_id)
        if not trader:
            return
        
        if trader.win_rate < settings['filters']['min_trader_win_rate']:
            return
        
        # Calculate position size
        allocation = settings['allocation_per_trader'] / 100
        position_size = min(
            action['value'] * allocation,
            settings['risk_limits']['max_position_size']
        )
        
        # Execute copy trade
        logger.info(f"Copy trade: {follower_id} copying {action['symbol']} from {trader_id}")
        
        # Here would integrate with broker API
        return {
            "follower_id": follower_id,
            "trader_id": trader_id,
            "symbol": action['symbol'],
            "copied_size": position_size,
            "original_size": action['value']
        }
