"""
Gamification - Achievement System
Inspired by Duolingo, Fitbit, Reddit badges
Engages users through rewards and progress tracking
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from decimal import Decimal


class AchievementTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    LEGENDARY = "legendary"


class AchievementCategory(Enum):
    TRADING = "trading"
    INVESTING = "investing"
    SAVING = "saving"
    LEARNING = "learning"
    SOCIAL = "social"
    STREAK = "streak"
    MILESTONE = "milestone"


@dataclass
class Achievement:
    """Achievement definition"""
    id: str
    name: str
    description: str
    category: AchievementCategory
    tier: AchievementTier
    
    # Requirements
    requirement_type: str  # "count", "amount", "streak", "completion"
    requirement_value: Any
    
    # Rewards
    points: int
    badge_icon: str
    reward_cashback_pct: Optional[float] = None  # e.g., 0.5% extra cashback for 30 days
    
    # Metadata
    is_hidden: bool = False  # Secret achievements
    is_repeatable: bool = False
    expires_at: Optional[datetime] = None  # Seasonal achievements


@dataclass
class UserAchievement:
    """User's progress and completion of an achievement"""
    user_id: str
    achievement_id: str
    
    progress: Any  # Current progress toward requirement
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    times_completed: int = 0  # For repeatable achievements
    
    # Rewards claimed
    points_claimed: bool = False
    rewards_claimed: bool = False
    claimed_at: Optional[datetime] = None


