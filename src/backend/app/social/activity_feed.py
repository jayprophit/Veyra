"""
Social Activity Feed System for Veyra

Implements:
- Real-time activity stream
- Trade sharing
- Social interactions (likes, comments)
- Following system
- Notifications
- Leaderboard integration

Inspired by BuddyBoss and social trading platforms like eToro.
"""

import json
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
from collections import deque

logger = logging.getLogger(__name__)


class ActivityCategory(Enum):
    """Categories of activities."""
    TRADE = "trade"
    STRATEGY = "strategy"
    PORTFOLIO = "portfolio"
    ACHIEVEMENT = "achievement"
    SOCIAL = "social"
    MARKET = "market"
    SYSTEM = "system"


class PrivacyLevel(Enum):
    """Privacy settings for activities."""
    PUBLIC = "public"
    FOLLOWERS = "followers"
    PRIVATE = "private"


@dataclass
class Activity:
    """Represents a single activity in the feed."""
    id: str
    user_id: str
    user_name: str
    user_avatar: Optional[str]
    category: ActivityCategory
    action: str
    description: str
    timestamp: datetime
    privacy: PrivacyLevel
    metadata: Dict[str, Any] = field(default_factory=dict)
    likes: List[str] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    shares: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'user_avatar': self.user_avatar,
            'category': self.category.value,
            'action': self.action,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'privacy': self.privacy.value,
            'metadata': self.metadata,
            'engagement': {
                'likes': len(self.likes),
                'comments': len(self.comments),
                'shares': self.shares
            },
            'has_comments': len(self.comments) > 0
        }


@dataclass
class UserSocialProfile:
    """User's social profile."""
    user_id: str
    user_name: str
    bio: str = ""
    avatar_url: Optional[str] = None
    followers: Set[str] = field(default_factory=set)
    following: Set[str] = field(default_factory=set)
    blocked_users: Set[str] = field(default_factory=set)
    is_public: bool = True
    allow_copy_trading: bool = True
    show_portfolio: bool = True
    show_trades: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'followers_count': len(self.followers),
            'following_count': len(self.following),
            'is_public': self.is_public,
            'settings': {
                'allow_copy_trading': self.allow_copy_trading,
                'show_portfolio': self.show_portfolio,
                'show_trades': self.show_trades
            }
        }


