"""
Gamification and Rewards System for Financial Master

Implements:
- Points system for trading activities
- Achievement badges
- Leaderboards
- Streak tracking
- Level progression
- Reward redemption

Inspired by GamiPress and gaming reward mechanics.
"""

import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class AchievementTier(Enum):
    """Achievement difficulty tiers."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class ActivityType(Enum):
    """Types of activities that earn points."""
    TRADE_EXECUTED = "trade_executed"
    TRADE_PROFIT = "trade_profit"
    TRADE_STOPLOSS = "trade_stoploss"
    STRATEGY_CREATED = "strategy_created"
    STRATEGY_SHARED = "strategy_shared"
    STRATEGY_COPIED = "strategy_copied"
    LEARNING_COMPLETED = "learning_completed"
    DAILY_LOGIN = "daily_login"
    REFERRAL = "referral"
    COMMUNITY_POST = "community_post"
    COPY_TRADE_FOLLOWER = "copy_trade_follower"
    PORTFOLIO_MILESTONE = "portfolio_milestone"
    RISK_MANAGEMENT = "risk_management"
    STREAK_MAINTAINED = "streak_maintained"


@dataclass
class Achievement:
    """Represents an unlockable achievement."""
    id: str
    name: str
    description: str
    icon: str
    tier: AchievementTier
    points_reward: int
    requirements: Dict[str, Any]
    unlocked_at: Optional[datetime] = None
    progress: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'tier': self.tier.value,
            'points_reward': self.points_reward,
            'requirements': self.requirements,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress': self.progress
        }


@dataclass
class UserGamificationProfile:
    """User's gamification profile and progress."""
    user_id: str
    total_points: int = 0
    level: int = 1
    experience: int = 0
    streak_days: int = 0
    last_activity_date: Optional[datetime] = None
    achievements: List[Achievement] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    unlocked_features: List[str] = field(default_factory=list)
    trade_count: int = 0
    profitable_trades: int = 0
    strategies_created: int = 0
    strategies_shared: int = 0
    copy_traders_following: int = 0
    referrals_made: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'total_points': self.total_points,
            'level': self.level,
            'experience': self.experience,
            'streak_days': self.streak_days,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'achievements': [a.to_dict() for a in self.achievements],
            'badges': self.badges,
            'unlocked_features': self.unlocked_features,
            'stats': {
                'trade_count': self.trade_count,
                'profitable_trades': self.profitable_trades,
                'strategies_created': self.strategies_created,
                'strategies_shared': self.strategies_shared,
                'copy_traders_following': self.copy_traders_following,
                'referrals_made': self.referrals_made
            }
        }