class AchievementManager:
    """
    Manages achievements, progress tracking, and rewards
    """
    
    def __init__(self):
        self.achievements: Dict[str, Achievement] = {}
        self.user_achievements: Dict[str, List[UserAchievement]] = {}
        self._initialize_achievements()
    
    def _initialize_achievements(self):
        """Create default achievement catalog"""
        
        default_achievements = [
            # Trading Achievements
            Achievement(
                id="first_trade",
                name="First Steps",
                description="Complete your first trade",
                category=AchievementCategory.TRADING,
                tier=AchievementTier.BRONZE,
                requirement_type="count",
                requirement_value=1,
                points=100,
                badge_icon="🎯"
            ),
            Achievement(
                id="day_trader",
                name="Day Trader",
                description="Complete 50 trades in a single day",
                category=AchievementCategory.TRADING,
                tier=AchievementTier.SILVER,
                requirement_type="count",
                requirement_value=50,
                points=500,
                badge_icon="⚡"
            ),
            Achievement(
                id="perfect_timing",
                name="Perfect Timing",
                description="Buy at the day's low and sell at the day's high",
                category=AchievementCategory.TRADING,
                tier=AchievementTier.GOLD,
                requirement_type="completion",
                requirement_value=True,
                points=1000,
                badge_icon="⏰"
            ),
            Achievement(
                id="high_roller",
                name="High Roller",
                description="Execute a single trade over $100,000",
                category=AchievementCategory.TRADING,
                tier=AchievementTier.PLATINUM,
                requirement_type="amount",
                requirement_value=100000,
                points=2500,
                badge_icon="💎"
            ),
            
            # Investing Achievements
            Achievement(
                id="diversified",
                name="Diversified Portfolio",
                description="Hold 10 different assets simultaneously",
                category=AchievementCategory.INVESTING,
                tier=AchievementTier.BRONZE,
                requirement_type="count",
                requirement_value=10,
                points=200,
                badge_icon="🌈"
            ),
            Achievement(
                id="dividend_king",
                name="Dividend King",
                description="Receive dividends from 5 different companies in one month",
                category=AchievementCategory.INVESTING,
                tier=AchievementTier.SILVER,
                requirement_type="count",
                requirement_value=5,
                points=500,
                badge_icon="👑"
            ),
            Achievement(
                id="millionaire",
                name="Millionaire",
                description="Reach $1,000,000 portfolio value",
                category=AchievementCategory.INVESTING,
                tier=AchievementTier.PLATINUM,
                requirement_type="amount",
                requirement_value=1000000,
                points=5000,
                badge_icon="💰"
            ),
            Achievement(
                id="ten_bagger",
                name="Ten Bagger",
                description="Have a stock increase 10x from your purchase price",
                category=AchievementCategory.INVESTING,
                tier=AchievementTier.DIAMOND,
                requirement_type="completion",
                requirement_value=True,
                points=10000,
                badge_icon="🚀"
            ),
            
            # Saving Achievements
            Achievement(
                id="saving_starter",
                name="Saving Starter",
                description="Save $1,000 through automated rules",
                category=AchievementCategory.SAVING,
                tier=AchievementTier.BRONZE,
                requirement_type="amount",
                requirement_value=1000,
                points=150,
                badge_icon="🐷"
            ),
            Achievement(
                id="roundup_master",
                name="Round-Up Master",
                description="Save $500 through round-ups alone",
                category=AchievementCategory.SAVING,
                tier=AchievementTier.SILVER,
                requirement_type="amount",
                requirement_value=500,
                points=400,
                badge_icon="🔄"
            ),
            Achievement(
                id="financial_freedom",
                name="Financial Freedom",
                description="Save 6 months of expenses in emergency fund",
                category=AchievementCategory.SAVING,
                tier=AchievementTier.GOLD,
                requirement_type="completion",
                requirement_value=True,
                points=1500,
                badge_icon="🗝️"
            ),
            
            # Learning Achievements
            Achievement(
                id="student",
                name="Student Investor",
                description="Complete 5 educational modules",
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.BRONZE,
                requirement_type="count",
                requirement_value=5,
                points=200,
                badge_icon="📚"
            ),
            Achievement(
                id="analyst",
                name="Stock Analyst",
                description="Read 50 earnings reports",
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.SILVER,
                requirement_type="count",
                requirement_value=50,
                points=600,
                badge_icon="📊"
            ),
            Achievement(
                id="oracle",
                name="The Oracle",
                description="Make 10 accurate predictions using AI tools",
                category=AchievementCategory.LEARNING,
                tier=AchievementTier.GOLD,
                requirement_type="count",
                requirement_value=10,
                points=1200,
                badge_icon="🔮"
            ),
            
            # Social Achievements
            Achievement(
                id="influencer",
                name="Influencer",
                description="Get 100 followers as a Popular Investor",
                category=AchievementCategory.SOCIAL,
                tier=AchievementTier.SILVER,
                requirement_type="count",
                requirement_value=100,
                points=800,
                badge_icon="⭐"
            ),
            Achievement(
                id="copycat_king",
                name="Copycat King",
                description="Have 500 people copy your trades",
                category=AchievementCategory.SOCIAL,
                tier=AchievementTier.GOLD,
                requirement_type="count",
                requirement_value=500,
                points=2000,
                badge_icon="👥"
            ),
            
            # Streak Achievements
            Achievement(
                id="week_warrior",
                name="Week Warrior",
                description="Check portfolio 7 days in a row",
                category=AchievementCategory.STREAK,
                tier=AchievementTier.BRONZE,
                requirement_type="streak",
                requirement_value=7,
                points=100,
                badge_icon="🔥"
            ),
            Achievement(
                id="month_master",
                name="Month Master",
                description="30 day login streak",
                category=AchievementCategory.STREAK,
                tier=AchievementTier.SILVER,
                requirement_type="streak",
                requirement_value=30,
                points=500,
                badge_icon="🔥🔥"
            ),
            Achievement(
                id="quarterly_champion",
                name="Quarterly Champion",
                description="90 day login streak",
                category=AchievementCategory.STREAK,
                tier=AchievementTier.GOLD,
                requirement_type="streak",
                requirement_value=90,
                points=1500,
                badge_icon="🔥🔥🔥"
            ),
            Achievement(
                id="yearly_legend",
                name="Yearly Legend",
                description="365 day login streak",
                category=AchievementCategory.STREAK,
                tier=AchievementTier.LEGENDARY,
                requirement_type="streak",
                requirement_value=365,
                points=10000,
                badge_icon="🔥🔥🔥🔥"
            ),
            
            # Milestone Achievements
            Achievement(
                id="centurion",
                name="Centurion",
                description="Complete 100 trades",
                category=AchievementCategory.MILESTONE,
                tier=AchievementTier.BRONZE,
                requirement_type="count",
                requirement_value=100,
                points=250,
                badge_icon="⚔️"
            ),
            Achievement(
                id="trading_veteran",
                name="Trading Veteran",
                description="Complete 1,000 trades",
                category=AchievementCategory.MILESTONE,
                tier=AchievementTier.SILVER,
                requirement_type="count",
                requirement_value=1000,
                points=750,
                badge_icon="🎖️"
            ),
            Achievement(
                id="market_master",
                name="Market Master",
                description="Complete 10,000 trades",
                category=AchievementCategory.MILESTONE,
                tier=AchievementTier.GOLD,
                requirement_type="count",
                requirement_value=10000,
                points=2500,
                badge_icon="🏆"
            ),
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement
    
    async def update_progress(
        self,
        user_id: str,
        achievement_id: str,
        progress: Any
    ) -> Optional[UserAchievement]:
        """
        Update user's progress toward an achievement
        
        Returns UserAchievement if newly completed
        """
        if achievement_id not in self.achievements:
            return None
        
        achievement = self.achievements[achievement_id]
        
        # Get or create user achievement
        user_achs = self.user_achievements.get(user_id, [])
        user_ach = next((ua for ua in user_achs if ua.achievement_id == achievement_id), None)
        
        if not user_ach:
            user_ach = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id,
                progress=progress
            )
            user_achs.append(user_ach)
            self.user_achievements[user_id] = user_achs
        
        # Check if completed
        was_completed = user_ach.is_completed
        
        if achievement.requirement_type == "count":
            if progress >= achievement.requirement_value:
                user_ach.is_completed = True
        elif achievement.requirement_type == "amount":
            if Decimal(str(progress)) >= Decimal(str(achievement.requirement_value)):
                user_ach.is_completed = True
        elif achievement.requirement_type == "streak":
            if progress >= achievement.requirement_value:
                user_ach.is_completed = True
        elif achievement.requirement_type == "completion":
            if progress == achievement.requirement_value:
                user_ach.is_completed = True
        
        # Record completion time
        if user_ach.is_completed and not was_completed:
            user_ach.completed_at = datetime.utcnow()
            user_ach.times_completed += 1
            return user_ach  # Return to notify of completion
        
        return None
    
    async def get_user_achievements(
        self,
        user_id: str,
        category: Optional[AchievementCategory] = None,
        completed_only: bool = False
    ) -> Dict[str, Any]:
        """Get all achievements for a user"""
        user_achs = self.user_achievements.get(user_id, [])
        
        # Filter by category if specified
        if category:
            category_ids = [a.id for a in self.achievements.values() if a.category == category]
            user_achs = [ua for ua in user_achs if ua.achievement_id in category_ids]
        
        if completed_only:
            user_achs = [ua for ua in user_achs if ua.is_completed]
        
        # Calculate totals
        total_points = sum(
            self.achievements[ua.achievement_id].points
            for ua in user_achs if ua.is_completed
        )
        
        # Group by category
        by_category = {}
        for ua in user_achs:
            ach = self.achievements[ua.achievement_id]
            cat = ach.category.value
            if cat not in by_category:
                by_category[cat] = {"completed": 0, "total": 0, "points": 0}
            by_category[cat]["total"] += 1
            if ua.is_completed:
                by_category[cat]["completed"] += 1
                by_category[cat]["points"] += ach.points
        
        return {
            "user_id": user_id,
            "total_achievements": len(self.achievements),
            "completed": len([ua for ua in user_achs if ua.is_completed]),
            "in_progress": len([ua for ua in user_achs if not ua.is_completed]),
            "total_points": total_points,
            "by_category": by_category,
            "recent_completions": [
                {
                    "achievement": self.achievements[ua.achievement_id].name,
                    "completed_at": ua.completed_at.isoformat() if ua.completed_at else None,
                    "points": self.achievements[ua.achievement_id].points,
                    "icon": self.achievements[ua.achievement_id].badge_icon
                }
                for ua in sorted(
                    [ua for ua in user_achs if ua.is_completed],
                    key=lambda x: x.completed_at or datetime.min,
                    reverse=True
                )[:5]
            ]
        }
    
    async def claim_reward(self, user_id: str, achievement_id: str) -> Dict[str, Any]:
        """Claim rewards for a completed achievement"""
        user_achs = self.user_achievements.get(user_id, [])
        user_ach = next((ua for ua in user_achs if ua.achievement_id == achievement_id), None)
        
        if not user_ach:
            return {"error": "Achievement not found"}
        
        if not user_ach.is_completed:
            return {"error": "Achievement not yet completed"}
        
        if user_ach.rewards_claimed:
            return {"error": "Rewards already claimed"}
        
        achievement = self.achievements[achievement_id]
        
        user_ach.rewards_claimed = True
        user_ach.claimed_at = datetime.utcnow()
        
        return {
            "success": True,
            "achievement": achievement.name,
            "points_earned": achievement.points,
            "cashback_reward": f"{achievement.reward_cashback_pct}% extra cashback for 30 days" if achievement.reward_cashback_pct else None
        }
