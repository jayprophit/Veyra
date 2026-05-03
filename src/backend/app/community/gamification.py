"""
Gamification Engine
Points, badges, ranks, and achievements
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import uuid

class BadgeType(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

@dataclass
class Badge:
    id: str
    name: str
    description: str
    type: BadgeType
    icon: str
    requirement: str
    points_value: int

@dataclass
class UserAchievement:
    badge_id: str
    earned_at: datetime
    progress: float  # 0-1 for multi-step achievements

class GamificationEngine:
    """
    Points, badges, and achievement system
    """
    
    def __init__(self):
        self.badges: Dict[str, Badge] = {}
        self.user_achievements: Dict[str, List[UserAchievement]] = {}
        self.user_points: Dict[str, int] = {}
        self.user_ranks: Dict[str, str] = {}
        
        self._initialize_default_badges()
    
    def _initialize_default_badges(self):
        """Create default achievement badges"""
        default_badges = [
            # Trading badges
            Badge("badge_first_trade", "First Trade", "Make your first trade", 
                  BadgeType.BRONZE, "🎯", "Complete 1 trade", 10),
            Badge("badge_10_trades", "Active Trader", "Complete 10 trades",
                  BadgeType.BRONZE, "📈", "Complete 10 trades", 50),
            Badge("badge_100_trades", "Pro Trader", "Complete 100 trades",
                  BadgeType.SILVER, "💹", "Complete 100 trades", 200),
            Badge("badge_profit_100", "Century Club", "Make $100 profit",
                  BadgeType.BRONZE, "💰", "Profit $100", 25),
            Badge("badge_profit_1000", "Thousandaire", "Make $1,000 profit",
                  BadgeType.SILVER, "💵", "Profit $1,000", 100),
            Badge("badge_profit_10000", "Ten Thousand", "Make $10,000 profit",
                  BadgeType.GOLD, "💎", "Profit $10,000", 500),
            
            # Goal badges
            Badge("badge_first_goal", "Goal Setter", "Set your first financial goal",
                  BadgeType.BRONZE, "🎯", "Set 1 goal", 10),
            Badge("badge_goal_reached", "Goal Crusher", "Reach a financial goal",
                  BadgeType.SILVER, "🏆", "Complete 1 goal", 100),
            Badge("badge_5_goals", "Overachiever", "Reach 5 financial goals",
                  BadgeType.GOLD, "🏅", "Complete 5 goals", 300),
            
            # Learning badges
            Badge("badge_first_course", "Student", "Complete your first course",
                  BadgeType.BRONZE, "📚", "Complete 1 course", 20),
            Badge("badge_course_master", "Scholar", "Complete 5 courses",
                  BadgeType.SILVER, "🎓", "Complete 5 courses", 100),
            
            # Social badges
            Badge("badge_social", "Social Butterfly", "Follow 10 users",
                  BadgeType.BRONZE, "🦋", "Follow 10 users", 15),
            Badge("badge_helper", "Helper", "Comment on 10 posts",
                  BadgeType.BRONZE, "🤝", "Comment 10 times", 20),
            
            # Streak badges
            Badge("badge_7_day_streak", "Week Warrior", "7-day login streak",
                  BadgeType.BRONZE, "🔥", "Login 7 days", 30),
            Badge("badge_30_day_streak", "Monthly Master", "30-day login streak",
                  BadgeType.SILVER, "🔥", "Login 30 days", 100),
            Badge("badge_365_day_streak", "Legend", "365-day login streak",
                  BadgeType.PLATINUM, "🔥", "Login 365 days", 1000),
            
            # Special badges
            Badge("badge_early_adopter", "Early Adopter", "Joined in beta",
                  BadgeType.PLATINUM, "🚀", "Beta user", 500),
            Badge("badge_referral", "Ambassador", "Refer 5 friends",
                  BadgeType.GOLD, "👥", "Refer 5 users", 250),
        ]
        
        for badge in default_badges:
            self.badges[badge.id] = badge
    
    def award_badge(self, user_id: str, badge_id: str) -> bool:
        """Award a badge to user"""
        if badge_id not in self.badges:
            return False
        
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = []
        
        # Check if already earned
        if any(a.badge_id == badge_id for a in self.user_achievements[user_id]):
            return False
        
        # Award badge
        achievement = UserAchievement(
            badge_id=badge_id,
            earned_at=datetime.now(),
            progress=1.0
        )
        self.user_achievements[user_id].append(achievement)
        
        # Add points
        badge = self.badges[badge_id]
        self.add_points(user_id, badge.points_value)
        
        return True
    
    def add_points(self, user_id: str, points: int):
        """Add points to user"""
        if user_id not in self.user_points:
            self.user_points[user_id] = 0
        
        self.user_points[user_id] += points
        self._update_rank(user_id)
    
    def _update_rank(self, user_id: str):
        """Update user rank based on points"""
        points = self.user_points.get(user_id, 0)
        
        # Rank thresholds
        if points >= 10000:
            rank = "Legend"
        elif points >= 5000:
            rank = "Diamond"
        elif points >= 2500:
            rank = "Platinum"
        elif points >= 1000:
            rank = "Gold"
        elif points >= 500:
            rank = "Silver"
        elif points >= 100:
            rank = "Bronze"
        else:
            rank = "Novice"
        
        self.user_ranks[user_id] = rank
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user's gamification stats"""
        achievements = self.user_achievements.get(user_id, [])
        badges_earned = [self.badges.get(a.badge_id) for a in achievements if a.badge_id in self.badges]
        
        return {
            'user_id': user_id,
            'total_points': self.user_points.get(user_id, 0),
            'rank': self.user_ranks.get(user_id, 'Novice'),
            'badges_earned': len(achievements),
            'badges': [
                {
                    'id': b.id,
                    'name': b.name,
                    'type': b.type.value,
                    'icon': b.icon,
                    'earned_at': next((a.earned_at for a in achievements if a.badge_id == b.id), None)
                }
                for b in badges_earned if b
            ],
            'next_rank': self._get_next_rank_info(user_id)
        }
    
    def _get_next_rank_info(self, user_id: str) -> Dict:
        """Get info about next rank"""
        points = self.user_points.get(user_id, 0)
        rank = self.user_ranks.get(user_id, 'Novice')
        
        thresholds = {
            'Novice': 100,
            'Bronze': 500,
            'Silver': 1000,
            'Gold': 2500,
            'Platinum': 5000,
            'Diamond': 10000
        }
        
        next_threshold = thresholds.get(rank)
        if next_threshold:
            needed = next_threshold - points
            return {
                'current_rank': rank,
                'points_needed': max(0, needed),
                'progress': points / next_threshold
            }
        
        return {'current_rank': rank, 'max_rank_reached': True}
    
    def check_achievements(self, user_id: str, event_type: str, data: Dict) -> List[Badge]:
        """Check and award achievements based on events"""
        awarded = []
        
        if event_type == 'trade':
            trade_count = data.get('total_trades', 0)
            if trade_count >= 1:
                if self.award_badge(user_id, 'badge_first_trade'):
                    awarded.append(self.badges['badge_first_trade'])
            if trade_count >= 10:
                if self.award_badge(user_id, 'badge_10_trades'):
                    awarded.append(self.badges['badge_10_trades'])
            if trade_count >= 100:
                if self.award_badge(user_id, 'badge_100_trades'):
                    awarded.append(self.badges['badge_100_trades'])
        
        elif event_type == 'profit':
            profit = data.get('total_profit', 0)
            if profit >= 100:
                if self.award_badge(user_id, 'badge_profit_100'):
                    awarded.append(self.badges['badge_profit_100'])
            if profit >= 1000:
                if self.award_badge(user_id, 'badge_profit_1000'):
                    awarded.append(self.badges['badge_profit_1000'])
            if profit >= 10000:
                if self.award_badge(user_id, 'badge_profit_10000'):
                    awarded.append(self.badges['badge_profit_10000'])
        
        elif event_type == 'goal_completed':
            goals_completed = data.get('total_goals', 0)
            if goals_completed >= 1:
                if self.award_badge(user_id, 'badge_goal_reached'):
                    awarded.append(self.badges['badge_goal_reached'])
            if goals_completed >= 5:
                if self.award_badge(user_id, 'badge_5_goals'):
                    awarded.append(self.badges['badge_5_goals'])
        
        elif event_type == 'login_streak':
            streak = data.get('streak_days', 0)
            if streak >= 7:
                if self.award_badge(user_id, 'badge_7_day_streak'):
                    awarded.append(self.badges['badge_7_day_streak'])
            if streak >= 30:
                if self.award_badge(user_id, 'badge_30_day_streak'):
                    awarded.append(self.badges['badge_30_day_streak'])
            if streak >= 365:
                if self.award_badge(user_id, 'badge_365_day_streak'):
                    awarded.append(self.badges['badge_365_day_streak'])
        
        return awarded
    
    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        """Get top users by points"""
        sorted_users = sorted(
            self.user_points.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {
                'user_id': user_id,
                'points': points,
                'rank': self.user_ranks.get(user_id, 'Novice')
            }
            for user_id, points in sorted_users
        ]
