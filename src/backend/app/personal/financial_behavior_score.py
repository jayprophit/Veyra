"""
Financial Behavior Scoring & Gamification
Track financial habits, assign scores, provide achievements and streaks
NOT China's social credit - this is personal financial wellness tracking
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal
from datetime import datetime, date, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ScoreCategory(Enum):
    SAVINGS = "savings"
    BUDGET = "budget"
    DEBT = "debt"
    INVESTING = "investing"
    LITERACY = "literacy"
    SECURITY = "security"
    TAX_EFFICIENCY = "tax_efficiency"
    EMERGENCY_PREP = "emergency_prep"


class AchievementTier(Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass
class Achievement:
    id: str
    name: str
    description: str
    tier: AchievementTier
    category: ScoreCategory
    criteria: str
    date_earned: Optional[datetime] = None
    icon: str = "🏆"
    points: int = 100


@dataclass
class Streak:
    category: str
    current_days: int
    longest_days: int
    last_activity: datetime
    description: str


@dataclass
class ScoreComponent:
    category: ScoreCategory
    score: int  # 0-100
    weight: float
    details: Dict[str, Any]
    last_updated: datetime
    trend: str  # improving, stable, declining


@dataclass
class FinancialProfile:
    overall_score: int
    percentile: int  # vs other users
    components: Dict[ScoreCategory, ScoreComponent]
    achievements: List[Achievement]
    streaks: List[Streak]
    recent_milestones: List[str]
    next_goals: List[str]
    level: int
    xp: int
    title: str  # Novice, Apprentice, Journeyman, Expert, Master


class FinancialBehaviorScorer:
    """Calculate personal financial wellness scores"""
    
    # Score weights (total = 1.0)
    WEIGHTS = {
        ScoreCategory.SAVINGS: 0.20,
        ScoreCategory.BUDGET: 0.15,
        ScoreCategory.DEBT: 0.15,
        ScoreCategory.INVESTING: 0.15,
        ScoreCategory.TAX_EFFICIENCY: 0.10,
        ScoreCategory.EMERGENCY_PREP: 0.10,
        ScoreCategory.SECURITY: 0.10,
        ScoreCategory.LITERACY: 0.05
    }
    
    def __init__(self):
        self.user_data: Dict[str, Any] = {}
        self.achievements_db = self._init_achievements()
        self.user_achievements: Set[str] = set()
        self.streaks: Dict[str, Streak] = {}
        self.activity_log: List[Dict[str, Any]] = []
        
    def _init_achievements(self) -> Dict[str, Achievement]:
        """Initialize achievement database"""
        return {
            # Savings Achievements
            "first_saved": Achievement("first_saved", "First Steps", "Save £100", AchievementTier.BRONZE, ScoreCategory.SAVINGS, "savings >= 100", icon="💰"),
            "savings_starter": Achievement("savings_starter", "Starter Saver", "Save £1,000", AchievementTier.SILVER, ScoreCategory.SAVINGS, "savings >= 1000", icon="💎"),
            "savings_builder": Achievement("savings_builder", "Wealth Builder", "Save £10,000", AchievementTier.GOLD, ScoreCategory.SAVINGS, "savings >= 10000", icon="🏦"),
            "savings_master": Achievement("savings_master", "Savings Master", "Save £50,000", AchievementTier.PLATINUM, ScoreCategory.SAVINGS, "savings >= 50000", icon="👑"),
            "six_month_emergency": Achievement("six_month_emergency", "Rainy Day Ready", "Build 6-month emergency fund", AchievementTier.GOLD, ScoreCategory.EMERGENCY_PREP, "emergency_fund_months >= 6", icon="☂️"),
            
            # Budget Achievements
            "budget_beginner": Achievement("budget_beginner", "Budget Beginner", "Stay under budget for 1 month", AchievementTier.BRONZE, ScoreCategory.BUDGET, "under_budget_months >= 1", icon="📊"),
            "budget_pro": Achievement("budget_pro", "Budget Pro", "Stay under budget for 6 months", AchievementTier.SILVER, ScoreCategory.BUDGET, "under_budget_months >= 6", icon="📈"),
            "no_spend_week": Achievement("no_spend_week", "No-Spend Hero", "Complete 7-day no-spend challenge", AchievementTier.SILVER, ScoreCategory.BUDGET, "no_spend_streak >= 7", icon="🚫"),
            
            # Debt Achievements
            "debt_free": Achievement("debt_free", "Debt Free!", "Pay off all debts", AchievementTier.PLATINUM, ScoreCategory.DEBT, "debt_balance == 0", icon="🆓"),
            "debt_slayer": Achievement("debt_slayer", "Debt Slayer", "Pay off £10,000 in debt", AchievementTier.GOLD, ScoreCategory.DEBT, "debt_paid >= 10000", icon="⚔️"),
            "first_debt_cleared": Achievement("first_debt_cleared", "First Victory", "Clear first debt", AchievementTier.SILVER, ScoreCategory.DEBT, "debts_cleared >= 1", icon="✅"),
            
            # Investing Achievements
            "first_investment": Achievement("first_investment", "Investor", "Make first investment", AchievementTier.BRONZE, ScoreCategory.INVESTING, "investment_made == true", icon="📈"),
            "dca_warrior": Achievement("dca_warrior", "DCA Warrior", "3 months of consistent investing", AchievementTier.SILVER, ScoreCategory.INVESTING, "dca_streak >= 3", icon="🔄"),
            "dca_legend": Achievement("dca_legend", "DCA Legend", "12 months of consistent investing", AchievementTier.GOLD, ScoreCategory.INVESTING, "dca_streak >= 12", icon="⭐"),
            "portfolio_diverse": Achievement("portfolio_diverse", "Diversified", "Hold 5+ different assets", AchievementTier.SILVER, ScoreCategory.INVESTING, "asset_count >= 5", icon="🌈"),
            "isa_maxed": Achievement("isa_maxed", "ISA Champion", "Max out ISA allowance", AchievementTier.GOLD, ScoreCategory.TAX_EFFICIENCY, "isa_contribution >= 20000", icon="🛡️"),
            "lisa_bonus": Achievement("lisa_bonus", "Bonus Winner", "Receive LISA government bonus", AchievementTier.SILVER, ScoreCategory.TAX_EFFICIENCY, "lisa_bonus_received > 0", icon="🎁"),
            
            # Literacy Achievements
            "quiz_whiz": Achievement("quiz_whiz", "Quiz Whiz", "Score 100% on financial quiz", AchievementTier.BRONZE, ScoreCategory.LITERACY, "quiz_perfect == true", icon="🎓"),
            "course_complete": Achievement("course_complete", "Course Graduate", "Complete financial course", AchievementTier.SILVER, ScoreCategory.LITERACY, "course_completed == true", icon="📜"),
            
            # Security Achievements
            "secure_account": Achievement("secure_account", "Fort Knox", "Enable 2FA on all accounts", AchievementTier.GOLD, ScoreCategory.SECURITY, "2fa_coverage == 100%", icon="🔒"),
            "password_master": Achievement("password_master", "Password Master", "All passwords strong + unique", AchievementTier.SILVER, ScoreCategory.SECURITY, "password_score >= 90", icon="🔑"),
        }
    
    def calculate_savings_score(
        self,
        savings_balance: Decimal,
        monthly_income: Decimal,
        savings_rate: Decimal,  # % of income saved
        consistency_months: int
    ) -> ScoreComponent:
        """Calculate savings behavior score"""
        score = 0
        details = {}
        
        # Savings rate scoring
        if savings_rate >= 20:
            score += 40
            details["savings_rate"] = "Excellent (20%+ saved)"
        elif savings_rate >= 10:
            score += 30
            details["savings_rate"] = "Good (10-20% saved)"
        elif savings_rate >= 5:
            score += 20
            details["savings_rate"] = "Fair (5-10% saved)"
        else:
            score += 10
            details["savings_rate"] = "Needs improvement (<5% saved)"
        
        # Consistency bonus
        consistency_score = min(consistency_months * 2, 30)
        score += consistency_score
        details["consistency_bonus"] = f"+{consistency_score} for {consistency_months} months consistency"
        
        # Emergency fund adequacy
        months_expenses = savings_balance / (monthly_income * Decimal("0.5")) if monthly_income > 0 else Decimal("0")
        if months_expenses >= 6:
            score += 30
            details["emergency_fund"] = "Excellent (6+ months)"
        elif months_expenses >= 3:
            score += 20
            details["emergency_fund"] = "Good (3-6 months)"
        elif months_expenses >= 1:
            score += 10
            details["emergency_fund"] = "Starter (1-3 months)"
        else:
            details["emergency_fund"] = "Critical (<1 month)"
        
        return ScoreComponent(
            category=ScoreCategory.SAVINGS,
            score=min(100, score),
            weight=self.WEIGHTS[ScoreCategory.SAVINGS],
            details=details,
            last_updated=datetime.now(),
            trend="improving" if consistency_months > 3 else "stable"
        )
    
    def calculate_debt_score(
        self,
        total_debt: Decimal,
        debt_to_income: Decimal,
        on_time_payment_streak: int,
        payoff_progress_percent: Decimal
    ) -> ScoreComponent:
        """Calculate debt management score"""
        score = 50  # Start at neutral
        details = {}
        
        # DTI scoring
        if debt_to_income <= 20:
            score += 25
            details["debt_to_income"] = "Excellent (under 20%)"
        elif debt_to_income <= 36:
            score += 15
            details["debt_to_income"] = "Good (20-36%)"
        elif debt_to_income <= 50:
            score += 0
            details["debt_to_income"] = "Fair (36-50%)"
        else:
            score -= 15
            details["debt_to_income"] = "Concerning (over 50%)"
        
        # Payment history
        if on_time_payment_streak >= 12:
            score += 25
            details["payment_history"] = "Perfect (12+ months on time)"
        elif on_time_payment_streak >= 6:
            score += 15
            details["payment_history"] = "Good (6-12 months)"
        elif on_time_payment_streak >= 3:
            score += 5
            details["payment_history"] = "Improving (3-6 months)"
        
        # Payoff progress
        progress_score = min(int(payoff_progress_percent / 2), 25)
        score += progress_score
        details["payoff_progress"] = f"+{progress_score} for {payoff_progress_percent:.1f}% paid off"
        
        return ScoreComponent(
            category=ScoreCategory.DEBT,
            score=max(0, min(100, score)),
            weight=self.WEIGHTS[ScoreCategory.DEBT],
            details=details,
            last_updated=datetime.now(),
            trend="improving" if on_time_payment_streak > 6 else "stable"
        )
    
    def check_achievements(self, user_data: Dict[str, Any]) -> List[Achievement]:
        """Check and award new achievements"""
        new_achievements = []
        
        for ach_id, achievement in self.achievements_db.items():
            if ach_id in self.user_achievements:
                continue
            
            # Check criteria
            earned = False
            criteria = achievement.criteria
            
            if "savings >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("savings_balance", 0) >= threshold:
                    earned = True
            
            elif "debt_balance == 0" in criteria:
                if user_data.get("total_debt", 1) == 0:
                    earned = True
            
            elif "debts_cleared >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("debts_cleared", 0) >= threshold:
                    earned = True
            
            elif "dca_streak >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("dca_streak", 0) >= threshold:
                    earned = True
            
            elif "under_budget_months >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("under_budget_months", 0) >= threshold:
                    earned = True
            
            elif "no_spend_streak >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("no_spend_streak", 0) >= threshold:
                    earned = True
            
            elif "isa_contribution >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("isa_contribution", 0) >= threshold:
                    earned = True
            
            elif "emergency_fund_months >= " in criteria:
                threshold = int(criteria.split(">= ")[1])
                if user_data.get("emergency_fund_months", 0) >= threshold:
                    earned = True
            
            if earned:
                achievement.date_earned = datetime.now()
                self.user_achievements.add(ach_id)
                new_achievements.append(achievement)
                logger.info(f"Achievement earned: {achievement.name} ({achievement.tier.value})")
        
        return new_achievements
    
    def update_streak(self, category: str, activity_completed: bool, description: str = ""):
        """Update activity streak"""
        now = datetime.now()
        
        if category not in self.streaks:
            self.streaks[category] = Streak(category, 0, 0, now, description)
        
        streak = self.streaks[category]
        
        if activity_completed:
            # Check if consecutive day
            if (now - streak.last_activity).days <= 1:
                streak.current_days += 1
                streak.longest_days = max(streak.longest_days, streak.current_days)
            else:
                streak.current_days = 1
            
            streak.last_activity = now
            
            logger.info(f"Streak updated: {category} = {streak.current_days} days")
        else:
            # Streak broken
            if streak.current_days > 0:
                logger.info(f"Streak broken: {category} (was {streak.current_days} days)")
            streak.current_days = 0
    
    def calculate_overall_score(self, user_data: Dict[str, Any]) -> FinancialProfile:
        """Calculate complete financial wellness profile"""
        components = {}
        
        # Calculate each component
        if "savings_balance" in user_data:
            components[ScoreCategory.SAVINGS] = self.calculate_savings_score(
                user_data["savings_balance"],
                user_data.get("monthly_income", Decimal("2500")),
                user_data.get("savings_rate", Decimal("10")),
                user_data.get("savings_consistency_months", 1)
            )
        
        if "total_debt" in user_data:
            components[ScoreCategory.DEBT] = self.calculate_debt_score(
                user_data["total_debt"],
                user_data.get("debt_to_income", Decimal("0")),
                user_data.get("on_time_payments", 0),
                user_data.get("payoff_progress", Decimal("0"))
            )
        
        # Calculate weighted overall score
        weighted_score = 0
        for component in components.values():
            weighted_score += component.score * component.weight
        
        # Fill missing categories with average
        missing_weight = sum(self.WEIGHTS[cat] for cat in ScoreCategory if cat not in components)
        if missing_weight > 0:
            avg_existing = sum(c.score for c in components.values()) / len(components) if components else 50
            weighted_score += avg_existing * missing_weight
        
        overall = int(weighted_score)
        
        # Determine percentile (mock - would be based on user database)
        percentile = min(99, max(1, overall - 10))
        
        # Determine level and title
        level = overall // 10
        titles = {
            0: "Novice", 1: "Beginner", 2: "Apprentice", 3: "Journeyman",
            4: "Adept", 5: "Expert", 6: "Specialist", 7: "Professional",
            8: "Master", 9: "Grandmaster", 10: "Legend"
        }
        title = titles.get(level, "Mystic")
        
        # Check for new achievements
        new_achievements = self.check_achievements(user_data)
        
        # Get all earned achievements
        earned_achievements = [
            self.achievements_db[ach_id] 
            for ach_id in self.user_achievements 
            if ach_id in self.achievements_db
        ]
        
        # Calculate XP
        xp = sum(a.points for a in earned_achievements)
        xp += overall * 10  # Score contributes to XP
        
        # Generate next goals
        next_goals = self._generate_goals(user_data, components)
        
        return FinancialProfile(
            overall_score=overall,
            percentile=percentile,
            components=components,
            achievements=earned_achievements + new_achievements,
            streaks=list(self.streaks.values()),
            recent_milestones=[f"Overall score: {overall}"],
            next_goals=next_goals,
            level=level,
            xp=xp,
            title=title
        )
    
    def _generate_goals(self, user_data: Dict[str, Any], components: Dict[ScoreCategory, ScoreComponent]) -> List[str]:
        """Generate personalized next goals"""
        goals = []
        
        # Find lowest scoring categories
        sorted_components = sorted(components.items(), key=lambda x: x[1].score)
        
        for cat, component in sorted_components[:3]:
            if component.score < 70:
                if cat == ScoreCategory.SAVINGS:
                    goals.append("Increase savings rate to 15%")
                elif cat == ScoreCategory.DEBT:
                    goals.append("Pay off highest interest debt")
                elif cat == ScoreCategory.BUDGET:
                    goals.append("Stay under budget for 1 month")
                elif cat == ScoreCategory.INVESTING:
                    goals.append("Start DCA with £20/month")
                elif cat == ScoreCategory.EMERGENCY_PREP:
                    goals.append("Build 3-month emergency fund")
                elif cat == ScoreCategory.TAX_EFFICIENCY:
                    goals.append("Open ISA before tax year end")
        
        # Achievement-based goals
        if "dca_warrior" not in self.user_achievements:
            goals.append("Maintain DCA streak for 3 months")
        
        if "six_month_emergency" not in self.user_achievements:
            goals.append("Build 6-month emergency fund")
        
        return goals[:5]  # Top 5 goals


# Global scorer instance
_behavior_scorer: Optional[FinancialBehaviorScorer] = None


def get_behavior_scorer() -> FinancialBehaviorScorer:
    """Get or create global behavior scorer"""
    global _behavior_scorer
    if _behavior_scorer is None:
        _behavior_scorer = FinancialBehaviorScorer()
    return _behavior_scorer