class ActivityFeed:
    """
    Social activity feed system for Veyra.
    
    Features:
    - Real-time activity streaming
    - Privacy controls
    - Following system
    - Social interactions
    - Notifications
    """
    
    def __init__(self, max_feed_size: int = 10000):
        """
        Initialize the activity feed.
        
        Args:
            max_feed_size: Maximum number of activities to keep in memory
        """
        self.max_feed_size = max_feed_size
        
        # Activity storage (in production, use Redis/database)
        self.global_feed: deque = deque(maxlen=max_feed_size)
        self.user_feeds: Dict[str, deque] = {}
        self.user_profiles: Dict[str, UserSocialProfile] = {}
        
        # Activity callbacks for notifications
        self.activity_callbacks: List[Callable] = []
        
        # Real-time subscribers
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        
        logger.info("ActivityFeed initialized")
    
    def get_or_create_profile(self, user_id: str, user_name: str = "") -> UserSocialProfile:
        """Get or create a user's social profile."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserSocialProfile(
                user_id=user_id,
                user_name=user_name or f"User_{user_id[:8]}"
            )
            logger.info(f"Created social profile for user {user_id}")
        return self.user_profiles[user_id]
    
    async def create_activity(self,
                            user_id: str,
                            category: ActivityCategory,
                            action: str,
                            description: str,
                            metadata: Optional[Dict[str, Any]] = None,
                            privacy: PrivacyLevel = PrivacyLevel.PUBLIC) -> Activity:
        """
        Create a new activity in the feed.
        
        Args:
            user_id: User who performed the action
            category: Activity category
            action: Action type (e.g., 'executed_trade', 'shared_strategy')
            description: Human-readable description
            metadata: Additional data
            privacy: Privacy level
            
        Returns:
            Created Activity
        """
        profile = self.get_or_create_profile(user_id)
        
        # Generate unique ID
        activity_id = f"{user_id}_{datetime.now().timestamp()}"
        
        activity = Activity(
            id=activity_id,
            user_id=user_id,
            user_name=profile.user_name,
            user_avatar=profile.avatar_url,
            category=category,
            action=action,
            description=description,
            timestamp=datetime.now(),
            privacy=privacy,
            metadata=metadata or {}
        )
        
        # Add to global feed
        self.global_feed.appendleft(activity)
        
        # Add to user's personal feed
        if user_id not in self.user_feeds:
            self.user_feeds[user_id] = deque(maxlen=1000)
        self.user_feeds[user_id].appendleft(activity)
        
        # Add to followers' feeds
        for follower_id in profile.followers:
            if follower_id not in self.user_feeds:
                self.user_feeds[follower_id] = deque(maxlen=1000)
            self.user_feeds[follower_id].appendleft(activity)
        
        # Notify real-time subscribers
        await self._notify_subscribers(activity)
        
        # Trigger callbacks
        await self._trigger_callbacks(activity)
        
        logger.info(f"Activity created: {action} by user {user_id}")
        
        return activity
    
    async def get_feed(self,
                     user_id: str,
                     category: Optional[ActivityCategory] = None,
                     limit: int = 50,
                     offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get personalized feed for a user.
        
        Args:
            user_id: User requesting the feed
            category: Filter by category (optional)
            limit: Number of activities to return
            offset: Pagination offset
            
        Returns:
            List of activities
        """
        user_profile = self.get_or_create_profile(user_id)
        
        # Get activities from global feed and user's feed
        activities = []
        seen_ids = set()
        
        # Add from user's personal feed first
        if user_id in self.user_feeds:
            for activity in self.user_feeds[user_id]:
                if activity.id not in seen_ids:
                    if self._can_view_activity(user_id, activity):
                        if category is None or activity.category == category:
                            activities.append(activity)
                            seen_ids.add(activity.id)
        
        # Add from global feed for public activities
        for activity in self.global_feed:
            if len(activities) >= limit + offset:
                break
            
            if activity.id not in seen_ids:
                if self._can_view_activity(user_id, activity):
                    if category is None or activity.category == category:
                        activities.append(activity)
                        seen_ids.add(activity.id)
        
        # Apply pagination
        paginated = activities[offset:offset + limit]
        
        return [a.to_dict() for a in paginated]
    
    def _can_view_activity(self, viewer_id: str, activity: Activity) -> bool:
        """Check if a user can view an activity."""
        # Owner can always view
        if activity.user_id == viewer_id:
            return True
        
        # Check privacy settings
        if activity.privacy == PrivacyLevel.PRIVATE:
            return False
        
        if activity.privacy == PrivacyLevel.FOLLOWERS:
            activity_user_profile = self.user_profiles.get(activity.user_id)
            if activity_user_profile:
                return viewer_id in activity_user_profile.followers
            return False
        
        # Check if viewer is blocked
        activity_user_profile = self.user_profiles.get(activity.user_id)
        if activity_user_profile:
            if viewer_id in activity_user_profile.blocked_users:
                return False
        
        return True
    
    async def follow_user(self, follower_id: str, target_user_id: str) -> bool:
        """Follow a user."""
        if follower_id == target_user_id:
            return False
        
        follower_profile = self.get_or_create_profile(follower_id)
        target_profile = self.get_or_create_profile(target_user_id)
        
        # Add to following
        follower_profile.following.add(target_user_id)
        
        # Add to followers
        target_profile.followers.add(follower_id)
        
        # Create follow activity
        await self.create_activity(
            user_id=follower_id,
            category=ActivityCategory.SOCIAL,
            action='followed_user',
            description=f"started following {target_profile.user_name}",
            metadata={'target_user_id': target_user_id}
        )
        
        logger.info(f"User {follower_id} followed {target_user_id}")
        return True
    
    async def unfollow_user(self, follower_id: str, target_user_id: str) -> bool:
        """Unfollow a user."""
        follower_profile = self.get_or_create_profile(follower_id)
        target_profile = self.get_or_create_profile(target_user_id)
        
        if target_user_id in follower_profile.following:
            follower_profile.following.remove(target_user_id)
            target_profile.followers.discard(follower_id)
            logger.info(f"User {follower_id} unfollowed {target_user_id}")
            return True
        
        return False
    
    async def like_activity(self, user_id: str, activity_id: str) -> bool:
        """Like an activity."""
        activity = self._find_activity(activity_id)
        if not activity:
            return False
        
        if user_id in activity.likes:
            return False  # Already liked
        
        activity.likes.append(user_id)
        
        # Create like notification
        await self._create_notification(
            user_id=activity.user_id,
            type='like',
            message=f"{self.get_or_create_profile(user_id).user_name} liked your activity",
            related_activity_id=activity_id
        )
        
        return True
    
    async def comment_on_activity(self,
                                user_id: str,
                                activity_id: str,
                                comment: str) -> Optional[Dict[str, Any]]:
        """Comment on an activity."""
        activity = self._find_activity(activity_id)
        if not activity:
            return None
        
        user_profile = self.get_or_create_profile(user_id)
        
        comment_data = {
            'id': f"comment_{datetime.now().timestamp()}",
            'user_id': user_id,
            'user_name': user_profile.user_name,
            'user_avatar': user_profile.avatar_url,
            'comment': comment,
            'timestamp': datetime.now().isoformat()
        }
        
        activity.comments.append(comment_data)
        
        # Create comment notification
        await self._create_notification(
            user_id=activity.user_id,
            type='comment',
            message=f"{user_profile.user_name} commented on your activity",
            related_activity_id=activity_id
        )
        
        return comment_data
    
    async def share_activity(self, user_id: str, activity_id: str) -> bool:
        """Share an activity."""
        activity = self._find_activity(activity_id)
        if not activity:
            return False
        
        activity.shares += 1
        
        # Create share activity
        await self.create_activity(
            user_id=user_id,
            category=ActivityCategory.SOCIAL,
            action='shared_activity',
            description=f"shared {activity.user_name}'s activity",
            metadata={'original_activity_id': activity_id}
        )
        
        return True
    
    def _find_activity(self, activity_id: str) -> Optional[Activity]:
        """Find an activity by ID."""
        for activity in self.global_feed:
            if activity.id == activity_id:
                return activity
        
        for feed in self.user_feeds.values():
            for activity in feed:
                if activity.id == activity_id:
                    return activity
        
        return None
    
    async def _create_notification(self,
                                   user_id: str,
                                   type: str,
                                   message: str,
                                   related_activity_id: Optional[str] = None):
        """Create a notification for a user."""
        # In production, this would send push notifications, emails, etc.
        logger.info(f"Notification for {user_id}: {message}")
    
    async def _notify_subscribers(self, activity: Activity):
        """Notify real-time subscribers."""
        # Notify user's subscribers
        if activity.user_id in self.subscribers:
            for queue in self.subscribers[activity.user_id]:
                try:
                    queue.put_nowait(activity.to_dict())
                except asyncio.QueueFull:
                    pass
        
        # Notify global subscribers
        if 'global' in self.subscribers:
            for queue in self.subscribers['global']:
                try:
                    queue.put_nowait(activity.to_dict())
                except asyncio.QueueFull:
                    pass
    
    async def _trigger_callbacks(self, activity: Activity):
        """Trigger registered callbacks."""
        for callback in self.activity_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(activity)
                else:
                    callback(activity)
            except Exception as e:
                logger.error(f"Error in activity callback: {e}")
    
    def register_callback(self, callback: Callable):
        """Register an activity callback."""
        self.activity_callbacks.append(callback)
    
    async def subscribe_to_feed(self, user_id: str) -> asyncio.Queue:
        """Subscribe to real-time feed updates."""
        if user_id not in self.subscribers:
            self.subscribers[user_id] = []
        
        queue = asyncio.Queue(maxsize=100)
        self.subscribers[user_id].append(queue)
        return queue
    
    async def unsubscribe_from_feed(self, user_id: str, queue: asyncio.Queue):
        """Unsubscribe from feed updates."""
        if user_id in self.subscribers:
            if queue in self.subscribers[user_id]:
                self.subscribers[user_id].remove(queue)
    
    def get_trending(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending activities."""
        cutoff = datetime.now() - __import__('datetime').timedelta(hours=hours)
        
        # Score activities by engagement
        scored_activities = []
        for activity in self.global_feed:
            if activity.timestamp > cutoff:
                score = (
                    len(activity.likes) * 2 +
                    len(activity.comments) * 3 +
                    activity.shares * 5
                )
                scored_activities.append((activity, score))
        
        # Sort by score
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        
        return [a.to_dict() for a, _ in scored_activities[:limit]]
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's social statistics."""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return None
        
        # Calculate engagement metrics
        user_activities = self.user_feeds.get(user_id, [])
        total_likes = sum(len(a.likes) for a in user_activities)
        total_comments = sum(len(a.comments) for a in user_activities)
        total_shares = sum(a.shares for a in user_activities)
        
        return {
            'profile': profile.to_dict(),
            'engagement': {
                'total_activities': len(user_activities),
                'total_likes_received': total_likes,
                'total_comments_received': total_comments,
                'total_shares': total_shares
            },
            'is_following_you': False,  # Would need current user context
            'you_are_following': False
        }


# Singleton instance
activity_feed = ActivityFeed()


# Convenience functions
async def share_trade(user_id: str,
                     symbol: str,
                     side: str,
                     quantity: float,
                     price: float,
                     pnl: Optional[float] = None):
    """Share a trade to the activity feed."""
    description = f"executed a {side} trade: {quantity} {symbol} @ ${price:.2f}"
    if pnl is not None:
        description += f" (P&L: ${pnl:+.2f})"
    
    return await activity_feed.create_activity(
        user_id=user_id,
        category=ActivityCategory.TRADE,
        action='executed_trade',
        description=description,
        metadata={
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'pnl': pnl
        }
    )


async def share_strategy(user_id: str, strategy_name: str, strategy_id: str):
    """Share a strategy to the activity feed."""
    return await activity_feed.create_activity(
        user_id=user_id,
        category=ActivityCategory.STRATEGY,
        action='shared_strategy',
        description=f"shared strategy: {strategy_name}",
        metadata={'strategy_id': strategy_id, 'strategy_name': strategy_name}
    )


async def share_achievement(user_id: str, achievement_name: str, tier: str):
    """Share an achievement to the activity feed."""
    return await activity_feed.create_activity(
        user_id=user_id,
        category=ActivityCategory.ACHIEVEMENT,
        action='unlocked_achievement',
        description=f"unlocked {tier} achievement: {achievement_name}",
        metadata={'achievement_name': achievement_name, 'tier': tier}
    )
