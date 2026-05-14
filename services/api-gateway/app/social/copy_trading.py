"""
Copy Trading System
Enables users to copy trades of successful investors
Inspired by eToro's popular investor program
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio


class RiskLevel(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class PopularInvestor:
    """Top trader that others can copy"""
    user_id: str
    username: str
    display_name: str
    bio: str
    risk_level: RiskLevel
    
    # Performance metrics
    total_return_12m: float
    total_return_all_time: float
    monthly_returns: List[float] = field(default_factory=list)
    
    # Risk metrics
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    
    # Social metrics
    copiers_count: int = 0
    total_copied_amount: float = 0.0
    followers: int = 0
    
    # Trading style
    preferred_assets: List[str] = field(default_factory=list)
    average_holding_period: str = "medium"  # short/medium/long
    trading_frequency: str = "moderate"  # low/moderate/high
    
    # Verification & badges
    is_verified: bool = False
    badges: List[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    joined_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        score = 0
        
        # Return component (40%)
        score += min(self.total_return_12m * 100, 40)
        
        # Risk component (30%)
        if self.max_drawdown < 0.1:
            score += 30
        elif self.max_drawdown < 0.2:
            score += 20
        elif self.max_drawdown < 0.3:
            score += 10
        
        # Win rate component (20%)
        score += self.win_rate * 20
        
        # Popularity component (10%)
        score += min(self.copiers_count / 100, 10)
        
        return min(score, 100)


@dataclass
class CopyRelationship:
    """Tracks a copier -> popular investor relationship"""
    copier_id: str
    popular_investor_id: str
    
    # Copy settings
    amount_allocated: float
    max_trade_size: Optional[float] = None
    stop_loss_percentage: Optional[float] = None
    copy_proportional: bool = True  # Copy same % of portfolio
    copy_open_trades: bool = True
    
    # Performance tracking
    started_at: datetime = field(default_factory=datetime.utcnow)
    total_profit_loss: float = 0.0
    total_return_pct: float = 0.0
    fees_paid: float = 0.0
    
    # Status
    is_active: bool = True
    paused_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    stop_reason: Optional[str] = None


class CopyTradingManager:
    """
    Manages copy trading relationships and trade replication
    """
    
    def __init__(self):
        self.popular_investors: Dict[str, PopularInvestor] = {}
        self.copy_relationships: Dict[str, CopyRelationship] = {}
        self.pending_trades: asyncio.Queue = asyncio.Queue()
        
        # Revenue sharing config
        self.revenue_share_tiers = {
            "tier_1": {"min_copiers": 1, "max_copiers": 100, "share_pct": 0.50},
            "tier_2": {"min_copiers": 101, "max_copiers": 500, "share_pct": 0.60},
            "tier_3": {"min_copiers": 501, "max_copiers": 2000, "share_pct": 0.70},
            "tier_4": {"min_copiers": 2001, "max_copiers": float('inf'), "share_pct": 0.80}
        }
    
    async def register_popular_investor(
        self,
        user_id: str,
        username: str,
        display_name: str,
        bio: str,
        risk_level: RiskLevel,
        performance_history: Dict[str, Any]
    ) -> PopularInvestor:
        """
        Register a user as a popular investor
        
        Requirements:
        - Minimum 3 months trading history
        - Positive returns
        - Verified identity
        """
        investor = PopularInvestor(
            user_id=user_id,
            username=username,
            display_name=display_name,
            bio=bio,
            risk_level=risk_level,
            total_return_12m=performance_history.get("return_12m", 0),
            total_return_all_time=performance_history.get("return_all_time", 0),
            max_drawdown=performance_history.get("max_drawdown", 0),
            sharpe_ratio=performance_history.get("sharpe_ratio", 0),
            win_rate=performance_history.get("win_rate", 0),
            is_verified=True,
            badges=["verified_trader"]
        )
        
        self.popular_investors[user_id] = investor
        return investor
    
    async def start_copying(
        self,
        copier_id: str,
        popular_investor_id: str,
        amount: float,
        copy_settings: Optional[Dict] = None
    ) -> CopyRelationship:
        """
        Start copying a popular investor
        
        Args:
            copier_id: User who wants to copy
            popular_investor_id: Investor to copy
            amount: Amount to allocate for copying
            copy_settings: Optional copy configuration
        """
        if popular_investor_id not in self.popular_investors:
            raise ValueError("Popular investor not found")
        
        investor = self.popular_investors[popular_investor_id]
        
        # Minimum copy amount check
        if amount < 200:
            raise ValueError("Minimum copy amount is $200")
        
        relationship = CopyRelationship(
            copier_id=copier_id,
            popular_investor_id=popular_investor_id,
            amount_allocated=amount,
            max_trade_size=copy_settings.get("max_trade_size") if copy_settings else None,
            stop_loss_percentage=copy_settings.get("stop_loss_pct") if copy_settings else None,
            copy_proportional=copy_settings.get("copy_proportional", True) if copy_settings else True,
            copy_open_trades=copy_settings.get("copy_open_trades", True) if copy_settings else True
        )
        
        # Store relationship
        rel_id = f"{copier_id}_{popular_investor_id}"
        self.copy_relationships[rel_id] = relationship
        
        # Update investor stats
        investor.copiers_count += 1
        investor.total_copied_amount += amount
        
        return relationship
    
    async def replicate_trade(
        self,
        popular_investor_id: str,
        trade: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Replicate a trade for all copiers
        
        Called when popular investor makes a trade
        """
        replicated_trades = []
        
        # Find all active copy relationships
        active_relationships = [
            rel for rel in self.copy_relationships.values()
            if rel.popular_investor_id == popular_investor_id and rel.is_active
        ]
        
        for rel in active_relationships:
            # Calculate copy size
            if rel.copy_proportional:
                # Copy same percentage of portfolio
                copy_size = trade["amount"] * (rel.amount_allocated / trade["investor_total_portfolio"])
            else:
                # Fixed amount copy
                copy_size = trade["amount"]
            
            # Apply max trade size limit
            if rel.max_trade_size and copy_size > rel.max_trade_size:
                copy_size = rel.max_trade_size
            
            replicated_trade = {
                "copier_id": rel.copier_id,
                "original_trade": trade,
                "copy_size": copy_size,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            }
            
            await self.pending_trades.put(replicated_trade)
            replicated_trades.append(replicated_trade)
        
        return replicated_trades
    
    async def stop_copying(
        self,
        copier_id: str,
        popular_investor_id: str,
        reason: str = "manual"
    ) -> Dict[str, Any]:
        """Stop copying a popular investor"""
        rel_id = f"{copier_id}_{popular_investor_id}"
        
        if rel_id not in self.copy_relationships:
            raise ValueError("Copy relationship not found")
        
        rel = self.copy_relationships[rel_id]
        rel.is_active = False
        rel.stopped_at = datetime.utcnow()
        rel.stop_reason = reason
        
        # Update investor stats
        investor = self.popular_investors[popular_investor_id]
        investor.copiers_count -= 1
        investor.total_copied_amount -= rel.amount_allocated
        
        return {
            "relationship_id": rel_id,
            "total_return": rel.total_return_pct,
            "fees_paid": rel.fees_paid,
            "duration_days": (rel.stopped_at - rel.started_at).days,
            "reason": reason
        }
    
    async def get_popular_investors(
        self,
        risk_filter: Optional[RiskLevel] = None,
        sort_by: str = "performance",
        limit: int = 20
    ) -> List[PopularInvestor]:
        """Get list of popular investors for discovery"""
        investors = list(self.popular_investors.values())
        
        # Filter by risk
        if risk_filter:
            investors = [i for i in investors if i.risk_level == risk_filter]
        
        # Filter active only
        investors = [i for i in investors if i.is_active]
        
        # Sort
        if sort_by == "performance":
            investors.sort(key=lambda x: x.total_return_12m, reverse=True)
        elif sort_by == "copiers":
            investors.sort(key=lambda x: x.copiers_count, reverse=True)
        elif sort_by == "score":
            investors.sort(key=lambda x: x.get_performance_score(), reverse=True)
        
        return investors[:limit]
    
    async def get_copy_performance(
        self,
        copier_id: str,
        popular_investor_id: str
    ) -> Dict[str, Any]:
        """Get performance of a copy relationship"""
        rel_id = f"{copier_id}_{popular_investor_id}"
        
        if rel_id not in self.copy_relationships:
            return {"error": "Relationship not found"}
        
        rel = self.copy_relationships[rel_id]
        investor = self.popular_investors[popular_investor_id]
        
        return {
            "copier_id": copier_id,
            "popular_investor": {
                "id": investor.user_id,
                "name": investor.display_name,
                "return_12m": investor.total_return_12m
            },
            "amount_allocated": rel.amount_allocated,
            "total_pnl": rel.total_profit_loss,
            "total_return_pct": rel.total_return_pct,
            "fees_paid": rel.fees_paid,
            "started_at": rel.started_at.isoformat(),
            "is_active": rel.is_active,
            "duration_days": (datetime.utcnow() - rel.started_at).days if rel.is_active else (rel.stopped_at - rel.started_at).days
        }
    
    async def calculate_revenue_share(
        self,
        popular_investor_id: str,
        period_fees: float
    ) -> Dict[str, float]:
        """Calculate revenue share for a popular investor"""
        investor = self.popular_investors.get(popular_investor_id)
        if not investor:
            return {"error": "Investor not found"}
        
        # Determine tier
        tier = None
        for tier_name, tier_config in self.revenue_share_tiers.items():
            if tier_config["min_copiers"] <= investor.copiers_count <= tier_config["max_copiers"]:
                tier = tier_config
                break
        
        if not tier:
            tier = self.revenue_share_tiers["tier_1"]
        
        share_amount = period_fees * tier["share_pct"]
        
        return {
            "total_fees": period_fees,
            "investor_share_pct": tier["share_pct"],
            "investor_share_amount": share_amount,
            "platform_share_amount": period_fees - share_amount,
            "tier": tier_name if tier else "unknown",
            "copiers_count": investor.copiers_count
        }
