"""
Activity Feed System
Social feed for user activities, trades, and updates
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

class ActivityType(Enum):
    TRADE = "trade"
    PORTFOLIO_UPDATE = "portfolio_update"
    GOAL_REACHED = "goal_reached"
    COMMENT = "comment"
    LIKE = "like"
    FOLLOW = "follow"
    POST = "post"
    ACHIEVEMENT = "achievement"

@dataclass
class Activity:
    id: str
    actor_id: str
    actor_name: str
    actor_avatar: str
    activity_type: ActivityType
    target_id: Optional[str]
    content: str
    metadata: Dict
    likes: int
    comments: List[Dict]
    created_at: datetime

class ActivityFeed:
    """
    Social activity feed similar to BuddyBoss/Facebook
    """
    
    def __init__(self):
        self.activities: Dict[str, Activity] = {}
        self.user_feeds: Dict[str, List[str]] = {}  # user_id -> activity_ids
        self.following: Dict[str, List[str]] = {}   # user_id -> followed_user_ids
    
    def create_activity(self, 
                       actor_id: str,
                       actor_name: str,
                       actor_avatar: str,
                       activity_type: ActivityType,
                       content: str,
                       target_id: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> Activity:
        """Create a new activity"""
        
        activity = Activity(
            id=str(uuid.uuid4()),
            actor_id=actor_id,
            actor_name=actor_name,
            actor_avatar=actor_avatar,
            activity_type=activity_type,
            target_id=target_id,
            content=content,
            metadata=metadata or {},
            likes=0,
            comments=[],
            created_at=datetime.now()
        )
        
        self.activities[activity.id] = activity
        
        # Add to actor's feed
        if actor_id not in self.user_feeds:
            self.user_feeds[actor_id] = []
        self.user_feeds[actor_id].insert(0, activity.id)
        
        return activity
    
    def get_feed(self, user_id: str, limit: int = 50) -> List[Activity]:
        """Get personalized activity feed"""
        feed_ids = self.user_feeds.get(user_id, [])
        
        # Include activities from followed users
        followed = self.following.get(user_id, [])
        for followed_id in followed:
            feed_ids.extend(self.user_feeds.get(followed_id, []))
        
        # Get unique activities, sorted by date
        activities = [self.activities[aid] for aid in set(feed_ids) if aid in self.activities]
        activities.sort(key=lambda x: x.created_at, reverse=True)
        
        return activities[:limit]
    
    def follow_user(self, user_id: str, target_user_id: str) -> bool:
        """Follow another user"""
        if user_id not in self.following:
            self.following[user_id] = []
        
        if target_user_id not in self.following[user_id]:
            self.following[user_id].append(target_user_id)
            
            # Create follow activity
            self.create_activity(
                actor_id=user_id,
                actor_name="User",  # Would fetch from user profile
                actor_avatar="",
                activity_type=ActivityType.FOLLOW,
                content=f"started following {target_user_id}",
                target_id=target_user_id
            )
            return True
        return False
    
    def like_activity(self, activity_id: str, user_id: str) -> bool:
        """Like an activity"""
        if activity_id in self.activities:
            self.activities[activity_id].likes += 1
            return True
        return False
    
    def add_comment(self, activity_id: str, user_id: str, 
                   user_name: str, comment: str) -> bool:
        """Add comment to activity"""
        if activity_id in self.activities:
            self.activities[activity_id].comments.append({
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'user_name': user_name,
                'content': comment,
                'created_at': datetime.now().isoformat()
            })
            return True
        return False
    
    def get_user_activities(self, user_id: str, limit: int = 50) -> List[Activity]:
        """Get all activities by a specific user"""
        user_activities = [a for a in self.activities.values() if a.actor_id == user_id]
        user_activities.sort(key=lambda x: x.created_at, reverse=True)
        return user_activities[:limit]
    
    # Convenience methods for financial activities
    def log_trade(self, user_id: str, user_name: str, symbol: str, 
                 action: str, quantity: float, price: float):
        """Log a trade to activity feed"""
        return self.create_activity(
            actor_id=user_id,
            actor_name=user_name,
            actor_avatar="",
            activity_type=ActivityType.TRADE,
            content=f"{action} {quantity} shares of {symbol} at ${price}",
            metadata={
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'total_value': quantity * price
            }
        )
    
    def log_goal_reached(self, user_id: str, user_name: str, 
                        goal_title: str, amount: float):
        """Log goal achievement"""
        return self.create_activity(
            actor_id=user_id,
            actor_name=user_name,
            actor_avatar="",
            activity_type=ActivityType.GOAL_REACHED,
            content=f"Reached goal: {goal_title} - ${amount}",
            metadata={'goal_title': goal_title, 'amount': amount}
        )
    
    def log_achievement(self, user_id: str, user_name: str, 
                       achievement_name: str, description: str):
        """Log achievement unlock"""
        return self.create_activity(
            actor_id=user_id,
            actor_name=user_name,
            actor_avatar="",
            activity_type=ActivityType.ACHIEVEMENT,
            content=f"Earned achievement: {achievement_name}",
            metadata={'achievement': achievement_name, 'description': description}
        )
