"""
Automated Savings Rules Engine
Implements smart savings rules like round-ups, payday save, AI optimizer
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
import asyncio


class RuleType(Enum):
    ROUND_UP = "round_up"  # Round up transactions
    PAYDAY_SAVE = "payday_save"  # Save on payday
    PERCENTAGE = "percentage"  # Save % of income
    AI_OPTIMIZED = "ai_optimized"  # AI determines amount
    WEEKLY_CHALLENGE = "weekly_challenge"  # 52-week challenge
    SPARE_CHANGE = "spare_change"  # Save change from transactions
    GOAL_BASED = "goal_based"  # Save towards specific goal
    WEATHER = "weather"  # Save when it rains (round up more)
    FRIENDS = "friends"  # Save when friends save (social)


class RuleTrigger(Enum):
    TRANSACTION = "transaction"
    SCHEDULED = "scheduled"
    BALANCE_CHANGE = "balance_change"
    AI_PREDICTION = "ai_prediction"


@dataclass
class AutoSaveRule:
    """Automated savings rule configuration"""
    rule_id: str
    user_id: str
    rule_type: RuleType
    
    # Configuration
    name: str
    description: str
    is_active: bool = True
    
    # Amount settings
    base_amount: Optional[Decimal] = None  # Fixed amount
    percentage: Optional[float] = None  # Percentage of transaction
    round_to: Optional[int] = None  # Round to nearest (for round-ups)
    max_per_transaction: Optional[Decimal] = None
    max_per_day: Optional[Decimal] = None
    max_per_week: Optional[Decimal] = None
    
    # Trigger settings
    trigger: RuleTrigger = RuleTrigger.TRANSACTION
    schedule: Optional[str] = None  # Cron expression for scheduled
    
    # Target
    destination_account: str = "savings"
    goal_id: Optional[str] = None  # Link to specific goal
    
    # Filters
    min_transaction_amount: Optional[Decimal] = None
    max_transaction_amount: Optional[Decimal] = None
    categories_include: Optional[List[str]] = None
    categories_exclude: Optional[List[str]] = None
    merchants_include: Optional[List[str]] = None
    merchants_exclude: Optional[List[str]] = None
    
    # Stats
    total_saved: Decimal = Decimal("0")
    transactions_count: int = 0
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class SavedAmount:
    """Record of automated savings"""
    id: str
    rule_id: str
    user_id: str
    amount: Decimal
    source_transaction_id: Optional[str]
    source_description: str
    saved_at: datetime
    destination: str


class SavingsRulesEngine:
    """
    Manages and executes automated savings rules
    Inspired by Plum, Chip, Monzo, Cleo
    """
    
    def __init__(self):
        self.rules: Dict[str, AutoSaveRule] = {}
        self.saved_amounts: List[SavedAmount] = []
        self.daily_limits: Dict[str, Decimal] = {}  # user_id -> amount today
        self.weekly_limits: Dict[str, Decimal] = {}  # user_id -> amount this week
        
        # Rule type handlers
        self.rule_handlers: Dict[RuleType, Callable] = {
            RuleType.ROUND_UP: self._handle_round_up,
            RuleType.PAYDAY_SAVE: self._handle_payday_save,
            RuleType.PERCENTAGE: self._handle_percentage,
            RuleType.AI_OPTIMIZED: self._handle_ai_optimized,
            RuleType.WEEKLY_CHALLENGE: self._handle_weekly_challenge,
            RuleType.SPARE_CHANGE: self._handle_spare_change,
            RuleType.GOAL_BASED: self._handle_goal_based,
        }
    
    async def create_rule(
        self,
        user_id: str,
        rule_type: RuleType,
        name: str,
        config: Dict[str, Any]
    ) -> AutoSaveRule:
        """
        Create a new automated savings rule
        
        Examples:
        - Round up to nearest $1
        - Save 10% of salary on payday
        - AI-optimized savings based on spending patterns
        """
        rule = AutoSaveRule(
            rule_id=f"rule_{user_id}_{rule_type.value}_{datetime.utcnow().timestamp()}",
            user_id=user_id,
            rule_type=rule_type,
            name=name,
            description=config.get("description", ""),
            base_amount=Decimal(str(config["base_amount"])) if "base_amount" in config else None,
            percentage=config.get("percentage"),
            round_to=config.get("round_to"),
            max_per_transaction=Decimal(str(config["max_per_transaction"])) if "max_per_transaction" in config else None,
            max_per_day=Decimal(str(config["max_per_day"])) if "max_per_day" in config else None,
            max_per_week=Decimal(str(config["max_per_week"])) if "max_per_week" in config else None,
            trigger=RuleTrigger(config.get("trigger", "transaction")),
            destination_account=config.get("destination", "savings"),
            goal_id=config.get("goal_id")
        )
        
        self.rules[rule.rule_id] = rule
        return rule
    
    async def process_transaction(
        self,
        user_id: str,
        transaction: Dict[str, Any]
    ) -> List[SavedAmount]:
        """
        Process a transaction and apply matching savings rules
        
        Called when user makes any transaction
        """
        saved_amounts = []
        
        # Find active rules for user
        user_rules = [
            r for r in self.rules.values()
            if r.user_id == user_id and r.is_active and r.trigger == RuleTrigger.TRANSACTION
        ]
        
        for rule in user_rules:
            # Check filters
            if not self._passes_filters(rule, transaction):
                continue
            
            # Calculate amount to save
            handler = self.rule_handlers.get(rule.rule_type)
            if handler:
                amount = await handler(rule, transaction)
                
                if amount and amount > 0:
                    # Check limits
                    amount = self._apply_limits(user_id, rule, amount)
                    
                    if amount > 0:
                        saved = SavedAmount(
                            id=f"save_{datetime.utcnow().timestamp()}",
                            rule_id=rule.rule_id,
                            user_id=user_id,
                            amount=amount,
                            source_transaction_id=transaction.get("id"),
                            source_description=transaction.get("description", ""),
                            saved_at=datetime.utcnow(),
                            destination=rule.destination_account
                        )
                        
                        self.saved_amounts.append(saved)
                        saved_amounts.append(saved)
                        
                        # Update rule stats
                        rule.total_saved += amount
                        rule.transactions_count += 1
                        rule.last_triggered = datetime.utcnow()
        
        return saved_amounts
    
    async def _handle_round_up(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Round up transaction to nearest amount"""
        amount = Decimal(str(transaction.get("amount", 0)))
        
        if amount <= 0:
            return None
        
        round_to = rule.round_to or 1  # Default to nearest dollar
        rounded = (amount / round_to).quantize(1) * round_to
        saved = rounded - amount
        
        if saved > 0:
            return saved
        
        return None
    
    async def _handle_payday_save(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Save on payday when salary/income received"""
        description = transaction.get("description", "").lower()
        
        # Detect payday keywords
        payday_keywords = ["salary", "payroll", "wage", "income", "deposit"]
        
        if any(kw in description for kw in payday_keywords):
            amount = Decimal(str(transaction.get("amount", 0)))
            
            if rule.percentage:
                return (amount * Decimal(str(rule.percentage)) / 100).quantize(Decimal("0.01"))
            elif rule.base_amount:
                return rule.base_amount
        
        return None
    
    async def _handle_percentage(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Save percentage of each transaction"""
        if not rule.percentage:
            return None
        
        amount = Decimal(str(transaction.get("amount", 0)))
        
        if amount > 0:
            saved = (amount * Decimal(str(rule.percentage)) / 100).quantize(Decimal("0.01"))
            return saved
        
        return None
    
    async def _handle_ai_optimized(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """AI determines optimal amount to save"""
        # In production: Use ML model to predict safe-to-save amount
        # Based on: account balance, upcoming bills, spending patterns, income
        
        # Mock AI calculation
        account_balance = Decimal("5000")  # Would be fetched from account
        upcoming_bills = Decimal("1200")  # Would be calculated from bills
        
        safe_to_save = (account_balance - upcoming_bills) * Decimal("0.05")  # Save 5% of safe buffer
        
        if safe_to_save > 10:
            return min(safe_to_save, Decimal("50"))  # Cap at $50 per transaction
        
        return None
    
    async def _handle_weekly_challenge(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """52-week challenge: week 1 = $1, week 2 = $2, etc."""
        week_number = datetime.utcnow().isocalendar()[1]
        return Decimal(str(week_number))
    
    async def _handle_spare_change(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Save spare change (decimal part)"""
        amount = Decimal(str(transaction.get("amount", 0)))
        
        if amount > 0:
            change = amount % 1  # Decimal part
            if change > 0:
                return change
        
        return None
    
    async def _handle_goal_based(
        self,
        rule: AutoSaveRule,
        transaction: Dict[str, Any]
    ) -> Optional[Decimal]:
        """Save towards a specific goal"""
        if not rule.goal_id:
            return None
        
        # In production: Calculate based on goal deadline and current progress
        return rule.base_amount
    
    def _passes_filters(self, rule: AutoSaveRule, transaction: Dict[str, Any]) -> bool:
        """Check if transaction passes rule filters"""
        amount = Decimal(str(transaction.get("amount", 0)))
        
        # Min/max amount filters
        if rule.min_transaction_amount and amount < rule.min_transaction_amount:
            return False
        if rule.max_transaction_amount and amount > rule.max_transaction_amount:
            return False
        
        # Category filters
        category = transaction.get("category", "").lower()
        if rule.categories_include and category not in [c.lower() for c in rule.categories_include]:
            return False
        if rule.categories_exclude and category in [c.lower() for c in rule.categories_exclude]:
            return False
        
        return True
    
    def _apply_limits(
        self,
        user_id: str,
        rule: AutoSaveRule,
        amount: Decimal
    ) -> Decimal:
        """Apply daily/weekly/transaction limits"""
        # Per transaction limit
        if rule.max_per_transaction and amount > rule.max_per_transaction:
            amount = rule.max_per_transaction
        
        # Daily limit tracking
        today = datetime.utcnow().date()
        daily_key = f"{user_id}_{today}"
        current_daily = self.daily_limits.get(daily_key, Decimal("0"))
        
        if rule.max_per_day:
            remaining_daily = rule.max_per_day - current_daily
            if amount > remaining_daily:
                amount = max(remaining_daily, Decimal("0"))
        
        self.daily_limits[daily_key] = current_daily + amount
        
        return amount
    
    async def get_savings_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of automated savings for user"""
        user_rules = [r for r in self.rules.values() if r.user_id == user_id]
        user_savings = [s for s in self.saved_amounts if s.user_id == user_id]
        
        total_saved = sum(s.amount for s in user_savings)
        
        # Calculate this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        this_month = sum(s.amount for s in user_savings if s.saved_at >= month_start)
        
        return {
            "user_id": user_id,
            "total_saved": float(total_saved),
            "this_month": float(this_month),
            "active_rules": len([r for r in user_rules if r.is_active]),
            "total_transactions": len(user_savings),
            "rules_summary": [
                {
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "type": r.rule_type.value,
                    "total_saved": float(r.total_saved),
                    "is_active": r.is_active
                }
                for r in user_rules
            ]
        }
