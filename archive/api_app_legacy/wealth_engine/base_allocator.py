"""Base Allocator Interface - All allocators must implement this"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class AllocationStrategy(Enum):
    ADAPTIVE = "adaptive"                          # Threshold-based progression
    HOLISTIC = "holistic"                          # All-module orchestration
    AGGRESSIVE_GROWTH = "aggressive_growth"        # High risk, high return
    CONSERVATIVE_PRESERVATION = "conservative"     # Capital preservation
    MULTI_POT = "multi_pot"                          # Cross-platform coordination
    AI_OPTIMIZED = "ai_optimized"                    # ML-driven selection

@dataclass
class UserProfile:
    user_id: str
    employment_type: str      # 'stable', 'variable', 'gig', 'unemployed'
    monthly_income_avg: float
    monthly_income_min: float
    monthly_income_max: float
    risk_tolerance: str       # 'conservative', 'moderate', 'aggressive'
    time_horizon_years: int
    current_capital: float
    target_capital: float
    preferences: Dict[str, Any]
    constraints: Dict[str, Any]

@dataclass
class AllocationDecision:
    timestamp: datetime
    amount: float
    source: str
    strategy: AllocationStrategy
    allocations: List[Dict]
    expected_return_annual: float
    risk_score: float
    liquidity_score: float
    confidence: float
    reasoning: str

class BaseAllocator(ABC):
    """Abstract base class for all wealth allocators"""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.allocation_history = []
        self.performance_metrics = {}
    
    @abstractmethod
    def can_allocate(self, amount: float) -> bool:
        """Check if this allocator can handle given amount"""
        pass
    
    @abstractmethod
    def allocate(self, amount: float, context: Dict) -> AllocationDecision:
        """Make allocation decision"""
        pass
    
    @abstractmethod
    def get_recommended_capital_range(self) -> tuple:
        """Return (min, max) capital this allocator works best with"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Human-readable name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Description of strategy"""
        pass
    
    def track_allocation(self, decision: AllocationDecision):
        """Track allocation for performance analysis"""
        self.allocation_history.append(decision)
    
    def get_performance(self) -> Dict:
        """Calculate performance metrics"""
        if not self.allocation_history:
            return {}
        
        returns = [d.expected_return_annual for d in self.allocation_history]
        return {
            'avg_expected_return': sum(returns) / len(returns) if returns else 0,
            'total_allocations': len(self.allocation_history),
            'total_capital_allocated': sum(d.amount for d in self.allocation_history)
        }