class RewardsSystem:
    """
    Comprehensive gamification and rewards system.
    
    Features:
    - Points for trading activities
    - Achievement badges with tiers
    - Level progression system
    - Daily streaks
    - Feature unlocking
    - Leaderboards
    """
    
    # Point values for different activities
    ACTIVITY_POINTS = {
        ActivityType.TRADE_EXECUTED: 10,
        ActivityType.TRADE_PROFIT: 50,
        ActivityType.TRADE_STOPLOSS: 25,  # Reward for risk management
        ActivityType.STRATEGY_CREATED: 100,
        ActivityType.STRATEGY_SHARED: 150,
        ActivityType.STRATEGY_COPIED: 75,
        ActivityType.LEARNING_COMPLETED: 200,
        ActivityType.DAILY_LOGIN: 25,
        ActivityType.REFERRAL: 500,
        ActivityType.COMMUNITY_POST: 30,
        ActivityType.COPY_TRADE_FOLLOWER: 100,
        ActivityType.PORTFOLIO_MILESTONE: 250,
        ActivityType.RISK_MANAGEMENT: 40,
        ActivityType.STREAK_MAINTAINED: 50
    }
    
    # Level thresholds (experience points)
    LEVEL_THRESHOLDS = [
        0,          # Level 1
        500,        # Level 2
        1500,       # Level 3
        3000,       # Level 4
        5000,       # Level 5
        8000,       # Level 6
        12000,      # Level 7
        17000,      # Level 8
        23000,      # Level 9
        30000,      # Level 10
        40000,      # Level 11
        55000,      # Level 12
        75000,      # Level 13
        100000,     # Level 14
        130000,     # Level 15
        170000,     # Level 16
        220000,     # Level 17
        280000,     # Level 18
        350000,     # Level 19
        450000      # Level 20+
    ]
    
    # Features unlocked at different levels
    LEVEL_UNLOCKS = {
        2: ['advanced_charts', 'custom_indicators'],
        3: ['paper_trading', 'strategy_backtesting'],
        5: ['automated_trading', 'webhooks'],
        7: ['api_access', 'advanced_analytics'],
        10: ['premium_strategies', 'priority_support'],
        15: ['early_access', 'beta_features'],
        20: ['vip_status', 'exclusive_perks']
    }
    
    def __init__(self):
        self.user_profiles: Dict[str, UserGamificationProfile] = {}
        self.achievements_catalog = self._initialize_achievements()
        self.leaderboard: List[tuple] = []  # (user_id, total_points)
        self.activity_callbacks: Dict[ActivityType, List[Callable]] = defaultdict(list)
        
        logger.info("RewardsSystem initialized")
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize the achievement catalog."""
        return {
            # Trading Achievements
            'first_trade': Achievement(
                id='first_trade',
                name='First Steps',
                description='Execute your first trade',
                icon='🎯',
                tier=AchievementTier.BRONZE,
                points_reward=50,
                requirements={'trade_count': 1}
            ),
            'profitable_trader': Achievement(
                id='profitable_trader',
                name='Profitable Trader',
                description='Make 10 profitable trades',
                icon='💰',
                tier=AchievementTier.BRONZE,
                points_reward=100,
                requirements={'profitable_trades': 10}
            ),
            'trading_veteran': Achievement(
                id='trading_veteran',
                name='Trading Veteran',
                description='Execute 100 trades',
                icon='⚔️',
                tier=AchievementTier.SILVER,
                points_reward=250,
                requirements={'trade_count': 100}
            ),
            'master_trader': Achievement(
                id='master_trader',
                name='Master Trader',
                description='Execute 1000 trades with 60%+ win rate',
                icon='👑',
                tier=AchievementTier.GOLD,
                points_reward=1000,
                requirements={'trade_count': 1000, 'win_rate': 0.60}
            ),
            
            # Strategy Achievements
            'strategy_creator': Achievement(
                id='strategy_creator',
                name='Strategy Creator',
                description='Create your first strategy',
                icon='🧠',
                tier=AchievementTier.BRONZE,
                points_reward=100,
                requirements={'strategies_created': 1}
            ),
            'strategy_sharer': Achievement(
                id='strategy_sharer',
                name='Strategy Sharer',
                description='Share a strategy with the community',
                icon='📢',
                tier=AchievementTier.SILVER,
                points_reward=200,
                requirements={'strategies_shared': 1}
            ),
            'strategy_guru': Achievement(
                id='strategy_guru',
                name='Strategy Guru',
                description='Create 10 strategies with 100+ total copies',
                icon='🏆',
                tier=AchievementTier.GOLD,
                points_reward=500,
                requirements={'strategies_created': 10, 'total_copies': 100}
            ),
            
            # Risk Management Achievements
            'risk_manager': Achievement(
                id='risk_manager',
                name='Risk Manager',
                description='Use stop-loss on 20 trades',
                icon='🛡️',
                tier=AchievementTier.SILVER,
                points_reward=150,
                requirements={'stoploss_count': 20}
            ),
            'portfolio_protector': Achievement(
                id='portfolio_protector',
                name='Portfolio Protector',
                description='Maintain positive risk-adjusted returns for 30 days',
                icon='🛡️',
                tier=AchievementTier.GOLD,
                points_reward=400,
                requirements={'positive_sharpe_days': 30}
            ),
            
            # Community Achievements
            'influencer': Achievement(
                id='influencer',
                name='Trading Influencer',
                description='Get 50 followers on copy trading',
                icon='🌟',
                tier=AchievementTier.GOLD,
                points_reward=500,
                requirements={'followers': 50}
            ),
            'community_helper': Achievement(
                id='community_helper',
                name='Community Helper',
                description='Make 20 helpful community posts',
                icon='🤝',
                tier=AchievementTier.SILVER,
                points_reward=300,
                requirements={'helpful_posts': 20}
            ),
            
            # Streak Achievements
            'consistent_trader': Achievement(
                id='consistent_trader',
                name='Consistent Trader',
                description='Maintain a 7-day trading streak',
                icon='🔥',
                tier=AchievementTier.BRONZE,
                points_reward=100,
                requirements={'streak_days': 7}
            ),
            'dedicated_trader': Achievement(
                id='dedicated_trader',
                name='Dedicated Trader',
                description='Maintain a 30-day trading streak',
                icon='🔥🔥',
                tier=AchievementTier.SILVER,
                points_reward=300,
                requirements={'streak_days': 30}
            ),
            'legendary_trader': Achievement(
                id='legendary_trader',
                name='Legendary Trader',
                description='Maintain a 100-day trading streak',
                icon='🔥🔥🔥',
                tier=AchievementTier.GOLD,
                points_reward=1000,
                requirements={'streak_days': 100}
            ),
            
            # Learning Achievements
            'eager_learner': Achievement(
                id='eager_learner',
                name='Eager Learner',
                description='Complete 5 learning modules',
                icon='📚',
                tier=AchievementTier.BRONZE,
                points_reward=200,
                requirements={'modules_completed': 5}
            ),
            'trading_scholar': Achievement(
                id='trading_scholar',
                name='Trading Scholar',
                description='Complete all beginner courses',
                icon='🎓',
                tier=AchievementTier.SILVER,
                points_reward=500,
                requirements={'beginner_courses': 'all'}
            ),
            
            # Special Achievements
            'early_adopter': Achievement(
                id='early_adopter',
                name='Early Adopter',
                description='Join during beta phase',
                icon='🚀',
                tier=AchievementTier.PLATINUM,
                points_reward=2000,
                requirements={'beta_user': True}
            ),
            'top_referrer': Achievement(
                id='top_referrer',
                name='Top Referrer',
                description='Refer 10 active users',
                icon='🎁',
                tier=AchievementTier.GOLD,
                points_reward=1000,
                requirements={'referrals': 10}
            ),
        }
    
    def get_or_create_profile(self, user_id: str) -> UserGamificationProfile:
        """Get or create a user's gamification profile."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserGamificationProfile(user_id=user_id)
            logger.info(f"Created gamification profile for user {user_id}")
        return self.user_profiles[user_id]
    
    async def record_activity(self, 
                            user_id: str, 
                            activity_type: ActivityType,
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record a user activity and award points.
        
        Returns:
            Dict with points earned, level up info, and unlocked achievements
        """
        profile = self.get_or_create_profile(user_id)
        
        # Calculate points
        base_points = self.ACTIVITY_POINTS.get(activity_type, 10)
        
        # Streak bonus
        streak_bonus = self._calculate_streak_bonus(profile.streak_days)
        
        # Level bonus (higher level = more points)
        level_bonus = int(base_points * (profile.level * 0.05))
        
        total_points = base_points + streak_bonus + level_bonus
        
        # Award points
        profile.total_points += total_points
        profile.experience += total_points
        
        # Update stats
        await self._update_stats(profile, activity_type, metadata)
        
        # Check for level up
        level_up_info = await self._check_level_up(profile)
        
        # Check for achievements
        new_achievements = await self._check_achievements(profile)
        
        # Update streak
        await self._update_streak(profile)
        
        # Update leaderboard
        self._update_leaderboard(user_id, profile.total_points)
        
        # Trigger callbacks
        await self._trigger_callbacks(activity_type, user_id, total_points)
        
        logger.info(f"Activity recorded for user {user_id}: {activity_type.value} (+{total_points} points)")
        
        return {
            'points_earned': total_points,
            'total_points': profile.total_points,
            'experience': profile.experience,
            'level': profile.level,
            'level_up': level_up_info,
            'new_achievements': [a.to_dict() for a in new_achievements],
            'streak_days': profile.streak_days,
            'unlocked_features': profile.unlocked_features
        }
    
    def _calculate_streak_bonus(self, streak_days: int) -> int:
        """Calculate bonus points for streak."""
        if streak_days >= 100:
            return 100
        elif streak_days >= 30:
            return 50
        elif streak_days >= 7:
            return 25
        elif streak_days >= 3:
            return 10
        return 0
    
    async def _update_stats(self, 
                          profile: UserGamificationProfile, 
                          activity_type: ActivityType,
                          metadata: Optional[Dict[str, Any]]):
        """Update user statistics based on activity."""
        if activity_type == ActivityType.TRADE_EXECUTED:
            profile.trade_count += 1
        elif activity_type == ActivityType.TRADE_PROFIT:
            profile.profitable_trades += 1
        elif activity_type == ActivityType.STRATEGY_CREATED:
            profile.strategies_created += 1
        elif activity_type == ActivityType.STRATEGY_SHARED:
            profile.strategies_shared += 1
        elif activity_type == ActivityType.REFERRAL:
            profile.referrals_made += 1
        elif activity_type == ActivityType.COPY_TRADE_FOLLOWER:
            profile.copy_traders_following += 1
    
    async def _check_level_up(self, profile: UserGamificationProfile) -> Optional[Dict[str, Any]]:
        """Check if user should level up."""
        current_level = profile.level
        new_level = current_level
        
        # Find new level based on experience
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if profile.experience >= threshold:
                new_level = i + 1
        
        if new_level > current_level:
            profile.level = new_level
            
            # Check for unlocked features
            unlocked = []
            for level, features in self.LEVEL_UNLOCKS.items():
                if current_level < level <= new_level:
                    profile.unlocked_features.extend(features)
                    unlocked.extend(features)
            
            logger.info(f"User {profile.user_id} leveled up to {new_level}!")
            
            return {
                'old_level': current_level,
                'new_level': new_level,
                'unlocked_features': unlocked,
                'bonus_points': new_level * 100  # Level up bonus
            }
        
        return None
    
    async def _check_achievements(self, profile: UserGamificationProfile) -> List[Achievement]:
        """Check for newly unlocked achievements."""
        new_achievements = []
        
        for achievement_id, achievement in self.achievements_catalog.items():
            # Check if already unlocked
            if any(a.id == achievement_id for a in profile.achievements):
                continue
            
            # Check requirements
            if self._check_achievement_requirements(profile, achievement):
                # Unlock achievement
                achievement.unlocked_at = datetime.now()
                achievement.progress = 1.0
                profile.achievements.append(achievement)
                profile.total_points += achievement.points_reward
                profile.badges.append(achievement.icon)
                
                new_achievements.append(achievement)
                logger.info(f"User {profile.user_id} unlocked achievement: {achievement.name}")
        
        return new_achievements
    
    def _check_achievement_requirements(self, 
                                     profile: UserGamificationProfile, 
                                     achievement: Achievement) -> bool:
        """Check if user meets achievement requirements."""
        reqs = achievement.requirements
        
        if 'trade_count' in reqs:
            if profile.trade_count < reqs['trade_count']:
                return False
        
        if 'profitable_trades' in reqs:
            if profile.profitable_trades < reqs['profitable_trades']:
                return False
        
        if 'strategies_created' in reqs:
            if profile.strategies_created < reqs['strategies_created']:
                return False
        
        if 'strategies_shared' in reqs:
            if profile.strategies_shared < reqs['strategies_shared']:
                return False
        
        if 'streak_days' in reqs:
            if profile.streak_days < reqs['streak_days']:
                return False
        
        if 'referrals' in reqs:
            if profile.referrals_made < reqs['referrals']:
                return False
        
        if 'followers' in reqs:
            if profile.copy_traders_following < reqs['followers']:
                return False
        
        return True
    
    async def _update_streak(self, profile: UserGamificationProfile):
        """Update daily streak."""
        today = datetime.now().date()
        
        if profile.last_activity_date:
            last_date = profile.last_activity_date.date()
            
            if today == last_date:
                # Already active today, no streak change
                return
            elif today - last_date == timedelta(days=1):
                # Consecutive day, increment streak
                profile.streak_days += 1
                
                # Award streak bonus
                await self.record_activity(
                    profile.user_id,
                    ActivityType.STREAK_MAINTAINED
                )
            else:
                # Streak broken
                profile.streak_days = 1
        else:
            # First activity
            profile.streak_days = 1
        
        profile.last_activity_date = datetime.now()
    
    def _update_leaderboard(self, user_id: str, points: int):
        """Update the global leaderboard."""
        # Remove old entry if exists
        self.leaderboard = [(uid, pts) for uid, pts in self.leaderboard if uid != user_id]
        
        # Add new entry
        self.leaderboard.append((user_id, points))
        
        # Sort by points (descending)
        self.leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top 100
        self.leaderboard = self.leaderboard[:100]
    
    async def _trigger_callbacks(self, 
                               activity_type: ActivityType, 
                               user_id: str, 
                               points: int):
        """Trigger registered activity callbacks."""
        for callback in self.activity_callbacks.get(activity_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(user_id, points)
                else:
                    callback(user_id, points)
            except Exception as e:
                logger.error(f"Error in activity callback: {e}")
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Get the top users on the leaderboard."""
        result = []
        for rank, (user_id, points) in enumerate(self.leaderboard[:top_n], 1):
            profile = self.user_profiles.get(user_id)
            if profile:
                result.append({
                    'rank': rank,
                    'user_id': user_id,
                    'points': points,
                    'level': profile.level,
                    'badges': profile.badges[:5]  # Top 5 badges
                })
        return result
    
    def get_user_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user statistics."""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return None
        
        # Calculate next level progress
        current_level = profile.level
        next_level_exp = self.LEVEL_THRESHOLDS[current_level] if current_level < len(self.LEVEL_THRESHOLDS) else float('inf')
        current_level_exp = self.LEVEL_THRESHOLDS[current_level - 1]
        
        level_progress = 0.0
        if next_level_exp != float('inf'):
            level_progress = (profile.experience - current_level_exp) / (next_level_exp - current_level_exp)
        
        return {
            'profile': profile.to_dict(),
            'next_level_progress': level_progress,
            'next_level_points_needed': max(0, next_level_exp - profile.experience),
            'rank': self._get_user_rank(user_id),
            'total_achievements': len(profile.achievements),
            'achievements_by_tier': self._count_achievements_by_tier(profile),
            'activity_streak': profile.streak_days,
            'win_rate': profile.profitable_trades / profile.trade_count if profile.trade_count > 0 else 0
        }
    
    def _get_user_rank(self, user_id: str) -> Optional[int]:
        """Get user's rank on the leaderboard."""
        for rank, (uid, _) in enumerate(self.leaderboard, 1):
            if uid == user_id:
                return rank
        return None
    
    def _count_achievements_by_tier(self, profile: UserGamificationProfile) -> Dict[str, int]:
        """Count achievements by tier."""
        counts = defaultdict(int)
        for achievement in profile.achievements:
            counts[achievement.tier.value] += 1
        return dict(counts)
    
    def register_activity_callback(self, 
                                  activity_type: ActivityType, 
                                  callback: Callable):
        """Register a callback for a specific activity type."""
        self.activity_callbacks[activity_type].append(callback)
    
    def redeem_points(self, 
                     user_id: str, 
                     points_cost: int, 
                     reward_type: str) -> bool:
        """Redeem points for rewards."""
        profile = self.get_or_create_profile(user_id)
        
        if profile.total_points < points_cost:
            return False
        
        profile.total_points -= points_cost
        logger.info(f"User {user_id} redeemed {points_cost} points for {reward_type}")
        return True


# Singleton instance
rewards_system = RewardsSystem()


async def award_points(user_id: str, 
                      activity_type: ActivityType,
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to award points."""
    return await rewards_system.record_activity(user_id, activity_type, metadata)
